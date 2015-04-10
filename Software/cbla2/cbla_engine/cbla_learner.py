__author__ = 'Matthew'

from .cbla_expert import Expert
from .cbla_robot import Robot
import random
import numpy as np
import warnings
from collections import defaultdict
from collections import OrderedDict

class Learner(object):

    def __init__(self, S0, M0, **config_kwargs):

        # default configurations
        self.config = dict()
        self._set_default_config()

        # custom configurations
        for param, value in config_kwargs.items():
            self.config[param] = value

        # sensorimotor variables
        self.S = S0
        self.M = M0
        self.S_predicted = self.S

        # expert
        self.expert = self.expert = Expert(**self.config)

        # learner information
        self.info = dict()

        # misc. variables
        self.exploring_rate = self.config['exploring_rate']


    def _set_default_config(self):
        self.config['exploring_rate'] = 0.5
        self.config['exploring_rate_range'] = (0.05, 0.8)
        self.config['exploring_reward_range'] = (-50.0, 10.0)
        self.config['adapt_exploring_rate'] = True

    def learn(self, S1, M):

        if M != self.M:
            warnings.warn("Robot did not do that action Learner selected.", RuntimeWarning)

        # add exemplar to expert
        selected_expert = self.expert.append(self.S + self.M, S1, self.S_predicted)

        # set current state to S1
        self.S = S1

        return selected_expert

    def select_action(self, robot: Robot):

        # from a set of possible action, select one
        M_candidates = robot.get_possible_action(num_sample=100)
        M1, M_best, val_best, is_exploring = self.action_selection(self.S, M_candidates)

        # if action-value is too low, enter idle mode
        is_doing_idle_action = False
        if robot.enter_idle_mode(reward=val_best):
            if robot.is_doing_idle_action():
                M1 = robot.get_idle_action()
                is_doing_idle_action = True

        self.M = M1

        # save to info
        self.info['best_action'] = (M_best, val_best)
        self.info['is_exploring'] = is_exploring
        self.info['is_doing_idle_action'] = is_doing_idle_action

        self.adapt_exploring_rate(action_value=val_best)

        return self.M

    def predict(self):

        self.S_predicted = self.expert.predict(self.S, self.M)

        return self.S_predicted

    def action_selection(self, S1, M_candidates, method='oudeyer'):

        # compute the M with the highest learning rate
        M_best = [0]
        val_best = -float("inf")
        for M_candidate in M_candidates:
            val = self.expert.evaluate_action(S1, M_candidate)
            if val > val_best:
                M_best = [M_candidate]
                val_best = val
            elif val == val_best:
                M_best.append(M_candidate)

        # select the M1 randomly from the list of best
        M_best = random.choice(M_best)

        is_exploring = (random.random() < self.exploring_rate)
        # select one randomly if it's exploring
        if is_exploring:
            M1 = random.choice(M_candidates)
        else:
            M1 = M_best

        return M1, M_best, val_best, is_exploring

    def adapt_exploring_rate(self, action_value):

        # update learning rate based on reward
        if self.config['adapt_exploring_rate']:  # if it was exploring, stick with the original learning rate
            exploring_rate_range = self.config['exploring_rate_range']
            reward_range = self.config['exploring_reward_range']
            if action_value < reward_range[0]:
                self.exploring_rate = exploring_rate_range[0]
            elif action_value > reward_range[1]:
                self.exploring_rate = exploring_rate_range[1]
            else:
                m = (exploring_rate_range[0] - exploring_rate_range[1]) / (reward_range[0] - reward_range[1])
                b = exploring_rate_range[0] - m * reward_range[0]
                self.exploring_rate = m * action_value + b

        return self.exploring_rate

    def get_expert_info(self) -> defaultdict:

        info = defaultdict(dict)

        self.expert.save_expert_info(info)

        return info


def weighted_choice_sub(weights, min_percent=0.05):
    min_weight = min(weights)
    weights = [x - min_weight for x in weights]
    adj_val = min_percent * max(weights)
    weights = [x + adj_val for x in weights]

    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i

    return random.randint(0, len(weights) - 1)
