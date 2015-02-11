import random
from copy import copy
import os
import threading
from time import sleep
from time import clock
from datetime import datetime


from RegionsManager import Expert
from DataCollector import DataCollector


class CBLA_Engine(threading.Thread):
    def __init__(self, robot, data_collect: DataCollector=None, id: int=0, sim_duration: int=2000, exploring_rate: float=0.05,
                 split_thres: int=1000, mean_err_thres: float=1.0, kga_delta: int=50, kga_tau:int=10,
                 saving_freq: int=250):

        # ~~ configuration ~~
        self.data_collect = data_collect

        # number of time step
        self.sim_duration = sim_duration

        # use adaptive learning rate
        self.adapt_exploring_rate = False

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
                self.expert = Expert(split_thres=split_thres, mean_err_thres=mean_err_thres, kga_delta=kga_delta,
                                     kga_tau=kga_tau)
        else:
            self.data_collect = DataCollector

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
        L = float("-inf")

        # t0= clock()
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
            self.data_collect.enqueue(self.robot.name, 'state', copy(S1), time=datetime.now())

            term_print_str += ''.join(map(str, ("Actual S1: ", S1, '\n')))

            # add exemplar to expert
            self.expert.append(S + M, S1, S1_predicted)

            # split is being done within append
            # expert.split()  # won't actually split if the condition is not met

            # random action or the best action
            term_print_str += ''.join(map(str, ("Exploring Rate: ", self.exploring_rate, '\n')))
            #print("Exploring Rate: ", self.exploring_rate)
            is_exploring = (random.random() < self.exploring_rate)

            #START ---- the Oudeyer way ----- START

            # # generate a list of possible action given the state
            # M_candidates = self.robot.get_possible_action(state=S1, num_sample=5)
            #
            # if is_exploring:
            #     M1 = random.choice(M_candidates)
            #
            # else:
            #     M1 = 0
            #     highest_L = float("-inf")
            #     for M_candidate in M_candidates:
            #         L = self.expert.evaluate_action(S1, M_candidate)
            #         if L > highest_L:
            #             M1 = M_candidate
            #             highest_L = L
            #     term_print_str += ''.join(map(str, ("Expected Reward: ", highest_L, '\n')))
            #     #print("Expected Reward", highest_L)
            #     L = highest_L
            # term_print_str += ''.join(map(str, ("Next Action: ", M1, '\n')))
            # #print("Next Action", M1)

            #END ---- the Oudeyer way ----- END

            #START ---- the Probabilistic way ----- START

            # generate a list of possible action given the state
            M_candidates = self.robot.get_possible_action(state=S1, num_sample=150)
            term_print_str += ''.join(map(str, ("Possible M's: ", M_candidates, '\n')))

            L_list = []
            for M_candidate in M_candidates:
                L_list.append(self.expert.evaluate_action(S1, M_candidate))

            M_idx = weighted_choice_sub(L_list, min_percent=self.exploring_rate)
            L = max(L_list)
            term_print_str += ''.join(map(str, ("Highest Expected Reward: ", L, '\n')))
            #print("Highest Expected Reward", L)
            M1 = M_candidates[M_idx]
            term_print_str += ''.join(map(str, ("Next Action: ", M1, '\n')))
            #print("Next Action", M1)

            #END ---- the Probabilistic way ----- END



            # update learning rate based on reward
            if is_exploring and self.adapt_exploring_rate:  # if it was exploring, stick with the original learning rate
                exploring_rate_range = [0.5, 0.01]
                reward_range = [0.01, 100.0]
                if L < reward_range[0]:
                    self.exploring_rate = exploring_rate_range[0]
                elif L > reward_range[1]:
                    self.exploring_rate = exploring_rate_range[1]
                else:
                    m = (exploring_rate_range[0] - exploring_rate_range[1]) / (reward_range[0] - reward_range[1])
                    b = exploring_rate_range[0] - m * reward_range[0]
                    self.exploring_rate = m * L + b

            # record the mean errors of each region
            mean_errors = []
            region_ids = []
            self.expert.save_mean_errors(mean_errors)
            self.data_collect.enqueue(self.robot.name, 'expert', copy(self.expert), time=datetime.now())
            self.data_collect.enqueue(self.robot.name, 'mean_error', copy(mean_errors), time=datetime.now())

            # set to current state

            S = S1
            M = M1

            real_time = clock()
            term_print_str += ("Time Step = %fs" % (real_time - real_time_0))  # output to terminal

            print(term_print_str, end='\n\n')

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

