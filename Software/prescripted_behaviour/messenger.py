import threading
import queue
from time import clock
from time import sleep

from interactive_system.InteractiveCmd import command_object


class Messenger(threading.Thread):

    def __init__(self, interactive_cmd, msg_period: float):

        super(Messenger, self).__init__(daemon=True)

        self.msg_q = queue.Queue()
        self.t0 = 0.0
        self.msg_period = msg_period

        self.cmd = interactive_cmd

    def run(self):

        self.t0 = clock()
        while True:


            sleep(self.msg_period - (clock() - self.t0))
            self.t0 = clock()

    def __send_message(self):

        self.cmd.send_commands()

    def load_message(self, msg: command_object):

        self.msg_q.put_nowait(msg)

