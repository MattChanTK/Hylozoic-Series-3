from threading import Thread
from queue import Queue
from collections import defaultdict
from copy import copy
from copy import deepcopy
import pickle
import os
import shutil
import time
import glob


class DataCollector(Thread):

    def __init__(self, data_file=None, file_save_freq=50):

        super(DataCollector, self).__init__(name='DataCollect', daemon=False)

        self.packet_queue = Queue()
        self.states_update_queue = Queue()

        # if using saved data
        if isinstance(data_file, (dict, defaultdict)):
            self.data_file = data_file
            self.data_file['file_num'] += 1

        # if having no data
        else:
            self.data_file = dict()
            self.data_file['data'] = defaultdict(list)
            self.data_file['state'] = defaultdict(dict)

            now = time.strftime("%y-%m-%d_%H-%M-%S", time.localtime())
            self.data_file['file_name'] = 'cbla_data_%s' % now
            self.data_file['file_num'] = 1

        self.filetype = ".pkl"

        self.save_to_file()

        self.program_terminating = False

        self.file_save_freq = file_save_freq

    def run(self):

        packet_count = 0
        while not self.program_terminating or not self.packet_queue.empty() or not self.states_update_queue.empty():

            # saving run-time data to memory
            if not self.packet_queue.empty():

                node_name, packet_data = self.packet_queue.get_nowait()
                self.data_file['data'][node_name].append(packet_data)
                packet_count += 1

            # saving state data to memory
            if not self.states_update_queue.empty():

                node_name, states_val = self.states_update_queue.get_nowait()
                self.data_file['state'][node_name] = states_val

            # saving to file
            if packet_count >= self.file_save_freq and not self.program_terminating:
                self.save_to_file()

        self.save_to_file()

        # remove tmp files
        curr_dir = os.getcwd()
        os.chdir(os.path.join(curr_dir, "cbla_data"))
        temp_files = glob.glob("*.tmp")
        for temp_file in temp_files:
            os.remove(temp_file)

    def append_data_packet(self, node_name, data_packet):

        self.packet_queue.put((node_name, copy(data_packet)))

    def update_state(self, node_name, states_update):

        self.states_update_queue.put((node_name, deepcopy(states_update)))

    def end_data_collection(self):

        self.program_terminating = True

    def save_to_file(self):

        save_to_file('%s (%d)%s' % (self.data_file['file_name'], self.data_file['file_num'], self.filetype),
                     self.data_file)


def retrieve_data(file_name=None):

    # ====== retrieving data ======
    # change folder to "cbla_data". This is where al the data will be stored
    curr_dir = os.getcwd()
    os.chdir(os.path.join(curr_dir, "cbla_data"))

    data_import = None
    try:
        if file_name is None:
            data_file = max(glob.iglob('cbla_data*.[Pp][Kk][Ll]'), key=os.path.getctime)
        else:
            data_file = file_name

    except Exception:
        print("Cannot use saved data")

    else:
        try:
            with open(data_file, 'rb') as input:
                data_import = pickle.load(input)
        except EOFError:
            print("File Error!")

    os.chdir(curr_dir)

    data_collector = DataCollector(data_import)

    return data_collector


def save_to_file(filename, data):

    # change folder to "cbla_data". This is where al the data will be stored
    curr_dir = os.getcwd()
    os.chdir(os.path.join(curr_dir, "cbla_data"))

    # create a temp file
    temp_filename = "__%s.tmp" % filename
    with open(temp_filename, 'wb') as output:
        pickle.dump(data, output, protocol=3)

        output.flush()
        os.fsync(output.fileno())

    # move original file
    shutil.copy(temp_filename, filename)
    os.chdir(curr_dir)


