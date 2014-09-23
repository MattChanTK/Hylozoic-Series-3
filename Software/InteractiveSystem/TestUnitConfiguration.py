import SystemParameters as SysParam
from SystemParameters import enum_dict
import struct
import re

class SimplifiedTestUnit(SysParam.SystemParameters):

    def __init__(self):
        super(SimplifiedTestUnit, self).__init__()

    def additional_config_routine(self):

        self.request_type_ids = enum_dict('basic', 'prgm', 'wave')
        self.var_encode_func["int8s"] = self.__set_int8_array

        # import parameters from files
        self.output_param_config_filename = 'param_config_output_simplified'
        self.input_param_config_filename = 'param_config_input_simplified'

        self._import_param_from_file()

    def parse_message_content(self, msg):

        # byte 0 and byte 63: the msg signature; can ignore

        # byte 1:  protocell
        self.input_state['protocell_0_ambient_light_sensor_state'] = msg[1]
        self.input_state['protocell_1_ambient_light_sensor_state'] = msg[2]

        # byte 11 to 18: tentacle_0
        self.input_state['tentacle_0_ir_0_state'] = msg[11]
        self.input_state['tentacle_0_ir_1_state'] = msg[12]
        self.input_state['tentacle_0_acc_x_state'] = struct.unpack_from('h', msg[13:15])[0]
        self.input_state['tentacle_0_acc_y_state'] = struct.unpack_from('h', msg[15:17])[0]
        self.input_state['tentacle_0_acc_z_state'] = struct.unpack_from('h', msg[17:19])[0]

        # byte 21 to 28: tentacle_0
        self.input_state['tentacle_1_ir_0_state'] = msg[21]
        self.input_state['tentacle_1_ir_1_state'] = msg[22]
        self.input_state['tentacle_1_acc_x_state'] = struct.unpack_from('h', msg[23:25])[0]
        self.input_state['tentacle_1_acc_y_state'] = struct.unpack_from('h', msg[25:27])[0]
        self.input_state['tentacle_1_acc_z_state'] = struct.unpack_from('h', msg[27:29])[0]

        # byte 31 to 38: tentacle_0
        self.input_state['tentacle_2_ir_0_state'] = msg[31]
        self.input_state['tentacle_2_ir_1_state'] = msg[32]
        self.input_state['tentacle_2_acc_x_state'] = struct.unpack_from('h', msg[33:35])[0]
        self.input_state['tentacle_2_acc_y_state'] = struct.unpack_from('h', msg[35:37])[0]
        self.input_state['tentacle_2_acc_z_state'] = struct.unpack_from('h', msg[37:39])[0]

        # # byte 1 and 2: analog 0 state
        # self.input_state['analog_0_state'] = struct.unpack_from('H', msg[1:3])[0]
        # # byte 3 and 4: ambient light sensor state
        # self.input_state['ambient_light_state'] = struct.unpack_from('H', msg[3:5])[0]
        #
        # # byte 5 and 6: ir sensor 0 state
        # self.input_state['ir_0_state'] = struct.unpack_from('H', msg[5:7])[0]
        #
        # # byte 7 and 8: ir sensor 1 state
        # self.input_state['ir_1_state'] = struct.unpack_from('H', msg[7:9])[0]

    def _compose_outgoing_msg(self, content):

        if self.request_type == 'basic':

            # byte 0: indicator LED on or off
            content[0] = self.output_param['indicator_led_on']

            # byte 3 to 4: blinking frequency of the indicator LED
            content[1:3] = struct.pack('H', self.output_param['indicator_led_period'])

            # byte 5: high power LED level
            content[3] = self.output_param['high_power_led_level']

            # byte 6 to 7: high power LED reflex threshold
            content[4:6] = struct.pack('H', self.output_param['high_power_led_reflex_threshold'])

            # byte 8: SMA 0 level
            content[6] = self.output_param['sma_0_level']

            # byte 9: SMA 1 level
            content[7] = self.output_param['sma_1_level']

            # byte 10: Reflex 0 level
            content[8] = self.output_param['reflex_0_level']

            # byte 11: Reflex 1 level
            content[9] = self.output_param['reflex_1_level']

        elif self.request_type == 'prgm':
            content[0] = self.output_param['program_teensy']

        elif self.request_type == 'wave':

            # byte 0 to 32: indicator led wave
            content[0:32] = self.output_param['indicator_led_wave']


    def __set_int8_array(self, input_type, raw_input):

        if raw_input is None:
            raise TypeError("The array must not be empty.")

        # extract the numbers from the string
        input = re.split('_*', raw_input)
        input = list(filter(None, input))

        for i in range(len(input)):
            try:
                input[i] = int(input[i])
            except ValueError:
                raise TypeError(input_type + " must be an array of integers separated by '_'.")
            else:
                if 0 <= input[i] < 256:
                    self.output_param[input_type] = input
                else:
                    raise TypeError("Elements of " + input_type + " must be positive and less than 255")

