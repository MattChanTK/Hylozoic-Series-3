__author__ = 'Matthew'

from time import clock

from abstract_node.node import *
from interactive_system import Messenger

import cbla_engine


class CBLA_Base_Node(Node):

    def __init__(self, messenger: Messenger, cluster_name: str, data_collector: cbla_engine.DataCollector,
                 node_name='cbla_node'):


        if not isinstance(cluster_name, str):
            raise TypeError('cluster_name must be a string!')

        if not isinstance(node_name, str):
            raise TypeError('node_name must be a string!')


        # reference to the data collector
        self.data_collector = data_collector

        super(CBLA_Base_Node, self).__init__(messenger, node_name="%s.%s" % (cluster_name, node_name))

        self.state_save_period = 20  # seconds

        self.cbla_robot = None
        self.cbla_learner = None

    def instantiate(self, cbla_robot: cbla_engine.Robot, learner_config=None):

        if isinstance(cbla_robot, cbla_engine.Robot):
            self.cbla_robot = cbla_robot
        else:
            raise AttributeError("CBLA_Robot must be implemented in the child class")

        # create learner
        M0 = self.cbla_robot.compute_initial_motor()
        S0 = self.cbla_robot.read()

        # load previous learner expert
        try:
            past_state = self.data_collector.data_file['state'][self.node_name]
        except KeyError:
            past_state = None

        if not isinstance(learner_config, dict):
            learner_config = dict()
        self.cbla_learner = cbla_engine.Learner(S0, M0, past_state=past_state,
                                                **learner_config)

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
        self.out_var['best_val'] = Var(0)

        self.cbla_states = dict()

    def run(self):

        # add information about the robot's label to data_collector
        label_info = dict()
        if 's_name' in self.cbla_robot.config:
            label_info['input_label_name'] = self.cbla_robot.config['s_names']
        if 'm_name' in self.cbla_robot.config:
            label_info['output_label_name'] = self.cbla_robot.config['m_names']

        if label_info:
            self.data_collector.update_state(node_name=self.node_name, states_update=label_info)

        last_save_states_time = clock()
        while self.alive:
            # adjust the robot's wait time between act() and read()
            self.cbla_robot.curr_wait_time = max(self.cbla_robot.config['wait_time'],
                                                 self.messenger.estimated_msg_period * 6)

            # update CBLA Engine
            data_packet = self.cbla_engine.update()

            # save the data
            self.data_collector.append_data_packet(self.node_name, data_packet)

            self.out_var['loop_time'].val = data_packet['loop_period']
            self.out_var['idle_mode'].val = data_packet['in_idle_mode']
            self.out_var['node_step'].val = data_packet['step']
            self.out_var['best_val'].val = data_packet['best_action_value']

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

        self.data_collector.update_state(self.node_name, self.cbla_states)


class CBLA_Node(CBLA_Base_Node):

    def __init__(self, messenger: Messenger, data_collector: cbla_engine.DataCollector,
                 cluster_name: str, node_type: str, node_id: int,
                 in_vars: OrderedDict, out_vars: OrderedDict,
                 s_keys: tuple=(), s_ranges: tuple=(), s_names: tuple=(),
                 m_keys: tuple=(), m_ranges: tuple=(), m_names: tuple=(),
                 node_version: str='', RobotClass=None):

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
        super(CBLA_Node, self).__init__(messenger=messenger, data_collector=data_collector,
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
            robot_class = RobotClass
        else:
            robot_class = cbla_engine.Robot

        # instantiate
        self.instantiate(cbla_robot=self._build_robot(RobotClass=robot_class),
                         learner_config=self._get_learner_config())

    def _build_robot(self, RobotClass=cbla_engine.Robot) -> cbla_engine.Robot:

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
                                sample_window=20, sample_period=0.1,
                               )
        return cbla_robot

    def _get_learner_config(self) -> dict:

        return None
