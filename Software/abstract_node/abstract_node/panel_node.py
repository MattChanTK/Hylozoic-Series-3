__author__ = 'Matthew'

from datetime import datetime
import random

from abstract_node.node import *
from interactive_system import Messenger
import csv
import os
import winsound

class UserStudyPanel(Node):

    log_folder_name = 'user_study_log'

    def __init__(self, messenger: Messenger, node_name="user_study_panel", log_file_name=None,
                 prescripted_active_var=Var(0), **in_vars):

        super(UserStudyPanel, self).__init__(messenger, node_name=node_name)

        self.datetime_str_fmt_us = "%Y-%m-%d %H:%M:%S:%f" # "%Y-%m-%d_%H-%M-%S-%f"

        # output variables
        self.out_var['sample_number'] = Var(0)
        self.out_var['curr_time'] = Var(datetime.now().strftime(self.datetime_str_fmt_us))
        if isinstance(prescripted_active_var, Var):
            self.out_var['prescripted_mode_active'] = prescripted_active_var
        else:
            self.out_var['prescripted_mode_active'] = Var(0)

        # input variables
        in_vars_list = []
        for in_var_name, in_var in in_vars.items():
            if isinstance(in_var, Var):
                in_vars_list.append([in_var_name, in_var])
        # sort them
        in_vars_list = sorted(in_vars_list, key=lambda x: x[0])
        for in_var_name, in_var in in_vars_list:
            self.in_var[in_var_name] = in_var

        # compose the log file path
        log_path = os.path.join(os.getcwd(), self.log_folder_name)
        if not isinstance(log_file_name, str):
            log_file_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        # instantiate the snapshot taker
        self.snapshot_taker = CSV_Snapshot(log_path, log_file_name, row_info=self.out_var, variables=self.in_var)

    def run(self):

        while self.alive:

            self.out_var['curr_time'].val = datetime.now().strftime(self.datetime_str_fmt_us)

            sleep(self.messenger.estimated_msg_period*10)


class CSV_Snapshot(object):

    def __init__(self, csv_folder_path, csv_filename, row_info: OrderedDict, variables: OrderedDict):

        self.folder = csv_folder_path
        self.filename = csv_filename
        if not isinstance(row_info, dict):
            self.row_info = OrderedDict()
        else:
            self.row_info = row_info
        self.var_list = OrderedDict()

        # make the list of variables to save
        for var_name, var in variables.items():
            if isinstance(var, Var):
                self.var_list[var_name] = var
            else:
                raise TypeError("Variables must be of Var type!")

        # making sure the folder exist
        if not os.path.isdir(self.folder):
            os.makedirs(self.folder)

        # input the header if new file
        file_path = os.path.join(self.folder, self.filename)
        if not os.path.exists(file_path):
            with open(file_path, 'a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=',')
                csv_writer.writerow(tuple(self.row_info.keys()) + tuple(self.var_list.keys()))

    def take_snapshot(self):

        file_path = os.path.join(self.folder, self.filename)
        try:
            with open(file_path, 'a', newline='') as csv_file:

                # make a beep sound
                freq = 1000 # Set Frequency To 1000 Hertz
                dur = 1000 # Set Duration To 1000 ms == 1 second
                winsound.Beep(freq,dur)

                self.row_info['sample_number'].val += 1

                fieldnames = list(self.row_info.keys()) + list(self.var_list.keys())
                csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=',')

                var_dict = OrderedDict()
                for info_name, info in self.row_info.items():
                    var_dict[info_name] = info.val
                for var_name, var in self.var_list.items():
                    var_dict[var_name] = var.val

                csv_writer.writerow(var_dict)

        except PermissionError:
            print("Failed to sample; the file is already opened.")









