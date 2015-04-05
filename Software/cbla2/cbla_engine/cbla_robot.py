__author__ = 'Matthew'

from abstract_node import Var

from time import sleep
import numpy as np
import random


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

        # compute initial action
        self.M0 = self.compute_initial_motor()

        # idle mode related variables
        self.in_idle_mode = False
        self.step_in_active_mode = 0


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

        return self.out_vars

    def wait(self, wait_time_s=0.03):

        sleep(wait_time_s)

    def read(self) -> tuple:
        # computer the sensor variables
        S = []
        for var in self.in_vars:
            S.append(var.val)
        return tuple(S)

    def get_possible_action(self, num_sample=100) -> tuple:

        x_dim = 1
        X = np.zeros((num_sample, x_dim))

        for i in range(num_sample):
            X[i, x_dim - 1] = max(min(self.M0[x_dim - 1] - int(num_sample / 2) + i, 255), 0)

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