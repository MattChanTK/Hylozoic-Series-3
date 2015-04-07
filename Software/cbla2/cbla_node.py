__author__ = 'Matthew'

from time import clock
from abstract_node.node import *
from interactive_system import Messenger
import cbla_engine


class CBLA_Tentacle(Node):

    def __init__(self, messenger: Messenger, teensy_name: str,
                 ir_0: Var=Var(0), ir_1: Var=Var(0), acc: Var=Var(0), cluster_activity: Var=Var(0),
                 left_ir: Var=Var(0), right_ir: Var=Var(0),
                 frond: Var=Var(0), reflex_0: Var=Var(0), reflex_1: Var=Var(0), node_name='cbla_tentacle'):

        if not isinstance(teensy_name, str):
            raise TypeError('teensy_name must be a string!')

        self.teensy_name = teensy_name

        super(CBLA_Tentacle, self).__init__(messenger, node_name='%s.%s' % (teensy_name, node_name))

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


        # create learner
        M0 = self.cbla_robot.compute_initial_motor()
        S0 = self.cbla_robot.read()
        self.cbla_learner = cbla_engine.Learner(S0, M0)

        # create CBLA engine
        self.cbla_engine = cbla_engine.CBLA_Engine(self.cbla_robot, self.cbla_learner)

        # internal output variables
        self.out_var['S'] = Var(self.cbla_robot.S0)
        self.out_var['M'] = Var(self.cbla_robot.M0)

    def run(self):

        while True:
            # adjust the robot's wait time between act() and read()
            self.cbla_robot.config['wait_time'] = self.messenger.estimated_msg_period*2

            # update CBLA Engine
            self.cbla_engine.update()

            # update the node's internal variables
            self.out_var['S'].val = self.cbla_robot.S0
            self.out_var['M'].val = self.cbla_robot.M0





class CBLA_Protocell(Node):

    def __init__(self, messenger: Messenger, teensy_name: str,
                 als: Var=Var(0), cluster_activity: Var=Var(0),
                 led: Var=Var(0), node_name='cbla_protocell'):


        if not isinstance(teensy_name, str):
            raise TypeError('teensy_name must be a string!')

        self.teensy_name = teensy_name

        super(CBLA_Protocell, self).__init__(messenger, node_name='%s.%s' % (teensy_name, node_name))

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

        # create learner
        M0 = self.cbla_robot.compute_initial_motor()
        S0 = self.cbla_robot.read()
        self.cbla_learner = cbla_engine.Learner(S0, M0)

        # create CBLA engine
        self.cbla_engine = cbla_engine.CBLA_Engine(self.cbla_robot, self.cbla_learner)

        # internal output variables
        self.out_var['S'] = Var(self.cbla_robot.S0)
        self.out_var['M'] = Var(self.cbla_robot.M0)

    def run(self):

        while True:
            # adjust the robot's wait time between act() and read()
            self.cbla_robot.config['wait_time'] = self.messenger.estimated_msg_period * 2

            # update CBLA Engine
            self.cbla_engine.update()

            # update the node's internal variables
            self.out_var['S'].val = self.cbla_robot.S0
            self.out_var['M'].val = self.cbla_robot.M0