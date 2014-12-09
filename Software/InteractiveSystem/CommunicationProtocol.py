import SystemParameters as SysParam
import struct
import re



class CBLATestBed(SysParam.SystemParameters):
    def __init__(self):
        super(CBLATestBed, self).__init__()

    def additional_config_routine(self):

        self.var_encode_func["int8s"] = self.__set_int8_array

        # import parameters from files
        self.output_param_config_filename = 'CBLATestBed_output_config'
        self.input_param_config_filename = 'CBLATestBed_input_config'

        self._import_param_from_file()

    def parse_message_content(self, msg):

        # byte 0 and byte 63: the msg signature; can ignore

        # byte 1: reply type
        self.reply_type = msg[1]

        #=== Default reply type =====
        if self.reply_type == 0:

            # >>>>> byte 2 to byte 9: Protocell 0 and 1

            # byte 2 to 3: ambient light sensor 0 state
            self.input_state['protocell_0_als_state'] = struct.unpack_from('H', msg[2:4])[0]

            # byte 4 to 5: ambient light sensor 1 state
            self.input_state['protocell_1_als_state'] = struct.unpack_from('H', msg[4:6])[0]


            # >>>>> byte 10 to byte 19: TENTACLE 0
            # >>>>> byte 20 to byte 29: TENTACLE 1
            # >>>>> byte 30 to byte 39: TENTACLE 2
            # >>>>> byte 40 to byte 49: TENTACLE 3
            for j in range(4):
                device_header = 'tentacle_%d_' % j
                byte_offset = 10*j + 10

                # byte x0 --- IR 0 sensor state
                self.input_state[device_header + 'ir_0_state'] = struct.unpack_from('H', msg[byte_offset+0:byte_offset+2])[0]
                # byte x2 --- IR 1 sensor state
                self.input_state[device_header + 'ir_1_state'] = struct.unpack_from('H', msg[byte_offset+2:byte_offset+4])[0]
                # byte x4 -- Accelerometer state (x-axis)
                self.input_state[device_header + 'acc_x_state'] = struct.unpack_from('h', msg[byte_offset+4:byte_offset+6])[0]
                # byte x6 -- Accelerometer state (y-axis)
                self.input_state[device_header + 'acc_y_state'] = struct.unpack_from('h', msg[byte_offset+6:byte_offset+8])[0]
                # byte x8 -- Accelerometer state (z-axis)
                self.input_state[device_header + 'acc_z_state'] = struct.unpack_from('h', msg[byte_offset+8:byte_offset+10])[0]


    def _compose_outgoing_msg(self, content):

        # NOTE: contents is two bytes offset for the header
        # max 61 bytes in content

        if self.request_type == 'basic':

            # >>>>>> byte 2 to 9: ON-BOARD <<<<<<<
            # byte 2: indicator LED on or off
            content[0] = self.output_param['indicator_led_on']

            # byte 3 to 4: blinking frequency of the indicator LED
            content[1:3] = struct.pack('H', self.output_param['indicator_led_period'])

            # >>>> byte 10: CONFIG VARIABLES <<<<<
            # byte 10: operation mode
            content[8] = self.output_param['operation_mode']

            # byte 11: reply message type request
            content[9] = self.output_param['reply_type_request']

            # >>>>> byte 30 to byte 39
            content[28] = self.output_param['neighbour_activation_state']

        elif self.request_type == 'tentacle_high_level':

            # (15 bytes each)
            # >>>>> byte 2 to byte 16: TENTACLE 0
            # >>>>> byte 17 to byte 31: TENTACLE 1
            # >>>>> byte 32 to byte 46: TENTACLE 2
            # >>>>> byte 47 to byte 61: TENTACLE 3
            for j in range(4):
                device_header = 'tentacle_%d_' % j
                byte_offset = 15*j

                # byte x0 --- IR sensor 0 activation threshold
                content[byte_offset+0] = self.output_param[device_header+'ir_0_threshold']
                # byte x2 --- IR sensor 1 activation threshold
                content[byte_offset+2] = self.output_param[device_header+'ir_1_threshold']

                # byte x4 --- ON period of Tentacle arm activation
                content[byte_offset+4] = self.output_param[device_header+'arm_cycle_on_threshold']
                # byte x5 --- OFF period of Tentacle arm activation
                content[byte_offset+5] = self.output_param[device_header+'arm_cycle_off_threshold']

                # byte x6 --- Reflex channel 1 period
                content[byte_offset+6] = self.output_param[device_header+'arm_cycle_reflex_0_period']
                # byte x8 --- Reflex channel 2 period
                content[byte_offset+8] = self.output_param[device_header+'arm_cycle_reflex_1_period']

                # byte x10 --- tentacle motion activation
                content[byte_offset+10] = self.output_param[device_header+'arm_motion_on']

                # byte x11 --- reflex channel 1 wave type
                content[byte_offset+11] = self.output_param[device_header+'reflex_0_wave_type']
                # byte x12 --- reflex channel 2 wave type
                content[byte_offset+12] = self.output_param[device_header+'reflex_1_wave_type']

        elif self.request_type == 'tentacle_low_level':
            # (15 bytes each)
            # >>>>> byte 2 to byte 16: TENTACLE 0
            # >>>>> byte 17 to byte 31: TENTACLE 1
            # >>>>> byte 32 to byte 46: TENTACLE 2
            # >>>>> byte 47 to byte 61: TENTACLE 3
            for j in range(4):
                device_header = 'tentacle_%d_' % j
                byte_offset = 15*j

                # byte x0 --- tentacle SMA wire 0
                content[byte_offset+0] = self.output_param[device_header+'sma_0_level']
                # byte x1 --- tentacle SMA wire 1
                content[byte_offset+1] = self.output_param[device_header+'sma_1_level']
                # byte x2 --- reflex actuation level
                content[byte_offset+2] = self.output_param[device_header+'reflex_0_level']
                # byte x4 --- reflex actuation level
                content[byte_offset+3] = self.output_param[device_header+'reflex_1_level']

        elif self.request_type == 'protocell':
            # (15 bytes each)
            # >>>>> byte 2 to byte 16: PROTOCELL 0
            # >>>>> byte 17 to byte 31: PROTOCELL 1
            for j in range(4):
                device_header = 'protocell_%d_' % j
                byte_offset = 15*j

                # byte x0 --- Ambient light sensor threshold
                content[byte_offset+0] = self.output_param[device_header+'als_threshold']
                # byte x2 --- high-power LED cycle period
                content[byte_offset+2] = self.output_param[device_header+'cycle_period']
                # byte x4 --- high-power LED level
                content[byte_offset+4] = self.output_param[device_header+'led_level']
                # byte x5 --- high-power led wave type
                content[byte_offset+5] = self.output_param[device_header+'led_wave_type']

        elif self.request_type == 'prgm':
            content[0] = self.output_param['program_teensy']

        # elif self.request_type == 'wave':
        #
        #     # byte 0 to 32: indicator led wave
        #     content[0:32] = self.output_param['indicator_led_wave']

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


class SimplifiedTestUnit(SysParam.SystemParameters):

    def __init__(self):
        super(SimplifiedTestUnit, self).__init__()

    def additional_config_routine(self):

        self.request_type_ids = enum_dict('basic', 'prgm', 'wave')
        self.var_encode_func["int8s"] = self.__set_int8_array

        # import parameters from files
        self.output_param_config_filename = 'simplified_output_config'
        self.input_param_config_filename = 'simplified_input_config'

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

