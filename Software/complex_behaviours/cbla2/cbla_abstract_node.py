__author__ = 'Matthew'

from cbla_node import *


class CBLA_Abstract_Node(CBLA_Node):

    def __init__(self, messenger: Messenger, data_collector: cbla_engine.DataCollector,
                 teensy_name: str, node_type: str, node_id: int,
                 in_vars: OrderedDict, out_vars: OrderedDict,
                 s_keys: tuple=(), s_ranges: tuple=(), s_names: tuple=(),
                 m_keys: tuple=(), m_ranges: tuple=(), m_names: tuple=(),
                 node_version: str=''):

        # defining the name of the node
        self.node_type = str(node_type)
        if '_' in self.node_type:
            raise NameError('node_type can not have any \'_\'!')
        self.node_id = int(node_id)
        self.node_version = str(node_version)
        node_name = 'cbla_%s_%d' % (node_type, node_id)
        if self.node_version:
            node_name += '-%s' % self.node_version

        # initializing the cbla_node
        super(CBLA_Abstract_Node, self).__init__(messenger=messenger, teensy_name=teensy_name,
                                            data_collector=data_collector, node_name=node_name)

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
            if key not in self.in_var:
                raise AttributeError('%s key is not in in_var' % key)

        self.s_keys = tuple(s_keys)
        self.s_ranges = tuple(s_ranges)
        self.s_names = tuple(s_names)

        self.m_keys = tuple(s_keys)
        self.m_ranges = tuple(s_ranges)
        self.m_names = tuple(s_names)

        # instantiate
        self.instantiate(cbla_robot=self._build_robot(),
                         learner_config=self._get_learner_config())

    def _build_robot(self) -> cbla_engine.Robot:

        s_vars = []
        # defining the input variables
        for s_key in self.s_keys:
            s_vars.append(self.in_var[s_key])

        m_vars = []
        # defining the output variables
        for m_key in self.m_keys:
            m_vars.append(self.in_var[m_key])

        # create robot
        cbla_robot = cbla_engine.Robot(s_vars, m_vars,
                                       s_ranges=self.s_ranges, m_ranges=self.m_ranges,
                                       s_names=self.s_names, m_names=self.m_names,
                                       sample_window=20, sample_period=0.1,
                                      )
        return cbla_robot

    def _get_learner_config(self) -> dict:

        return None


class CBLA_Light_Node(CBLA_Abstract_Node):

    def _get_learner_config(self):

        # learner configuration
        learner_config = dict()
        learner_config['split_thres'] = 120
        learner_config['split_thres_growth_rate'] = 1.5
        learner_config['split_lock_count_thres'] = 10
        learner_config['mean_err_thres'] = 0.025
        learner_config['reward_smoothing'] = 1
        learner_config['kga_delta'] = 2
        learner_config['kga_tau'] = 8

        return learner_config

class CBLA_HalfFin_Node(CBLA_Abstract_Node):

    pass

class CBLA_Reflex_Node(CBLA_Abstract_Node):

    pass