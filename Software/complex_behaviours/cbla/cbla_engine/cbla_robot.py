__author__ = 'Matthew'

from abstract_node import Var, DataLogger

from time import sleep
import numpy as np
import random
from time import clock
from collections import deque
import math


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

        # adaptive activity level related variables
        self.avg_action_value_2 = 0
        self.act_val_count = 0
        self.prev_action_value = deque(maxlen=self.config['prev_values_deque_size'])
        self.prev_rel_action_value = deque(maxlen=self.config['prev_rel_values_deque_size'])

        # compute initial action
        self.M0 = Var(self.compute_initial_motor())
        self.S0 = Var(None)

        # the range of each sensory measurement
        self.s_ranges = [None] * len(self.in_vars)

        # the max range of selectable m
        self.m_max_val = 1

        # the variables monitoring the state of the system
        self.internal_state = dict()
        self.internal_state['avg_act_val_2'] = Var(0.0)
        self.internal_state['rel_act_val'] = Var(0.0)
        self.internal_state['avg_rel_act_val'] = Var(0.0)
        self.internal_state['m_max_val'] = Var(self.m_max_val)

    def _set_default_config(self):

        self.config['sample_number'] = 30
        self.config['sample_period'] = 5.0
        self.config['wait_time'] = 0.0  # 4.0

        # adaptive activity level related constants
        self.config['prev_values_deque_size'] = 15
        self.config['prev_rel_values_deque_size'] = 4
        self.config['min_avg_action_value'] = 0.0001
        # self.config['max_act_val_count'] = 15

        self.config['min_m_max_val'] = 0.00001
        self.config['low_action_m_max_val'] = 0.90
        self.config['low_rel_action_val_thres'] = 20.0

    def renew_robot(self, new_s_vars, new_m_vars):

        # check if they have the same length
        if len(new_s_vars) != len(self.in_vars):
            raise ValueError
        if len(new_m_vars) != len(self.out_vars):
            raise ValueError

        # replace old var with new var address
        for i in range(len(new_s_vars)):
            self.in_vars[i] = new_s_vars[i]
        for i in range(len(new_m_vars)):
            self.out_vars[i] = new_m_vars[i]

        # compute initial action
        self.M0 = Var(self.compute_initial_motor())
        self.S0 = Var(None)

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
                X[i, x_dim - 1] = random.uniform(0, self.m_max_val)

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
        self.curr_wait_time = max(self.sample_speed_limit, self.config['wait_time'])
        sleep(max(0, self.curr_wait_time))

    def read(self, sample_method='average') -> tuple:

        S = []

        # sample the sensor variables
        in_vals = self._sample(method=sample_method)

        if not isinstance(in_vals, tuple):
            raise TypeError('in_vals must be a tuple! It cannot be a %s' % str(in_vals))

        # normalize if the range is specified
        for i in range(len(in_vals)):

            # preset s_range mode
            s = None
            if 's_ranges' in self.config and len(self.config['s_ranges']) > 0:
                val_range = self.config['s_ranges'][i]
                if isinstance(val_range, tuple) and len(val_range) == 2:
                    s = normalize(in_vals[i], val_range[0], val_range[1])
            if s is None:
                s = in_vals[i]

            # adaptive s_range mode
            # if self.s_ranges[i]:
            #     if in_vals[i] < self.s_ranges[i][0]:
            #         self.s_ranges[i][0] = in_vals[i]
            #     if in_vals[i] > self.s_ranges[i][1]:
            #         self.s_ranges[i][1] = in_vals[i] + 1
            #
            # elif in_vals[i] != 0:
            #     self.s_ranges[i] = [in_vals[i], in_vals[i] + 1]
            #
            # else:
            #     self.s_ranges[i] = None
            #
            # if self.s_ranges[i]:
            #     s = normalize(in_vals[i], self.s_ranges[i][0], self.s_ranges[i][1])
            # else:
            #     s = 0.5

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

    def adapt_m_max_val(self, action_val=None):

        if action_val:

            try:
                rel_action_val = action_val**2/self.avg_action_value_2
            except ZeroDivisionError:
                rel_action_val = 1.0

            self.prev_rel_action_value.append(rel_action_val)
            avg_rel_action_val = float(np.mean(list(self.prev_rel_action_value)))

            self.m_max_val = self.map_sigmoid(rel_action_val,
                                              b=self.config['min_m_max_val'],
                                              d=self.config['low_action_m_max_val'],
                                              c=self.config['low_rel_action_val_thres'])

            # self.m_max_val = self.map_linear(rel_action_val,
            #                                   b=self.config['min_m_max_val'],
            #                                   d=self.config['low_action_m_max_val'],
            #                                   c=self.config['low_rel_action_val_thres'],
            #                                   k=1.0)

            self.internal_state['avg_act_val_2'].val = self.avg_action_value_2
            self.internal_state['rel_act_val'].val = rel_action_val
            self.internal_state['avg_rel_act_val'].val = avg_rel_action_val
            self.internal_state['m_max_val'].val = self.m_max_val

            if self.act_val_count < self.config['prev_values_deque_size']:
                self.act_val_count += 1

            self.avg_action_value_2 = self.avg_action_value_2 + (action_val**2 - self.avg_action_value_2)/self.act_val_count

            # save the action value to memory
            self.prev_action_value.append(action_val)

    def adapt_m_max_val_windowing(self, action_val=None):

        if action_val:

            # calculate the mean square of action value
            if len(self.prev_action_value) > min(self.prev_action_value.maxlen, len(self.out_vars)+len(self.in_vars)):

                avg_action_val_2 = float(np.mean(np.square(list(self.prev_action_value))))
                # making sure that the average action isn't too small
                avg_action_val_2 = max(self.config['min_avg_action_value'], avg_action_val_2)

                # no value added if it's less than the avg_action Value
                try:
                    rel_action_val = action_val**2/avg_action_val_2
                except ZeroDivisionError:
                    rel_action_val = 1.0

                self.prev_rel_action_value.append(rel_action_val)
                avg_rel_action_val = float(np.mean(list(self.prev_rel_action_value)))

                self.m_max_val = self.map_sigmoid(rel_action_val,
                                                  b=self.config['min_m_max_val'],
                                                  d=self.config['low_action_m_max_val'],
                                                  c=self.config['low_rel_action_val_thres'])

                # self.m_max_val = self.map_linear(rel_action_val,
                #                                   b=self.config['min_m_max_val'],
                #                                   d=self.config['low_action_m_max_val'],
                #                                   c=self.config['low_rel_action_val_thres'],
                #                                   k=1.0)


                self.internal_state['rel_act_val'].val = rel_action_val
                self.internal_state['avg_rel_act_val'].val = avg_rel_action_val
                self.internal_state['m_max_val'].val = self.m_max_val

            else:
                self.internal_state['rel_act_val'].val = 0.0
                self.internal_state['avg_rel_act_val'].val = 0.0
                self.internal_state['m_max_val'].val = self.m_max_val

        # save the action value to memory
        self.prev_action_value.append(action_val)

    @classmethod
    def map_sigmoid(cls, x, b, d, c) -> float:

        if not isinstance(d, (int, float)) or not 0 < d < 1:
            raise ValueError("d must be a float between 0 and 1!  Not %s" % str(d))

        if not isinstance(b, (int, float)) or not 0 < b < 1:
            raise ValueError("b must be a float between 0 and 1!  Not %s" % str(b))

        if not isinstance(c, (int, float)) or not c > 0:
            raise ValueError("c must be a float greater than 0!  Not %s" % str(c))

        a = math.log(1/b -1)
        k = -1/c * (math.log(1/d-1)-a)

        y = 1/(1+math.exp(-k*x + a))
        return y

    @classmethod
    def map_linear(cls, x, b, d, c, k=0.5) -> float:

        if not isinstance(d, (int, float)) or not 0 < d < 1:
            raise ValueError("d must be a float between 0 and 1!  Not %s" % str(d))

        if not isinstance(b, (int, float)) or not 0 < b < 1:
            raise ValueError("b must be a float between 0 and 1!  Not %s" % str(b))

        if not isinstance(c, (int, float)) or not c > 0:
            raise ValueError("c must be a float greater than 0!  Not %s" % str(c))

        m = k*(1/(c-d))

        y = m*x + b

        return min(max(y, 0), 1)


class Robot_Light(Robot):

    def _set_default_config(self):
        super(Robot_Light, self)._set_default_config()

        self.config['sample_number'] = 15
        self.config['sample_period'] = 1.0
        self.config['wait_time'] = 0.0  # 4.0

        self.config['prev_values_deque_size'] = 38 #75  # 150
        self.config['prev_rel_values_deque_size'] = 5

        self.config['min_m_max_val'] = 0.01
        self.config['low_action_m_max_val'] = 0.99
        self.config['low_rel_action_val_thres'] = 16.0


    def read(self, sample_method=None):

        return super(Robot_Light, self).read(sample_method='average')


class Robot_HalfFin(Robot):

    def _set_default_config(self):
        super(Robot_HalfFin, self)._set_default_config()

        self.config['sample_number'] = 20
        self.config['sample_period'] = 5.0
        self.config['wait_time'] = 0.0  #4.0

        self.config['prev_values_deque_size'] = 8 #15 #30
        self.config['prev_rel_values_deque_size'] = 1

        self.config['min_m_max_val'] = 0.001
        self.config['low_action_m_max_val'] = 0.99
        self.config['low_rel_action_val_thres'] = 8.0

    def read(self, sample_method=None):

        return super(Robot_HalfFin, self).read(sample_method='average')

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

            out_val = int(unnormalize(M[i], val_range[0], val_range[1]))

            # make it 0 if it's at the lower bound
            if out_val == val_range[0]:
                out_val = 0
            self.out_vars[i].val = out_val

        self.M0.val = tuple(M)
        return self.out_vars


class Robot_Reflex(Robot):

    def _set_default_config(self):
        super(Robot_Reflex, self)._set_default_config()

        self.config['sample_number'] = 5
        self.config['sample_period'] = 0.5
        self.config['wait_time'] = 0.0  # 2.0

        self.config['prev_values_deque_size'] = 75 #150 # 300 # 100
        self.config['prev_rel_values_deque_size'] = 8

        self.config['min_m_max_val'] = 0.005
        self.config['low_action_m_max_val'] = 0.999
        self.config['low_rel_action_val_thres'] = 8.0

    def read(self, sample_method=None):
        return super(Robot_Reflex, self).read(sample_method='average')


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