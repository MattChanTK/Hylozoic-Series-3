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
    def __init__(self, robot, data_collect: DataCollector=None, id: int=0, sim_duration=2000,
                 target_loop_period: float=0.1,
                 exploring_rate: float=0.15, learning_rate=0.25,
                 split_thres: int=1000, mean_err_thres: float=1.0, kga_delta: int=50, kga_tau:int=10,
                 snapshot_period: float=2):

        # ~~ configuration ~~
        self.data_collect = data_collect

        # number of time step
        self.sim_duration = sim_duration

        # target loop speed
        self.target_loop_period = target_loop_period

        # use adaptive learning rate
        self.adapt_exploring_rate = True

        # exploring rate
        self.exploring_rate = exploring_rate

        # ~~ instantiation ~~

        self.robot = copy(robot)
        self.engine_id = id
        self.snapshot_period = snapshot_period
        self.expert_ids = [0]

        # instantiate an Expert
        if self.data_collect is not None and isinstance(self.data_collect, DataCollector):

            try:
                self.expert = data_collect.get_assigned_element(self.robot.name, 'expert', 'val')
                self.t0 = data_collect.get_assigned_element(self.robot.name, 'expert', 'step')

            except KeyError:
                self.expert = Expert(split_thres=split_thres, mean_err_thres=mean_err_thres,
                                     learning_rate=learning_rate,
                                     kga_delta=kga_delta, kga_tau=kga_tau)

                self.t0 = 0
        else:
            self.data_collect = DataCollector()

        self.data_collect.data_collection.set_robot_actuator_labels(self.robot.name, self.robot.actuate_vars)
        self.data_collect.data_collection.set_robot_sensor_labels(self.robot.name, self.robot.report_vars)

        # ~~ initiating threads ~~
        self.killed = False
        threading.Thread.__init__(self)
        self.daemon = True
        # self.start()

    def run(self):

        # initial training action
        Mi = self.robot.get_possible_action()

        # initial conditions
        t = self.t0
        self.time_step = t

        last_expert_save_time = 0
        S = self.robot.S
        M = Mi[random.randint(0, len(Mi)) - 1]
        val_best = float("-inf")


        # t0= clock()
        is_exploring_count = 0

        while t < self.sim_duration and self.killed == False:


            real_time_0 = clock()
            curr_datetime = datetime.now()

            t += 1

            # save the current time step
            self.data_collect.enqueue_assign(self.robot.name, 'time_step', t, time=curr_datetime, step=t)

            term_print_str = self.robot.name
            term_print_str += ''.join(map(str, ("\nTest case t = ", t, " -- ", S, M, '\n')))


            # have the expert make prediction
            S1_predicted = self.expert.predict(S, M)

            term_print_str += ''.join(map(str, ("Predicted S1: ", S1_predicted, '\n')))

            self.data_collect.enqueue(self.robot.name, 'action', M, time=curr_datetime, step=t)
            self.data_collect.enqueue(self.robot.name, 'prediction', S1_predicted, time=curr_datetime, step=t)

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

            curr_datetime = datetime.now()
            self.data_collect.enqueue(self.robot.name, 'state', S1, time=curr_datetime, step=t)

            term_print_str += ''.join(map(str, ("Actual S1: ", S1, '\n')))

            # add exemplar to expert
            selected_expert = self.expert.append(S + M, S1, S1_predicted)
            self.data_collect.enqueue(self.robot.name, 'selected expert', selected_expert, time=curr_datetime, step=t)

            try:
                self.data_collect.enqueue(self.robot.name, 'reward', self.expert.rewards_history[-1], time=curr_datetime, step=t)
            except TypeError:
                self.data_collect.enqueue(self.robot.name, 'reward', -float('inf'), time=curr_datetime, step=t)

            # generate a list of possible action given the state
            M_candidates = self.robot.get_possible_action(state=S1, num_sample=255)
            term_print_str += ''.join(map(str, ("Possible M's: ", M_candidates, '\n')))


            # Oudeyer's way of action selection
            M1, M_best, val_best, is_exploring = self.action_selection_oudeyer(S1, M_candidates)

            self.data_collect.enqueue(self.robot.name, 'best action', M_best, time=curr_datetime, step=t)

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
            self.data_collect.enqueue(self.robot.name, 'mean error', val=mean_errors, time=curr_datetime, step=t)

            # record the values of each region
            action_values = []
            self.expert.save_action_values(action_values)
            self.data_collect.enqueue(self.robot.name, 'action value', val=action_values, time=curr_datetime, step=t)

            # record the action count of each region
            action_count = []
            self.expert.save_action_count(action_count)
            self.data_collect.enqueue(self.robot.name, 'action count', val=action_count, time=curr_datetime, step=t)


            # store the expert
            self.data_collect.enqueue_assign(self.robot.name, 'expert', val=self.expert, time=curr_datetime, step=t)

            # record expert_history periodcally
            if real_time_0 - last_expert_save_time > self.snapshot_period:
                # update expert ids
                expert_ids = []
                self.expert.save_expert_ids(expert_ids)
                self.data_collect.enqueue(self.robot.name, 'region ids history', val=expert_ids, time=curr_datetime, step=t)

                # deepcoying experts
                self.data_collect.enqueue(self.robot.name, 'expert history', val=deepcopy(self.expert), time=curr_datetime, step=t)
                last_expert_save_time = real_time_0

                # make snapshot_period slight longer over time
                self.snapshot_period = min(900, self.snapshot_period*1.2)

            # set to current state
            S = S1
            M = M1

            # wait until loop time reaches target loop period
            sleep(max(0, self.target_loop_period - (clock() - real_time_0)))

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
