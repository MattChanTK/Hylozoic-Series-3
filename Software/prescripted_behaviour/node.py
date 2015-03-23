import threading
from interactive_system import Messenger
from interactive_system.InteractiveCmd import command_object
from time import sleep

class Node(threading.Thread):

    def __init__(self, messenger: Messenger.Messenger, node_name=None):

        super(Node, self).__init__(daemon=True)

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
    def get_out_var_list(self) -> tuple:
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

    def send_output_cmd(self, teensy, *output):

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


class Test_Node(Node):

    def __init__(self, messenger: Messenger.Messenger, input_addr):

        super(Test_Node, self).__init__(messenger)

        self.in_var['ir_sensor_1'] = input_addr

    def run(self):

        while True:
            print('[%s] %s: %f' % (self.node_name, 'sensor_out', self.in_var['ir_sensor_1'].val))
            sleep(0.5)


class Tentacle(Node):

    def __init__(self, messenger: Messenger.Messenger, teensy_name: str, tentacle_num: int, ir_0: Var, ir_1: Var):

        if not isinstance(teensy_name, str):
            raise TypeError('teensy_name must be a string!')

        self.teensy_name = teensy_name

        if not isinstance(tentacle_num, int):
            raise TypeError('Tentacle number must an integer!')


        super(Tentacle, self).__init__(messenger, node_name='Tentacle %d' % tentacle_num)

        # defining the input variables
        self.in_var['ir_sensor_0'] = ir_0
        self.in_var['ir_sensor_1'] = ir_1

        # defining the output variables
        self.out_var['tentacle_out'] = Var(0)
        self.tentacle_sma_name = 'tentacle_%d_arm_motion_on' % tentacle_num
        self.out_var['reflex_out_0'] = Var(0)
        self.tentacle_reflex_0_name = 'tentacle_%d_reflex_0_level' % tentacle_num
        self.out_var['reflex_out_1'] = Var(0)
        self.tentacle_reflex_1_name = 'tentacle_%d_reflex_1_level' % tentacle_num




    def run(self):

        while True:
            output_changed = False
            if self.in_var['ir_sensor_1'].val > 1400 and self.out_var['tentacle_out'].val ==0:
                self.out_var['tentacle_out'].val = 3
                self.out_var['reflex_out_0'].val = 100
                self.out_var['reflex_out_1'].val = 100
                output_changed = True

            elif self.in_var['ir_sensor_1'].val <= 1000 and self.out_var['tentacle_out'].val > 0:

                self.out_var['tentacle_out'].val = 0
                self.out_var['reflex_out_0'].val = 0
                self.out_var['reflex_out_1'].val = 0
                output_changed = True

            if output_changed:

                self.send_output_cmd(self.teensy_name,
                                     (self.tentacle_sma_name, self.out_var['tentacle_out']),
                                     (self.tentacle_reflex_0_name, self.out_var['reflex_out_0']),
                                     (self.tentacle_reflex_1_name, self.out_var['reflex_out_1']))

            print('%d, %d, %d' % (self.out_var['tentacle_out'].val,
                                  self.out_var['reflex_out_0'].val,
                                  self.out_var['reflex_out_1'].val))


            sleep(self.messenger.estimated_msg_period*2)

class IR_Proximity_Sensor(Node):

    def __init__(self, messenger: Messenger.Messenger, teensy_name: str, sensor_name: str):
        super(IR_Proximity_Sensor, self).__init__(messenger, node_name='ir sensor')

        if not isinstance(teensy_name, str):
            raise TypeError('teensy_name must be a string!')

        if not isinstance(sensor_name, str):
            raise TypeError('sensor_name must be a string!')

        self.teensy_name = teensy_name
        self.sensor_name = sensor_name

        # define output variables
        self.out_var['sensor_raw'] = Var(0)


    def run(self):

        while True:
            sample = self.read_sample()
            self.out_var['sensor_raw'].val = sample[self.teensy_name][0][self.sensor_name]

            #print('[%s] %s: %f' % (self.node_name, 'sensor_out', self.out_var['sensor_raw'].val))
            sleep(self.messenger.estimated_msg_period)






