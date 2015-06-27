from time import sleep
import random
from collections import deque
import numpy as np

from abstract_node import *
from abstract_node.simple_data_collect import*


class Test_Fin(Node):

    def __init__(self, messenger: Messenger, teensy_name: str,
                 ir_0: Var=Var(0), ir_1: Var=Var(0), acc: Var=Var(0), cluster_activity: Var=Var(0),
                 left_ir: Var=Var(0), right_ir: Var=Var(0),
                 fin: Var=Var(0), reflex_0: Var=Var(0), reflex_1: Var=Var(0), node_name='test_fin'):

        if not isinstance(teensy_name, str):
            raise TypeError('teensy_name must be a string!')

        self.teensy_name = teensy_name


        super(Test_Fin, self).__init__(messenger, node_name='%s.%s' % (teensy_name, node_name))

        # defining the input variables
        self.in_var['ir_sensor_0'] = ir_0
        self.in_var['ir_sensor_1'] = ir_1
        self.in_var['acc'] = acc
        self.in_var['left_ir'] = left_ir
        self.in_var['right_ir'] = right_ir
        self.in_var['cluster_activity'] = cluster_activity

        # defining the output variables
        self.out_var['fin_out'] = fin
        self.out_var['reflex_out_0'] = reflex_0
        self.out_var['reflex_out_1'] = reflex_1
        self.out_var['cluster_activity'] = cluster_activity

        # parameters
        self.ir_on_thres = 1400
        self.ir_off_thres = 1000

    def run(self):

        while self.alive:

            # frond's sensor
            if self.in_var['ir_sensor_1'].val > self.ir_on_thres:

                if self.out_var['fin_out'].val == 0:
                    self.out_var['cluster_activity'].val += 1

                motion_type = 3
                if self.in_var['left_ir'].val > self.ir_on_thres and self.in_var['right_ir'].val > self.ir_on_thres:
                    motion_type = random.choice((1, 2))
                elif self.in_var['left_ir'].val > self.ir_on_thres:
                    motion_type = 1
                elif self.in_var['right_ir'].val > self.ir_on_thres:
                    motion_type = 2

                self.out_var['fin_out'].val = motion_type


            elif self.in_var['ir_sensor_1'].val <= self.ir_off_thres and self.out_var['fin_out'].val > 0:
                self.out_var['fin_out'].val = 0

            # scout's sensor
            if self.in_var['ir_sensor_0'].val > self.ir_on_thres and \
                    (self.out_var['reflex_out_0'].val == 0 or self.out_var['reflex_out_1'].val == 0):
                self.out_var['reflex_out_0'].val = 100
                self.out_var['reflex_out_1'].val = 100
                self.out_var['cluster_activity'].val += 1

            elif self.in_var['ir_sensor_0'].val <= self.ir_off_thres and \
                    (self.out_var['reflex_out_0'].val > 0 or self.out_var['reflex_out_1'].val > 0):

                self.out_var['reflex_out_0'].val = 0
                self.out_var['reflex_out_1'].val = 0

            sleep(self.messenger.estimated_msg_period*2)


class Cycling_Fin(Fin):

    def run(self):

        t0 = clock()
        exp_step = (10, 100, 180)

        # initial values
        motion_type = 0
        t_flip = 5.0
        t_flip_k = 0

        while self.alive:

            delta_t = clock() - t0

            # no movement
            if delta_t < exp_step[0]:
                motion_type = 0

            # rapid L-R-L-R...
            elif delta_t < exp_step[1]:

                if delta_t > (t_flip*t_flip_k + exp_step[0]):

                    if motion_type == 1:
                        motion_type = 2
                    else:
                        motion_type = 1
                    t_flip_k += 1

            # slow up-down-up-down...
            elif delta_t < exp_step[2]:
                if delta_t < (exp_step[2]-exp_step[1])/2 + exp_step[1]:
                    motion_type = 3
                else:
                    motion_type = 0



            self.in_var['motion_type'].val = motion_type

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

            sleep(self.messenger.estimated_msg_period * 2)

class Interactive_Light(Simple_Node):

    def __init__(self, messenger: Messenger, node_name='interactive_light',
                 als: Var=Var(0), fin_ir: Var=Var(0),
                 led: Var=Var(0),
                 local_action_prob: Var=Var(0), sleep_time: Var=Var(0.025)):

        super(Interactive_Light, self).__init__(messenger, node_name='%s' % node_name, output=led,
                                         als=als, fin_ir=fin_ir,
                                         local_action_prob=local_action_prob, sleep_time=sleep_time)

    def run(self):

        t_cluster = clock()
        while self.alive:

            # cluster activity
            if clock() - t_cluster > 1.0:
                do_local_action = random.random() < self.in_var['local_action_prob'].val
                if do_local_action or self.in_var['fin_ir'].val > 1000:

                    for i in range(5):
                        self.out_var['output'].val = 0
                        while self.out_var['output'].val < 100:
                            out_val = self.out_var['output'].val + max(1, int(self.out_var['output'].val*0.1))
                            self.out_var['output'].val = max(0, min(255, out_val))
                            sleep(self.in_var['sleep_time'].val)
                        while self.out_var['output'].val > 0:
                            out_val = self.out_var['output'].val - max(1, int(self.out_var['output'].val*0.1))
                            self.out_var['output'].val = max(0, min(255, out_val))
                            sleep(self.in_var['sleep_time'].val)

                        self.in_var['local_action_prob'].val = 0
                t_cluster = clock()

            self.out_var['output'].val = 0

            sleep(self.messenger.estimated_msg_period * 2)

class Interactive_Scout_Reflex(Simple_Node):

    def __init__(self, messenger: Messenger, node_name='interactive_reflex_actuator',
                 output: Var=Var(0), ir_sensor: Var=Var(0), **config):

        super(Interactive_Scout_Reflex, self).__init__(messenger, node_name='%s' % node_name, output=output, ir_sensor=ir_sensor)

        # default parameters
        self.config = dict()
        self.config['ir_on_thres'] = 950
        self.config['ir_off_thres'] = 700
        self.config['step_period'] = 0.025
        self.config['max_val'] = 255

        # custom parameters
        if isinstance(config, dict):
            for name, arg in config.items():
                self.config[name] = arg



    def run(self):

        reached_max = False
        while self.alive:


            # scout's sensor
            if self.in_var['ir_sensor'].val > self.config['ir_on_thres'] and not reached_max:

                if self.out_var['output'].val < self.config['max_val']:
                    out_val = self.out_var['output'].val + max(1, int(self.out_var['output'].val*0.1))
                    self.out_var['output'].val = max(0, min(255, out_val))

                    sleep(self.config['step_period'])
                else:
                    reached_max = True

            elif self.in_var['ir_sensor'].val < self.config['ir_off_thres'] or reached_max:

                if self.out_var['output'].val > 0:
                    out_val = self.out_var['output'].val - max(1, int(self.out_var['output'].val*0.1))
                    self.out_var['output'].val = max(0, min(255, out_val))
                    sleep(self.config['step_period'])
                else:
                    reached_max = False

            sleep(self.messenger.estimated_msg_period * 2)


class Interactive_Half_Fin(Simple_Node):

    def __init__(self, messenger: Messenger, node_name='Interactive_Half_Fin',
                 output: Var=Var(0), fin_ir: Var=Var(0), scout_ir: Var=Var(0), side_ir: Var=Var(0),
                 local_action_prob: Var=Var(0), **config):

        super(Interactive_Half_Fin, self).__init__(messenger, node_name='%s' % node_name, output=output,
                                                   fin_ir=fin_ir, scout_ir=scout_ir, side_ir=side_ir,
                                                   local_action_prob=local_action_prob)

        # default parameters
        self.config = dict()
        self.config['ir_on_thres'] = 950
        self.config['ir_off_thres'] = 700
        self.config['T_on'] = 300
        self.config['T_off'] = 5
        # custom parameters
        if isinstance(config, dict):
            for name, arg in config.items():
                self.config[name] = arg

        # controller
        self.controller = SMA_Controller(self.out_var['output'], **self.config)

    def run(self):

        t_cluster = clock()
        T_set = self.config['T_off']
        do_local_action = False
        while self.alive:
            # scout's sensor
            if self.in_var['fin_ir'].val > self.config['ir_on_thres']:

                # turn on unless scout ir doesn't detect anything and side ir does
                if self.in_var['scout_ir'].val < self.config['ir_off_thres'] and self.in_var['side_ir'].val > self.config['ir_on_thres']:
                    T_set = self.config['T_off']
                else:
                    T_set = self.config['T_on']

            elif self.in_var['fin_ir'].val < self.config['ir_off_thres'] and T_set > self.config['T_off'] and not do_local_action:

                T_set = self.config['T_off']

            else:

                if clock() - t_cluster > 3.0:
                    do_local_action = random.random() < self.in_var['local_action_prob'].val

                    if do_local_action:
                        T_set = self.config['T_on']
                    t_cluster = clock()

            self.controller.update(T_set)
            # if 'tentacle_1' in self.node_name:
            #     print('T = %f;   out = %f ' % (self.controller.T_model, self.controller.output.val ))

            sleep(self.messenger.estimated_msg_period * 2)


class Cluster_Activity(Simple_Node):

    def __init__(self, messenger: Messenger, node_name='Local_Activity',
                 output: Var=Var(0), inputs: tuple=(Var(0),), **config):

        input_vars = dict()
        for i in range(len(inputs)):
            if isinstance(inputs[i], Var):
                input_vars['input_%d' % i] = inputs[i]

        super(Cluster_Activity, self).__init__(messenger, node_name='%s' % node_name, output=output, **input_vars)

        # default parameters
        self.config = dict()
        self.config['activity_denom'] = len(inputs)
        self.config['activity_expon'] = 3.0
        self.config['min_prob'] = 0.00
        self.config['max_prob'] = 0.8

        # custom parameters
        if isinstance(config, dict):
            for name, arg in config.items():
                self.config[name] = arg

    def run(self):

        while self.alive:

            # determine level of activity
            activity = 0
            for var in self.in_var.values():
                activity += (var.val > 20)
            activity = activity**self.config['activity_expon']
            activity = max(0, min(self.config['activity_denom']**self.config['activity_expon'], activity))

            prob = activity/self.config['activity_denom']**self.config['activity_expon']
            self.out_var['output'].val = max(self.config['min_prob'], min(self.config['max_prob'], prob ))

            sleep(max(0, self.messenger.estimated_msg_period * 2))
           #print(self.out_var['output'].val)


class Parameter_Config(Node):

    def __init__(self, messenger: Messenger, node_name='param_config',
                 **params):

        super(Parameter_Config, self).__init__(messenger, node_name=node_name)

        # defining the input variables
        for param_name, init_value in params.items():
            if isinstance(init_value, Var):
                self.out_var[param_name] = init_value
            else:
                self.out_var[param_name] = Var(init_value)

    def run(self):
        pass





