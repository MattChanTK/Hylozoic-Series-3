import math
import random

import matplotlib.pyplot as plt
import pickle
import numpy as np
from copy import copy
import Visualization as Viz
import os
import threading
from time import sleep

from RegionsManager import Expert
# from SimSystem import DiagonalPlane as Robot
import InteractiveCmd
from InteractiveCmd import command_object


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

class CBLA_Behaviours(InteractiveCmd.InteractiveCmd):

    class Node():

        def __init__(self, interactive_cmd,  teensy_name, actuate_vars, report_vars, sync_barrier, name=""):


            self.interactive_cmd = interactive_cmd
            self.teensy_name = teensy_name
            self.sync_barrier = sync_barrier
            self.name = teensy_name + " " + str(name)

            # ToDo need a more encapsulated appraoch
            self.reply_types = self.interactive_cmd.teensy_manager.get_teensy_thread(self.teensy_name).param.reply_types
            self.request_types = self.interactive_cmd.teensy_manager.get_teensy_thread(self.teensy_name).param.request_types

            self.actuate_vars = actuate_vars
            self.M0 = tuple([0] * len(actuate_vars))

            self.report_vars = report_vars
            self.S = tuple([0]*len(report_vars))


        def actuate(self, M):

            if not isinstance(M, tuple):
                raise (TypeError, "M must be a tuple")
            if len(M) != len(self.actuate_vars):
                raise (ValueError, "M must have " + len(self.actuate_vars) +" elements!")

            # move tentacle 0 up
            for i in range(len(self.actuate_vars)):

                cmd_obj = command_object(self.teensy_name, self.__get_request_type(self.actuate_vars[i]))
                cmd_obj.add_param_change(self.actuate_vars[i], int(M[i]))

            self.M0 = M

            with self.interactive_cmd.lock:
                self.interactive_cmd.enter_command(cmd_obj)

            # wait for other thread in the same sync group to finish
            self.sync_barrier.write_barrier.wait()



        def report(self):

            # wait for other thread in the same sync group to finish
            self.sync_barrier.read_barrier.wait()

            # collect sample
            with self.sync_barrier.lock:
                sample = self.sync_barrier.sample[self.teensy_name]

            # if the first sample read was unsuccessful, just return the default value
            if sample is None:
                print("timed out")
                return self.S

            # if the data wasn't new, it means that it timed out
            if sample[1] == False:
                print("timed out")

            sample = sample[0]

            # construct the S vector for the node
            s = []
            for var in self.report_vars:
                s.append(sample[var])
            self.S = tuple(s)
            return self.S

        def get_possible_action(self, state=None, num_sample=1000):

            x_dim = 1

            X = np.zeros((num_sample, x_dim))

            for i in range(num_sample):
                X[i, x_dim-1] = max(min(self.M0[x_dim-1]-int(num_sample/2) + i, 255), 0)

            M_candidates = tuple(map(tuple, X))

            return M_candidates

        def __get_reply_type(self, var):
            for reply_type, vars in self.reply_types.items():
                if var in vars:
                    return reply_type

            raise (ValueError, "Variable not found!")

        def __get_request_type(self, var):
            for request_type, vars in self.request_types.items():
                if var in vars:
                    return request_type

            raise (ValueError, "Variable not found!")

    class Indicator_Node(Node):

        def get_possible_action(self, state=None, num_sample=2):

            return ((0,),(1,))

    class CBLA_Engine(threading.Thread):

        def __init__(self, robot, loop_delay=0, use_saved_expert=False, sim_duration=2000, exploring_rate=0.05):

            # ~~ configuration ~~
            self.is_using_saved_expert = use_saved_expert

            # number of time step
            self.sim_duration = sim_duration

            # use adaptive learning rate
            self.adapt_exploring_rate = False

            # exploring rate
            self.exploring_rate = exploring_rate



            # ~~ instantiation ~~

            self.robot = robot
            self.loop_delay = loop_delay


            # instantiate an Expert
            # TODO add teensy name to filename

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

                self.expert = Expert()
                self.action_history = []
                self.state_history = []
                self.mean_error_history = []


            # ~~ initiating threads ~~
            threading.Thread.__init__(self)
            self.daemon = False
            self.start()

        def run(self):

            # initial training action
            Mi = self.robot.get_possible_action(num_sample=10)

            # initial conditions
            t = 0
            S = (0,)
            M = Mi[0]
            L = float("-inf")


            while t < self.sim_duration:

                t += 1
                term_print_str = self.robot.name
                term_print_str += ''.join(map(str, ("\nTest case t = ", t, " -- ", S, M, '\n')))


                # have the expert make prediction
                S1_predicted = self.expert.predict(S, M)

                term_print_str += ''.join(map(str, ("Predicted S1: ", S1_predicted, '\n')))


                # do action
                self.action_history.append(M)
                self.state_history.append(S)

                self.robot.actuate(M)

                sleep(self.loop_delay)

                # read sensor
                S1 = self.robot.report()
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
                        exploring_rate = m*L + b

                # record the mean errors of each region
                mean_errors = []
                region_ids = []
                self.expert.save_mean_errors(mean_errors)
                self.mean_error_history.append(copy(mean_errors))

                # set to current state

                S = S1
                if t < len(Mi):
                    M = Mi[t]
                else:
                    M = M1

                # output to terminal
                print(term_print_str)

                # output to files
                if t % 1000 == 0 or t >= self.sim_duration:
                    with open(self.robot.name + '_expert_backup.pkl', 'wb') as output:
                        pickle.dump(self.expert, output, pickle.HIGHEST_PROTOCOL)

                    with open(self.robot.name + '_action_history_backup.pkl', 'wb') as output:
                        pickle.dump(self.action_history, output, pickle.HIGHEST_PROTOCOL)

                    with open(self.robot.name + '_state_history_backup.pkl', 'wb') as output:
                        pickle.dump(self.state_history, output, pickle.HIGHEST_PROTOCOL)

                    with open(self.robot.name + '_mean_error_history_backup.pkl', 'wb') as output:
                        pickle.dump(self.mean_error_history, output, pickle.HIGHEST_PROTOCOL)

            self.visualize()


        def visualize(self):

            self.expert.print()

            # find out what are the ids that existed
            region_ids = sorted(list(zip(*self.mean_error_history[-1]))[0])

            Viz.plot_expert_tree(self.expert, region_ids)
            Viz.plot_evolution(self.state_history, title='State vs Time', y_label='S(t)', fig_num=1, subplot_num=261)
            # Viz.plot_evolution(self.action_history, title='Action vs Time', y_label='M(t)[1]', y_dim=1, fig_num=1, subplot_num=261)
            Viz.plot_evolution(self.action_history, title='Action vs Time', y_label='M(t)[0]', y_dim=0, fig_num=1, subplot_num=262)
            Viz.plot_model(self.expert, region_ids, x_idx=1, y_idx=0, fig_num=1, subplot_num=263)
            Viz.plot_model(self.expert, region_ids, x_idx=0, y_idx=0, fig_num=1, subplot_num=269)
            Viz.plot_regional_mean_errors(self.mean_error_history, region_ids, fig_num=1, subplot_num=234)
            Viz.plot_model_3D(self.expert, region_ids, x_idx=(0, 1), y_idx=0, fig_num=1, subplot_num=122)
            # Viz.plot_model_3D(self.expert, region_ids, x_idx=(1, 2), y_idx=0, fig_num=1, subplot_num=122, data_only=False)


            plt.ioff()
            plt.show()

    class Sync_Barrier():

        def __init__(self, interactive_cmd, num_threads, barrier_timeout=1, read_timeout=1):

            self.interactive_cmd = interactive_cmd

            self.write_barrier = threading.Barrier(num_threads, action=self.write_barrier_action, timeout=barrier_timeout)
            self.read_barrier = threading.Barrier(num_threads, action=self.read_barrier_action, timeout=barrier_timeout)

            self.sample = None
            self.read_timeout = read_timeout
            self.lock = threading.Lock()

        def read_barrier_action(self):
            with self.interactive_cmd.lock:
                self.interactive_cmd.update_input_states(self.interactive_cmd.teensy_manager.get_teensy_name_list())

            with self.interactive_cmd.lock:
                with self.lock:
                    self.sample = self.interactive_cmd.get_input_states(self.interactive_cmd.teensy_manager.get_teensy_name_list(),
                                                                        ('all',), timeout=self.read_timeout)

        def write_barrier_action(self):
            with self.interactive_cmd.lock:
                self.interactive_cmd.send_commands()



    def run(self):


        teensy_names = self.teensy_manager.get_teensy_name_list()

        # initially update the Teensys with all the output parameters here
        self.update_output_params(teensy_names)

        # synchonization barrier for all LEDs
        self.sync_barrier_led = CBLA_Behaviours.Sync_Barrier(self, len(teensy_names)*1, barrier_timeout=0.5)
        # synchonization barrier for all SMAs
        self.sync_barrier_sma = CBLA_Behaviours.Sync_Barrier(self, len(teensy_names)*1, barrier_timeout=15)

        # semaphore for restricting only one thread to access this thread at any given time
        self.lock = threading.Lock()
        self.cbla_engine = dict()
        for teensy_name in teensy_names:

            # instantiate robots
            robot_led = CBLA_Behaviours.Node(self, teensy_name, ('protocell_0_led_level',), ('protocell_0_als_state',),  self.sync_barrier_led, name='(LED)')
            robot_sma = CBLA_Behaviours.Indicator_Node(self, teensy_name, ('indicator_led_on',), ('protocell_1_als_state',),  self.sync_barrier_sma, name='(SMA)')

            # instantiate CBLA Engines
            with self.lock:
                self.cbla_engine[teensy_name + '_led'] = CBLA_Behaviours.CBLA_Engine(robot_led, loop_delay=0.05)
                self.cbla_engine[teensy_name + '_sma'] = CBLA_Behaviours.CBLA_Engine(robot_sma, loop_delay=2)

