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

folder_name = "session_data"


class SimpleDataCollector(threading.Thread):

    def __init__(self, data_file=None, file_save_freq=50, file_header='generic_data'):

        super(SimpleDataCollector, self).__init__(name='SimpleDataCollect', daemon=False)

        self.packet_queue = Queue()

        # if using saved data
        if isinstance(data_file, (dict, defaultdict)):
            self.data_file = data_file
            self.data_file['file_num'] += 1
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

        self.filetype = ".pkl"

        self.__save_to_file()

        self.program_terminating = False

        self.file_save_freq = file_save_freq

        self.data_file_lock = threading.Lock()

    def run(self):

        packet_count = 0
        sleep_time = 0.001

        while not self.program_terminating or not self.packet_queue.empty():

            with self.data_file_lock:

                # saving run-time data to memory
                if not self.packet_queue.empty():

                    node_name, packet_data = self.packet_queue.get_nowait()
                    self.data_file['data'][node_name].append(packet_data)
                    packet_count += 1

                # saving to file
                if packet_count >= self.file_save_freq and not self.program_terminating:
                    self.__save_to_file()
                    packet_count = 0

                # don't sleep if program is terminating
                if self.program_terminating:
                    sleep_time = 0

            sleep(sleep_time)

        self.__save_to_file()
        print("Data Collector saved all data to disk.")

        # remove tmp files
        curr_dir = os.getcwd()
        os.chdir(os.path.join(curr_dir, folder_name))
        temp_files = glob.glob("*%s*.tmp" % self.data_file['file_name'])
        for temp_file in temp_files:
            os.remove(temp_file)

    def append_data_packet(self, node_name, data_packet):

        self.packet_queue.put((node_name, copy(data_packet)))

    def end_data_collection(self):

        self.program_terminating = True

    def __save_to_file(self):

        # put saved timestamp to file
        try:
            self.data_file['session_end_time'][self.data_file['file_num'] - 1] = datetime.now()
        except KeyError:  # first session
            self.data_file['session_end_time'] = [datetime.now()]
        except IndexError:  # first save of the session
            self.data_file['session_end_time'].append(datetime.now())

        save_to_file('%s (%d)%s' % (self.data_file['file_name'], self.data_file['file_num'], self.filetype),
                     self.data_file)

    def deepcopy_data_file(self):
        with self.data_file_lock:
            return deepcopy(self.data_file)


def retrieve_data(file_name=None, file_header='generic_data'):

    # ====== retrieving data ======
    curr_dir = os.getcwd()
    target_dir = os.path.join(curr_dir, folder_name)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    os.chdir(target_dir)

    data_file = None
    disk_file = None
    try:
        if file_name is None:
            disk_file = max(glob.iglob('%s*.[Pp][Kk][Ll]' % file_header), key=os.path.getctime)
        else:
            disk_file = file_name

    except Exception:
        print("Cannot use saved data")

    else:
        try:
            with open(disk_file, 'rb') as input:
                data_file = pickle.load(input)
        except EOFError:
            print("File Error!")

    os.chdir(curr_dir)

    return data_file, disk_file


def save_to_file(filename, data):

    # change folder to "cbla_data". This is where al the data will be stored
    curr_dir = os.getcwd()
    target_dir = os.path.join(curr_dir, folder_name)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    os.chdir(target_dir)

    # create a temp file
    temp_filename = "__%s.tmp" % filename
    with open(temp_filename, 'wb') as output:
        pickle.dump(data, output, protocol=3)

        output.flush()
        os.fsync(output.fileno())

    # move original file
    shutil.copy(temp_filename, filename)
    os.chdir(curr_dir)


