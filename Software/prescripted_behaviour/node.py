import threading
from interactive_system import Messenger
from interactive_system.InteractiveCmd import command_object
from time import sleep

class Node(threading.Thread):

    def __init__(self, messenger: Messenger.Messenger, node_name=None):

        super(Node, self).__init__(name=node_name, daemon=True)

        self.node_name = 'generic'
        self.messenger = messenger

        # constructing the list of input variables
        self.in_var = dict()

        # constructing the list of output variables
        self.out_var = dict()

        if isinstance(node_name, str):
            self.node_name = node_name

    @property
    def in_var_list(self) -> tuple:
        return tuple(self.in_var.keys())

    @property
    def out_var_list(self) -> tuple:
        return tuple(self.out_var.keys())

    def run(self):
        raise SystemError('Run must be defined in the child class')

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



class Var(object):

    def __init__(self, val=0):
        self.__val = val

    @property
    def val(self):
        return self.__val

    @val.setter
    def val(self, new_val):
        self.__val = new_val

class Input_Node(Node):

    def __init__(self, messenger: Messenger.Messenger, teensy_name: str, node_name='input_node', **input_name):
        super(Input_Node, self).__init__(messenger, node_name='%s.%s' % (teensy_name, node_name, ))

        if not isinstance(teensy_name, str):
            raise TypeError('teensy_name must be a string!')


        self.teensy_name = teensy_name
        self.in_dev = dict()

        for name, input_dev in input_name.items():
            self.out_var[name] = Var(0)
            self.in_dev[name] = input_dev

        self.print_to_term = False


    def run(self):

        while True:

            out_var_list = []
            for name in self.out_var.keys():
                out_var_list.append((self.in_dev[name], self.out_var[name]))

                sample = self.read_sample()
                self.out_var[name].val = sample[self.teensy_name][0][self.in_dev[name]]

                if self.print_to_term:
                    print('[%s] %s: %f' % (self.in_dev[name], 'sensor_out', self.out_var[name].val))
                sleep(self.messenger.estimated_msg_period)


class Output_Node(Node):

    def __init__(self, messenger: Messenger.Messenger, teensy_name: str, node_name='output_node', **output_name):

        super(Output_Node, self).__init__(messenger, node_name='%s.%s' % (teensy_name, node_name))

        if not isinstance(teensy_name, str):
            raise TypeError('teensy_name must be a string!')

        self.teensy_name = teensy_name
        self.out_dev = dict()

        for name, output_dev in output_name.items():
            self.in_var[name] = Var(0)
            self.out_dev[name] = output_dev

        self.print_to_term = False

    def run(self):

        while True:

            in_var_list = []
            for name in self.in_var.keys():
                in_var_list.append((self.out_dev[name], self.in_var[name]))

            self.send_output_cmd(self.teensy_name, tuple(in_var_list))
            if self.print_to_term:
                print('[%s] %s: %f' % (self.out_dev[name], 'action_out', self.in_var[name].val))
            sleep(self.messenger.estimated_msg_period * 2)
