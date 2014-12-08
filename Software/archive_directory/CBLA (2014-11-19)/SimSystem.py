__author__ = 'Matthew'
import math
import random
import numpy as np
import copy

class SimpleFunction():

    def __init__(self):
        self.S = (100,)
        self.M0 = (0,)

    def actuate(self, M):
        if not isinstance(M, tuple):
            raise(TypeError, "M must be a tuple")
        if len(M) != len(self.M0):
            raise(ValueError, "M must be %d dimension" % len(self.M0))

        S1 = list(copy.copy(self.S))

        for i in range(len(self.S)):
            S1[i] = M[0]*0.5

            if 55 > M[0] > 10:
                continue
                S1[i] += random.uniform(-M[0]*0.5, M[0]*0.5)
            elif -10 > M[0] > -55:
                continue
                S1[i] += random.uniform(-10, 10)
            elif -10 <= M[0] <= 10:
                S1[i] += math.sin(self.S[0]/10)*50
            # elif M[0] >= 55:
            #     S1[i] += (math.sin(self.S[0]/5)*25 + random.uniform(-20, 20))
            else:
                #S1[i] += math.sin(self.S[0]/5)*25
                #S1[i] += random.uniform(-M[0], M[0])
                S1[i] += random.uniform(-80, 80)


        self.S = tuple(S1)

    def report(self):
        return self.S

    def get_possible_action(self, state=None, num_sample=10):

        if state is None:
            state = self.S

        M_candidates = []
        for sample in range(num_sample):
            m = []
            for i in range(len(self.M0)):
                m.append(random.uniform(-70, 70))
            M_candidates.append(tuple(m))

        return M_candidates
