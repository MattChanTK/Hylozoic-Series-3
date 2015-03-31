__author__ = 'Matthew'
import threading
import tkinter as tk
from collections import OrderedDict

from abstract_node.node import *
from low_level_node import *


class GUI(threading.Thread):
    def __init__(self, node_list: dict):

        super(GUI, self).__init__(name='gui', daemon=True)

        self.root = tk.Tk()
        self.root.resizable(True, True)

        self.node_list = node_list

        self.status_text = OrderedDict()
        self.action_text = OrderedDict()

        for name, node in node_list.items():
            if isinstance(node, Input_Node):
                for var_name in node.out_var_list:
                    self.status_text[(name, var_name)] = tk.Label(self.root,
                                                                  text="%s = %d" % (name, node.out_var[var_name].val),
                                                                  fg='blue')

            elif isinstance(node, Output_Node) or isinstance(node, Frond):
                for var_name in node.in_var_list:
                    self.action_text[(name, var_name)] = tk.Label(self.root,
                                                                  text="%s = %d" % (name, node.in_var[var_name].val),
                                                                  fg='red')


    def run(self):

        for label in self.status_text.values():
            label.pack(fill=tk.X, padx=10)
        for label in self.action_text.values():
            label.pack(fill=tk.X, padx=10)
        self.root.after(500, self.updateGUI)
        self.root.mainloop()

        self.updateGUI()

    def updateGUI(self):
        for name, label in self.status_text.items():
            msg = "%s.%s:\t\t%d" % (name[0], name[1], self.node_list[name[0]].out_var[name[1]].val)
            label["text"] = msg

        for name, label in self.action_text.items():
            msg = "%s.%s:\t%d" % (name[0], name[1], self.node_list[name[0]].in_var[name[1]].val)
            label["text"] = msg

        self.root.after(500, self.updateGUI)
        self.root.update()



if __name__ == '__main__':
    pass