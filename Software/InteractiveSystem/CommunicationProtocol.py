from cgi import maxlen
import SystemParameters as SysParam
import struct
import re
from collections import deque
import math



class CBLATestBed(SysParam.SystemParameters):
    def __init__(self):
        super(CBLATestBed, self).__init__()

        # internal variable for high-level input features
        for j in range(4):
            device_header = 'tentacle_%d_' % j
            self.input_state[device_header + "acc_waveform"] = deque(maxlen=2000)


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

			# >>>>> byte 50: TENTACLE 0
			# >>>>> byte 51: TENTACLE 1
			# >>>>> byte 52: TENTACLE 2
			# >>>>> byte 53: TENTACLE 3

            for j in range(4):
                device_header = 'tentacle_%d_' % j
                byte_offset = j + 50

                self.input_state[device_header + 'cycling'] = msg[byte_offset]


            self.__store_input_states()

            if self.output_param['derive_inputs'] == True:
                self.output_param['derive_inputs'] = False
                self.__derive_input_states()

    def __store_input_states(self):

        for j in range(4):
            device_header = 'tentacle_%d_' % j
            acc_state = (self.input_state[device_header + 'acc_x_state'],
                         self.input_state[device_header + 'acc_y_state'],
                         self.input_state[device_header + 'acc_z_state'])

            self.input_state[device_header + "acc_waveform"].append(acc_state)

    def __derive_input_states(self):
        # import pickle

        # internal variable for high-level input features
        for j in range(4):
            device_header = 'tentacle_%d_' % j

            waveform_zipped = list(zip(*self.input_state[device_header + "acc_waveform"]))
            # with open(str(j) + '_acc_reading.pkl', 'wb') as output:
            #     pickle.dump(waveform_zipped , output, pickle.HIGHEST_PROTOCOL)
            window = self.output_param['acc_diff_window']
            gap = self.output_param['acc_diff_gap']
            self.input_state[device_header + "wave_diff_x"] = sum(waveform_zipped[0][-window:]) - sum(waveform_zipped[0][-(window + gap):-gap])
            self.input_state[device_header + "wave_diff_y"] = sum(waveform_zipped[1][-window:]) - sum(waveform_zipped[1][-(window + gap):-gap])
            self.input_state[device_header + "wave_diff_z"] = sum(waveform_zipped[2][-window:]) - sum(waveform_zipped[2][-(window + gap):-gap])

            window = self.output_param['acc_mean_window']
            self.input_state[device_header + "wave_mean_x"] = sum(waveform_zipped[0][-window:])/window
            self.input_state[device_header + "wave_mean_y"] = sum(waveform_zipped[1][-window:])/window
            self.input_state[device_header + "wave_mean_z"] = sum(waveform_zipped[2][-window:])/window

            #print(waveform_zipped[0])




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
                content[1:3] = struct.pack('H', self.output_param['indicator_led_period'])

                # byte x0 --- IR sensor 0 activation threshold
                content[byte_offset+0:byte_offset+2] = struct.pack('H', self.output_param[device_header+'ir_0_threshold'])
                # byte x2 --- IR sensor 1 activation threshold
                content[byte_offset+2:byte_offset+4] = struct.pack('H', self.output_param[device_header+'ir_1_threshold'])

                # byte x4 --- ON period of Tentacle arm activation
                content[byte_offset+4] = self.output_param[device_header+'arm_cycle_on_period']
                # byte x5 --- OFF period of Tentacle arm activation
                content[byte_offset+5] = self.output_param[device_header+'arm_cycle_off_period']

                # byte x6 --- Reflex channel 1 period
                content[byte_offset+6:byte_offset+8] = struct.pack('H', self.output_param[device_header+'arm_reflex_0_period'])
                # byte x8 --- Reflex channel 2 period
                content[byte_offset+8:byte_offset+10] = struct.pack('H', self.output_param[device_header+'arm_reflex_1_period'])

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
            for j in range(2):
                device_header = 'protocell_%d_' % j
                byte_offset = 15*j

                # byte x0 --- Ambient light sensor threshold
                content[byte_offset+0:byte_offset+2] = struct.pack('H', self.output_param[device_header+'als_threshold'])
                # byte x2 --- high-power LED cycle period
                content[byte_offset+2:byte_offset+4] = struct.pack('H', self.output_param[device_header+'cycle_period'])
                # byte x4 --- high-power LED level
                content[byte_offset+4] = self.output_param[device_header+'led_level']
                # byte x5 --- high-power led wave type
                content[byte_offset+5] = self.output_param[device_header+'led_wave_type']

        elif self.request_type == 'prgm':
            content[0] = self.output_param['program_teensy']

        elif self.request_type == 'wave_change':
            # byte 2: wave type
            content[0] = self.output_param['wave_type']
            # byte 12 to 43: indicator led wave
            content[10:42] = self.output_param['new_wave']

        elif self.request_type == 'read_only':
            pass

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

