from copy import copy
from time import perf_counter
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
        self.config['snapshot_interval'] = 60

        # custom configurations
        for param, value in config_kwargs.items():
            self.config[param] = value

        self.learner_lock = threading.Lock()
        self.robot_lock = threading.Lock()

        # instantiate the robot
        with self.robot_lock:
            self.robot = robot

        # instantiate the learner
        with self.learner_lock:
            self.learner = learner

        # initialization
        with self.robot_lock, self.learner_lock:
            self.M = self.learner.select_action(self.robot)

        # start from previous if necessary
        self.update_count = self.config['update_count_start']

        # snapshot parameters and variables
        self.snapshot_interval = self.config['snapshot_interval']
        self.last_snapshot_t = clock()

    def update(self):

        t0 = clock()
        self.update_count += 1

        # save snapshot or not
        snapshot = False
        if t0 - self.last_snapshot_t > self.snapshot_interval:
            snapshot = True
            self.last_snapshot_t = t0

        with self.robot_lock:
            # act
            self.robot.act(self.M)

            # wait
            self.robot.wait()

            # read
            S2 = self.robot.read()
            # print('t = %d:  M = %f;   S2 = %f' % (self.update_count, self.M[0], S2[0]))

        # learn
        with self.learner_lock:
            # learn
            self.learner.learn(S2, self.M)

            # select action
            with self.robot_lock:
                self.M = self.learner.select_action(self.robot)

            # predict
            S_predicted = self.learner.predict()

        # save to data packet

        data_packet = dict()
        data_packet[DataLogger.packet_time_key] = perf_counter()
        data_packet['step'] = self.update_count
        data_packet['loop_period'] = clock() - t0
        data_packet['S'] = S2
        data_packet['M'] = self.M
        data_packet['S1_predicted'] = S_predicted
        data_packet['rel_act_val'] = self.robot.internal_state['rel_act_val'].val
        data_packet['m_max_val'] = self.robot.internal_state['m_max_val'].val

        data_packet.update(self.learner.info)

        # save expert info to data_packet
        expert_info = self.learner.get_expert_info(snap_shot=snapshot)
        data_packet.update(expert_info)

        return data_packet

    @staticmethod
    def print_data_packet(data_packet: dict, header=""):

        print_str = header + '\n'
        for name, packet in data_packet.items():
            print_str += ("%s: %s\n" % (name, str(packet)))

        print(print_str + '\n')

def copy_var_list(var_list: list) -> list:

    copied_list = []
    for var in var_list:
        if not isinstance(var, Var):
            raise TypeError("copy_var_list only handles Var type")
        copied_list.append(Var(copy(var.val)))

    return copied_list