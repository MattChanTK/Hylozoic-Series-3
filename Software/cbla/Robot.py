import threading
from time import sleep
from time import clock
import re
import queue
import numpy as np
import random

from interactive_system.InteractiveCmd import command_object

class Node():

    def __init__(self, actuate_vars, report_vars, sync_barrier, name="", msg_setting=0, hidden_vars=()):

        self.sync_barrier = sync_barrier
        self.name = str(name)
        self.msg_setting = msg_setting

        self.actuate_vars = actuate_vars
        self.M0 = tuple([0] * len(actuate_vars))

        self.report_vars = report_vars
        self.S = tuple([0]*len(report_vars))

        self.hidden_vars = hidden_vars
        self.hidden_state = tuple([0]*len(hidden_vars))

        self.idled = False
        self.idled_step = 0

        self.past_reward = 0

    @property
    def activation_reward(self):
        return 1.0

    @property
    def activation_reward_delta(self):
        return 5.0

    @property
    def idling_reward(self):
        return -1.0

    @property
    def idling_prob(self):
        return 0.8

    @property
    def min_steps_before_idling(self):
        return 200

    @property
    def idling_reward_window(self):
        return 10

    def actuate(self, M):

        if not isinstance(M, tuple):
            raise (TypeError, "M must be a tuple")
        if len(M) != len(self.actuate_vars):
            raise (ValueError, "M must have " + str(len(self.actuate_vars)) + " elements!")

        for i in range(len(self.actuate_vars)):
            self.sync_barrier.action_q.put((self.actuate_vars[i][0], (self.actuate_vars[i][1], M[i])))

        self.M0 = M
        # wait for other thread in the same sync group to finish
        self.sync_barrier.write_barrier.wait()

    def report(self, hidden_vars_only=False) -> tuple:

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

            # extract the hidden variables
            hidden = []
            for var in self.hidden_vars:
                hidden.append(sample[var[0]][0][var[1]])
            self.hidden_state = tuple(hidden)

            if hidden_vars_only:
                return self.hidden_state

            # construct the S vector for the node
            s = []
            for var in self.report_vars:
                s.append(sample[var[0]][0][var[1]])
            self.S = tuple(s)



            sleep(max(0, self.sync_barrier.sample_period - (clock()-t_sample)))

            #print(self.name, 'sample period ',clock()-t_sample)
        return self.S

    def get_possible_action(self, num_sample=100) -> tuple:

        x_dim = 1

        X = np.zeros((num_sample, x_dim))

        for i in range(num_sample):
            X[i, x_dim-1] = max(min(self.M0[x_dim-1]-int(num_sample/2) + i, 255), 0)

        M_candidates = tuple(set((map(tuple, X))))

        return M_candidates

    def is_idling(self, reward, step) -> bool:

        if self.idled and \
                (reward > self.activation_reward or abs(reward - self.past_reward) > self.activation_reward_delta):
                self.idled = False
        elif not self.idled and reward < self.idling_reward and step-self.idled_step > self.min_steps_before_idling:
                self.idled = True
                self.idled_step = step

        if self.idled and random.random() < self.idling_prob:
            return True
        else:
            return False

    def get_idle_action(self) -> tuple:
        return tuple([0] * len(self.actuate_vars))


    @staticmethod
    def _return_derive_param(counter) -> dict:
        return None


class Protocell_Node(Node):

    @Node.activation_reward.getter
    def activation_reward(self):
        return 35.0

    @Node.activation_reward_delta.getter
    def activation_reward_delta(self):
        return 100.0

    @Node.idling_reward.getter
    def idling_reward(self):
        return 5.0

    @Node.min_steps_before_idling.getter
    def min_steps_before_idling(self):
        return 300

    @Node.idling_prob.getter
    def idling_prob(self):
        return 0.95

    @Node.idling_reward_window.getter
    def idling_reward_window(self):
        return 20


    def get_possible_action(self, state=None, num_sample=100) -> tuple:
        x_dim = 1

        X = np.zeros((num_sample, x_dim))

        for i in range(num_sample):
            X[i, x_dim - 1] = max(min(self.M0[x_dim - 1] - int(num_sample / 2) + i, 100), 0)

        M_candidates = tuple(set((map(tuple, X))))

        return M_candidates

    def get_idle_action(self) -> tuple:
        action = [0] * len(self.actuate_vars)
        # for i in range(len(self.actuate_vars)):
        #     action[i] = random.randint(0, 4)
        return tuple(action)


class Tentacle_Arm_Node(Node):

    @Node.activation_reward.getter
    def activation_reward(self):
        return 35.0

    @Node.activation_reward_delta.getter
    def activation_reward_delta(self):
        return 100.0

    @Node.idling_reward.getter
    def idling_reward(self):
        return 1.0

    @Node.min_steps_before_idling.getter
    def min_steps_before_idling(self):
        return 10

    @Node.idling_prob.getter
    def idling_prob(self):
        return 0.95

    @Node.idling_reward_window.getter
    def idling_reward_window(self):
        return 1

    def get_possible_action(self, num_sample=4) -> tuple:

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
            cycling_id = self.hidden_vars.index((self.actuate_vars[j][0], re.sub('arm_motion_on', 'cycling', self.actuate_vars[j][1])))
            if self.hidden_state is not None and self.hidden_state[cycling_id] > 0:
                for i in range(len(X)):
                    X[i][j] = self.M0[j]

        M_candidates = tuple(set(map(tuple, X)))
        return M_candidates

    @staticmethod
    def _return_derive_param(counter):

        derive_param = dict()
        derive_param['acc_mean_window'] = max(1, int(counter))
        derive_param['acc_diff_window'] = counter
        derive_param['acc_diff_gap'] = 10
        derive_param['ir_mean_window'] = max(1, int(counter))


        return derive_param


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



def toDigits(n, b):
    """Convert a positive number n to its digit representation in base b."""
    digits = []
    while n > 0:
        digits.insert(0, n % b)
        n  = n // b
    return digits
