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
        self.sample_speed_limit = 0.0
        self.curr_wait_time = max(self.sample_speed_limit, self.config['wait_time'])

        # idle mode related variables
        self.prev_rewards = deque(maxlen=self.config['prev_rewards_deque_size'])
        self.in_idle_mode = False
        self.step_in_active_mode = 0

        # compute initial action
        self.M0 = Var(self.compute_initial_motor())
        self.S0 = Var(None)

    def _set_default_config(self):
        self.config['wait_time'] = 0.05
        self.config['sample_number'] = 10
        self.config['sample_period'] = 0.1

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

    def get_possible_action(self, num_sample=50) -> tuple:

        num_dim = len(self.M0.val)

        X = np.zeros((num_sample, num_dim))

        for i in range(num_sample):
            for x_dim in range(num_dim):
                X[i, x_dim - 1] = random.random()

        M_candidates = tuple(set((map(tuple, X))))

        return M_candidates

    def act(self, M: tuple):

        # copy the selected action to the memory
        if not isinstance(M, (list, tuple)):
            raise TypeError("M must be a tuple or list!")
        if len(M) != len(self.out_vars):
            raise ValueError("M and out_var must be the same length!")

        # compute the actual output variable
        for i in range(len(self.out_vars)):
            # un-normalize if the range is specified
            if 'm_ranges' in self.config and len(self.config['m_ranges']) > 0:
                val_range = self.config['m_ranges'][i]
            self.out_vars[i].val = int(unnormalize(M[i], val_range[0], val_range[1]))

        self.M0.val = tuple(M)
        return self.out_vars

    def wait(self):
        if self.config['sample_period'] <= 0:
            self.curr_wait_time = max(self.sample_speed_limit, self.config['wait_time'])
        else:
            self.curr_wait_time = 0
        sleep(max(0, self.curr_wait_time))

    def read(self, sample_method='default') -> tuple:

        S = []

        # sample the sensor variables
        in_vals = self._sample(method=sample_method)

        if not isinstance(in_vals, tuple):
            raise TypeError('in_vals must be a tuple! It cannot be a %s' % str(in_vals))

        # normalize if the range is specified
        for i in range(len(in_vals)):
            s = None
            if 's_ranges' in self.config and len(self.config['s_ranges']) > 0:
                val_range = self.config['s_ranges'][i]
                if isinstance(val_range, tuple) and len(val_range) == 2:
                    s = normalize(in_vals[i], val_range[0], val_range[1])
            if s is None:
                s = in_vals[i]

            S.append(s)

        self.S0.val = tuple(S)
        return tuple(S)

    def _sample(self, method='default') -> tuple:

        # sample the sensor variables
        if method == 'average':
            return self._sample_average()
        elif method == 'max':
            return self._sample_max()
        else:
            return self.__sample_current()

    def __sample_current(self) -> tuple:
        in_vals = []
        for i in range(len(self.in_vars)):
            in_val = self.in_vars[i].val
            if not isinstance(in_val, (int, float)):
                raise TypeError('Value of in_var[%d] is not an int nor a float' % i)
            in_vals.append(in_val)
        return tuple(in_vals)

    def _sample_few(self) -> tuple:

        # making sure sample_period does not exceed the messenger reading speed
        sample_period = max(self.config['sample_period'], self.sample_speed_limit)

        try:
            max_sample_number = max(1, int(sample_period/self.sample_speed_limit))
        except ZeroDivisionError:
            max_sample_number = 100

        sample_number = min(self.config['sample_number'], max_sample_number)

        # sample the sensor variables
        samples = []
        t0 = clock()

        while sample_number > 0:

            # if first run
            if self.S0.val is None:
                sample_number = 0
            else:
                # sleep first
                time_remained = sample_period - (clock() - t0)
                if time_remained > 0:
                    sleep(time_remained/sample_number)
                    sample_number -= 1
                else:
                    sample_number = 0

            # collect sample
            in_vals = self.__sample_current()

            # store into memory
            samples.append(in_vals)

        return tuple(samples)

    def _sample_average(self):

        samples = self._sample_few()

        # compute average
        sample_mean = []
        samples_zipped = zip(*list(samples))
        for sample in samples_zipped:
            sample_mean.append(np.average(sample))

        return tuple(sample_mean)

    def _sample_max(self):

        samples = self._sample_few()
        # compute max
        sample_max = []
        samples_zipped = zip(*list(samples))
        for sample in samples_zipped:
            sample_max.append(np.max(sample))

        return tuple(sample_max)

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


class Robot_HalfFin(Robot):

    def _set_default_config(self):
        super(Robot_HalfFin, self)._set_default_config()

        self.config['sample_number'] = 10
        self.config['sample_period'] = 4.0
        self.config['wait_time'] = 0.0

        self.config['activation_reward_delta'] = 0.006
        self.config['activation_reward'] = 0.003
        self.config['idling_reward'] = 0.00001
        self.config['min_step_before_idling'] = 15
        self.config['idling_prob'] = 0.999

    def read(self, sample_method=None):
        return super(Robot_HalfFin, self).read(sample_method='default')


class Robot_Light(Robot):

    def _set_default_config(self):
        super(Robot_Light, self)._set_default_config()

        self.config['sample_number'] = 30
        self.config['sample_period'] = 1.0
        self.config['wait_time'] = 0.0

        self.config['activation_reward_delta'] = 0.2
        self.config['activation_reward'] = 0.06
        self.config['idling_reward'] = 0.01
        self.config['min_step_before_idling'] = 20
        self.config['idling_prob'] = 0.999

    def read(self, sample_method=None):

        return super(Robot_Light, self).read(sample_method='default')


class Robot_Reflex(Robot):

    def _set_default_config(self):
        super(Robot_Reflex, self)._set_default_config()

        self.config['sample_number'] = 30
        self.config['sample_period'] = 1.0

        self.config['wait_time'] = 2.0
        self.config['prev_rewards_deque_size'] = 10
        self.config['activation_reward_delta'] = 0.5
        self.config['activation_reward'] = 0.05
        self.config['idling_reward'] = -0.01
        self.config['min_step_before_idling'] = 200
        self.config['idling_prob'] = 0.98

    def read(self, sample_method=None):
        return super(Robot_Reflex, self).read(sample_method='default')


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

def unnormalize(norm_val: float, low_bound: float, hi_bound: float) -> float:
    if low_bound >= hi_bound:
        raise ValueError("Lower Bound cannot be greater than or equal to the Upper Bound!")

    return norm_val*(hi_bound - low_bound) + low_bound