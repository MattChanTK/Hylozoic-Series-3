import random
from copy import copy
from copy import deepcopy
import os
import threading
from time import sleep
from time import clock
from datetime import datetime


from RegionsManager import Expert
from DataCollector import DataCollector


class CBLA_Engine(threading.Thread):
    def __init__(self, robot, data_collect: DataCollector=None, id: int=0, sim_duration=2000, exploring_rate: float=0.15,
                 split_thres: int=1000, mean_err_thres: float=1.0, kga_delta: int=50, kga_tau:int=10, learning_rate=0.25,
                 saving_freq: int=250):

        # ~~ configuration ~~
        self.data_collect = data_collect

        # number of time step
        self.sim_duration = sim_duration

        # use adaptive learning rate
        self.adapt_exploring_rate = True

        # exploring rate
        self.exploring_rate = exploring_rate

        # ~~ instantiation ~~

        self.robot = copy(robot)
        self.engine_id = id
        self.saving_freq = saving_freq

        # instantiate an Expert
        if self.data_collect is not None and isinstance(self.data_collect, DataCollector):

            try:
                self.expert = data_collect.get_element_val(self.robot.name, 'expert')

            except KeyError:
                self.expert = Expert(split_thres=split_thres, mean_err_thres=mean_err_thres,
                                     learning_rate=learning_rate,
                                     kga_delta=kga_delta, kga_tau=kga_tau)
        else:
            self.data_collect = DataCollector

        self.data_collect.data_collection.set_robot_actuator_labels(self.robot.name, self.robot.actuate_vars)
        self.data_collect.data_collection.set_robot_sensor_labels(self.robot.name, self.robot.report_vars)

        # ~~ initiating threads ~~
        self.killed = False
        threading.Thread.__init__(self)
        self.daemon = True
        #self.start()

    def run(self):

        # initial training action
        Mi = self.robot.get_possible_action()

        # initial conditions
        t = 0
        S = self.robot.S
        M = Mi[random.randint(0, len(Mi)) - 1]
        val_best = float("-inf")


        # t0= clock()
        is_exploring_count = 0

        while t < self.sim_duration and self.killed == False:


            real_time_0 = clock()

            t += 1

            term_print_str = self.robot.name
            term_print_str += ''.join(map(str, ("\nTest case t = ", t, " -- ", S, M, '\n')))


            # have the expert make prediction
            S1_predicted = self.expert.predict(S, M)

            term_print_str += ''.join(map(str, ("Predicted S1: ", S1_predicted, '\n')))

            self.data_collect.enqueue(self.robot.name, 'action', copy(M), time=datetime.now())
            self.data_collect.enqueue(self.robot.name, 'prediction', copy(S1_predicted), time=datetime.now())

            # do action
            self.robot.actuate(M)

            # read sensor
            S1 = self.robot.report()

            # artificially inject noise
            # noise = 0
            # if M[0] < 50:
            #     noise = 1000
            # elif M[0] < 100:
            #     noise = 500
            # S1 = list(S1)
            # S1[0] += random.gauss(0, noise)
            # S1 = tuple(S1)


            self.data_collect.enqueue(self.robot.name, 'state', copy(S1), time=datetime.now())

            term_print_str += ''.join(map(str, ("Actual S1: ", S1, '\n')))

            # add exemplar to expert
            selected_expert = self.expert.append(S + M, S1, S1_predicted)
            self.data_collect.enqueue(self.robot.name, 'selected expert', copy(selected_expert), time=datetime.now())

            try:
                self.data_collect.enqueue(self.robot.name, 'reward', copy(self.expert.rewards_history[-1]), time=datetime.now())
            except TypeError:
                self.data_collect.enqueue(self.robot.name, 'reward', -float('inf'), time=datetime.now())

            # generate a list of possible action given the state
            M_candidates = self.robot.get_possible_action(state=S1, num_sample=255)
            term_print_str += ''.join(map(str, ("Possible M's: ", M_candidates, '\n')))


            # Oudeyer's way of action selection
            M1, M_best, val_best, is_exploring = self.action_selection_oudeyer(S1, M_candidates)

            self.data_collect.enqueue(self.robot.name, 'best action', copy(M_best), time=datetime.now())

            term_print_str += ''.join(map(str, ("Best Action: ", M_best, '\n')))
            term_print_str += ''.join(map(str, ("Highest Value: ", val_best, '\n')))

            # random action or the best action
            term_print_str += ''.join(map(str, ("Expected exploring Rate: ", self.exploring_rate, '\n')))
            is_exploring_count += is_exploring
            term_print_str += ''.join(map(str, ("Overall exploring Rate: ", is_exploring_count / t, '\n')))

            if is_exploring:
                exploring_flag = '*'
            else:
                exploring_flag = ''
            term_print_str += ''.join(map(str, ("Next Action: ", M1, exploring_flag, '\n')))


            # update learning rate based on reward
            if self.adapt_exploring_rate:  # if it was exploring, stick with the original learning rate
                exploring_rate_range = [0.8, 0.05]
                reward_range = [-50.0, 10.0]
                if val_best < reward_range[0]:
                    self.exploring_rate = exploring_rate_range[0]
                elif val_best > reward_range[1]:
                    self.exploring_rate = exploring_rate_range[1]
                else:
                    m = (exploring_rate_range[0] - exploring_rate_range[1]) / (reward_range[0] - reward_range[1])
                    b = exploring_rate_range[0] - m * reward_range[0]
                    self.exploring_rate = m * val_best + b

            # record the mean errors of each region
            mean_errors = []
            self.expert.save_mean_errors(mean_errors)
            self.data_collect.enqueue(self.robot.name, 'mean error', copy(mean_errors), time=datetime.now())

            # record the values of each region
            action_values = []
            self.expert.save_action_values(action_values)
            self.data_collect.enqueue(self.robot.name, 'action value', copy(action_values), time=datetime.now())

            # record the action count of each region
            action_count = []
            self.expert.save_action_count(action_count)
            self.data_collect.enqueue(self.robot.name, 'action count', copy(action_count), time=datetime.now())

            self.data_collect.enqueue(self.robot.name, 'expert', deepcopy(self.expert), time=datetime.now())


            # set to current state
            S = S1
            M = M1

            real_time = clock()
            term_print_str += ("Time Step = %fs" % (real_time - real_time_0))  # output to terminal

            print(term_print_str, end='\n\n')

    # ==== action section methods====
    def action_selection_oudeyer(self, S1, M_candidates):

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

    def action_selection_probabilistic(self, S1, M_candidates):

        L_list = []
        for M_candidate in M_candidates:
            L_list.append(self.expert.evaluate_action(S1, M_candidate))

        L_best = max(L_list)
        M_best = M_candidates[L_list.index(L_best)]

        M_idx = weighted_choice_sub(L_list, min_percent=self.exploring_rate)


        M1 = M_candidates[M_idx]

        return M1, M_best, L_best

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
