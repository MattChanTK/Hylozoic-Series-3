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
                S1[i] += math.sin(m/10.0)*10.0

        self.S = tuple(S1)

    def report(self):
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


class SimpleDataSource(SimpleFunction):

    def __init__(self, filename=None):

        if not isinstance(filename, str):
            raise(TypeError, "filename must be a string")

        with open(filename, 'rb') as data_pickle:
            self.data = pickle.load(data_pickle)
            self.label = pickle.load(data_pickle)




def generate_data(function, num_sample=1000, randomize=True):

    X = function.get_possible_action(num_sample=num_sample, randomize=randomize)
    Y = [None]*num_sample

    for n in range(num_sample):
        function.actuate(X[n])
        Y[n] = np.asarray(function.report())
    Y = np.asmatrix(np.asarray(Y))

    X = np.asmatrix(np.asarray(X))

    return X, Y



if __name__ == '__main__':

    func = SimpleFunction(low_bound=(-80, -80), high_bound=(80, 80))
    data, label = (generate_data(func, num_sample=10, randomize=False))

    with open('SimpleData.pkl', 'wb') as data_pickle:
        pickle.dump(data, data_pickle, pickle.HIGHEST_PROTOCOL)
        pickle.dump(label, data_pickle, pickle.HIGHEST_PROTOCOL)

    test = SimpleDataSource('SimpleData.pkl')

    print(test.label)
    print(test.data)
