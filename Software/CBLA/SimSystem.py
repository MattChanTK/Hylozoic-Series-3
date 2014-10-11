__author__ = 'Matthew'
import math

class SimpleFunction():

    def __init__(self):
        self.S = (100,)

    def actuate(self, M):
        if not isinstance(M, tuple):
            raise(TypeError, "M must be a tuple")
        self.S = (100*math.cos(M[0]),)

    def report(self):
        return self.S
