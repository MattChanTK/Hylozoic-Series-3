import struct

class SystemParameters():

    msg_length = 64

    def __init__(self):

        #==== outputs ====
        self.output_param = dict()
        # ---defaults---
        self.output_param['indicator_led_on'] = True
        self.output_param['indicator_led_period'] = 100

        #~~~~ variable type ~~~~
        self.var_list = dict()
        self.var_list["bool"] = ('indicator_led_on',)
        self.var_list["int8"] = ()
        self.var_list["int16"] = ('indicator_led_period',)
        #~~~ function to encode variable type ~~~~
        self.var_encode_func = dict()
        self.var_encode_func["bool"] = self.__set_bool_var
        self.var_encode_func["int8"] = self.__set_int8_var
        self.var_encode_func["int16"] = self.__set_int_var

        #==== inputs ====
        self.input_state = dict()
        # ---defaults---
        self.input_state['analog_0_state'] = 0

        #=== request type ====
        self.request_types = dict()
        self.request_types['basic'] = ('indicator_led_on', 'indicator_led_period')
        self.request_types['wave_1'] = ()
        self.request_type_ids = enum_dict('basic', 'wave_1')
        self.request_type = 'basic'

    def __var_encode(self, func, args):
         func(*args)

    def get_input_state(self, state_type):
        if isinstance(state_type, str):
            if state_type in self.input_state:
                return self.input_state[state_type]
            else:
                raise ValueError(state_type + " does not exist!")
        else:
            raise TypeError("'State type' must be a string!")

    def set_request_type(self, change_request_type):
        self.request_type = change_request_type
        return self.request_type

    def set_output_param(self, param_type, param_val):

        try:
            if param_type not in self.request_types[self.request_type]:
                return 1
        except KeyError:
            return -1

        if isinstance(param_type, str):
            if param_type in self.output_param:
                for var_type, var_entry in self.var_list.items():
                    if param_type in var_entry:
                        try:
                            self.var_encode_func[var_type](param_type, int(param_val))
                            break
                        except KeyError:
                            raise KeyError("There isn't any encode function for " + str(var_type))
                else:
                    #warning! this function does not do type error check on values
                    self.output_param[param_type] = param_val
            else:
                raise ValueError(param_type + " does not exist!")
        else:
            raise TypeError("'Parameter type' must be a string!")

        return 0


    def __set_int_var(self, input_type, input, num_bit=16):
        if isinstance(input, int):
            if input > 2**num_bit - 1 or input < 0:
                raise TypeError(input_type + " must either be positive and less than " + str(2**num_bit))
            self.output_param[input_type] = input
        else:
            raise TypeError(input_type + " must be an integer")

    def __set_int8_var(self, input_type, input, num_bit=16):
        self.__set_int_var(input_type, input, 8)

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

        # byte 0 and byte 63: the msg signature; left as 0 for now
        signature_front = bytearray(chr(0), 'utf-8')
        signature_back = bytearray(chr(0), 'utf-8')

        # byte 1: type of request
        header = bytearray(chr(self.request_type_ids[self.request_type]), 'utf-8')

        # create an 64 - 3 bytes of zeros (w/o the signature and header)
        content = bytearray(chr(0)*(SystemParameters.msg_length - 3), 'utf-8')

        self.__compose_outgoing_msg(content)

        return signature_front + header + content + signature_back

    def __compose_outgoing_msg(self, content):

        if self.request_type == 'basic':
            # byte 0: indicator LED on or off
            content[0] = self.output_param['indicator_led_on']

            # byte 1 to 2: blinking frequency of the indicator LED
            content[1:3] = struct.pack('H', self.output_param['indicator_led_period'])


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