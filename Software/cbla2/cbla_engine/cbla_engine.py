from copy import copy
from collections import OrderedDict


from .cbla_robot import *
from .cbla_learner import *

class CBLA_Engine(object):

    def __init__(self, robot: Robot, learner: Learner, **config_kwargs):

        # instantiate the configuration parameters
        self.config = dict()
        # default configurations
        self.config['print_to_term'] = False

        # custom configurations
        for param, value in config_kwargs.items():
            self.config[param] = value

        # instantiate the robot
        self.robot = robot
        self.learner = learner

        # instantiate the data collector
        self.data_packet = OrderedDict()

        # initialization
        self.M = self.learner.select_action(self.robot)
        self.update_count = 0

    def update(self):

        t0 = clock()
        self.update_count += 1

        # act
        self.robot.act(self.M)

        # wait
        self.robot.wait()

        # read
        S2 = self.robot.read()

        # learn
        self.learner.learn(S2, self.M)

        # select action
        self.M = self.learner.select_action(self.robot)

        # predict
        S_predicted = self.learner.predict()

        # save to data packet
        self.data_packet['time'] = clock()
        self.data_packet['step'] = self.update_count
        self.data_packet['loop_period'] = self.data_packet['time'] - t0
        self.data_packet['S'] = S2
        self.data_packet['M'] = self.M
        self.data_packet['S1_predicted'] = S_predicted
        self.data_packet['in_idle_mode'] = self.robot.is_in_idle_mode()
        self.data_packet.update(self.learner.info)
        self.data_packet.update(self.learner.get_expert_info())


    def print_data_packet(self, header=""):

        print_str = header + '\n'
        for name, packet in self.data_packet.items():
            print_str += ("%s: %s\n" % (name, str(packet)))

        print(print_str + '\n')

def copy_var_list(var_list: list) -> list:

    copied_list = []
    for var in var_list:
        if not isinstance(var, Var):
            raise TypeError("copy_var_list only handles Var type")
        copied_list.append(Var(copy(var.val)))

    return copied_list