__author__ = 'Matthew'
import tkinter as tk
from collections import OrderedDict

from .node import *
from .low_level_node import *

class Main_GUI(Node):

    def __init__(self, messenger):

        super(Main_GUI, self).__init__(messenger, node_name='main_gui')

        self.root = tk.Tk()
        self.frame_list = []

    def add_frame(self, *child_frame):

        self.frame_list += child_frame


    def run(self):
        self.pack_frames()
        for frame in self.frame_list:
            frame.run()
            frame.updateFrame()
        self.root.mainloop()

    def pack_frames(self):
        for frame in self.frame_list:
            frame.pack()


class Display_Frame(tk.Frame):

    def __init__(self, tk_master, node_list: OrderedDict):

        super(Display_Frame, self).__init__(tk_master)

        self.node_list = node_list
        self.status_text = OrderedDict()
        self.action_text = OrderedDict()
        self.status_frame = tk.Frame()
        self.action_frame = tk.Frame()

        self.status_frame.pack(side=tk.LEFT)
        self.action_frame.pack(side=tk.LEFT)

        for name, node in node_list.items():
            if isinstance(node, Input_Node):
                for var_name in node.out_var_list:
                    self.status_text[(name, var_name)] = tk.Label(self.status_frame,
                                                                  text="%s = %d" % (name, node.out_var[var_name].val),
                                                                  fg='blue')

            elif isinstance(node, Output_Node) or isinstance(node, Frond):
                for var_name in node.in_var_list:
                    self.action_text[(name, var_name)] = tk.Label(self.action_frame,
                                                                  text="%s = %d" % (name, node.in_var[var_name].val),
                                                                  fg='red')



    def run(self):

        for label in self.status_text.values():
            label.pack(fill=tk.X, padx=10)
        for label in self.action_text.values():
            label.pack(fill=tk.X, padx=10)

    def updateFrame(self):
        for name, label in self.status_text.items():
            msg = "%s.%s:\t\t%d" % (name[0], name[1], self.node_list[name[0]].out_var[name[1]].val)
            label["text"] = msg

        for name, label in self.action_text.items():
            msg = "%s.%s:\t%d" % (name[0], name[1], self.node_list[name[0]].in_var[name[1]].val)
            label["text"] = msg

        self.after(500, self.updateFrame)
        self.update()


class Control_Frame(tk.Frame):

    def __init__(self, tk_master, control_var: OrderedDict):

        super(Control_Frame, self).__init__(tk_master)

        self.label_list = OrderedDict()
        self.entry_list = OrderedDict()
        self.control_var = OrderedDict()

        for name, var in control_var.items():
            self.label_list[name] = tk.Label(self, text=name)
            self.entry_list[name] = tk.Entry(self)
            self.control_var[name] = var

    def run(self):

        for name, entry in self.entry_list.items():
            self.label_list[name].pack()
            entry.insert(0, '0')
            entry.pack()

    def updateFrame(self):

        for name, entry in self.entry_list.items():
            try:
                curr_val = int(entry.get())
                if curr_val > 255 or curr_val < 0:
                    raise ValueError

                if curr_val != self.control_var[name].val:
                    self.control_var[name].val = curr_val

            except ValueError:
                self.label_list[name].config(fg='red')
            else:
                self.label_list[name].config(fg='black')

        self.after(100, self.updateFrame)
        self.update()


if __name__ == '__main__':
    pass