from threading import Thread
from queue import Queue
from collections import defaultdict
from copy import copy
import pickle
import os
import shutil
import time
import glob


class DataCollector(Thread):

    def __init__(self, data_file=None, file_save_freq=10):

        super(DataCollector, self).__init__(name='DataCollect', daemon=False)

        self.packet_queue = Queue()

        # if using saved data
        if isinstance(data_file, (dict, defaultdict)):
            self.data_file = data_file
            self.filename = data_file['file_name']
            self.filenum = data_file['file_num'] + 1

        # if having no data
        else:
            self.data_file = defaultdict(list)
            now = time.strftime("%y-%m-%d_%H-%M-%S", time.localtime())
            self.filename = 'cbla_data_%s' % now
            self.filenum = 1

        self.filetype = ".pkl"

        self.data_file['file_name'] = self.filename
        self.data_file['file_num'] = self.filenum

        save_to_file('%s (%d)%s' % (self.filename, self.filenum, self.filetype), self.data_file)

        self.program_terminating = False

        self.file_save_freq = file_save_freq

    def run(self):

        packet_count = 0
        while not self.program_terminating or self.packet_queue.not_empty():

            if not self.packet_queue.empty():

                packet_name, packet_data = self.packet_queue.get_nowait()
                self.data_file[packet_name].append(packet_data)
                packet_count += 1

            if packet_count >= self.file_save_freq:
                save_to_file('%s (%d)%s' % (self.filename, self.filenum, self.filetype), self.data_file)

        save_to_file('%s (%d)%s' % (self.filename, self.filenum, self.filetype), self.data_file)

        # remove tmp files
        temp_files = glob.glob("*.tmp")
        for temp_file in temp_files:
            os.remove(temp_file)

    def append_data_packet(self, node_name, data_packet):

        self.packet_queue.put((node_name, copy(data_packet)))

    def end_data_collection(self):

        self.program_terminating = True


def retrieve_data(file_name=None):

    # ====== retrieving data ======
    # change folder to "pickle_jar". This is where al the data will be stored
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

    data_collector = DataCollector(data_import)

    return data_collector


def save_to_file(filename, data):

    # create a temp file
    temp_filename = "__%s.tmp" % filename
    with open(temp_filename, 'wb') as output:
        pickle.dump(data, output, protocol=3)

        output.flush()
        os.fsync(output.fileno())

    # move original file
    shutil.copy(temp_filename, filename)
