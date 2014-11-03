__author__ = 'Matthew'
import math
import random

class SimpleFunction():

    def __init__(self):
        self.S = (100,)

    def actuate(self, M):
        if not isinstance(M, tuple):
            raise(TypeError, "M must be a tuple")

        S1 = M[0]*0.5

        if 25 > M[0] > 10:
            S1 += random.uniform(-0.1, 0.1)
        elif -10 > M[0] > -25:
            S1 += random.uniform(-0.1, 0.1)
        elif -10 <= M[0] <= 10:
            S1 += math.sin(M[0])*10
        else:
            S1 += random.uniform(-M[0], M[0])

        self.S = (S1,)

    def report(self):
        return self.S
