__author__ = 'Matthew'

import math
import random
from copy import copy
from sklearn import linear_model
from sklearn.cluster import KMeans
from sklearn.cluster import Ward
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier as knn
from sklearn.svm import SVC
import matplotlib.pyplot as plt
import numpy as np

class Expert():

    max_training_data_num = 5000

    def __init__(self, id=0, level=0):

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

        # mapping between S(t+1) to M(t+1)
        self.sm_relation = linear_model.LinearRegression()

        # error is max at first
        self.mean_error = float("inf")

        # knowledge gain assessor
        self.kga = KGA(self.mean_error)

        # historical reward history
        self.rewards_history = [0]

        # number of re-training
        self.training_count = 0


    def append(self, SM, S1, S1_predicted=None):

        if not isinstance(SM, tuple):
            raise(TypeError, "SM must be a tuple")
        if not isinstance(S1, tuple):
            raise(TypeError, "S1 must be a tuple")
        if S1_predicted is not None and not isinstance(S1_predicted, tuple):
            raise(TypeError, "S1_predicted must be a tuple")

        self.training_count += 1
        if self.left is None and self.right is None:
            self.training_data.append(SM)
            self.training_label.append(S1)

            if len(self.training_data) > Expert.max_training_data_num:
                self.training_data.pop(0)
                self.training_label.pop(0)

            # update prediction model
            self.train()

            # update the KGA
            if S1_predicted is not None:
                self.kga.append_error(S1, S1_predicted)
                self.mean_error = self.kga.calc_mean_error()  # used to determine if splitting is necessary
                self.rewards_history.append(self.kga.calc_reward())
                self.rewards_history = self.rewards_history[-1:]

            # #split if necessary
            self.split()

        # Cases when only one of the child is NONE
        elif self.left is None or self.right is None:
            raise(Exception, "Expert's Tree structure is corrupted! One child branch is missing")

        # delegate to child nodes
        elif self.region_splitter.classify(SM):
            self.right.append(SM, S1, S1_predicted)
        else:
            self.left.append(SM, S1, S1_predicted)

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
        split_threshold = 1000
        mean_error_threshold = 100 #-float('inf')
        #expected_reward_threshold = -0.001

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
                #self.region_splitter = RegionSplitter_oudeyer(self.training_data, self.training_label)
                self.region_splitter = RegionSplitter_oudeyer_modified(self.training_data, self.training_label)
                #self.region_splitter = RegionSplitter_PCA_KMean(self.training_data, self.training_label)

                # instantiate the left and right expert
                self.right = Expert(id=(self.expert_id + (1 << self.expert_level)), level=self.expert_level+1)
                self.left = Expert(id=self.expert_id,  level=self.expert_level+1)

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

                # if either of them is empty
                if len(self.left.training_data) == 0 or len(self.right.training_data) == 0:
                    # do not split
                    self.right = None
                    self.left = None
                    self.region_splitter = None
                    return

                # transferring "knowledge" to child nodes
                self.right.train()
                self.right.mean_error = self.mean_error
                self.right.rewards_history = copy(self.rewards_history)
                self.right.prediction_model = copy(self.predict_model)
                self.right.kga.errors = copy(self.kga.errors)
                self.right.training_count = 0
                self.left.train()
                self.left.mean_error = self.mean_error
                self.left.rewards_history = copy(self.rewards_history)
                self.left.prediction_model = copy(self.predict_model)
                self.left.kga.errors = copy(self.kga.errors)
                self.left.training_count = 0

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
    def calc_expected_reward(self):
        return self.rewards_history[-1]

    def get_next_action(self, S1, is_exploring, candidates=[]):

        if not isinstance(S1, tuple):
            raise(TypeError, "S1 must be a tuple")

        # this is leaf node
        if self.left is None and self.right is None:
            #print("Mean Error", self.mean_error)

            if len(self.training_data) == 0:
                raise(Exception, "This node has no training data!")

            if self.is_relevant(S1):
                # reward is just the reward in the most recent time region
                expected_reward = self.calc_expected_reward()

            else:
                expected_reward = -float("inf")

            M1 = self.get_possible_action(S1)

            if is_exploring and expected_reward > -float('inf'):
                candidates.append(copy(M1))

            return (M1, expected_reward)

        # Cases when only one of the child is NONE
        elif self.left is None and self.right is None:
            raise(Exception, "Expert's Tree structure is corrupted! One child branch is missing")

        else:
            # return the child node with the largest reward
            next_action_L = self.left.get_next_action(S1, is_exploring, candidates)
            next_action_R = self.right.get_next_action(S1, is_exploring, candidates)

            if (is_exploring and next_action_L[1] > -float("inf") and next_action_R[1] > -float("inf"))\
                or (next_action_L[1] == -float("inf") and next_action_L[1] == -float("inf")):
                if random.random() < 0.5:
                    return next_action_L
                else:
                    return next_action_R
            if next_action_L[1] > next_action_R[1]:
                return next_action_L
            else:
                return next_action_R

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

            expected_reward = self.calc_expected_reward()

            return expected_reward

        # Cases when only one of the child is NONE
        elif self.left is None and self.right is None:
            raise(Exception, "Expert's Tree structure is corrupted! One child branch is missing")

        else:

            if self.region_splitter.classify(S1+M1):
                return self.right.evaluate_action(S1, M1)
            else:
                return self.left.evaluate_action(S1, M1)

    def is_relevant(self, S1):
        #TODO how to know if the state is associated with the region
        # check if the S1 is within the min and max range of all existing data points
        data_transpose = list(zip(*self.training_data))
        for i in range(len(S1)):
            min_S = min(data_transpose[i])
            max_S = max(data_transpose[i])
            if min_S > S1[i] or max_S < S1[i]:
                return False
        return True

    def get_possible_action(self, S1):
        # TODO need a proper way to figure out what are the possible action

        # find out the indices of M data
        M_index = (len(S1), len(self.training_data[0]))

        # extract the M part of the data out
        M = zip(*self.training_data)
        M = tuple(M)[M_index[0]:M_index[1]]


        # # extract the S part of the data out
        # S = zip(*self.training_data)
        # S = tuple(S)[0:M_index[0]]
        #
        # random_select = False
        # try:
        #     self.sm_relation.fit(list(zip(*S)), list(zip(*M)))
        #     M1 = tuple(self.sm_relation.predict(S1))
        # except ValueError:
        #     random_select = True

        random_select = True
        if random_select:
        #take random number that falls within range method
            M1 = []
            # for i in range(len(M)):
            #     # find the max and min in each dimension
            #     min_M = min(M[i])
            #     max_M = max(M[i])
            #     # take a random number within the range
            #     M1.append(random.uniform(min_M, max_M))
            #
            # pick one of the previous action
            M1 = random.choice(list(zip(*M)))

            M1 = tuple(M1)

        # take the average of the M1 in each dimension method
        #M1 = tuple([sum(M1[i])/len(M1[i]) for i in range(len(M1))])

        return M1


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

    def save_mean_errors(self, mean_errors):

        # this is leaf node
        if self.left is None and self.right is None:
            mean_errors.append((self.expert_id, self.mean_error))
        else:

            self.left.save_mean_errors(mean_errors)
            self.right.save_mean_errors(mean_errors)


class RegionSplitter_KMean():

    def __init__(self, data, label):

        self.cut_dim = 0
        self.cut_val = 0

        data_dim_num = len(data[0])
        label_dim_num = len(label[0])

        data_zipped = list(zip(*data))

        #set to cut dimension 1
        # self.cut_dim = 1
        # self.clusterer = KMeans(n_clusters=2, init='k-means++')
        # self.clusterer.fit(list(zip(data_zipped[self.cut_dim])))
        # return

        # sort in each dimension
        dim_min = float("inf")
        for i in range(data_dim_num):

            # TODO: need proper clustering
            # k-mean cluster for the dimension
            clusterer = KMeans(n_clusters=2, init='k-means++')

            grouping = clusterer.fit_predict(list(zip(data_zipped[i])))

            groups = [[label[j] for j in range(len(data_zipped[i])) if grouping[j] == 0],
                      [label[j] for j in range(len(data_zipped[i])) if grouping[j] == 1]]

            weighted_avg_variance = []
            for group in groups:
                num_sample = len(group)
                group = zip(*group)

                variance = []
                for group_k in group:
                    mean = math.fsum(group_k)/len(group_k)
                    norm = math.fsum([x**2 for x in group_k])/len(group_k)
                    variance.append(math.fsum([((x - mean)**2)/norm for x in group_k]))
                weighted_avg_variance.append(math.fsum(variance)/len(variance)*num_sample)

            in_group_variance = math.fsum(weighted_avg_variance)

            if dim_min > in_group_variance:

                dim_min = in_group_variance
                self.cut_dim = i
                self.clusterer = clusterer


        # just cut in half
        #self.cut_val = exemplars[int(sample_num/2)][0][self.cut_dim]

    def classify(self, data):
        if not isinstance(data, tuple):
            raise(TypeError, "data must be a tuple")

        data = [(data[self.cut_dim],)]
        group = self.clusterer.predict(data)

        return group == 0
        # data[self.cut_dim] > self.cut_val


class RegionSplitter_PCA_KMean():
    def __init__(self, data, label):

        data_dim_num = len(data[0])
        label_dim_num = len(label[0])

        self.n_comp = min(1, data_dim_num)

        self.pca = PCA(n_components=self.n_comp)

        data = self.pca.fit_transform(data)
        data_zipped = list(zip(*data))

        # k-mean cluster for the dimension
        self.clusterer = KMeans(n_clusters=2, init='k-means++')

        self.clusterer.fit(list(zip(*data_zipped)))


    def classify(self, data):
        if not isinstance(data, tuple):
            raise(TypeError, "data must be a tuple")

        data = tuple(self.pca.transform(data)[0])
        group = self.clusterer.predict(data)

        return group == 0


class RegionSplitter_oudeyer():

    def __init__(self, data, label):

        self.cut_dim = 0
        self.cut_val = 0
        num_candidates = 50

        data_dim_num = len(data[0])
        label_dim_num = len(label[0])

        data_zipped = list(zip(*data))

        # sort in each dimension
        dim_min = float("inf")
        for i in range(data_dim_num):

            for k in range(num_candidates):
                # pick a random value
                max_val = max(data_zipped[i])
                min_val = min(data_zipped[i])
                cut_val = random.choice(np.linspace(min_val, max_val, num=100))

                groups = [[label[j] for j in range(len(data_zipped[i])) if data_zipped[i][j] <= cut_val],
                          [label[j] for j in range(len(data_zipped[i])) if data_zipped[i][j] > cut_val]]

                # check if any of the group is 0
                if len(groups[0]) == 0 or len(groups[1]) == 0:
                    continue

                weighted_avg_variance = []
                for group in groups:
                    num_sample = len(group)
                    group = zip(*group)

                    variance = []
                    for group_k in group:
                        mean = math.fsum(group_k)/len(group_k)
                        norm = max(math.fsum([x**2 for x in group_k])/len(group_k), 1)
                        variance.append(math.fsum([((x - mean)**2)/norm for x in group_k]))
                    weighted_avg_variance.append(math.fsum(variance)/len(variance)*num_sample)

                in_group_variance = math.fsum(weighted_avg_variance)

                if in_group_variance < dim_min:

                    dim_min = in_group_variance
                    self.cut_dim = i
                    self.cut_val = cut_val


        # just cut in half
        #self.cut_val = exemplars[int(sample_num/2)][0][self.cut_dim]

    def classify(self, data):
        if not isinstance(data, tuple):
            raise(TypeError, "data must be a tuple")

        group = data[self.cut_dim] <= self.cut_val

        return group == 0

class RegionSplitter_oudeyer_diff_var():

    def __init__(self, data, label):

        self.cut_dim = 0
        self.cut_val = 0
        min_group_size = 100
        num_candidates = 50

        data_dim_num = len(data[0])
        label_dim_num = len(label[0])

        data_zipped = list(zip(*data))

        # sort in each dimension
        dim_min = float("inf")
        for i in range(data_dim_num):

            for k in range(num_candidates):
                # pick a random value
                max_val = max(data_zipped[i])
                min_val = min(data_zipped[i])
                cut_val = random.choice(np.linspace(min_val, max_val, num=100))

                groups = [[label[j] for j in range(len(data_zipped[i])) if data_zipped[i][j] <= cut_val],
                          [label[j] for j in range(len(data_zipped[i])) if data_zipped[i][j] > cut_val]]

                # check if any of the group is 0
                if len(groups[0]) < min_group_size or len(groups[1]) < min_group_size:
                    continue

                weighted_avg_variance = []
                for group in groups:
                    num_sample = len(group)
                    group = zip(*group)

                    variance = []
                    for group_k in group:
                        mean = math.fsum(group_k)/len(group_k)
                        norm = max(math.fsum([x**2 for x in group_k])/len(group_k), 1)
                        variance.append(math.fsum([((x - mean)**2)/norm for x in group_k]))
                    weighted_avg_variance.append(math.fsum(variance)/len(variance)/num_sample)

                var_diff = -abs(weighted_avg_variance[1] - weighted_avg_variance[0])
                print("cut_dim=%d cut_val=%f var_diff=%f"%(i, cut_val,var_diff))
                if var_diff < dim_min:

                    dim_min = var_diff
                    self.cut_dim = i
                    self.cut_val = cut_val


        # just cut in half
        #self.cut_val = exemplars[int(sample_num/2)][0][self.cut_dim]

    def classify(self, data):
        if not isinstance(data, tuple):
            raise(TypeError, "data must be a tuple")

        group = data[self.cut_dim] <= self.cut_val

        return group == 0

class RegionSplitter_oudeyer_modified():

    def __init__(self, data, label):

        self.cut_dim = 0
        self.cut_val = 0
        num_candidates = 100
        min_group_size = 20

        data_dim_num = len(data[0])
        label_dim_num = len(label[0])

        data_zipped = list(zip(*data))

        # sort in each dimension
        dim_min = float("inf")
        for i in range(data_dim_num):

            for k in range(num_candidates):
                # pick a random value
                max_val = max(data_zipped[i])
                min_val = min(data_zipped[i])
                cut_val = random.uniform(min_val, max_val)

                groups = [[[data[j], label[j]] for j in range(len(data_zipped[i])) if data_zipped[i][j] <= cut_val],
                          [[data[j], label[j]] for j in range(len(data_zipped[i])) if data_zipped[i][j] > cut_val]]

                # check if any of the group is 0 or 1

                if len(groups[0]) < min_group_size or len(groups[1]) < min_group_size:
                    continue

                avg_error = []
                weighted_avg_variance = []
                for group in groups:

                    # calculate error with a linear model
                    data_k = list(zip(*group))[0]
                    label_k = list(zip(*group))[1]
                    predict_model = linear_model.LinearRegression()
                    predict_model.fit(data_k[:int(len(group)/2)], label_k[:int(len(group)/2)])
                    label_predict = predict_model.predict(data_k[int(len(group)/2)+1:])

                    rms_error = math.sqrt(math.fsum([(label_predict[sample] - label_k[int(len(group)/2)+1 + sample])**2 for sample in range(len(label_predict))])/len(label_predict))

                    num_sample = len(group)
                    group = zip(*group[0])

                    # calculate variance of data points
                    variance = []
                    for group_k in group:
                        mean = math.fsum(group_k)/len(group_k)
                        norm = max(math.fsum([x**2 for x in group_k])/len(group_k), 1)
                        variance.append(math.fsum([((x - mean)**2)/norm for x in group_k]))
                    weighted_avg_variance.append(math.fsum(variance)/len(variance)*num_sample)

                    avg_error.append(rms_error)

                error_diff = -(avg_error[0] - avg_error[1])**2
                smallest_error = min(avg_error)
                in_group_variance = math.fsum(weighted_avg_variance)
                #print('cut_dim=%d cut_val=%f avg_err=%f var=%f'%(i, cut_val, smallest_error, in_group_variance))

                score = (error_diff) / ((in_group_variance+1) *(smallest_error+1))

                if score < dim_min:

                    dim_min = score
                    self.cut_dim = i
                    self.cut_val = cut_val


        # just cut in half
        #self.cut_val = exemplars[int(sample_num/2)][0][self.cut_dim]

    def classify(self, data):
        if not isinstance(data, tuple):
            raise(TypeError, "data must be a tuple")

        group = data[self.cut_dim] <= self.cut_val

        return group == 0

class RegionSplitter():

    def __init__(self, data, label):


        data_dim_num = len(data[0])
        label_dim_num = len(label[0])

        data_label = zip(*(list(zip(*data)) + list(zip(*label))))

        # cluster data with labels
        clusterer = KMeans(n_clusters=2, init='k-means++')
        grouping = clusterer.fit_predict(list(data_label))
        self.classifier = SVC()
        self.classifier.fit(data, grouping)


    def classify(self, data):
        if not isinstance(data, tuple):
            raise(TypeError, "data must be a tuple")

        group = self.classifier.predict(data)

        return group==0


class KGA():

    def __init__(self, e0):
        if not isinstance(e0, float):
            raise(TypeError, "e0 must be a float")
        self.errors = [e0]

        # smoothing parameter
        self.delta = 100

        # time window
        self.tau = 30

    def append_error(self, S_actual, S_predicted):
        if not isinstance(S_actual, tuple):
            raise(TypeError, "S_actual must be a tuple")
        if not isinstance(S_predicted, tuple):
            raise(TypeError, "S_predicted must be a tuple")

        error = 0
        for i in range(len(S_actual)):
            error += (S_actual[i] - S_predicted[i])**2
        error /= len(S_actual)
        print("Prediction Error: ", error)
        self.errors.append(error)

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


if __name__ == "__main__":

    # generating exemplars
    exemplars = []
    for i in range(1,15):
        exemplar = ((math.floor(100*math.sin(math.pi*i/4)),),
                    (math.floor(100*math.sin(math.pi*i/3)),),
                    (math.floor(100*math.sin(math.pi*i/2)),))
        exemplars.append(exemplar)
    print("Generated exemplars: ", exemplars)

    # instantiate an Expert
    expert = Expert()

    # appending data to expert
    for exemplar in exemplars:

        S = exemplar[0]
        M = exemplar[1]
        S1 = exemplar[2]
        print("\n Test case ", S, M, S1)

        # have the expert make prediction
        S1_predicted = expert.predict(S, M)
        print(S1_predicted)

        # do action


        # add exemplar to expert
        expert.append(S + M, S1, S1_predicted)
        expert.split()  # won't actually split if the condition is not met

        M1, L = expert.get_next_action(S1)
        print("Expected Reward", L)
        print("Next Action", M1)

    expert.print()
