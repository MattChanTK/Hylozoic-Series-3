import math
import random
import pickle
from copy import copy
import os
import threading
from time import sleep
from time import clock
import re
import queue

import numpy as np

from RegionsManager import Expert

# from SimSystem import DiagonalPlane as Robot
from interactive_system import InteractiveCmd
from interactive_system.InteractiveCmd import command_object


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

def toDigits(n, b):
    """Convert a positive number n to its digit representation in base b."""
    digits = []
    while n > 0:
        digits.insert(0, n % b)
        n  = n // b
    return digits

class CBLA_Behaviours(InteractiveCmd.InteractiveCmd):

    class Node():

        def __init__(self, actuate_vars, report_vars, sync_barrier, name="", msg_setting=0):

            self.sync_barrier = sync_barrier
            self.name = str(name)
            self.msg_setting = msg_setting

            self.actuate_vars = actuate_vars
            self.M0 = tuple([0] * len(actuate_vars))

            self.report_vars = report_vars
            self.S = tuple([0]*len(report_vars))

        def actuate(self, M):

            if not isinstance(M, tuple):
                raise (TypeError, "M must be a tuple")
            if len(M) != len(self.actuate_vars):
                raise (ValueError, "M must have " + str(len(self.actuate_vars)) +" elements!")

            for i in range(len(self.actuate_vars)):
                self.sync_barrier.action_q.put((self.actuate_vars[i][0], (self.actuate_vars[i][1], M[i])))

            self.M0 = M
            # wait for other thread in the same sync group to finish
            self.sync_barrier.write_barrier.wait()

        def report(self) -> tuple:

            #wait for all thread to start at the same time
            self.sync_barrier.start_to_read_barrier.wait()

            while not self.sync_barrier.sample_interval_finished:

                t_sample = clock()

                # wait for other thread in the same sync group to finish
                self.sync_barrier.read_barrier.wait()

                # collect sample
                sample = self.sync_barrier.sample

                # if the first sample read was unsuccessful, just return the default value
                if sample is None:
                    print("unsuccessful read")
                    return self.S

                # if any one of those data wasn't new, it means that it timed out
                for teensy_name, sample_teensy in sample.items():

                    if not sample_teensy[1]:
                        print(teensy_name + " has timed out")

                # construct the S vector for the node
                s = []
                for var in self.report_vars:
                    s.append(sample[var[0]][0][var[1]])
                self.S = tuple(s)

                sleep(max(0, self.sync_barrier.sample_period - (clock()-t_sample)))

                #print(self.name, 'sample period ',clock()-t_sample)
            return self.S

        def get_possible_action(self, state=None, num_sample=100) -> tuple:

            x_dim = 1

            X = np.zeros((num_sample, x_dim))

            for i in range(num_sample):
                X[i, x_dim-1] = max(min(self.M0[x_dim-1]-int(num_sample/2) + i, 255), 0)

            M_candidates = tuple(set((map(tuple, X))))

            return M_candidates

        @staticmethod
        def _return_derive_param(counter) -> dict:
            return None


    class Protocell_Node(Node):
        pass

    class Tentacle_Arm_Node(Node):

        def get_possible_action(self, state=None, num_sample=4) -> tuple:

            # constructing a list of all possible action
            x_dim = len(self.actuate_vars)
            X = list(range(0, 4 ** x_dim))
            for i in range(len(X)):
                X[i] = toDigits(X[i], 4)
                filling = [0]*(x_dim - len(X[i]))
                X[i] = filling + X[i]
                #X[i] = [3] * x_dim


            # check if tentacles are cycling

            for j in range(x_dim):
                cycling_id = self.report_vars.index((self.actuate_vars[j][0], re.sub('arm_motion_on', 'cycling', self.actuate_vars[j][1])))
                if state is not None and state[cycling_id] > 0:
                    for i in range(len(X)):
                        X[i][j] = self.M0[j]

            M_candidates = tuple(set(map(tuple, X)))
            return M_candidates

        @staticmethod
        def _return_derive_param(counter):

            derive_param = dict()
            derive_param['acc_mean_window'] = counter
            derive_param['acc_diff_window'] = counter
            derive_param['acc_diff_gap'] = 10

            return derive_param

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


    class Sync_Barrier():

        def __init__(self, behaviour_cmd, num_threads, node_type, sample_period=0.1, sample_interval=0.4):

            self.cmd = behaviour_cmd
            self.node_type = node_type

            # barrier which ensure all threads read and write at the same time
            self.write_barrier = threading.Barrier(num_threads, action=self.write_barrier_action)
            self.read_barrier = threading.Barrier(num_threads, action=self.read_barrier_action)
            self.start_to_read_barrier = threading.Barrier(num_threads, action=self.start_to_read_barrier_action)

            # queue that store action pending from all threads
            self.action_q = queue.Queue()

            self.sample_counter = 0

            self.sample = None
            self.sample_period = sample_period
            self.sample_interval = sample_interval
            self.t0 = clock()
            self.sample_interval_finished = False

        def start_to_read_barrier_action(self):

            self.t0 = clock()
            self.sample_interval_finished = False
            self.sample_counter = 0


        def read_barrier_action(self):

            self.sample_counter += 1

              # when sampling interval is reached
            if clock() - self.t0 >= self.sample_interval and not self.sample_interval_finished  \
               or self.sample_interval <= self.sample_period:

                derive_param = self.node_type._return_derive_param(self.sample_counter)
                self.sample_interval_finished = True
                #print(self.sample_counter)
            else:
                derive_param = None

            # during the sampling interval
            with self.cmd.lock:

                #t0 = clock()
                self.cmd.update_input_states(self.cmd.teensy_manager.get_teensy_name_list(), derive_param=derive_param)
                #print("read barrier 1 time: ", clock() - t0)

                #t0= clock()
                self.sample = self.cmd.get_input_states(self.cmd.teensy_manager.get_teensy_name_list(), ('all',),
                                                            timeout=max(0.1, self.sample_interval))
                #print("read barrier 2 time: ", clock() - t0)


        def write_barrier_action(self):

            # categorize action in action_q based on teensy_name
            change_requests = dict()
            while not self.action_q.empty():
                action = self.action_q.get()
                try:
                    change_requests[action[0]].append(action[1])
                except KeyError:
                    change_requests[action[0]] = [action[1]]


            for teensy_name, output_params in change_requests.items():

                cmd_obj = command_object(teensy_name, msg_setting=1)
                for param in output_params:
                    cmd_obj.add_param_change(param[0], param[1])

                with self.cmd.lock:
                    self.cmd.enter_command(cmd_obj)

            with self.cmd.lock:
                self.cmd.send_commands()


    def run(self):

        curr_dir = os.getcwd()
        os.chdir(os.path.join(curr_dir, "pickle_jar"))

        teensy_names = self.teensy_manager.get_teensy_name_list()

        # initially update the Teensys with all the output parameters here
        self.update_output_params(teensy_names)

        # synchonization barrier for all LEDs
        self.sync_barrier_led = CBLA_Behaviours.Sync_Barrier(self, len(teensy_names)*1, node_type=CBLA_Behaviours.Protocell_Node,
                                                             sample_interval=0, sample_period=0.05)
        # synchonization barrier for all SMAs
        self.sync_barrier_sma = CBLA_Behaviours.Sync_Barrier(self, len(teensy_names)*3, node_type=CBLA_Behaviours.Tentacle_Arm_Node,
                                                             sample_interval=5, sample_period=0.33)

        # semaphore for restricting only one thread to access this thread at any given time
        self.lock = threading.Lock()
        self.cbla_engine = dict()
        for teensy_name in teensy_names:

            # set mode
            cmd_obj = command_object(teensy_name, 'basic')
            cmd_obj.add_param_change('operation_mode', 3)
            self.enter_command(cmd_obj)

            # instantiate robots
            protocell_action = ((teensy_name, 'protocell_0_led_level'),)
            protocell_sensor =  ((teensy_name, 'protocell_0_als_state'),)
            robot_led = CBLA_Behaviours.Protocell_Node(protocell_action, protocell_sensor, self.sync_barrier_led, name=(teensy_name + '_LED'), msg_setting=2)

            # -- raw accelerometer reading with all 3 arms ---
            #sma_action = ('tentacle_0_arm_motion_on','tentacle_1_arm_motion_on','tentacle_2_arm_motion_on',)
            #sma_sensor = ('tentacle_0_acc_z_state', 'tentacle_1_acc_z_state', 'tentacle_2_acc_z_state', 'tentacle_0_cycling', 'tentacle_1_cycling', 'tentacle_2_cycling'	)

            # --- one tentacle arm; derived acc features ---
            robot_sma = []
            for j in range(3):
                device_header = 'tentacle_%d_' % j
                sma_action = ((teensy_name, device_header + "arm_motion_on"),)
                sma_sensor = ((teensy_name, device_header + 'wave_mean_x'),
                              (teensy_name, device_header + 'wave_mean_y'),
                              (teensy_name, device_header + 'wave_mean_z'),
                              (teensy_name, device_header + 'cycling'))
                #sma_sensor = (device_header + 'wave_diff_x', device_header + 'wave_diff_y', device_header + 'wave_diff_z', device_header + 'cycling' )

                robot_sma.append(CBLA_Behaviours.Tentacle_Arm_Node(sma_action, sma_sensor,  self.sync_barrier_sma, name=(teensy_name + '_SMA_%d' % j), msg_setting=1))

            # instantiate CBLA Engines
            with self.lock:
                self.cbla_engine[teensy_name + '_LED'] = CBLA_Behaviours.CBLA_Engine(robot_led, id=1, sim_duration=float('inf'), use_saved_expert=False, split_thres=400, mean_err_thres=30.0, kga_delta=5, kga_tau=2, saving_freq=10)

                self.cbla_engine[teensy_name + '_SMA_0'] = CBLA_Behaviours.CBLA_Engine(robot_sma[0], id=2, sim_duration=float('inf'), use_saved_expert=False, split_thres=10, mean_err_thres=2.0, kga_delta=1, kga_tau=1, saving_freq=1)
                self.cbla_engine[teensy_name + '_SMA_1'] = CBLA_Behaviours.CBLA_Engine(robot_sma[1], id=3, sim_duration=float('inf'), use_saved_expert=False, split_thres=10, mean_err_thres=2.0, kga_delta=1, kga_tau=1, saving_freq=1)
                self.cbla_engine[teensy_name + '_SMA_2'] = CBLA_Behaviours.CBLA_Engine(robot_sma[2], id=4, sim_duration=float('inf'), use_saved_expert=False, split_thres=10, mean_err_thres=2.0, kga_delta=1, kga_tau=1, saving_freq=1)


        # waiting for all CBLA engines to terminate to do visualization
        name_list = []
        for name, engine in self.cbla_engine.items():
            name_list.append(name)
            engine.join()



