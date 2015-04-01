from time import sleep
import random

from abstract_node.node import *

class Tentacle(Node):

    def __init__(self, messenger: Messenger.Messenger, teensy_name: str,
                 ir_0: Var=Var(0), ir_1: Var=Var(0), acc: Var=Var(0), cluster_activity: Var=Var(0),
                 left_ir: Var=Var(0), right_ir: Var=Var(0),
                 frond: Var=Var(0), reflex_0: Var=Var(0), reflex_1: Var=Var(0), node_name='tentacle'):

        if not isinstance(teensy_name, str):
            raise TypeError('teensy_name must be a string!')

        self.teensy_name = teensy_name


        super(Tentacle, self).__init__(messenger, node_name='%s.%s' % (teensy_name, node_name))

        # defining the input variables
        self.in_var['ir_sensor_0'] = ir_0
        self.in_var['ir_sensor_1'] = ir_1
        self.in_var['acc'] = acc
        self.in_var['left_ir'] = left_ir
        self.in_var['right_ir'] = right_ir
        self.in_var['cluster_activity'] = cluster_activity

        # defining the output variables
        self.out_var['tentacle_out'] = frond
        self.out_var['reflex_out_0'] = reflex_0
        self.out_var['reflex_out_1'] = reflex_1
        self.out_var['cluster_activity'] = cluster_activity

        # parameters
        self.ir_on_thres = 1400
        self.ir_off_thres = 1000

    def run(self):

        while True:

            # frond's sensor
            if self.in_var['ir_sensor_1'].val > self.ir_on_thres:

                if self.out_var['tentacle_out'].val == 0:
                    self.out_var['cluster_activity'].val += 1

                motion_type = 3
                if self.in_var['left_ir'].val > self.ir_on_thres and self.in_var['right_ir'].val > self.ir_on_thres:
                    motion_type = random.choice((1, 2))
                elif self.in_var['left_ir'].val > self.ir_on_thres:
                    motion_type = 1
                elif self.in_var['right_ir'].val > self.ir_on_thres:
                    motion_type = 2

                self.out_var['tentacle_out'].val = motion_type


            elif self.in_var['ir_sensor_1'].val <= self.ir_off_thres and self.out_var['tentacle_out'].val > 0:
                self.out_var['tentacle_out'].val = 0

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

            # cluster activity
            # if self.in_var['cluster_activity'].val > 15:
            #     self.out_var['reflex_out_0'].val = 200
            #     self.out_var['reflex_out_1'].val = 200
            #     sleep(3)
            #     self.in_var['cluster_activity'].val = 0
            #     self.out_var['reflex_out_0'].val = 0
            #     self.out_var['reflex_out_1'].val = 0

            sleep(self.messenger.estimated_msg_period*2)


class Protocell(Node):

    def __init__(self, messenger: Messenger.Messenger, teensy_name: str,
                 als: Var=Var(0), cluster_activity: Var=Var(0),
                 led: Var=Var(0), node_name='protocell'):


        if not isinstance(teensy_name, str):
            raise TypeError('teensy_name must be a string!')

        self.teensy_name = teensy_name

        super(Protocell, self).__init__(messenger, node_name='%s.%s' % (teensy_name, node_name))

        # defining the input variables
        self.in_var['als'] = als
        self.in_var['cluster_activity'] = cluster_activity

        # defining the output variables
        self.out_var['led'] = led
        self.out_var['cluster_activity'] = cluster_activity


    def run(self):
        while True:

            # cluster activity
            if self.in_var['cluster_activity'].val > 10:

                for i in range(5):
                    self.out_var['led'].val = 0
                    while self.out_var['led'].val < 100:
                        self.out_var['led'].val += max(1, int(self.out_var['led'].val*0.1))
                        sleep(0.025)
                    while self.out_var['led'].val > 0:
                        self.out_var['led'].val -= max(1, int(self.out_var['led'].val*0.1))
                        sleep(0.025)
                    self.in_var['cluster_activity'].val = 0

            self.out_var['led'].val = 0

            sleep(self.messenger.estimated_msg_period * 2)

