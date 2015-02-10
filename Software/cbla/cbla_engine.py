import random
import pickle
from copy import copy
import os
import threading
from time import sleep
from time import clock

from RegionsManager import Expert


class CBLA_Engine(threading.Thread):

    def __init__(self, robot, id=0, use_saved_expert=False, sim_duration=2000, exploring_rate=0.05,
                 split_thres=1000, mean_err_thres=1.0, kga_delta=50, kga_tau=10,
                 saving_freq=250):

        # ~~ configuration ~~
        self.is_using_saved_expert = use_saved_expert

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

        if self.is_using_saved_expert:

            with open(self.robot.name + '_expert_backup.pkl', 'rb') as input:
                self.expert = pickle.load(input)
            with open(self.robot.name + '_action_history_backup.pkl', 'rb') as input:
                self.action_history = pickle.load(input)
            with open(self.robot.name + '_state_history_backup.pkl', 'rb') as input:
                self.state_history = pickle.load(input)
            with open(self.robot.name + '_mean_error_history_backup.pkl', 'rb') as input:
                self.mean_error_history = pickle.load(input)

        else:

            self.expert = Expert(split_thres=split_thres, mean_err_thres=mean_err_thres, kga_delta=kga_delta, kga_tau=kga_tau)
            self.action_history = []
            self.state_history = []
            self.mean_error_history = []


        # ~~ initiating threads ~~
        threading.Thread.__init__(self)
        self.daemon = False
        self.start()

    def run(self):

        # initial training action
        Mi = self.robot.get_possible_action()

        # initial conditions
        t = 0
        S = self.robot.S
        M = Mi[random.randint(0, len(Mi))-1]
        L = float("-inf")

        #t0= clock()
        while t < self.sim_duration:


            real_time_0 = clock()

            t += 1

            term_print_str = self.robot.name
            term_print_str += ''.join(map(str, ("\nTest case t = ", t, " -- ", S, M, '\n')))


            # have the expert make prediction
            S1_predicted = self.expert.predict(S, M)

            term_print_str += ''.join(map(str, ("Predicted S1: ", S1_predicted, '\n')))



            self.action_history.append(M)
            self.state_history.append(S)
            #print(self.robot.name, "CBLA Time", clock()-t0)

            # do action
            #t0 = clock()
            self.robot.actuate(M)
            #print(self.robot.name, "Write Time", clock() - t0)

            # read sensor
            #t0 = clock()
            S1 = self.robot.report()
            #print(self.robot.name, "Read Time", clock() - t0)

            #t0 = clock()
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
            term_print_str += ''.join(map(str, ("Possible M's: ", M_candidates , '\n')))


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
                    m = (exploring_rate_range[0] - exploring_rate_range[1])/(reward_range[0] - reward_range[1])
                    b = exploring_rate_range[0] - m*reward_range[0]
                    self.exploring_rate = m*L + b

            # record the mean errors of each region
            mean_errors = []
            region_ids = []
            self.expert.save_mean_errors(mean_errors)
            self.mean_error_history.append(copy(mean_errors))

            # set to current state

            S = S1
            M = M1



            # output to files
            if t % self.saving_freq == 0 or t >= self.sim_duration:

                with open(self.robot.name + '_expert_backup.pkl', 'wb') as output:
                    pickle.dump(self.expert, output, pickle.HIGHEST_PROTOCOL)

                with open(self.robot.name + '_action_history_backup.pkl', 'wb') as output:
                    pickle.dump(self.action_history, output, pickle.HIGHEST_PROTOCOL)

                with open(self.robot.name + '_state_history_backup.pkl', 'wb') as output:
                    pickle.dump(self.state_history, output, pickle.HIGHEST_PROTOCOL)

                with open(self.robot.name + '_mean_error_history_backup.pkl', 'wb') as output:
                    pickle.dump(self.mean_error_history, output, pickle.HIGHEST_PROTOCOL)


            real_time = clock()
            term_print_str += ("Time Step = %fs" % (real_time - real_time_0))  # output to terminal

            print(term_print_str, end='\n\n')


def weighted_choice_sub(weights, min_percent=0.05):
    min_weight = min(weights)
    weights = [x-min_weight for x in weights]
    adj_val = min_percent*max(weights)
    weights = [x+adj_val for x in weights]

    rnd = random.random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i

    return random.randint(0, len(weights)-1)