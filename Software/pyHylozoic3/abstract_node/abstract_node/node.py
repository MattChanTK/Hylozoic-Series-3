'''Base classes for all Nodes and variables in the Hylozoic 3 system'''
# Author: Matthew TK Chan <matthewchan@ieee.org>


import threading

from interactive_system import Messenger
from interactive_system import command_object
from time import sleep
from collections import OrderedDict


class Var(object):

    """Generic variable type use in the Hylozoic 3 system
    
    This provides a standard interface for all variables within the system. 
    This allows all variables, including those of immutable types, to be passed by refernce through this mutable object.
    
    Parameters
    ------------
    
    val (default = 0)
        Value of the variable
        
    Attributes
    ------------
    
    __val
        Value of the variable
        
    Examples
    ------------
        >>> a = Var((1, 2, 3))
        >>> a.val = {a_dict: (9, 8, 7)}
        >>> print(a.val['a_dict'])
    
    """

    def __init__(self, val=0):
        self.__val = val

    @property
    def val(self):
        return self.__val

    @val.setter
    def val(self, new_val):
        self.__val = new_val


class Node(threading.Thread):
    '''The base class for all Nodes in the Hylozoic 3 system
    
    This provides a standard structure that represents each independent abstract component in the system.
    Each Node is a thread. This allows Nodes in the system to run asynchronously.
    Each Node has a set of input and output variables of type Var. A Node interacts with other Nodes by means of having common variables.
    
    Parameters
    -----------
    
    messenger: Messenger
        The Messenger associated with the Node. The loop period of a Node should not be shorter than its Messenger.
        
    node_name : str (default = None)
        The name of the node. It is used to differentiate the different Nodes in the system. If no name is provided, it will be called "generic"
        
    Attributes
    -----------
    
    '''

    def __init__(self, messenger: Messenger, node_name=None):

        super(Node, self).__init__(name=node_name, daemon=True)

        self.node_name = 'generic'
        self.messenger = messenger

        # constructing the list of input variables
        self.in_var = OrderedDict()

        # constructing the list of output variables
        self.out_var = OrderedDict()

        if isinstance(node_name, str):
            self.node_name = node_name

        self.update_freq = 2
        self.alive = True

    @property
    def in_var_list(self) -> tuple:
        return tuple(self.in_var.keys())

    @property
    def out_var_list(self) -> tuple:
        return tuple(self.out_var.keys())

    def run(self):
        raise SystemError('Run must be defined in the child class')

    def add_in_var(self, var: Var, var_key: str):

        if not isinstance(var, Var):
            raise TypeError("in_var must be of type Var!")

        if not isinstance(var_key, str):
            raise TypeError("var_key must be of type str!")

        self.in_var[var_key] = var

    def read_sample(self, print_warning=False):

        sample = self.messenger.sample
        if print_warning:
            # if the first sample read was unsuccessful, just return the default value
            if sample is None:
                print("unsuccessful read")

            # if any one of those data wasn't new, it means that it timed out
            for teensy_name, sample_teensy in sample.items():
                if not sample_teensy[1]:
                    print(teensy_name + " has timed out")

        return sample

    def send_output_cmd(self, teensy, output):

        if output:
            if not isinstance(teensy, str):
                raise TypeError('Teensy name must be string!')

            cmd_obj = command_object(teensy, msg_setting=1)
        else:
            return


        for output_name, value in output:
            if isinstance(value, Var):
                value = value.val
            cmd_obj.add_param_change(output_name, value)

        self.messenger.load_message(cmd_obj)


class Input_Node(Node):

    def __init__(self, messenger: Messenger, teensy_name: str, node_name='input_node', **input_name):
        super(Input_Node, self).__init__(messenger, node_name='%s.%s' % (teensy_name, node_name, ))

        if not isinstance(teensy_name, str):
            raise TypeError('teensy_name must be a string!')


        self.teensy_name = teensy_name
        self.in_dev = dict()

        for name, input_dev in input_name.items():
            self.out_var[name] = Var(0)
            self.in_dev[name] = input_dev

        self.print_to_term = False
        self.update_freq = 1.5

    def run(self):

        while self.alive:

            if self.teensy_name not in self.messenger.active_teensy_list:
                self.alive = False
                print('%s is no longer functional. Terminated.' % self.node_name)
                return

            out_var_list = []
            sample = self.read_sample()

            for name in self.out_var.keys():
                out_var_list.append((self.in_dev[name], self.out_var[name]))

                self.out_var[name].val = sample[self.teensy_name][0][self.in_dev[name]]

                if self.print_to_term:
                    print('[%s] %s: %f' % (self.in_dev[name], 'sensor_out', self.out_var[name].val))
            sleep(self.messenger.estimated_msg_period * self.update_freq)


class Output_Node(Node):

    def __init__(self, messenger: Messenger, teensy_name: str, node_name='output_node', **output_name):

        super(Output_Node, self).__init__(messenger, node_name='%s.%s' % (teensy_name, node_name))

        if not isinstance(teensy_name, str):
            raise TypeError('teensy_name must be a string!')

        self.teensy_name = teensy_name
        self.out_dev = dict()

        for name, output_dev in output_name.items():
            self.in_var[name] = Var(0)
            self.out_dev[name] = output_dev

        self.print_to_term = False
        self.update_freq = 2

    def run(self):

        while self.alive:

            if self.teensy_name not in self.messenger.active_teensy_list:
                self.alive = False
                print('%s is no longer functional. Terminated.' % self.node_name)
                return

            in_var_list = []
            for name in self.in_var.keys():
                in_var_list.append((self.out_dev[name], self.in_var[name]))

            self.send_output_cmd(self.teensy_name, tuple(in_var_list))
            for name in self.in_var.keys():
                if self.print_to_term:
                    print('[%s] %s: %f' % (self.out_dev[name], 'action_out', self.in_var[name].val))
            sleep(self.messenger.estimated_msg_period * self.update_freq)


class Simple_Node(Node):

    def __init__(self, messenger: Messenger, node_name='simple_node', output: Var=Var(0), **input_var):

        super(Simple_Node, self).__init__(messenger, node_name='%s' % node_name)

        self.out_var['output'] = output

        for name, input_var in input_var.items():
            self.in_var[name] = input_var

        self.print_to_term = False
