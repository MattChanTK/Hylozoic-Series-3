"""
The extension of PBAI Fin Test Bed (PFTB) that creates the Nodes that enable CBLA behaviours
"""

__author__ = 'Matthew'

from pftb_prescripted import PFTB_Prescripted
import cbla
from cbla import cbla_engine
from abstract_node import DataLogger

from collections import OrderedDict
import os
from sklearn import linear_model

class PFTB_CBLA(PFTB_Prescripted):

    """CBLA Extension for the PBAI Fin Test Bed (PFTB)

    This class inherits the PFTB_Prescripted and creates the CBLA Nodes that control and sample the Prescripted Nodes

    """

    log_dir = 'cbla_log'
    log_header = 'pftb_cbla'

    def __init__(self, Teensy_manager, auto_start=True, mode='isolated',
                 create_new_log=True, log_dir_path=None,
                 start_prescripted=False, in_user_study=False):

         # setting up the data collector
        if not isinstance(log_dir_path, str):
            log_dir_path = os.path.join(os.getcwd(), self.log_dir)

        print("Create New Log? ", create_new_log)
        print("Log Directory: ", log_dir_path)
        print("Directory Exists? ", os.path.exists(log_dir_path))
        # create new entry folder if creating new log
        if create_new_log or not os.path.exists(log_dir_path):
            latest_log_dir = None
        # add a new session folder if continuing from old log
        else:
            # use the latest data log
            all_log_dir = []
            for dir in os.listdir(log_dir_path):
                dir_path = os.path.join(log_dir_path, dir)
                if os.path.isdir(dir_path) and mode in dir:
                    all_log_dir.append(dir_path)

            if len(all_log_dir) > 0:
                latest_log_dir = max(all_log_dir, key=os.path.getmtime)
            else:
                latest_log_dir = None
        # create the data_logger
        self.data_logger = DataLogger(log_dir=self.log_dir, log_header='%s_%s' % (self.log_header, mode),
                                      log_path=latest_log_dir,
                                      save_freq=2.0, sleep_time=0.20, mode=mode)


        super(PFTB_CBLA, self).__init__(Teensy_manager=Teensy_manager, auto_start=auto_start)

    def init_routines(self):

        super(PFTB_CBLA, self).init_routines()
        self.init_cbla_nodes()

    def init_cbla_nodes(self):

        cbla_nodes = OrderedDict()

        teensy_names = tuple(self.teensy_manager.get_teensy_name_list())

         # instantiate all the basic components
        for teensy_name in teensy_names:

            # check if the teensy exists
            if teensy_name not in self.teensy_manager.get_teensy_name_list():
                print('%s does not exist!' % teensy_name)
                continue

            # Constructing the CBLA Nodes

            # ===== constructing the CBLA iFin Nodes =====
            for j in range(self.NUM_FIN):
                # defining the input variables
                in_vars = OrderedDict()
                in_vars['fin_ir'] = self.node_list['%s.f%d.ir-f' % (teensy_name, j)].out_var['input']
                in_vars['left_ir'] = self.node_list['%s.f%d.ir-s' % (teensy_name, (j + 1) % self.NUM_FIN)].out_var['input']
                in_vars['right_ir'] = self.node_list['%s.f%d.ir-s' % (teensy_name, j)].out_var['input']

                # defining the output variables
                out_vars = OrderedDict()
                out_vars['fin_on_level'] = self.node_list['%s.f%d.iFin' % (teensy_name, j)].in_var['fin_on_level']

                # Constructing the CBLA Node with Speaker 0
                iFin = PFTB_CBLA_iFin_Node(RobotClass=PFTB_iFin_Robot,
                                            messenger=self.messenger, data_logger=self.data_logger,
                                            cluster_name=teensy_name, node_type='iFin', node_id=j,
                                            in_vars=in_vars, out_vars=out_vars,
                                            s_keys=('fin_ir', 'left_ir', 'right_ir'),
                                            s_ranges=((0, 4095), (0, 4095), (0, 4095),),
                                            s_names=('Fin IR', 'Left IR', 'Right IR',),
                                            m_keys=('fin_on_level', ),
                                            m_ranges=((60, 300), ),
                                            m_names=('Fin On Level', ),
                                            )

                cbla_nodes[iFin.node_name] = iFin

            # ===== constructing the CBLA iReflex Nodes =====
            for j in range(self.NUM_FIN):
                # defining the input variables
                in_vars = OrderedDict()
                in_vars['reflex_ir'] = self.node_list['%s.f%d.ir-s' % (teensy_name, j)].out_var['input']

                # defining the output variables
                out_vars = OrderedDict()
                out_vars['target_level'] = self.node_list['%s.f%d.iReflex' % (teensy_name, j)].in_var['target_level']

                # Constructing the CBLA Reflex Node
                iReflex = PFTB_CBLA_iReflex_Node(RobotClass=PFTB_iReflex_Robot,
                                                 messenger=self.messenger, data_logger=self.data_logger,
                                                 cluster_name=teensy_name, node_type='iReflex', node_id=j,
                                                 in_vars=in_vars, out_vars=out_vars,
                                                 s_keys=('reflex_ir',),
                                                 s_ranges=((0, 4095), ),
                                                 s_names=('Reflex IR',),
                                                 m_keys=('target_level', ),
                                                 m_ranges=((40, 255), ),
                                                 m_names=('Reflex Actuator', ),
                                                 )

                cbla_nodes[iReflex.node_name] = iReflex

        # instantiate the node after the linking process
        for cbla_node in cbla_nodes.values():
            if isinstance(cbla_node, cbla.CBLA_Generic_Node):
                cbla_node.instantiate()

        self.node_list.update(cbla_nodes)

    def start_nodes(self):

        super(PFTB_CBLA, self).start_nodes()

        # start the Data Collector
        self.data_logger.start()
        print('Data Collector initialized.')

    def terminate(self):

        super(PFTB_CBLA, self).terminate()
         # terminating the data_collection thread
        self.data_logger.end_data_collection()
        self.data_logger.join()
        print("Data Logger is terminated.")


class PFTB_CBLA_iFin_Node(cbla.CBLA_Generic_Node):

    """
    This class extends a CBLA Generic Node and modifies some of its parameters.
    """

    def _get_learner_config(self):

        # learner configuration
        learner_config = dict()
        learner_config['split_thres'] = 16              # Number of exemplars needed to split
        learner_config['split_thres_growth_rate'] = 1.2 # growth of split_thres after each split
        learner_config['split_lock_count_thres'] = 3    # number of loop of not splitting after an unsuccessful split
        learner_config['split_quality_thres_0'] = 0.3   # initial split quality threshold
        learner_config['split_quality_decay'] = 0.9     # reduction in split quality threshold after every split
        learner_config['mean_err_thres'] = 0.02         # the mean error required before splitting
        learner_config['reward_smoothing'] = 1          # number of reward to average when computing action value
        learner_config['kga_delta'] = 1                 # window size for the KGA
        learner_config['kga_tau'] = 2                   # tau for the KGA
        learner_config['prediction_model'] = linear_model.LinearRegression()

        return learner_config

class PFTB_iFin_Robot(cbla_engine.Robot):

    def _set_default_config(self):
        super(PFTB_iFin_Robot, self)._set_default_config()

        self.config['sample_number'] = 20 # Number of samples within sample period
        self.config['sample_period'] = 5.0
        self.config['wait_time'] = 0.0

        # Windows Size for calculating Relative Action Value
        self.config['prev_values_deque_size'] = 10

        # Sigmoid function: https://www.desmos.com/calculator/nwqfj9bgud
        self.config['min_m_max_val'] = 0.05 #b
        self.config['low_action_m_max_val'] = 0.90 #d
        self.config['low_rel_action_val_thres'] = 7.5 #c


    def read(self, sample_method=None):

        return super(PFTB_iFin_Robot, self).read(sample_method='average')


class PFTB_CBLA_iReflex_Node(cbla.CBLA_Generic_Node):

    def _get_learner_config(self):

        # learner configuration
        learner_config = dict()
        learner_config['split_thres'] = 100             # Number of exemplars needed to split
        learner_config['split_thres_growth_rate'] = 1.2 # growth of split_thres after each split
        learner_config['split_lock_count_thres'] = 20   # number of loop of not splitting after an unsuccessful split
        learner_config['split_quality_thres_0'] = 0.3   # initial split quality threshold
        learner_config['split_quality_decay'] = 0.9     # reduction in split quality after every split
        learner_config['mean_err_thres'] = 0.04         # the mean error required before splitting
        learner_config['reward_smoothing'] = 10         # number of reward to average when computing action value
        learner_config['kga_delta'] = 2                 # window size for the KGA
        learner_config['kga_tau'] = 5                   # tau for the KGA
        learner_config['prediction_model'] = linear_model.LinearRegression()

        return learner_config

class PFTB_iReflex_Robot(cbla_engine.Robot):

    def _set_default_config(self):
        super(PFTB_iReflex_Robot, self)._set_default_config()

        self.config['sample_number'] = 5 # Number of samples within sample period
        self.config['sample_period'] = 0.5
        self.config['wait_time'] = 0.0

        # Windows Size for calculating Relative Action Value
        self.config['prev_values_deque_size'] = 150

        # Sigmoid function: https://www.desmos.com/calculator/nwqfj9bgud
        self.config['min_m_max_val'] = 0.005 #b
        self.config['low_action_m_max_val'] = 0.99 #d
        self.config['low_rel_action_val_thres'] = 10.0 #c




    def read(self, sample_method=None):

        return super(PFTB_iReflex_Robot, self).read(sample_method='average')
