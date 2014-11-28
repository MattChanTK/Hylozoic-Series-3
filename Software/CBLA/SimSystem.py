__author__ = 'Matthew'
import math
import random
import numpy as np
import copy
import pickle


class SimpleFunction():

    def __init__(self, low_bound=(-80,), high_bound=(80,)):


        if not isinstance(low_bound, tuple):
            raise(TypeError, "low_bound must be a tuple")
        if not isinstance(high_bound, tuple):
            raise(TypeError, "high_bound must be a tuple")
        if len(low_bound) != len(high_bound):
            raise(ValueError, "low_bound and high_bound must be the same dimension")


        self.m_high_bound = high_bound
        self.m_low_bound = low_bound

        self.M0 = low_bound  # data
        self.S = (0,)  # label


    def actuate(self, M):
        if not isinstance(M, tuple):
            raise(TypeError, "M must be a tuple")
        if len(M) != len(self.M0):
            raise(ValueError, "M must be %d dimension" % len(self.M0))

        S1 = [0]*len(self.S)
        for i in range(len(self.S)):
            for m in M:
                S1[i] += math.sin(m/25.0)*10.0

        self.S = tuple(S1)
        self.M0 = M

    def report(self, report_m=False):

        if report_m:
            return self.S, self.M0

        return self.S

    def get_possible_action(self, state=None, num_sample=1000, randomize=True):

        x_dim = len(self.m_low_bound)

        X = np.zeros((num_sample, x_dim))

        if randomize:
            for i in range(x_dim):
                X[:, i] = np.random.uniform(self.m_low_bound[i], self.m_high_bound[i], num_sample)
        else:
            for i in range(x_dim):
                X[:, i] = np.linspace(self.m_low_bound[i], self.m_high_bound[i], num_sample)

        M_candidates = tuple(map(tuple, X))

        return M_candidates

class SimpleFunction2(SimpleFunction):

    def actuate(self, M):
        if not isinstance(M, tuple):
            raise(TypeError, "M must be a tuple")
        if len(M) != len(self.M0):
            raise(ValueError, "M must be %d dimension" % len(self.M0))

        S1 = [0]*len(self.S)


        if M[0] > 25:
            for i in range(len(self.S)):
                for m in M:
                    S1[i] += M[0]/5

        elif M[0] > -25:
            for i in range(len(self.S)):
                for m in M:
                    S1[i] += math.sin(m/7.0)*10.0
        else:
            for i in range(len(self.S)):
                for m in M:
                    S1[i] += math.sin(m/7.0)*10.0 + random.uniform(M[0]/15, -M[0]/15)

        self.S = tuple(S1)
        self.M0 = M


class SimpleFunction3(SimpleFunction):

    def actuate(self, M):
        if not isinstance(M, tuple):
            raise(TypeError, "M must be a tuple")
        if len(M) != len(self.M0):
            raise(ValueError, "M must be %d dimension" % len(self.M0))

        S1 = [0]*len(self.S)


        for i in range(len(self.S)):
            for m in M:
                if m >25:
                    S1[i] += M[0]/5
                elif m > -15:
                    S1[i] += math.sin(m/15.0)*10.0
                else:
                    S1[i] += math.sin(m/15.0)*10.0 + random.uniform(m/25, -m/25)


        self.S = tuple(S1)
        self.M0 = M

class DiagonalPlane(SimpleFunction):
    def actuate(self, M):
        if not isinstance(M, tuple):
            raise(TypeError, "M must be a tuple")
        if len(M) != len(self.M0):
            raise(ValueError, "M must be %d dimension" % len(self.M0))

        S1 = [0]*len(self.S)


        for i in range(len(self.S)):
            if math.fsum(M) > 0:
                S1[i] = 0
            else:
                S1[i] =0 + random.uniform(-60, 60)

        self.S = tuple(S1)
        self.M0 = M

class DiagonalPlane2(SimpleFunction):
    def actuate(self, M):
        if not isinstance(M, tuple):
            raise(TypeError, "M must be a tuple")
        if len(M) != len(self.M0):
            raise(ValueError, "M must be %d dimension" % len(self.M0))

        S1 = [0]*len(self.S)


        for i in range(len(self.S)):
            if math.fsum(M) > 20:
                S1[i] = 0
            elif math.fsum(M) > -40:
                S1[i] = math.sin(M[0]/25.0)*30.0
            else:
                S1[i] =0 + random.uniform(-60, 60)

        self.S = tuple(S1)
        self.M0 = M

class SimpleDataSource(SimpleFunction):

    def __init__(self, filename):

        if not isinstance(filename, str):
            raise(TypeError, "filename must be a string")

        with open(filename, 'rb') as data_pickle:
            self.data = pickle.load(data_pickle)
            self.label = pickle.load(data_pickle)

        self.M0 = tuple(self.data.tolist()[0])
        self.S = tuple(self.label.tolist()[0])

    def __get_closest_data_point(self, x):

        if len(self.data[0]) != len(x):
            raise(ValueError, "x must have the same dimension as the data source")

        deltas = self.data - x
        dist_2 = np.einsum('ij,ij->i', deltas, deltas)
        return np.argmin(dist_2)

    def actuate(self, x_req):

        x_in_idx = self.__get_closest_data_point(x_req)
        self.S = tuple(self.label.tolist()[x_in_idx])
        self.M0 = tuple(self.data.tolist()[x_in_idx])

    def get_possible_action(self, state=None, num_sample=1000, randomize=None):

        indices = np.random.choice(len(self.data), size=num_sample, replace=False)
        M_candidates = tuple(map(tuple, (self.data[indices, :].tolist())))
        return M_candidates


def generate_data(function, num_sample=1000, randomize=True):

    print("Generating Data Set")
    X = function.get_possible_action(num_sample=num_sample, randomize=randomize)
    Y = [None]*num_sample

    for n in range(num_sample):
        function.actuate(X[n])
        Y[n] = np.asarray(function.report())
    Y = np.asarray(Y)

    X = np.asarray(X)

    return X, Y



if __name__ == '__main__':

    func = SimpleFunction3(low_bound=(-80, -80 ), high_bound=(80, 80))
    data, label = (generate_data(func, num_sample=10000, randomize=True))

    with open('SimpleData.pkl', 'wb') as data_pickle:
        pickle.dump(data, data_pickle, pickle.HIGHEST_PROTOCOL)
        pickle.dump(label, data_pickle, pickle.HIGHEST_PROTOCOL)

    test = SimpleDataSource('SimpleData.pkl')
