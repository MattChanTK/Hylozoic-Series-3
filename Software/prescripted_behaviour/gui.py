__author__ = 'Matthew'
import tkinter as tk
from node import *

class GUI(object):
    def __init__(self, node_list: dict):
        self.root = tk.Tk()
        self.node_list = node_list
        self.status_text = dict()
        self.action_text = dict()

        for name, node in node_list.items():
            if isinstance(node, Input_Node):
                self.status_text[name] = tk.Label(self.root, text="%s = %d" % (name, node.out_var['input'].val))

            if isinstance(node, Output_Node):
                self.action_text[name] = tk.Label(self.root, text="%s = %d" % (name, node.in_var['output'].val))

        self.updateGUI()

    def run(self):


        for label in self.status_text.values():
            label.pack()
        for label in self.action_text.values():
            label.pack()
        self.root.after(500, self.updateGUI)
        self.root.mainloop()

    def updateGUI(self):
        for name, label in self.status_text.items():
            msg = "%s = %d" % (name, self.node_list[name].out_var['input'].val)
            label["text"] = msg

        for name, label in self.action_text.items():
            msg = "%s = %d" % (name, self.node_list[name].in_var['output'].val)
            label["text"] = msg


        self.root.after(500, self.updateGUI)
        self.root.update()



if __name__ == '__main__':
    pass