__author__ = 'Matthew'

from time import clock
from abstract_node.node import *
from interactive_system import Messenger
import cbla_engine


class CBLA_Node(Node):

    def __init__(self, messenger: Messenger, teensy_name: str, data_collector: cbla_engine.DataCollector,
                 node_name='cbla_node'):


        if not isinstance(teensy_name, str):
            raise TypeError('teensy_name must be a string!')

        self.teensy_name = teensy_name

        # reference to the data collector
        self.data_collector = data_collector

        super(CBLA_Node, self).__init__(messenger, node_name='%s.%s' % (teensy_name, node_name))

        self.state_save_freq = 1000

        self.cbla_robot = None
        self.cbla_learner = None

    def instantiate(self):

        if self.cbla_robot is None:
            raise AttributeError("CBLA_Robot must be implemented in the child class")

        # create learner
        M0 = self.cbla_robot.compute_initial_motor()
        S0 = self.cbla_robot.read()

        # load previous learner expert
        try:
            past_state = self.data_collector.data_file['state'][self.node_name]
        except KeyError:
            past_state = None
        self.cbla_learner = cbla_engine.Learner(S0, M0, past_state=past_state)

        # load previous learner steps
        config = dict()
        try:
            config['update_count_start'] = past_state['learner_step']
        except KeyError:
            pass

        # create CBLA engine
        self.cbla_engine = cbla_engine.CBLA_Engine(self.cbla_robot, self.cbla_learner, **config)

        # internal output variables
        self.out_var['S'] = self.cbla_robot.S0
        self.out_var['M'] = self.cbla_robot.M0

        # output variables
        self.out_var['loop_time'] = Var(0)
        self.out_var['idle_mode'] = Var(False)
        self.out_var['node_step'] = Var(0)

        self.cbla_states = dict()

    def run(self):

        while self.alive:
            # adjust the robot's wait time between act() and read()
            self.cbla_robot.config['wait_time'] = max(0.01, self.messenger.estimated_msg_period * 2)

            # update CBLA Engine
            self.cbla_engine.update()

            # save the data
            with self.cbla_engine.data_packet_lock:
                self.data_collector.append_data_packet(self.node_name, self.cbla_engine.data_packet)

                self.out_var['loop_time'].val = self.cbla_engine.data_packet['loop_period']
                self.out_var['idle_mode'].val = self.cbla_engine.data_packet['in_idle_mode']
                self.out_var['node_step'].val = self.cbla_engine.data_packet['step']

            # self.cbla_engine.print_data_packet(header=self.node_name)

        self.save_states()

    def save_states(self):

        with self.cbla_engine.learner_lock:
            # save state when terminated
            self.cbla_states['learner_expert'] = self.cbla_engine.learner.expert
            self.cbla_states['learner_step'] = self.cbla_engine.update_count

        self.data_collector.update_state(self.node_name, self.cbla_states)


class CBLA_Tentacle(CBLA_Node):

    def __init__(self, messenger: Messenger, teensy_name: str, data_collector: cbla_engine.DataCollector,
                 ir_0: Var=Var(0), ir_1: Var=Var(0), acc: Var=Var(0), cluster_activity: Var=Var(0),
                 left_ir: Var=Var(0), right_ir: Var=Var(0),
                 frond: Var=Var(0), reflex_0: Var=Var(0), reflex_1: Var=Var(0), node_name='cbla_tentacle'):


        super(CBLA_Tentacle, self).__init__(messenger=messenger, teensy_name=teensy_name,
                                            data_collector=data_collector, node_name=node_name)


        # defining the input variables
        self.in_var['ir_0'] = ir_0
        self.in_var['ir_1'] = ir_1
        self.in_var['acc_x'] = acc.val[0]
        self.in_var['acc_y'] = acc.val[1]
        self.in_var['acc_z'] = acc.val[2]
        self.in_var['left_ir'] = left_ir
        self.in_var['right_ir'] = right_ir
        self.in_var['cluster_activity'] = cluster_activity

        # defining the output variables
        self.out_var['tentacle_out'] = frond
        self.out_var['reflex_out_0'] = reflex_0
        self.out_var['reflex_out_1'] = reflex_1
        self.out_var['cluster_activity'] = cluster_activity

        # defining the input variables
        in_vars = [self.in_var['acc_x'], self.in_var['acc_y'], self.in_var['acc_z'], self.in_var['ir_0']]
        in_vars_range = [(-512, 512), (-512, 512), (-512, 512), (0, 4095)]

        # defining the output variables
        out_vars = [self.out_var['tentacle_out']]

        # create robot
        self.cbla_robot = cbla_engine.Robot_Frond(in_vars, out_vars, in_vars_range=in_vars_range)

        # instantiate
        self.instantiate()



class CBLA_Protocell(CBLA_Node):

    def __init__(self, messenger: Messenger, teensy_name: str, data_collector: cbla_engine.DataCollector,
                 als: Var=Var(0), cluster_activity: Var=Var(0),
                 led: Var=Var(0), node_name='cbla_protocell'):

        super(CBLA_Protocell, self).__init__(messenger=messenger, teensy_name=teensy_name,
                                            data_collector=data_collector, node_name=node_name)

        # defining the input variables
        self.in_var['als'] = als
        self.in_var['cluster_activity'] = cluster_activity

        # defining the output variables
        self.out_var['protocell_out'] = led
        self.out_var['cluster_activity'] = cluster_activity


        in_vars = [self.in_var['als']]
        in_vars_range = [(0, 4096)]

        out_vars = [self.out_var['protocell_out']]

        # create robot
        self.cbla_robot = cbla_engine.Robot_Protocell(in_vars, out_vars, in_vars_range=in_vars_range)

        self.instantiate()
