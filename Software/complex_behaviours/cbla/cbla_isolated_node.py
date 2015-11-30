__author__ = 'Matthew'

from cbla_generic_node import CBLA_Generic_Node
import types
from sklearn import linear_model


class Isolated_Light_Node(CBLA_Generic_Node):

    def _get_learner_config(self):

        # learner configuration
        learner_config = dict()
        learner_config['split_thres'] = 70
        learner_config['split_thres_growth_rate'] = 1.2
        learner_config['split_lock_count_thres'] = 20
        learner_config['split_quality_thres_0'] = 0.3
        learner_config['split_quality_decay'] = 0.9
        learner_config['mean_err_thres'] = 0.02
        learner_config['reward_smoothing'] = 3
        learner_config['kga_delta'] = 2
        learner_config['kga_tau'] = 4
        # learner_config['prediction_model'] = linear_model.LinearRegression()
        learner_config['prediction_model'] = linear_model.Lasso(alpha=0.02,
                                                                positive=False,
                                                                normalize=False,
                                                                warm_start=True,
                                                                selection='random',
                                                                )

        return learner_config


class Isolated_HalfFin_Node(CBLA_Generic_Node):

    def _get_learner_config(self):

        # learner configuration
        learner_config = dict()
        learner_config['split_thres'] = 16
        learner_config['split_thres_growth_rate'] = 1.2
        learner_config['split_lock_count_thres'] = 3
        learner_config['split_quality_thres_0'] = 0.3
        learner_config['split_quality_decay'] = 0.9
        learner_config['mean_err_thres'] = 0.02
        learner_config['reward_smoothing'] = 1
        learner_config['kga_delta'] = 1
        learner_config['kga_tau'] = 2
        # learner_config['prediction_model'] = linear_model.LinearRegression()
        learner_config['prediction_model'] = linear_model.Lasso(alpha=0.02,
                                                                normalize=False,
                                                                warm_start=True,
                                                                selection='random'
                                                                )

        return learner_config


class Isolated_Reflex_Node(CBLA_Generic_Node):

    def _get_learner_config(self):

        # learner configuration
        learner_config = dict()
        learner_config['split_thres'] = 100
        learner_config['split_thres_growth_rate'] = 1.2
        learner_config['split_lock_count_thres'] = 20
        learner_config['split_quality_thres_0'] = 0.3
        learner_config['split_quality_decay'] = 0.9
        learner_config['mean_err_thres'] = 0.04
        learner_config['reward_smoothing'] = 10
        learner_config['kga_delta'] = 2
        learner_config['kga_tau'] = 5
        # learner_config['prediction_model'] = linear_model.LinearRegression()
        learner_config['prediction_model'] = linear_model.Lasso(alpha=0.02,
                                                                normalize=False,
                                                                warm_start=True,
                                                                selection='random'
                                                                )

        return learner_config
