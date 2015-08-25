__author__ = 'Matthew'

from datetime import datetime
import random

from abstract_node.node import *
from interactive_system import Messenger


class UserStudyPanel(Node):

    def __init__(self, messenger: Messenger, node_name="user_study_panel", **in_vars):

        super(UserStudyPanel, self).__init__(messenger, node_name=node_name)

        self.datetime_str_fmt_us = "%Y-%m-%d %H:%M:%S:%f" # "%Y-%m-%d_%H-%M-%S-%f"

        # output variables
        self.out_var['sample_number'] = Var(0)
        self.out_var['curr_time'] = Var(datetime.now().strftime(self.datetime_str_fmt_us))

        # input variables
        for in_var_name, in_var in in_vars.items():
            if isinstance(in_var, Var):
                self.in_var[in_var_name] = in_var

    def run(self):

        while self.alive:

            if random.randint(1, 100) == 5:
                self.out_var['sample_number'].val += 1

            self.out_var['curr_time'].val = datetime.now().strftime(self.datetime_str_fmt_us)

            sleep(self.messenger.estimated_msg_period*2)