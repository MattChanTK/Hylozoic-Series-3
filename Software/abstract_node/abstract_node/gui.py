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

        self._add_messenger_frame(messenger)


    def add_frame(self, *child_frame):

        self.frame_list += child_frame

    def _add_messenger_frame(self, messenger):

        # add the messenger frame automatically
        self.messenger_frame = Messenger_Frame(self.root, messenger)
        self.frame_list.append(self.messenger_frame)

    def run(self):
        self.pack_frames()
        for frame in self.frame_list:
            frame.run()
            frame.updateFrame()

        self.root.mainloop()

    def pack_frames(self):

        for frame in self.frame_list:
            if isinstance(frame, Messenger_Frame):
                frame.pack(side=tk.BOTTOM)
            else:
                frame.pack(side=tk.LEFT)



class Display_Frame(tk.Frame):

    def __init__(self, tk_master, node_list: OrderedDict):

        super(Display_Frame, self).__init__(tk_master)

        self.node_list = node_list

        self._construct_frame()

    def _construct_frame(self):

        self.status_text = OrderedDict()
        self.action_text = OrderedDict()
        self.status_frame = tk.Frame(self)
        self.action_frame = tk.Frame(self)

        self.status_frame.pack(side=tk.LEFT)
        self.action_frame.pack(side=tk.LEFT)

        # header label
        self.status_frame_label = tk.Label(self.status_frame, text="Sensor Readings", font=("Helvetica", 14))
        self.status_frame_label.grid(row=0, columnspan=2)
        self.action_frame_label = tk.Label(self.action_frame, text="Actuator Outputs", font=("Helvetica", 14))
        self.action_frame_label.grid(row=0, columnspan=2)

        # contents
        for name, node in self.node_list.items():
            if isinstance(node, Input_Node):
                for var_name in node.out_var_list:
                    self.status_text[(name, var_name)] = [tk.Label(self.status_frame,text="%s" % name, fg='blue'),
                                                          tk.Label(self.status_frame,
                                                                   text="###",
                                                                   fg='blue', width='8', anchor=tk.E, justify=tk.RIGHT)]

            elif isinstance(node, Output_Node) or isinstance(node, Frond):
                for var_name in node.in_var_list:
                    self.action_text[(name, var_name)] = [tk.Label(self.action_frame, text="%s" % name, fg='red'),
                                                          tk.Label(self.action_frame,
                                                                   text="###",
                                                                   fg='red', width='8', anchor=tk.E, justify=tk.RIGHT)]

    def run(self):

        row_id = 2
        for label in self.status_text.values():
            label[0].grid(column=0, row=row_id, ipadx=10, sticky=tk.W)
            label[1].grid(column=1, row=row_id, ipadx=10, sticky=tk.E)
            row_id += 1

        for label in self.action_text.values():
            label[0].grid(column=0, row=row_id, ipadx=10, sticky=tk.W)
            label[1].grid(column=1, row=row_id, ipadx=10, sticky=tk.E)
            row_id += 1

    def updateFrame(self):
        for name, label in self.status_text.items():

            msg = "%s" % str(self.node_list[name[0]].out_var[name[1]].val)[:6]
            label[1]["text"] = msg

        for name, label in self.action_text.items():
            msg = "%s" % str(self.node_list[name[0]].in_var[name[1]].val)[:6]
            label[1]["text"] = msg

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

class Messenger_Frame(tk.Frame):

    def __init__(self, tk_master, messenger):
        super(Messenger_Frame, self).__init__(tk_master)

        self.messenger = messenger

        # frame for showing the messenger speed
        self.messenger_time_label = tk.Label(self, text="Messenger Update Period: ###", fg='green',
                                             font=("Helvetica", 10), anchor=tk.E, justify=tk.RIGHT)


    def run(self):
        self.messenger_time_label.pack(side=tk.RIGHT, anchor=tk.E)

    def updateFrame(self):

        self.messenger_time_label["text"] = "Messenger Update Period: %.4fs" % self.messenger.estimated_msg_period
        self.after(100, self.updateFrame)
        self.update()



if __name__ == '__main__':
    pass