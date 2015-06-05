__author__ = 'Matthew'

from cbla_node import *
import types


class CBLA_Light_Node(CBLA_Node):

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

class CBLA_HalfFin_Node(CBLA_Node):

    def _get_learner_config(self):

        # learner configuration
        learner_config = dict()
        learner_config['split_thres'] = 10
        learner_config['split_thres_growth_rate'] = 1.2
        learner_config['split_lock_count_thres'] = 5
        learner_config['mean_err_thres'] = 0.015
        learner_config['reward_smoothing'] = 1
        learner_config['kga_delta'] = 1
        learner_config['kga_tau'] = 2
        learner_config['idle_mode_enable'] = False

        return learner_config

class CBLA_Reflex_Node(CBLA_Node):

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
