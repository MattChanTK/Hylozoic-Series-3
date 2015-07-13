__author__ = 'Matthew'

from time import perf_counter, clock
from collections import deque
from copy import copy
import numpy as np
from collections import defaultdict
import os

from abstract_node.node import *
from abstract_node.data_logger import DataLogger
from interactive_system import Messenger


class Fin(Node):

    ON_LEFT = 1
    ON_RIGHT = 2
    ON_CENTRE = 3
    OFF = 0

    T_ON_REF = 300

    def __init__(self, messenger: Messenger, teensy_name, node_name='frond', left_sma: Var=Var(0), right_sma: Var=Var(0),
                 motion_type: Var=Var(0), left_config=None, right_config=None):

        super(Fin, self).__init__(messenger, node_name='%s.%s' % (teensy_name, node_name))

        # output variables
        self.out_var['left_sma'] = left_sma
        self.out_var['right_sma'] = right_sma

        # input variable
        self.in_var['motion_type'] = motion_type

        # controller
        if left_config is None:
            left_config = dict()
        if right_config is None:
            right_config = dict()
        self.ctrl_left = SMA_Controller(self.out_var['left_sma'], **left_config)
        self.ctrl_right = SMA_Controller(self.out_var['right_sma'], **right_config)

        self.print_to_term = False

    def run(self):

        while self.alive:

            if self.in_var['motion_type'].val == Fin.ON_LEFT:

                T_left_ref = Fin.T_ON_REF
                T_right_ref = 0

            elif self.in_var['motion_type'].val == Fin.ON_RIGHT:
                T_left_ref = 0
                T_right_ref = Fin.T_ON_REF

            elif self.in_var['motion_type'].val == Fin.ON_CENTRE:
                T_left_ref = Fin.T_ON_REF
                T_right_ref = Fin.T_ON_REF

            else:
                T_left_ref = 0
                T_right_ref = 0

            self.ctrl_left.update(T_left_ref)
            self.ctrl_right.update(T_right_ref)

            sleep(self.messenger.estimated_msg_period*2)


class SMA_Controller(object):

    def __init__(self, output: Var, **kwargs):

        self.config = dict()
        self.config['KP'] = 12
        self.config['KI'] = 0.0001
        self.config['K_heating'] = 1.0
        self.config['K_dissipate'] = 0.22

        if kwargs is not None:
            for name, arg in kwargs.items():
                self.config[name] = arg

        self.KP = self.config['KP']
        self.KI = self.config['KI']
        self.K_heating = self.config['K_heating']
        self.K_dissipate = self.config['K_dissipate']

        self.output = output
        self.T_model = 0
        self.T_err_sum = 0
        self.t0 = clock()

    def update(self, T_ref):

        self.T_model += (self.K_heating * self.output.val - self.K_dissipate * self.T_model) * (clock() - self.t0)
        T_err = (T_ref - self.T_model)
        output_p = self.KP * T_err
        self.T_err_sum += T_err
        output_i = self.KI*self.T_err_sum
        self.output.val = int(min(max(0, output_p + output_i), 255))
        self.t0 = clock()
        return self.output.val


class Half_Fin(Simple_Node):

    def __init__(self, messenger: Messenger, node_name='frond_sma', sma: Var=Var(0), temp_ref: Var=Var(0), **config):

        super(Half_Fin, self).__init__(messenger, node_name='%s' % node_name, output=sma, temp_ref=temp_ref)

        # controller
        self.controller = SMA_Controller(self.out_var['output'], **config)

    def run(self):

        while self.alive:

            self.controller.update(self.in_var['temp_ref'].val)
            sleep(self.messenger.estimated_msg_period*2)


class LED_Driver(Simple_Node):

    def __init__(self, messenger: Messenger, node_name='LED_Driver',
                 led_ref: Var=Var(0), led_out: Var=Var(0), step_period=0):

        super(LED_Driver, self).__init__(messenger, node_name='%s' % node_name, output=led_out,
                                         led_ref=led_ref)

        self.step_period = step_period

    def run(self):

        while self.alive:

            if self.out_var['output'].val < self.in_var['led_ref'].val:
                led_out = self.out_var['output'].val + max(1, int(self.out_var['output'].val * 0.1))
                self.out_var['output'].val = max(0, min(255, led_out))
                sleeping_time = max(0, max(self.messenger.estimated_msg_period * 2, self.step_period))

            elif self.out_var['output'].val > self.in_var['led_ref'].val:
                led_out = self.out_var['output'].val - max(1, int(self.out_var['output'].val * 0.1))
                self.out_var['output'].val = max(0, min(255, led_out))
                sleeping_time = max(0, max(self.messenger.estimated_msg_period * 2, self.step_period))
            else:
                sleeping_time = max(0,self.messenger.estimated_msg_period * 2)

            sleep(sleeping_time)



class Data_Collector_Node(Node):

    def __init__(self, messenger: Messenger, node_name='data_collector', file_header='sys_id_data',
                 data_collect_period=1.0, create_new_log=True,
                 **variables):
        super(Data_Collector_Node, self).__init__(messenger, node_name=node_name)

        # defining the input variables
        for var_name, var in variables.items():
            if isinstance(var, Var):
                self.in_var[var_name] = var
            else:
                raise TypeError("Variables must be of Var type!")

        self.data_collect_period = data_collect_period

        # setting up the data collector
        log_dir_path = os.path.join(os.getcwd(), 'data_log')

        # create new entry folder if creating new log
        if create_new_log:
            latest_log_dir = None
        # add a new session folder if continuing from old log
        else:
            # use the latest data log
            all_log_dir = []
            for dir in os.listdir(log_dir_path):
                dir_path = os.path.join(log_dir_path, dir)
                if os.path.isdir(dir_path):
                    all_log_dir.append(dir_path)
            latest_log_dir = max(all_log_dir, key=os.path.getmtime)
        log_dir_path = os.path.join(os.getcwd(), 'data_log')

        # create the data_collector
        self.data_collect = DataLogger(log_dir=log_dir_path, log_header=file_header,
                                       log_path=latest_log_dir)

    def run(self):

        self.data_collect.start()

        loop_count = 0
        while self.alive:
            loop_count += 1
            data_packets = defaultdict(OrderedDict)

            for var_name, var in self.in_var.items():
                var_split = var_name.split('.')
                teensy_name = var_split[0]
                device_name = var_split[1]
                point_name = var_split[2]
                data_packets['%s.%s' % (teensy_name, device_name)][point_name] = copy(var.val)

            for packet_name, data_packet in data_packets.items():
                data_packet['packet_time'] = perf_counter()
                data_packet['step'] = loop_count

                self.data_collect.append_data_packet(packet_name, data_packet)

            sleep(max(self.messenger.estimated_msg_period*2, self.data_collect_period))

        self.data_collect.end_data_collection()
        self.data_collect.join()


class Pseudo_Differentiation(Node):

    def __init__(self, messenger: Messenger, node_name='Pseudo_Differentiation',
                 input_var: Var=Var(0),
                 diff_gap=1, smoothing=1, step_period=0.1):

        if not isinstance(input_var, Var):
            raise TypeError("input_var must be of type Var!")

        super(Pseudo_Differentiation, self).__init__(messenger, node_name=node_name)

        self.diff_gap = diff_gap
        self.smoothing = smoothing

        self.in_var['input'] = input_var
        self.out_var['output'] = Var()
        self.out_var['output'].val = 0

        self.input_deque = deque(maxlen=(self.smoothing+self.diff_gap))
        self.step_period = step_period

    def run(self):

        while self.alive:

            self.input_deque.append(copy(self.in_var['input'].val))

            # calculate differences
            val_list = list(self.input_deque)
            if len(val_list) >= self.diff_gap + 1:
                self.out_var['output'].val = np.mean(val_list[-self.smoothing:]) \
                                             - np.mean(val_list[:-self.diff_gap])
            sleep(self.step_period)


class Running_Average(Node):

    def __init__(self, messenger: Messenger, node_name='Pseudo_Differentiation',
                 input_var: Var=Var(0),
                 avg_window=1, step_period=0.1):


        if not isinstance(input_var, Var):
            raise TypeError("input_var must be of type Var!")

        super(Running_Average, self).__init__(messenger, node_name=node_name)

        self.avg_window = avg_window

        self.in_var['input'] = input_var
        self.out_var['output'] = Var()
        self.out_var['output'].val = 0

        self.input_deque = deque(maxlen=avg_window)
        self.step_period = step_period

    def run(self):
        while self.alive:

            self.input_deque.append(copy(self.in_var['input'].val))

            self.out_var['output'].val = np.mean(self.input_deque)

            sleep(self.step_period)





