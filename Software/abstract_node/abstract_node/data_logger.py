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

    def __init__(self, log_dir='log_data', log_header='generic_data', log_timestamp=None, log_path=None):

        now = time.strftime("%y-%m-%d_%H-%M-%S", time.localtime())

        # if a specific path is specified
        if isinstance(log_path, str) and os.path.isdir(log_path):
            log_dir_path = log_path
            log_name = os.path.split(log_dir_path)[-1]
        else:
            if log_timestamp == None:
                log_timestamp = now

            log_name =  '%s_%s' % (log_header, log_timestamp)
            log_dir_path = os.path.join(os.getcwd(), log_dir, log_name)

        # check if log directory even exist
        if not os.path.exists(log_dir_path):
            # create directory if does not exist
            os.makedirs(log_dir_path)

        # check if the log file exist
        log_path = os.path.join(log_dir_path, log_name)
        self.log_index_file = shelve.open(log_path, protocol=3, writeback=False)

        # if from previous session
        if self.log_index_file:

            try:
                self.log_index_file['num_session'] += 1
            except KeyError:
                raise KeyError('log file is corrupted!')

            curr_session = self.log_index_file['num_session']
        else:
            curr_session = 1
            self.log_index_file['time_created'] = now
            self.log_index_file['num_session'] = curr_session


        self.log_index_file[str(curr_session)] =  'session_%03d' % curr_session

        # create the session's directory
        session_dir_path = os.path.join(log_dir_path, self.log_index_file[str(curr_session)])
        os.mkdir(session_dir_path)

        # open the shelve for the session
        session_path = os.path.join(session_dir_path, self.log_index_file[str(curr_session)])
        self.session_shelf = shelve.open(session_path, protocol=3, writeback=False)
        self.session_shelf['time_created'] = now
        self.session_shelf['session_id'] = curr_session

        # queue for packet to come in
        self.__packet_queue = Queue()

        # variables
        self.__program_terminating = False

        # parameters
        self.sleep_time = 0.001


        super(DataLogger, self).__init__(name='DataLogger', daemon=False)

    def run(self):

        while not self.__program_terminating or not self.__packet_queue.empty():

            # saving run-time data to memory
            if not self.__packet_queue.empty():
                node_name, packet_data = self.__packet_queue.get_nowait()
                self.session_shelf[(node_name, 'data', time.localtime())] = packet_data

            if self.__program_terminating:
                self.sleep_time = 0.0

            sleep(self.sleep_time)

    def append_data_packet(self, node_name, data_packet):
        self.__packet_queue.put((node_name, copy(data_packet)))

    def end_data_collection(self):
        self.__program_terminating = True

# test script
if __name__ == '__main__':

    create_new_log = True
    log_dir_path = os.path.join(os.getcwd(), 'data_log')

    if create_new_log:
        latest_log_dir = None
    else:
        # use the latest data log
        all_log_dir = []
        for dir in os.listdir(log_dir_path):
            dir_path = os.path.join(log_dir_path, dir)
            if os.path.isdir(dir_path):
                all_log_dir.append(dir_path)
        latest_log_dir = max(all_log_dir, key=os.path.getmtime)

    data_logger = DataLogger(os.path.join(os.getcwd(), log_dir_path), log_path=latest_log_dir)
    data_logger.start()
    for i in range(1000):

        data_logger.append_data_packet('test_node', (i, i/2, i*2))

