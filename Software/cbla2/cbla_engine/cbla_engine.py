import random
from copy import copy
from copy import deepcopy
import os

from time import sleep
from time import clock
from datetime import datetime
import numpy as np
import warnings

from .cbla_robot import *
from .cbla_learner import *

class CBLA_Engine(object):

    def __init__(self, robot: Robot, learner: Learner, **config_kwargs):

        # instantiate the configuration parameters
        self.config = dict()
        # default configurations
        self.config['print_to_term'] = False

        # custom configurations
        for param, value in config_kwargs.items():
            self.config[param] = value

        # instantiate the robot
        self.robot = robot
        self.learner = learner

        # initialization
        self.M = self.learner.select_action(self.robot)

    def update(self, robot_wait=0.03):

        # act
        self.robot.act(self.M)

        # wait
        self.robot.wait(robot_wait)

        # read
        S2 = self.robot.read()

        # learn
        self.learner.learn(S2, self.M)

        # select action
        self.M = self.learner.select_action(self.robot)

        # predict
        self.learner.predict()



def copy_var_list(var_list: list) -> list:

    copied_list = []
    for var in var_list:
        if not isinstance(var, Var):
            raise TypeError("copy_var_list only handles Var type")
        copied_list.append(Var(copy(var.val)))

    return copied_list