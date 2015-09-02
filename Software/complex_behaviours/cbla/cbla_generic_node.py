__author__ = 'Matthew'

from time import clock

from abstract_node.node import *
from abstract_node import DataLogger
from interactive_system import Messenger
from sklearn import linear_model

import cbla_engine


class CBLA_Base_Node(Node):

    cbla_state_type_key = 'cbla_states'
    cbla_label_name_key = 'label_names'
    cbla_data_type_key = 'data'

    def __init__(self, messenger: Messenger, cluster_name: str, data_logger: DataLogger,
                 node_name='cbla_node'):

        if not isinstance(cluster_name, str):
            raise TypeError('cluster_name must be a string!')

        if not isinstance(node_name, str):
            raise TypeError('node_name must be a string!')

        # reference to the data collector
        self.data_logger = data_logger

        super(CBLA_Base_Node, self).__init__(messenger, node_name="%s.%s" % (cluster_name, node_name))

        self.cbla_robot = None
        self.cbla_learner = None

        # parameters
        self.state_save_period = 30.0 # seconds

        # load previous learner expert
        self.past_state = None
        current_session = self.data_logger.curr_session
        if current_session > 1:
            try:
                self.past_state = self.data_logger.get_packet(-1, self.node_name, CBLA_Base_Node.cbla_state_type_key)
                print('%s: Resuming from Session %d.' % (self.node_name, current_session))
            except KeyError:
                print('%s: Cannot find past state. The program will start fresh instead.' % self.node_name)


    def instantiate(self, cbla_robot: cbla_engine.Robot, learner_config=None):

        if isinstance(cbla_robot, cbla_engine.Robot):
            self.cbla_robot = cbla_robot
        else:
            raise AttributeError("CBLA_Robot must be implemented in the child class")

        # create learner
        M0 = self.cbla_robot.compute_initial_motor()
        S0 = self.cbla_robot.read()


        if not isinstance(learner_config, dict):
            learner_config = dict()
        self.cbla_learner = cbla_engine.Learner(S0, M0, past_state=self.past_state,
                                                **learner_config)

        # load previous learner steps
        config = dict()
        if self.past_state:
            try:
                config['update_count_start'] = self.past_state['learner_step']
            except KeyError:
                pass

        # create CBLA engine
        self.cbla_engine = cbla_engine.CBLA_Engine(self.cbla_robot, self.cbla_learner, **config)

        # internal output variables
        self.out_var['S'] = self.cbla_robot.S0
        self.out_var['M'] = self.cbla_robot.M0

        self.cbla_states = dict()
        self.cbla_states[DataLogger.info_type_key] = CBLA_Base_Node.cbla_state_type_key

    def run(self):

        # add information about the robot's label to data_collector
        label_info = dict()
        label_info[DataLogger.info_type_key] = 'label_names'
        if 's_name' in self.cbla_robot.config:
            label_info['input_label_name'] = self.cbla_robot.config['s_names']
        if 'm_name' in self.cbla_robot.config:
            label_info['output_label_name'] = self.cbla_robot.config['m_names']

        if label_info:
            self.data_logger.write_info(node_name=self.node_name, info_data=label_info)

        last_save_states_time = clock()
        while self.alive:
            # adjust the robot's wait time between act() and read()
            self.cbla_robot.sample_speed_limit = self.messenger.estimated_msg_period * 2

            # update CBLA Engine
            data_packet = self.cbla_engine.update()
            data_packet[DataLogger.packet_type_key] = CBLA_Base_Node.cbla_data_type_key

            # save the data
            self.data_logger.append_data_packet(self.node_name, data_packet)

            # cbla_engine.CBLA_Engine.print_data_packet(data_packet, header=self.node_name)

            # save state periodically
            curr_time = clock()
            if curr_time - last_save_states_time > self.state_save_period:
                self.save_states()
                last_save_states_time = curr_time

        self.save_states()

    def save_states(self):

        with self.cbla_engine.learner_lock:
            # save state when terminated
            self.cbla_states['learner_expert'] = self.cbla_engine.learner.expert
            self.cbla_states['learner_step'] = self.cbla_engine.update_count

        with self.cbla_engine.robot_lock:
            self.cbla_states['robot_object'] = self.cbla_robot

        self.data_logger.write_info(self.node_name, self.cbla_states)


class CBLA_Generic_Node(CBLA_Base_Node):

    def __init__(self, messenger: Messenger, data_logger: DataLogger,
                 cluster_name: str, node_type: str, node_id: int,
                 in_vars: OrderedDict, out_vars: OrderedDict,
                 s_keys: tuple=(), s_ranges: tuple=(), s_names: tuple=(),
                 m_keys: tuple=(), m_ranges: tuple=(), m_names: tuple=(),
                 node_version: str='', RobotClass=None, robot_config=None):

        # defining the name of the node
        self.cluster_name = str(cluster_name)
        self.node_type = str(node_type)
        if '_' in self.node_type:
            raise NameError('node_type can not have any \'_\'!')
        self.node_id = int(node_id)
        self.node_version = str(node_version)
        node_name = 'cbla_%s_%d' % (node_type, node_id)
        if self.node_version:
            node_name += '-%s' % self.node_version

        # initializing the cbla_node
        super(CBLA_Generic_Node, self).__init__(messenger=messenger, data_logger=data_logger,
                                        cluster_name=cluster_name, node_name=node_name)

        # defining the input variables
        for in_var_name, in_var in in_vars.items():
            if not isinstance(in_var, Var):
                raise TypeError("in_var must be of type Var!")

            self.in_var[in_var_name] = in_var

        # defining the output variables
        for out_var_name, out_var in out_vars.items():
            if not isinstance(out_var, Var):
                raise TypeError("out_var must be of type Var!")

            self.out_var[out_var_name] = out_var

        # defining the robot's parameters

        # check if each key is in the in_var
        for key in s_keys:
            if key not in self.in_var:
                raise AttributeError('%s key is not in in_var' % key)
        for key in m_keys:
            if key not in self.out_var:
                raise AttributeError('%s key is not in out_var' % key)

        self.s_keys = tuple(s_keys)
        self.s_ranges = tuple(s_ranges)
        self.s_names = tuple(s_names)

        self.m_keys = tuple(m_keys)
        self.m_ranges = tuple(m_ranges)
        self.m_names = tuple(m_names)

        if isinstance(RobotClass, type) and issubclass(RobotClass, cbla_engine.Robot):
            self.robot_class = RobotClass
        else:
            self.robot_class = cbla_engine.Robot

        # instantiate
        if not isinstance(robot_config, dict):
            self.robot_config = dict()
        else:
            self.robot_config = robot_config

    def instantiate(self, cbla_robot: cbla_engine.Robot=None, learner_config=None):
        if cbla_robot == None:
            if self.past_state:
                try:
                    cbla_robot = self.past_state['robot_object']

                    # check if it's a robot object
                    if not isinstance(cbla_robot, cbla_engine.Robot):
                        raise TypeError

                    # replacing with new addresses
                    self._renew_robot(cbla_robot)

                except(KeyError, TypeError, ValueError):
                    print("%s: Cannot not find saved robot_object. Creating new robot instead." % self.node_name)

                    cbla_robot = self._build_robot(RobotClass=self.robot_class, **self.robot_config)
            else:
                cbla_robot = self._build_robot(RobotClass=self.robot_class, **self.robot_config)
        else:
            self.robot_class = cbla_robot.__class__
            self.robot_config = cbla_robot.config

        if learner_config == None:
            learner_config = self._get_learner_config()

        super(CBLA_Generic_Node, self).instantiate(cbla_robot=cbla_robot, learner_config=learner_config)

    def add_in_var(self, var: Var, var_key: str, var_range:tuple=None, var_name:str=None):

        if not isinstance(var, Var):
            raise TypeError("in_var must be of type Var!")

        if not isinstance(var_key, str):
            raise TypeError("var_key must be of type str!")

        self.in_var[var_key] = var

        self.s_keys += (var_key,)

        if isinstance(var_range, (tuple, list)) and len(var_range) == 2:

            self.s_ranges += (var_range,)

        if isinstance(var_name, str):

            self.s_names += (var_name,)

    def _build_robot(self, RobotClass=cbla_engine.Robot, **robot_config) -> cbla_engine.Robot:

        s_vars = []
        # defining the input variables
        for s_key in self.s_keys:
            s_vars.append(self.in_var[s_key])

        m_vars = []
        # defining the output variables
        for m_key in self.m_keys:
            m_vars.append(self.out_var[m_key])

        # create robot
        cbla_robot = RobotClass(s_vars, m_vars,
                                s_ranges=self.s_ranges, m_ranges=self.m_ranges,
                                s_names=self.s_names, m_names=self.m_names,
                                **robot_config
                               )
        return cbla_robot

    def _renew_robot(self, old_robot: cbla_engine.Robot):

        s_vars = []
        # defining the input variables
        for s_key in self.s_keys:
            s_vars.append(self.in_var[s_key])

        m_vars = []
        # defining the output variables
        for m_key in self.m_keys:
            m_vars.append(self.out_var[m_key])

        old_robot.renew_robot(s_vars, m_vars)

    def _get_learner_config(self) -> dict:

        return None
