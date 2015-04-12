from copy import copy
from collections import OrderedDict
from datetime import datetime
import threading

from .cbla_robot import *
from .cbla_learner import *

class CBLA_Engine(object):

    def __init__(self, robot: Robot, learner: Learner, **config_kwargs):

        # instantiate the configuration parameters
        self.config = dict()
        # default configurations
        self.config['print_to_term'] = False
        self.config['update_count_start'] = 0
        self.config['exemplars_save_interval'] = 200

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

        # start from previous if necessary
        self.update_count = self.config['update_count_start']

        self.learner_lock = threading.Lock()


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
        with self.learner_lock:
            self.learner.learn(S2, self.M)

        # select action
        self.M = self.learner.select_action(self.robot)

        # predict
        S_predicted = self.learner.predict()

        # save to data packet
        self.data_packet['time'] = datetime.now()
        self.data_packet['step'] = self.update_count
        self.data_packet['loop_period'] = clock() - t0
        self.data_packet['S'] = S2
        self.data_packet['M'] = self.M
        self.data_packet['S1_predicted'] = S_predicted
        self.data_packet['in_idle_mode'] = self.robot.is_in_idle_mode()

        # save learner info to data_packet
        self.data_packet.update(self.learner.info)

        # save expert info to data_packet
        expert_info = self.learner.get_expert_info()
        if self.update_count % self.config['exemplars_save_interval']:
            # remove exemplars from expert info every certain number of times
            del expert_info['exemplars']
        self.data_packet.update(expert_info)


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