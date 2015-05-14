__author__ = 'Matthew'

from abstract_node import Var

from time import sleep
import numpy as np
import random
from collections import deque
from time import clock
from collections import deque


class Robot(object):

    def __init__(self, in_vars: list, out_vars: list, **config_kwargs):

        # default configurations
        self.config = dict()
        self._set_default_config()
        # custom configurations
        for param, value in config_kwargs.items():
            self.config[param] = value

        # construct the input and output variables
        self.in_vars = []
        for var in in_vars:
            if not isinstance(var, Var):
                raise TypeError('CBLA Engine only accepts Var type as sensor variable')
            self.in_vars.append(var)

        self.out_vars = []
        for var in out_vars:
            if not isinstance(var, Var):
                raise TypeError('CBLA Engine only accepts Var type as motor variable')
            self.out_vars.append(var)

        # the current wait_time
        self.curr_wait_time = self.config['wait_time']

        # idle mode related variables
        self.prev_rewards = deque(maxlen=self.config['prev_rewards_deque_size'])
        self.in_idle_mode = False
        self.step_in_active_mode = 0

        # compute initial action
        self.M0 = Var(self.compute_initial_motor())
        self.S0 = Var(None)

    def _set_default_config(self):
        self.config['wait_time'] = 0.05
        self.config['prev_rewards_deque_size'] = 10
        self.config['activation_reward_delta'] = 0.5
        self.config['activation_reward'] = 0.05
        self.config['idling_reward'] = -0.01
        self.config['min_step_before_idling'] = 200
        self.config['idling_prob'] = 0.98

    def compute_initial_motor(self) -> tuple:
        # compute the motor variables
        M0 = []
        for var in self.out_vars:
            M0.append(var.val)
        return tuple(M0)

    def act(self, M: tuple):

        # copy the selected action to the memory
        if not isinstance(M, (list, tuple)):
            raise TypeError("M must be a tuple or list!")
        if len(M) != len(self.out_vars):
            raise ValueError("M and out_var must be the same length!")

        # compute the actual output variable
        for i in range(len(self.out_vars)):
            self.out_vars[i].val = M[i]

        self.M0.val = tuple(M)
        return self.out_vars

    def wait(self):
        sleep(max(0, self.curr_wait_time))

    def read(self) -> tuple:
        # compute the sensor variables
        S = []
        for i in range(len(self.in_vars)):
            s = self.in_vars[i].val
            # normalize if the range is specified
            if 'in_vars_range' in self.config:
                val_range = self.config['in_vars_range'][i]
                if isinstance(val_range, tuple) and len(val_range) == 2:
                    s = normalize(self.in_vars[i].val, val_range[0], val_range[1])
            S.append(s)
        self.S0.val = tuple(S)
        return tuple(S)

    def get_possible_action(self, num_sample=100) -> tuple:

        num_dim = len(self.M0.val)

        X = np.zeros((num_sample, num_dim))

        for i in range(num_sample):
            for x_dim in range(num_dim):
                X[i, x_dim - 1] = random.randint(0, 255)

        M_candidates = tuple(set((map(tuple, X))))

        return M_candidates

    def enter_idle_mode(self, reward) -> bool:

        # if it is in idle mode and reward is high enough to exit idle mode
        if len(self.prev_rewards) > 2:
            rewards_delta = np.fabs(reward - np.mean(list(self.prev_rewards)))
        else:
            rewards_delta = 0

        # if isinstance(self, Robot_Frond):
        #     print('Reward: %f;   activation: %f' % (reward, self.config['activation_reward'] ))
        if self.in_idle_mode and (reward > self.config['activation_reward']
                                  or rewards_delta > self.config['activation_reward_delta']
                                  ):
            self.in_idle_mode = False
            self.step_in_active_mode = 0

        # if it is in active more and condition for entering idle mode is reached
        elif not self.in_idle_mode and reward < self.config['idling_reward'] and self.step_in_active_mode > self.config['min_step_before_idling']:
            self.in_idle_mode = True
            self.step_in_active_mode = 0

        # if it's in active mode
        elif not self.in_idle_mode:
            self.step_in_active_mode += 1

        # save the reward value to memory
        self.prev_rewards.append(reward)

        return self.in_idle_mode

    def is_doing_idle_action(self) -> bool:

        if self.in_idle_mode and random.random() < self.config['idling_prob']:
            return True
        else:
            return False

    def is_in_idle_mode(self) -> bool:
        return self.in_idle_mode

    def get_idle_action(self) -> tuple:
        return tuple([0] * len(self.M0.val))


class Robot_Frond(Robot):

    def _set_default_config(self):
        super(Robot_Frond, self)._set_default_config()

        self.config['activation_reward_delta'] = 0.03
        self.config['activation_reward'] = 0.015
        self.config['idling_reward'] = 0.000001
        self.config['min_step_before_idling'] = 1
        self.config['idling_prob'] = 0.999

    def get_possible_action(self, num_sample=10):
        # constructing a list of all possible action
        x_dim = len(self.M0.val)
        X = list(range(0, 4 ** x_dim))
        for i in range(len(X)):
            X[i] = toDigits(X[i], 4)
            filling = [0] * (x_dim - len(X[i]))
            X[i] = filling + X[i]

        M_candidates = tuple(set(map(tuple, X)))

        try:
            return tuple(random.sample(M_candidates, num_sample))
        except ValueError:
            return M_candidates


class Robot_Frond_0(Robot_Frond):

    def __init__(self, in_vars: list, out_vars: list, **config_kwargs):

        super(Robot_Frond_0, self).__init__(in_vars, out_vars, **config_kwargs)

        self.S_memory = deque(maxlen=self.config['sample_window'])

    def _set_default_config(self):
        super(Robot_Frond_0, self)._set_default_config()

        self.config['activation_reward_delta'] = 0.006
        self.config['activation_reward'] = 0.003
        self.config['idling_reward'] = 0.00001
        self.config['min_step_before_idling'] = 15
        self.config['idling_prob'] = 0.999

        self.config['sample_window'] = 10
        self.config['sample_period'] = 0.1

    def read(self) -> tuple:

        # making sure sample_period does not exceed the messenger reading speed
        sample_period = max(self.config['sample_period'], self.config['wait_time'])

        # compute the sensor variables
        for step in range(self.config['sample_window']):
            t0 = clock()
            S = []
            for i in range(len(self.in_vars)):
                s = self.in_vars[i].val

                # normalize if the range is specified
                if 'in_vars_range' in self.config:
                    val_range = self.config['in_vars_range'][i]
                    if isinstance(val_range, tuple) and len(val_range) == 2:
                        s = normalize(self.in_vars[i].val, val_range[0], val_range[1])
                S.append(s)

            # store into memory
            self.S_memory.append(tuple(S))

            # if first run
            if self.S0.val is None:
                break

            # wait for next period
            if step < self.config['sample_window'] - 1:
                sleep(max(0, sample_period - (clock() - t0)))

        # compute average
        S_mean = []
        s_zipped = zip(*list(self.S_memory))
        for s in s_zipped:
            S_mean.append(np.average(s))

        self.S0.val = tuple(S_mean)
        return tuple(S_mean)



class Robot_Protocell(Robot):

    def _set_default_config(self):
        super(Robot_Protocell, self)._set_default_config()
        self.config['wait_time'] = 0.1
        self.config['activation_reward_delta'] = 0.2
        self.config['activation_reward'] = 0.06
        self.config['idling_reward'] = 0.01
        self.config['min_step_before_idling'] = 20
        self.config['idling_prob'] = 0.999

    def get_possible_action(self, num_sample=5) -> tuple:

        num_dim = len(self.M0.val)

        X = np.zeros((num_sample, num_dim))

        for i in range(num_sample):
            for x_dim in range(num_dim):
                X[i, x_dim - 1] = random.randint(0, 100)

        M_candidates = tuple(set((map(tuple, X))))

        return M_candidates


def toDigits(n, b) -> list:
    """Convert a positive number n to its digit representation in base b."""
    digits = []
    while n > 0:
        digits.insert(0, n % b)
        n = n // b

    return digits


def normalize(orig_val: float, low_bound: float, hi_bound: float) -> float:

    if low_bound >= hi_bound:
        raise ValueError("Lower Bound cannot be greater than or equal to the Upper Bound!")

    return (orig_val - low_bound)/(hi_bound - low_bound)
