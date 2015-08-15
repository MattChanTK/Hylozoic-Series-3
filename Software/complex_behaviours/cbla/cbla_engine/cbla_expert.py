__author__ = 'Matthew'

import math
from copy import copy, deepcopy
from collections import defaultdict
from collections import deque
from time import perf_counter

from sklearn import linear_model
import numpy as np
# import warnings
# warnings.simplefilter("always")
from .cbla_region_splitter import RegionSplitter as RegionSplitter


class Expert():

    def __init__(self, id=0, level=0, **config_kwargs):

        # default expert configuration
        self.config = defaultdict(int)
        self.config['reward_smoothing'] = 1
        self.config['split_thres'] = 40
        self.config['split_thres_growth_rate'] = 1.0
        self.config['split_lock_count_thres'] = 1
        self.config['split_quality_thres_0'] = 0.0
        self.config['split_quality_decay'] = 1.0
        self.config['mean_err_thres'] = 0.0
        self.config['mean_err_0'] = 1.0
        self.config['action_value_0'] = 0.0
        self.config['reward_smoothing'] = 1
        self.config['learning_rate'] = 0.25
        self.config['kga_delta'] = 10
        self.config['kga_tau'] = 30
        self.config['max_training_data_num'] = 500
        self.config['prediction_model'] = linear_model.LinearRegression()

        # custom configurations
        for param, value in config_kwargs.items():
            self.config[param] = value

        # expert id
        self.expert_id = id
        self.expert_level = level

        # child expert
        self.left = None
        self.right = None

        # region splitter
        self.region_splitter = None

        # memory
        self.training_data = deque(maxlen=int(max(self.config['split_thres'], self.config['max_training_data_num'])))
        self.training_label = deque(maxlen=int(max(self.config['split_thres'], self.config['max_training_data_num'])))

        # prediction model
        self.predict_model = self.config['prediction_model']

        # error is max at first
        self.mean_error = self.config['mean_err_0']

        # expected reward - action-value
        self.learning_rate = self.config['learning_rate']
        self.action_value = self.config['action_value_0']

        # knowledge gain assessor
        self.kga = KGA(self.mean_error, delta=self.config['kga_delta'], tau=self.config['kga_tau'])

        # historical reward history
        self.rewards_history = [self.action_value]
        self.rewards_smoothing = self.config['reward_smoothing']

        # number of re-training
        self.training_count = 0

        # number of times that action associated with this region has been selected
        self.action_count = 0

        # the splitting thresholds
        self.split_thres = self.config['split_thres']
        self.split_thres_growth_rate = self.config['split_thres_growth_rate']
        self.split_quality_thres = self.config['split_quality_thres_0']
        self.split_quality_decay = self.config['split_quality_decay']
        self.mean_error_thres = self.config['mean_err_thres']
        self.split_lock_count = 0
        self.split_lock_count_thres = self.config['split_lock_count_thres']


    def append(self, SM, S1, S1_predicted=None):

        if not isinstance(SM, tuple):
            raise(TypeError, "SM must be a tuple")
        if not isinstance(S1, tuple):
            raise(TypeError, "S1 must be a tuple")
        if S1_predicted is not None and not isinstance(S1_predicted, tuple):
            raise(TypeError, "S1_predicted must be a tuple")

        self.training_count += 1
        self.action_count += 1
        if self.left is None and self.right is None:
            self.training_data.append(SM)
            self.training_label.append(S1)

            # update prediction model
            self.train()

            # update the KGA
            if S1_predicted is not None:
                self.kga.append_error(S1, S1_predicted)
                self.mean_error = self.kga.calc_mean_error()  # used to determine if splitting is necessary
                self.rewards_history.append(self.kga.calc_reward())
                self.rewards_history = self.rewards_history[-self.rewards_smoothing:]
                self.update_action_value()

            # split if necessary
            self.split()

            return self.expert_id

        # Cases when only one of the child is NONE
        elif self.left is None or self.right is None:
            raise(Exception, "Expert's Tree structure is corrupted! One child branch is missing")

        # delegate to child nodes
        elif self.region_splitter.classify(SM):
            return self.right.append(SM, S1, S1_predicted)
        else:
            return self.left.append(SM, S1, S1_predicted)

    def train(self):
        # number of samples needs to be at least the number of features
        num_sample = len(self.training_data)

        # no data
        if num_sample < 1:
            return

        # not enough features
        num_fea = len(self.training_data[0])
        if num_sample < num_fea:
            return

        try:
            self.predict_model.fit(self.training_data, self.training_label)
            # print(self.predict_model.coef_)
        except ValueError:
            pass

    def predict(self, S, M):

        if not isinstance(S, tuple):
            raise TypeError("S must be a tuple")
        if not isinstance(M, tuple):
            raise TypeError("M must be a tuple")

        # this is leaf node
        if self.left is None and self.right is None:
            try:
                S1 = self.predict_model.predict(S+M)
            except AttributeError:
                S1 = S

            if isinstance(S1, np.ndarray) and (len(S1) != len(S)):
                S1 = tuple(S1[0])
            else:
                S1 = tuple(S1)

            return S1

        # Cases when only one of the child is NONE
        elif self.left is None or self.right is None:
            raise(Exception, "Expert's Tree structure is corrupted! One child branch is missing")

        # delegate to child nodes
        if self.region_splitter.classify(S+M):
            return self.right.predict(S,M)
        else:
            return self.left.predict(S,M)

    def is_splitting(self):

        try:
            if self.split_lock_count > 0:
                self.split_lock_count -= 1
                return False
        except AttributeError:
            pass
        if len(self.training_data) > self.split_thres and \
            (self.mean_error > self.mean_error_thres):
            return True
        return False

    def split(self):

        # this is leaf node
        if self.left is None and self.right is None:

            if self.is_splitting():
                # print("It's splitting")
                # instantiate the splitter
                self.region_splitter = RegionSplitter(self.training_data, self.training_label)

                # don't split if the split quality is low
                if self.region_splitter.split_quality < self.split_quality_thres:
                    self.split_lock_count = self.split_lock_count_thres
                    return

                # instantiate the left and right expert
                child_config = self.config.copy()
                child_config['split_thres'] = self.split_thres*self.split_thres_growth_rate
                child_config['split_quality_decay'] = self.split_quality_decay*(2-self.split_quality_decay)

                self.right = Expert(id=(self.expert_id + (1 << self.expert_level)), level=self.expert_level+1,
                                    **child_config)
                self.left = Expert(id=self.expert_id,  level=self.expert_level+1,
                                   **child_config)

                # split the data to the correct region
                for i in range(len(self.training_data)):
                    if self.region_splitter.classify(self.training_data[i]):
                        self.right.training_data.append(self.training_data[i])
                        self.right.training_label.append(self.training_label[i])
                    else:
                        self.left.training_data.append(self.training_data[i])
                        self.left.training_label.append(self.training_label[i])

                # if either of them is empty (which shouldn't happen)
                if len(self.left.training_data) <= 1 or len(self.right.training_data) <= 1:
                    # do not split
                    self.right = None
                    self.left = None
                    self.region_splitter = None
                    # print("split cancelled")
                    self.split_lock_count = self.split_lock_count_thres
                    return

                # transferring "knowledge" to child nodes
                self.right.train()
                self.right.mean_error = self.mean_error
                self.right.rewards_history = copy(self.rewards_history)
                self.right.prediction_model = copy(self.predict_model)
                self.right.kga.errors = copy(self.kga.errors)
                self.right.training_count = 0
                self.right.action_count = self.action_count
                self.right.split_quality_thres = self.region_splitter.split_quality * self.split_quality_decay

                self.left.train()
                self.left.mean_error = self.mean_error
                self.left.rewards_history = copy(self.rewards_history)
                self.left.prediction_model = copy(self.predict_model)
                self.left.kga.errors = copy(self.kga.errors)
                self.left.training_count = 0
                self.left.action_count = self.action_count
                self.left.split_quality_thres = self.region_splitter.split_quality * self.split_quality_decay

                # clear the training data at the parent node so they don't get modified accidentally
                self.training_data.clear()
                self.training_label.clear()
                # clear everything as they are not needed any more
                self.mean_error = None
                self.predict_model = None
                self.kga = None
                self.rewards_history = None

        # Cases when only one of the child is NONE
        elif self.left is None and self.right is None:
            raise(Exception, "Expert's Tree structure is corrupted! One child branch is missing")

        else:
            # delegate to child nodes
            self.right.split()
            self.left.split()

    def update_action_value(self):
        #self.action_value *= 0.95
        #self.action_value += self.learning_rate*(math.fsum(self.rewards_history[-self.rewards_smoothing:])/len(self.rewards_history[-self.rewards_smoothing:]))
        self.action_value = math.fsum(self.rewards_history[-self.rewards_smoothing:])/len(self.rewards_history[-self.rewards_smoothing:])
        return self.action_value

    def get_largest_action_value(self):

        # this is leaf node
        if self.left is None and self.right is None:

            if len(self.training_data) == 0:
                raise (Exception, "This node has no training data!")

            return self.action_value

        # Cases when only one of the child is NONE
        elif self.left is None and self.right is None:
            raise (Exception, "Expert's Tree structure is corrupted! One child branch is missing")

        else:
            return max(self.left.get_largest_action_value(), self.right.get_largest_action_value())

    def evaluate_action(self, S1, M1):

        if not isinstance(S1, tuple):
            raise TypeError("S1 must be a tuple (current value = %s)" % str(S1) )
        if not isinstance(M1, tuple):
            raise TypeError("M1 must be a tuple (current value = %s)" % str(S1))

        # this is leaf node
        if self.left is None and self.right is None:
            #print("Mean Error", self.mean_error)
            return self.action_value

        # Cases when only one of the child is NONE
        elif self.left is None and self.right is None:
            raise(Exception, "Expert's Tree structure is corrupted! One child branch is missing")

        else:

            if self.region_splitter.classify(S1+M1):
                return self.right.evaluate_action(S1, M1)
            else:
                return self.left.evaluate_action(S1, M1)

    def print(self, level=0):

        # this is leaf node
        if self.left is None and self.right is None:
            mean_error_string = '%.*f' % (2, self.mean_error)
            print(len(self.training_data), "#", str(self.training_count), "(err =", mean_error_string, ";ER =", self.rewards_history[-1], ") --", self.training_data)
            #print(len(self.training_data), "#", str(self.expert_id), "(err =", mean_error_string, ";ER =", self.rewards_history[-1], ") --", self.training_data)

        else:
            print(" L ** ", end="")
            self.left.print(level+1)
            print((" ")*len(" L ** ")*level, "R ** ", end="")
            self.right.print(level+1)

    def save_expert_info(self, info, include_exemplars=False):

        # this is leaf node
        if self.left is None and self.right is None:

            try:
                info['expert_ids'].append(self.expert_id)
            except AttributeError:
                info['expert_ids'] = [self.expert_id]

            info['mean_errors'][self.expert_id] = self.mean_error
            info['action_values'][self.expert_id] = self.action_value
            info['action_counts'][self.expert_id] = self.action_count
            info['latest_rewards'][self.expert_id] = self.rewards_history[-1]

            if include_exemplars:
                info['exemplars'][self.expert_id] = [copy(self.training_data), copy(self.training_label)]

            info['prediction_model'][self.expert_id] = self.predict_model
        else:
            self.left.save_expert_info(info, include_exemplars=include_exemplars)
            self.right.save_expert_info(info, include_exemplars=include_exemplars)

class KGA():

    def __init__(self, e0, delta=50, tau=10):
        if not isinstance(e0, float):
            raise(TypeError, "e0 must be a float")
        self.errors = [e0]

        # smoothing parameter
        self.delta = delta

        # time window
        self.tau = tau

    def append_error(self, S_actual, S_predicted):
        if not isinstance(S_actual, tuple):
            raise(TypeError, "S_actual must be a tuple")
        if not isinstance(S_predicted, tuple):
            raise(TypeError, "S_predicted must be a tuple")

        error = 0
        for i in range(len(S_actual)):
            error += (S_actual[i] - S_predicted[i])**2
        error = math.sqrt(error/len(S_actual))
        #print("Prediction Error: ", error)
        self.errors.append(error)
        return error

    def calc_mean_error(self):

        # if there aren't enough error in the history yet
        if len(self.errors) == 0:
            mean_error = float("inf")
        else:
            errors = self.errors[-int(self.delta):]
            mean_error = math.fsum(errors)/len(errors)
        return mean_error

    def metaM(self):

        # if there aren't enough error in the history yet
        if len(self.errors) == 0:
            mean_error_predicted = float("inf")
        elif len(self.errors) <= self.tau:
            mean_error_predicted = self.errors[0]
        else:
            errors = self.errors[-int(self.delta+self.tau):-int(self.tau)]
            mean_error_predicted = math.fsum(errors)/len(errors)
        return mean_error_predicted

    def calc_reward(self):
        #remove old histories that are not needed
        self.errors = self.errors[-int(self.delta+self.tau):]
        reward = self.metaM() - self.calc_mean_error()
        if math.isnan(reward):  # happens when it's inf - inf
            reward = 0
        return reward
