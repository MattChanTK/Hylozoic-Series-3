__author__ = 'Matthew'

import threading
from queue import Queue
from collections import defaultdict
from copy import copy
from copy import deepcopy
import pickle
import os
import shutil
import datetime
import glob
from datetime import datetime, timedelta
from time import perf_counter, sleep, process_time
import shelve


class DataLogger(threading.Thread):

    def __init__(self, log_dir='log_data', log_header='generic_data',
                 log_timestamp=None, log_path=None,
                 **kwarg):

        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

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

        self.log_index_file[str(curr_session)] = 'session_%03d' % curr_session

        # create the session's directory
        session_dir_path = os.path.join(log_dir_path, self.log_index_file[str(curr_session)])
        os.mkdir(session_dir_path)

        # open the shelve for the session
        session_path = os.path.join(session_dir_path, self.log_index_file[str(curr_session)])
        self.session_shelf = shelve.open(session_path, protocol=3, writeback=False)
        self.session_shelf['session_id'] = curr_session

        # register the start time of the session
        self.clock0 = perf_counter()
        self.datetime0 = datetime.now()
        self.session_shelf['session_datetime0'] = self.datetime0
        self.session_shelf['session_clock0'] = self.clock0

        # queue for packet to come in
        self.__packet_queue = Queue()

        # data buffer in memory
        self.__data_buffer = defaultdict(list)

        # variables
        self.__program_terminating = False

        # parameters
        if 'sleep_time' in kwarg and isinstance(kwarg['sleep_time'], (float, int)):
            self.sleep_time = float(max(0.0, kwarg['sleep_time']))
        else:
            self.sleep_time = 0.0001

        if 'save_freq' in kwarg and isinstance(kwarg['save_freq'], (float, int)):
            self.save_freq = float(max(0.0, kwarg['save_freq']))
        else:
            self.save_freq = 2.0

        super(DataLogger, self).__init__(name='DataLogger', daemon=False)

    def run(self):

        last_saved_time = perf_counter()
        while not self.__program_terminating or not self.__packet_queue.empty():

            # saving run-time data to memory
            if not self.__packet_queue.empty():
                # get packet from queue
                node_name, packet_data = self.__packet_queue.get_nowait()

                # check if the packet has timestamp
                try:
                    packet_time = packet_data['packet_time']
                    if not isinstance(packet_time, float):
                        raise TypeError()
                except (KeyError, TypeError):
                    packet_time = perf_counter()
                    packet_data['packet_time'] = packet_time

                # check if the packet has type
                try:
                    packet_type = packet_data['type']
                    if not isinstance(packet_type, str):
                        raise TypeError()
                except (KeyError, TypeError):
                    packet_type = 'data'
                    packet_data['type'] = packet_type

                # save the packet data in the buffer
                self.__data_buffer[encode_struct(node_name, packet_type)].append(packet_data)

            # save data blocks to disk periodically
            if perf_counter() - last_saved_time > self.save_freq and not self.__program_terminating:
                self.__save_to_shelf()
                last_saved_time = perf_counter()

            # don't sleep if program is terminating
            if not self.__program_terminating:
                sleep(self.sleep_time)

        # save all remaining data in buffer to disk
        self.__save_to_shelf()
        print("Data Logger saved all data to disk.")

    def append_data_packet(self, node_name, data_packet):
        self.__packet_queue.put((node_name, copy(data_packet)))

    def end_data_collection(self):
        self.__program_terminating = True

    def __save_to_shelf(self):
        for data_block_key, data_block in self.__data_buffer.items():

            if data_block and len(data_block) > 0:
                # use the fist packet's time as timestamp for the block
                block_timestamp = data_block[0]['packet_time']
                # convert CPU time to datetime then to a string
                block_time_str = self.__clock2datetime(block_timestamp).strftime("%Y-%m-%d_%H-%M-%S-%f")
                # save to the shelf
                self.session_shelf[encode_struct(data_block_key, block_time_str)] = data_block

        # clear data_buffer
        self.__data_buffer = defaultdict(list)

    def __clock2datetime(self, clock_t: float):
        return self.datetime0 + timedelta(0, clock_t - self.clock0)

def encode_struct(*struct_labels, separator='//'):

    return separator.join(struct_labels)

def decode_struct(struct_str: str, separator='//'):

    if not isinstance(struct_str, str):
        raise ValueError("struct_str must be a str!")
    return struct_str.split(separator)


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

    data_logger = DataLogger(log_dir=log_dir_path, log_path=latest_log_dir)
    data_logger.start()

    pack_dict = dict()
    for i in range(10000):

        curr_time = perf_counter()
        pack_dict['type'] = i
        pack_dict['packet_time'] = curr_time

        # data_logger.append_data_packet('test_node', {'packet_time':curr_time})
        data_logger.append_data_packet('test_node', pack_dict)

