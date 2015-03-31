import threading
import queue
from time import clock
from time import sleep

from . import InteractiveCmd


class Messenger(threading.Thread):

    def __init__(self, interactive_cmd: InteractiveCmd.InteractiveCmd,
                 msg_period: float):

        self.t0 = 0.0
        self.msg_period = msg_period
        self.cmd = interactive_cmd
        self.cmd_q = queue.Queue()
        self.__estimated_msg_period = msg_period

        self.__sample = None
        self.sample_inputs(msg_period)

        super(Messenger, self).__init__(daemon=True, name='Messenger')

    @property
    def sample(self):
        return self.__sample

    @property
    def estimated_msg_period(self):
        return self.__estimated_msg_period

    def run(self):

        while True:
            self.t0 = clock()

            while not self.cmd_q.empty():
                msg = self.cmd_q.get_nowait()
                with self.cmd.lock:
                    self.cmd.enter_command(msg)

            with self.cmd.lock:
                self.cmd.send_commands()

            self.sample_inputs(self.msg_period)

            sleep(max(0, self.msg_period - (clock() - self.t0)))
            self.__estimated_msg_period = (9*self.__estimated_msg_period + clock() - self.t0)/10

            # print('Update time = %f' % (clock() - self.t0))

    def load_message(self, msg: InteractiveCmd.command_object):

        self.cmd_q.put_nowait(msg)
        #print(self.cmd_q.qsize())

    def sample_inputs(self, timeout_max=0.0):

        with self.cmd.lock:
            self.cmd.update_input_states(self.cmd.teensy_manager.get_teensy_name_list())

            self.__sample = self.cmd.get_input_states(self.cmd.teensy_manager.get_teensy_name_list(), ('all',),
                                                      timeout=max(0.1, timeout_max))
