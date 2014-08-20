import struct

class SystemParameters():

    msg_length = 64

    def __init__(self):

        #==== outputs ====
        self.output_param = dict()
        # ---defaults---
        self.output_param['indicator_led_on'] = True
        self.output_param['indicator_led_period'] = 100

        self.bool_var_list = ('indicator_led_on',)
        self.int8_var_list = ()
        self.int16_var_list = ('indicator_led_period',)

        #==== inputs ====
        self.input_state = dict()
        # ---defaults---
        self.input_state['analog_0_state'] = 0

        #=== list of behaviours for selection ====
        self.behaviour_type = enum_dict('INTERACTIVE', 'AUTO')
        self.behaviour = self.behaviour_type['INTERACTIVE']

    def set_behaviour_type(self, behaviour_type):
        if isinstance(behaviour_type, str):
            if behaviour_type in self.behaviour_type:
                self.behaviour = self.behaviour_type[behaviour_type]
            else:
                raise ValueError(behaviour_type + " does not exist!")
        else:
            raise TypeError("'State type' must be a string!")

    def get_input_state(self, state_type):
        if isinstance(state_type, str):
            if state_type in self.input_state:
                return self.input_state[state_type]
            else:
                raise ValueError(state_type + " does not exist!")
        else:
            raise TypeError("'State type' must be a string!")

    def set_output_param(self, param_type, param_val):
        if isinstance(param_type, str):
            if param_type in self.output_param:
                if param_type in self.bool_var_list:
                    self.__set_bool_var(param_type, int(param_val))
                elif param_type in self.int8_var_list:
                    self.__set_int_var(param_type, int(param_val), 8)
                elif param_type in self.int16_var_list:
                    self.__set_int_var(param_type, int(param_val), 16)
                else:
                    #warning! this function does not do type error check on values
                    self.output_param[param_type] = param_val
            else:
                raise ValueError(param_type + " does not exist!")
        else:
            raise TypeError("'Parameter type' must be a string!")


    def __set_int_var(self, input_type, input, num_bit):
        if isinstance(input, int):
            if input > 2**num_bit - 1 or input < 0:
                raise TypeError(input_type + " must either be positive and less than " + str(2**num_bit))
            self.output_param[input_type] = input
        else:
            raise TypeError(input_type + " must be an integer")

    def __set_bool_var(self, input_type, input):
        if isinstance(input, bool):
            self.output_param[input_type] = input
        elif input == 0:
            self.output_param[input_type] = False
        elif input == 1:
            self.output_param[input_type] = True
        else:
            raise TypeError(input_type + " must either be 'True' or 'False'")

    def parse_message_content(self, msg):

        # byte 0 and byte 63: the msg signature; can ignore

        # byte 1: analog 0 state
        self.input_state['analog_0_state'] = struct.unpack_from('H', msg[1:3])[0]

    def compose_message_content(self):

        # create an 64 bytes of zeros
        msg = bytearray(chr(0)*SystemParameters.msg_length, 'utf-8')

        # byte 0 and byte 63: the msg signature; left as 0 for now

        # byte 1: type of behaviour
        msg[1] = self.behaviour

        # byte 2: indicator LED on or off
        msg[2] = self.output_param['indicator_led_on']

        # byte 3 to 4: blinking frequency of the indicator LED
        msg[3:5] = struct.pack('H', self.output_param['indicator_led_period'])

        return msg

def enum_dict(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return enums

if __name__ == '__main__':
    def print_data(data, raw_dec=False):
        if data:
            i = 0
            print("Number of byte: " + str(len(data)))
            while i < len(data):
                if raw_dec:
                    char = int(data[i])
                else:
                    char = chr(data[i])
                print(char, end=" ")
                i += 1

            print('\n')

    s = SystemParameters()
    s.set_indicator_led_on(True)
    s.set_indicator_led_period(65535)
    print_data(s.compose_message_content(), raw_dec=True)