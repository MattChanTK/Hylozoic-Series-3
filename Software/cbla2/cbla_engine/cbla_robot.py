__author__ = 'Matthew'

from abstract_node import Var

from time import sleep
import numpy as np
import random
from collections import deque
from time import clock

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

        # idle mode related variables
        self.in_idle_mode = False
        self.step_in_active_mode = 0

        # compute initial action
        self.M0 = self.compute_initial_motor()
        self.S0 = None

    def _set_default_config(self):
        self.config['activation_reward_delta'] = 0.01
        self.config['activation_reward'] = 0.1
        self.config['idling_reward'] = 0.1
        self.config['min_step_before_idling'] = 0.1
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

        self.M0 = tuple(M)

        return self.out_vars

    def wait(self, wait_time_s=0.03):

        sleep(wait_time_s)

    def read(self) -> tuple:
        # compute the sensor variables
        S = []
        for var in self.in_vars:
            S.append(var.val)
        self.S0 = tuple(S)
        return tuple(S)

    def get_possible_action(self, num_sample=100) -> tuple:

        num_dim = len(self.M0)

        X = np.zeros((num_sample, num_dim))

        for i in range(num_sample):
            for x_dim in range(num_dim):
                X[i, x_dim - 1] = random.randint(0, 255)

        M_candidates = tuple(set((map(tuple, X))))

        return M_candidates

    def enter_idle_mode(self, reward) -> bool:

        # if it is in idle mode and reward is high enough to exit idle mode
        if self.in_idle_mode and reward > self.config['activation_reward']:
            self.in_idle_mode = False
            self.step_in_active_mode = 0

        # if it is in active more and condition for entering idle mode is reached
        elif not self.in_idle_mode and reward < self.config['idling_reward'] and self.step_in_active_mode > self.config['min_step_before_idling']:
            self.in_idle_mode = True
            self.step_in_active_mode = 0

        # if it's in active mode
        elif not self.in_idle_mode:
            self.step_in_active_mode += 1

        return self.in_idle_mode

    def is_doing_idle_action(self) -> bool:

        if self.in_idle_mode and random.random() < self.config['idling_prob']:
            return True
        else:
            return False

    def is_in_idle_mode(self) -> bool:
        return self.in_idle_mode

    def get_idle_action(self) -> tuple:
        return tuple([0] * len(self.M0))


class Robot_Frond(Robot):

    def __init__(self, in_vars: list, out_vars: list, **config_kwargs):

        super(Robot_Frond, self).__init__(in_vars, out_vars, **config_kwargs)

        self.S_memory = deque(maxlen=self.config['sample_window'])


    def _set_default_config(self):
        self.config['activation_reward_delta'] = 0.01
        self.config['activation_reward'] = 0.1
        self.config['idling_reward'] = 0.1
        self.config['min_step_before_idling'] = 0.1
        self.config['idling_prob'] = 0.98

        self.config['sample_window'] = 100
        self.config['sample_period'] = 0.01

    def act(self, M: tuple):

        pass

    def read(self) -> tuple:
        # compute the sensor variables

        for i in range(self.config['sample_window']):
            t0 = clock()
            S = []
            for var in self.in_vars:
                S.append(var.val)

            # store into memory
            self.S_memory.append(tuple(S))

            # wait for next period
            sleep(self.config['sample_period'] - (clock() - t0))

        # compute average
        S_mean = []
        s_zipped = zip(*list(self.S_memory))
        for s in s_zipped:
            S_mean.append(np.average(s))

        self.S0 = tuple(S_mean)
        return tuple(S_mean)

    def get_possible_action(self, num_sample=10):

        # constructing a list of all possible action
        x_dim = len(self.M0)
        X = list(range(0, 4 ** x_dim))
        for i in range(len(X)):
            X[i] = toDigits(X[i], 4)
            filling = [0] * (x_dim - len(X[i]))
            X[i] = filling + X[i]

        M_candidates = tuple(set(map(tuple, X)))

        try:
            return tuple(random.sample(M_candidates, num_sample))
        except ValueError:
            pass

        return M_candidates


class Robot_Protocell(Robot):
     pass


def toDigits(n, b):
    """Convert a positive number n to its digit representation in base b."""
    digits = []
    while n > 0:
        digits.insert(0, n % b)
        n = n // b

    return digits
