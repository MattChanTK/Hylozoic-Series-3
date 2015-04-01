__author__ = 'Matthew'
import tkinter as tk

from abstract_node.low_level_node import *
from abstract_node.gui import *


class Main_GUI(Main_GUI):

    def pack_frames(self):

        for frame in self.frame_list:
            frame.pack(side=tk.LEFT)


class Manual_Control_GUI(Control_Frame):

    pass

if __name__ == '__main__':
    pass