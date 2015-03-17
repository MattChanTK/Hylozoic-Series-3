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

        super(Messenger, self).__init__(daemon=True)



    def run(self):

        self.t0 = clock()
        while True:
            self.cmd.send_commands()
            sleep(self.msg_period - (clock() - self.t0))
            self.t0 = clock()






