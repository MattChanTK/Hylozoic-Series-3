__author__ = 'Matthew'
from time import perf_counter
from math import exp

from abstract_node.node import *
from interactive_system import Messenger

class Cluster_Activity(Node):

    def __init__(self, messenger: Messenger, node_name='Local_Activity',
                 output: Var=Var(0), **config):

        super(Cluster_Activity, self).__init__(messenger, node_name='%s' % node_name)

        # default parameters
        self.config = dict()
        self.config['min_prob'] = 0.00
        self.config['max_prob'] = 0.5

        self.out_var['local_prob'] = output

        # custom parameters
        if isinstance(config, dict):
            for name, arg in config.items():
                self.config[name] = arg

    def run(self):

        activity_denom = float(len(self.in_var))
        while self.alive:

            # determine level of activity
            activity = 0
            for var in self.in_var.values():
                activity += (var.val > 0.5)
            activity = max(0, min(activity_denom, activity))

            prob = self.gaussian_function(activity, a=self.config['max_prob'], b=activity_denom/2, c=activity_denom/10)

            self.out_var['local_prob'].val = max(self.config['min_prob'], min(self.config['max_prob'], prob ))
            # print('activity', activity, '  denom', activity_denom, '  prob', prob)

            sleep(max(0, self.messenger.estimated_msg_period * 2))

    @staticmethod
    def gaussian_function(x, a, b, c):
        return a*exp(-((x-b)**2)/(2*(c**2)))


class Neighbourhood_Manager(Node):

     def __init__(self, messenger: Messenger, node_name='neighbourhood_manager',
                 output: Var=Var(False), **config):

        super(Neighbourhood_Manager, self).__init__(messenger, node_name='%s' % node_name)

        # default parameters
        self.config = dict()
        self.config['active_thres'] = 0.5
        self.config['deactive_thres'] = 0.3
        self.config['active_period'] = 5.0
        self.config['activation_lock_period'] = 5.0

        self.out_var['neighbour_active'] = output

        # custom parameters
        if isinstance(config, dict):
            for name, arg in config.items():
                self.config[name] = arg

     def run(self):

         activation_time = perf_counter()
         activation_locked = False

         while self.alive:

            # determine if any of the neighbours are active
            activity_level = 0
            num_active = 0

            for var in self.in_var.values():
                if var.val > activity_level:
                    activity_level = var.val
                if var.val > self.config['active_thres']:
                    num_active += 1

            if self.out_var['neighbour_active'].val:
                if perf_counter() - activation_time > self.config['active_period'] or\
                   activity_level < self.config['deactive_thres']:
                    self.out_var['neighbour_active'].val = False
                    activation_locked = True

            elif not activation_locked and activity_level >= self.config['active_thres']:
                sleep(2.0)
                self.out_var['neighbour_active'].val = True
                activation_time = perf_counter()

            if activation_locked:
                if activity_level < self.config['deactive_thres']:
                    activation_locked = False

            sleep(max(0, self.messenger.estimated_msg_period * 10))