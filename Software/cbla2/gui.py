__author__ = 'Matthew'
import tkinter as tk

from abstract_node.gui import *

class CBLA2_Main_GUI(Main_GUI):

    def pack_frames(self):
        for frame in self.frame_list:
            frame.pack(side=tk.LEFT)


if __name__ == '__main__':
    pass