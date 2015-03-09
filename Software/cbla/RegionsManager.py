__author__ = 'Matthew'

from RegionSplitter import RegionSplitter_oudeyer as RegionSplitter
import math
import random
from copy import copy
from sklearn import linear_model

class Expert():

    max_training_data_num = 3000

    def __init__(self, id=0, level=0, split_thres=1000, split_thres_growth_rate=1.2,
                 split_quality_decay=0.5, split_lock_count_thres=250,
                 mean_err_thres=1.0, learning_rate=0.25, kga_delta=50, kga_tau=10):

        self.expert_id = id
        self.expert_level = level

        # child expert
        self.left = None
        self.right = None

        # region splitter
        self.region_splitter = None

        # memory
        self.training_data = []
        self.training_label = []

        # prediction model
        self.predict_model = linear_model.LinearRegression()
        #self.predict_model = SVR()

        # mapping between S(t+1) to M(t+1)
        self.sm_relation = linear_model.LinearRegression()

        # error is max at first
        self.mean_error = 0.0 #float("inf")

        # expected reward - action-value
        self.learning_rate = learning_rate
        self.action_value = 0.0

        # knowledge gain assessor
        self.kga = KGA(self.mean_error, delta=kga_delta, tau=kga_tau)

        # historical reward history
        self.rewards_history = [self.action_value]
        self.rewards_smoothing = 1

        # number of re-training
        self.training_count = 0

        # number of times that action associated with this region has been selected
        self.action_count = 0

        # the splitting thresholds
        self.split_thres = split_thres
        self.split_thres_growth_rate = split_thres_growth_rate
        self.split_quality_thres = -float('inf')
        self.split_quality_decay = split_quality_decay
        self.mean_error_thres = mean_err_thres
        self.split_lock_count = 0
        self.split_lock_count_thres = split_lock_count_thres


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

            if len(self.training_data) > max(self.split_thres, Expert.max_training_data_num):
                self.training_data.pop(0)
                self.training_label.pop(0)
                #print("reach max Training data")

            # update prediction model
            self.train()

            # update the KGA
            if S1_predicted is not None:
                self.kga.append_error(S1, S1_predicted)
                self.mean_error = self.kga.calc_mean_error()  # used to determine if splitting is necessary
                self.rewards_history.append(self.kga.calc_reward())
                self.rewards_history = self.rewards_history[-self.rewards_smoothing:]
                self.update_action_value()

            # #split if necessary
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
        try:
            self.predict_model.fit(self.training_data, self.training_label)
        except ValueError:
            pass

    def predict(self, S, M):

        if not isinstance(S, tuple):
            raise(TypeError, "S must be a tuple")
        if not isinstance(M, tuple):
            raise(TypeError, "M must be a tuple")

        # this is leaf node
        if self.left is None and self.right is None:
            try:
                S1 = tuple(self.predict_model.predict(S+M))
            except AttributeError:
                S1 = S
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
        split_threshold = self.split_thres
        mean_error_threshold = self.mean_error_thres  # -float('inf')

        try:
            if self.split_lock_count > 0:
                self.split_lock_count -= 1
                return False
        except AttributeError:
            pass
        if len(self.training_data) > split_threshold and \
            (self.mean_error > mean_error_threshold):# or self.calc_expected_reward() < expected_reward_threshold):
            return True
        return False

    def split(self):

        # this is leaf node
        if self.left is None and self.right is None:

            if self.is_splitting():
                print("It's splitting")
                # instantiate the splitter
                self.region_splitter = RegionSplitter(self.training_data, self.training_label)

                # instantiate the left and right expert
                self.right = Expert(id=(self.expert_id + (1 << self.expert_level)), level=self.expert_level+1,
                                    split_thres=self.split_thres*self.split_thres_growth_rate,
                                    split_thres_growth_rate=self.split_thres_growth_rate,
                                    split_quality_decay=self.split_quality_decay*(2-self.split_quality_decay),
                                    mean_err_thres=self.mean_error_thres,
                                    learning_rate=self.learning_rate, kga_tau=self.kga.tau, kga_delta=self.kga.delta)
                self.left = Expert(id=self.expert_id,  level=self.expert_level+1,
                                    split_thres=self.split_thres*self.split_thres_growth_rate,
                                    split_thres_growth_rate=self.split_thres_growth_rate,
                                    split_quality_decay=self.split_quality_decay*(2-self.split_quality_decay),
                                    mean_err_thres=self.mean_error_thres,
                                    learning_rate=self.learning_rate, kga_tau=self.kga.tau, kga_delta=self.kga.delta)

                # split the data to the correct region
                for i in range(len(self.training_data)):
                    if self.region_splitter.classify(self.training_data[i]):
                        self.right.training_data.append(self.training_data[i])
                        self.right.training_label.append(self.training_label[i])
                        # self.right.append(self.training_data[i], self.training_label[i])
                    else:
                        self.left.training_data.append(self.training_data[i])
                        self.left.training_label.append(self.training_label[i])
                        #self.left.append(self.training_data[i], self.training_label[i])

                # if either of them is empty  or if the split doesn't improve prediction error (low quality
                if len(self.left.training_data) == 0 or len(self.right.training_data) == 0 \
                        or self.region_splitter.split_quality < self.split_quality_thres:
                    # do not split
                    self.right = None
                    self.left = None
                    self.region_splitter = None
                    print("split cancelled")
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
                self.training_data = []
                self.training_label = []
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
            raise(TypeError, "S1 must be a tuple")
        if not isinstance(M1, tuple):
            raise(TypeError, "M1 must be a tuple")

        # this is leaf node
        if self.left is None and self.right is None:
            #print("Mean Error", self.mean_error)

            if len(self.training_data) == 0:
                raise(Exception, "This node has no training data!")

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

    def save_expert_ids(self, expert_ids):

        # this is leaf node
        if self.left is None and self.right is None:
            expert_ids.append(self.expert_id)
        else:
            self.left.save_expert_ids(expert_ids)
            self.right.save_expert_ids(expert_ids)

    def save_mean_errors(self, mean_errors):

        # this is leaf node
        if self.left is None and self.right is None:
            mean_errors.append((self.expert_id, self.mean_error))
        else:

            self.left.save_mean_errors(mean_errors)
            self.right.save_mean_errors(mean_errors)

    def save_action_values(self, values):

        # this is leaf node
        if self.left is None and self.right is None:
            values.append((self.expert_id, self.action_value))
        else:
            self.left.save_action_values(values)
            self.right.save_action_values(values)

    def save_action_count(self, action_count):

        # this is leaf node
        if self.left is None and self.right is None:
            action_count.append((self.expert_id, self.action_count))
        else:
            self.left.save_action_count(action_count)
            self.right.save_action_count(action_count)

    def save_exemplars(self, exemplars_data):

        # this is leaf node
        if self.left is None and self.right is None:
            exemplars_data[self.expert_id] = [copy(self.training_data), copy(self.training_label)]
        else:
            self.left.save_exemplars(exemplars_data)
            self.right.save_exemplars(exemplars_data)

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
        reward = round(self.metaM() - self.calc_mean_error(), 2)
        if math.isnan(reward):  # happens when it's inf - inf
            reward = 0
        return reward
