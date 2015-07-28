__author__ = 'Matthew'

from multiprocessing import Process, Queue, Event
import multiprocessing
import queue
import shelve
from time import sleep, perf_counter
import logging
import sys



class DataSaver(Process):

    def __init__(self, shelve_path):

        self.shelf = shelve.open(shelve_path, protocol=3, writeback=False)
        self.__data_queue = Queue()
        self.__program_terminating = Event()
        super(DataSaver, self).__init__(name="DataSaver")
        self.daemon = False

    def run(self):

        while (not self.__program_terminating.is_set()) or \
              (self.__program_terminating.is_set() and not self.__data_queue.empty()):

            # print('queue_size ', self.__data_queue.qsize())
            try:
                block_key, block_data = self.__data_queue.get(block=True, timeout=2)
            except queue.Empty:
                pass
            else:
                self.shelf[block_key] = block_data

            sleep(0.0001)

        self.shelf.close()

    def enqueue_data_block(self, data_block: tuple):
        if not isinstance(data_block, tuple) and len(data_block) == 2:
            raise TypeError("Data block must be a tuple of length 2!")

        self.__data_queue.put(data_block)

    def terminate_program(self):

        self.__program_terminating.set()


