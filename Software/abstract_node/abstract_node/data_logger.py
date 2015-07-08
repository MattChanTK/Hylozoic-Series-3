__author__ = 'Matthew'

import threading
from queue import Queue
from collections import defaultdict
from copy import copy
from copy import deepcopy
import pickle
import os
import shutil
import time
import glob
from datetime import datetime
from time import clock
from time import sleep
import shelve


class DataLogger(threading.Thread):

    def __init__(self, log_dir='log_data', log_header='generic_data'):

        log_dir_path = os.path.join(os.getcwd(), log_dir, log_header)
        # check if log directory even exist
        if not os.path.exists(log_dir_path):
            # create directory if does not exist
            os.makedirs(log_dir_path)

        # check if the log file exist
        log_path = os.path.join(log_dir_path, log_header)
        self.log_file = shelve.open(log_path, protocol=3, writeback=False)

        # if from previous session
        if 'file_num' in self.log_file:
            self.log_file['file_num'] += 1
            self.data_file['session_start_time'].append(datetime.now())

        # if having no data
        else:
            self.data_file = dict()
            self.data_file['data'] = defaultdict(list)

            now = time.strftime("%y-%m-%d_%H-%M-%S", time.localtime())
            self.data_file['file_name'] = '%s_%s' % (file_header, now)
            self.data_file['file_num'] = 1

            # put time stamp on the packet
            self.data_file['session_start_time'] = [datetime.now()]

        self.packet_queue = Queue()
        super(DataLogger, self).__init__(name='SimpleDataLogger', daemon=False)



# test script
if __name__ == '__main__':

    data_log_folder = 'data_log'
    data_logger = DataLogger(os.path.join(os.getcwd(), data_log_folder))

