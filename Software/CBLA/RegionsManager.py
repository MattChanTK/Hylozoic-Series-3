__author__ = 'Matthew'

import math

class Expert():


    def __init__(self):

        # child expert
        self.left = None
        self.right = None

        # region splitter
        self.region_splitter = None

        # memory
        self.training_data = []
        self.training_label = []

        # error is max at first
        self.mean_error = 99999999999.9

        # knowledge gain assessor
        self.kga = KGA(self.mean_error)

        # histroical reward history
        self.rewards_history = [0]

    def append(self, SM, S1):

        if not isinstance(SM, tuple):
            raise(TypeError, "SM must be a tuple")

        if not isinstance(S1, tuple):
            raise(TypeError, "S1 must be a tuple")

        if self.left is None and self.right is None:
            self.training_data.append(SM)
            self.training_label.append(S1)

            # update prediction model
            self.train()

            # update the KGA
            self.kga.append_error(SM[0:len(S1)], S1)
            self.mean_error = self.kga.calc_mean_error()  # used to determine if splitting is necessary
            self.rewards_history.append(self.kga.calc_reward())

        # TODO: add cases when only one of the child is NONE

        # delegate to child nodes
        elif self.region_splitter.classify(SM):
            self.right.append(SM, S1)
        else:
            self.left.append(SM, S1)

    def train(self):
        pass

    def predict(self, S, M):

        if not isinstance(S, tuple):
            raise(TypeError, "S must be a tuple")
        if not isinstance(M, tuple):
            raise(TypeError, "M must be a tuple")

        # this is leaf node
        if self.left is None and self.right is None:
            # Todo: need a real regressor
            return S

        # TODO: add cases when only one of the child is NONE

        # delegate to child nodes
        if self.region_splitter.classify(S+M):
            return self.right.predict(S,M)
        else:
            return self.left.predict(S,M)

    def is_splitting(self):
        split_threshold = 5
        if len(self.training_data) > split_threshold:
            return True
        return False

    def split(self):

        # this is leaf node
        if self.left is None and self.right is None:
            if self.is_splitting():

                # instantiate the splitter
                self.region_splitter = RegionSplitter(self.training_data, self.training_label)

                # instantiate the left and right expert
                self.right = Expert()
                self.left = Expert()

                # split the data to the correct region
                for i in range(len(self.training_data)):
                    if self.region_splitter.classify(self.training_data[i]):
                        self.right.append(self.training_data[i], self.training_label[i])
                    else:
                        self.left.append(self.training_data[i], self.training_label[i])

                # clear the training data at the parent node so they don't get modified accidentally
                self.training_data = []
                self.training_label = []

                # clear everything as they are not needed any more
                self.mean_error = None

                # knowledge gain assessor
                self.kga = None

                # histroical reward history
                self.rewards_history = None

        else:
            # delegate to child nodes
            self.right.split()
            self.left.split()

        # TODO: add cases when only one of the child is NONE

    def get_expected_reward(self, S1):

        if not isinstance(S1, tuple):
            raise(TypeError, "S1 must be a tuple")

        # this is leaf node
        if self.left is None and self.right is None:
            # TODO: deal cases when there's no training data

            # find out the indices of M data
            M_index = (len(self.training_data[0]) - len(S1), len(self.training_data[0]))

            # extract the M part of the data out
            M1 = zip(*self.training_data)
            M1 = tuple(M1)[M_index[0]:M_index[1]]

            # take the average of the M1 in each dimension
            M1 = tuple([sum(M1[i])/len(M1[i]) for i in range(len(M1))])

            if self.is_possible(S1, M1):
                # reward is just the reward in the most recent time region
                expected_reward = self.rewards_history[-1]
            else:
                expected_reward = -9999999999.999

            return (expected_reward, M1)

        # TODO: add cases when only one of the child is NONE

        # return the child node with the largest reward
        expected_reward_L = self.left.get_expected_reward(S1)
        expected_reward_R = self.right.get_expected_reward(S1)

        if expected_reward_L[0] > expected_reward_R[0]:
            return expected_reward_L
        else:
            return expected_reward_R

    def is_possible(self, S1, M1):
        # Todo: figure out how to tell if an action is possible given a state
        return True

    def print(self, level=0):

        # this is leaf node
        if self.left is None and self.right is None:
            print("--", self.training_data)

        else:
            print(" L ** ", end="")
            self.left.print(level+1)
            print("      " * level, "R ** ", end="")
            self.right.print(level+1)

class RegionSplitter():

    def __init__(self, data, label):

        self.cut_dim = 0
        self.cut_val = 0

        # Todo: need proper clustering

        sample_num = len(data)
        dim_num = len(data[0])

        # combina the data and the label for sorting purposes
        exemplars = [(data[i], label[i]) for i in range(sample_num)]

        # sort in each dimension
        dim_max_range = 0
        for i in range(dim_num):
            exemplars.sort(key=lambda exemplar: exemplar[0][i])

            if dim_max_range < exemplars[-1][0][i] - exemplars[0][0][i]:
                self.cut_dim = i

        self.cut_val = exemplars[int(sample_num/2)][0][self.cut_dim]

    def classify(self, data):
        if not isinstance(data, tuple):
            raise(TypeError, "S must be a tuple")

        return data[self.cut_dim] > self.cut_val


class KGA():

    def __init__(self, e0):
        if not isinstance(e0, float):
            raise(TypeError, "e0 must be a float")
        self.errors = [e0]

        # smoothing parameter
        self.delta = 5

        # time window
        self.tau = 4

    def append_error(self, S_actual, S_predicted):
        if not isinstance(S_actual, tuple):
            raise(TypeError, "S_actual must be a tuple")
        if not isinstance(S_predicted, tuple):
            raise(TypeError, "S_predicted must be a tuple")

        error = 0
        for i in range(len(S_actual)):
            error += (S_actual[i] - S_predicted[i])**2

        self.errors.append(error)

    def calc_mean_error(self):

        mean_error = math.fsum(self.errors[-self.delta:])/self.delta
        return mean_error

    def metaM(self):

        mean_error_predicted = math.fsum(self.errors[-(self.delta+self.tau):-(self.tau)])/self.delta
        return mean_error_predicted

    def calc_reward(self):

        return self.metaM() - self.calc_mean_error()

if __name__ == "__main__":

    # generating exemplars
    exemplars = []
    for i in range(1,15):
        exemplar = ((math.floor(100*math.sin(math.pi*i/4)),),
                    (math.floor(100*math.sin(math.pi*i/3)),),
                    (math.floor(100*math.sin(math.pi*i/2)),))
        exemplars.append(exemplar)

    print("Generated exemplars", exemplars)

    # instantiate an Expert
    expert = Expert()
    for data in exemplars:
        expert.append(data[0] + data[1], data[1])
        expert.split()

    S = (70,)
    M = (90,)
    print(expert.predict(S, M))
    S1 = (40,)
    expert.append(S+M, S1)
    expert.split()
    expert.print()

    print("Expected Reward", expert.get_expected_reward(S1))
    print("Errors", expert.kga.errors)