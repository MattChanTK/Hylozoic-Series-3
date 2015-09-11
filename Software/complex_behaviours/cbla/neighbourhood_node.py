__author__ = 'Matthew'

from abstract_node.node import *
from interactive_system import Messenger

class Cluster_Activity(Node):

    def __init__(self, messenger: Messenger, node_name='Local_Activity',
                 output: Var=Var(0), **config):

        super(Cluster_Activity, self).__init__(messenger, node_name='%s' % node_name)

        # default parameters
        self.config = dict()
        self.config['activity_expon'] = 3.0
        self.config['min_prob'] = 0.00
        self.config['max_prob'] = 0.8

        self.out_var['local_prob'] = output

        # custom parameters
        if isinstance(config, dict):
            for name, arg in config.items():
                self.config[name] = arg

    def add_in_var(self, var: Var, var_key: str):

        if not isinstance(var, Var):
            raise TypeError("in_var must be of type Var!")

        if not isinstance(var_key, str):
            raise TypeError("var_key must be of type str!")

        self.in_var[var_key] = var

    def run(self):

        activity_denom = len(self.in_var)
        while self.alive:

            # determine level of activity
            activity = 0
            for var in self.in_var.values():
                activity += (var.val > 0)
            activity = activity**self.config['activity_expon']
            activity = max(0, min(activity_denom**self.config['activity_expon'], activity))

            prob = activity/activity_denom**self.config['activity_expon']
            self.out_var['local_prob'].val = max(self.config['min_prob'], min(self.config['max_prob'], prob ))

            sleep(max(0, self.messenger.estimated_msg_period * 2))
           #print(self.out_var['output'].val)
