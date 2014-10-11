__author__ = 'Matthew'
import math

class SimpleFunction():

    def __init__(self):
        self.S = (100,)

    def actuate(self, M):
        if not isinstance(M, tuple):
            raise(TypeError, "M must be a tuple")
        if M[0] < -30:
            self.S = (100*math.sin(M[0]*0.005),)
        elif M[0] > 30:
            self.S = (100*math.sin(M[0]*0.5),)
        else:
            self.S = (100*math.sin(M[0]*0.05),)

    def report(self):
        return self.S
