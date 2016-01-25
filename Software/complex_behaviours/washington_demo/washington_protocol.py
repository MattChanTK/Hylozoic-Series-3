__author__ = 'Matthew'

from interactive_system import SystemParameters

import struct
import re
import os

class WashingtonSoundProtocol(SystemParameters):

    MODE_SELF_RUNNING_TEST = 0
    MODE_MANUAL_CONTROL = 1
    MODE_INACTIVE = 255

    NUM_SOUND = 6

    def __init__(self):
        super(WashingtonSoundProtocol, self).__init__()

    def additional_config_routine(self):

        # import parameters from files
        self.output_param_config_filename = 'washington_sound_node_output_config'
        self.input_param_config_filename = 'washington_sound_node_input_config'
        self._import_param_from_file(directory=os.path.join(os.getcwd(), 'protocol_variables'))

    def parse_message_content(self, msg):

        # byte 0 and byte 63: the msg signature; can ignore

        # byte 1: reply type
        self.reply_type = msg[1]

        # === Default reply type =====
        if self.reply_type == 0:

            device_offset = 2
            # >>>>> byte 2 to byte 9: Sound 0
            # >>>>> byte 10 to byte 17: Sound 1
            # >>>>> byte 18 to byte 25: Sound 2
            # >>>>> byte 26 to byte 33: Sound 3
            # >>>>> byte 34 to byte 41: Sound 4
            # >>>>> byte 42 to byte 49: Sound 5
            for j in range(self.NUM_SOUND):
                device_header = 'sound_%d_' % j
                byte_offset = 8*j + device_offset

                # byte x0 --- IR 0 sensor state
                self.input_state[device_header + 'analog_0_state'] = struct.unpack_from('H', msg[byte_offset+0:byte_offset+2])[0]
                # byte x2 --- IR 1 sensor state
                self.input_state[device_header + 'analog_1_state'] = struct.unpack_from('H', msg[byte_offset+2:byte_offset+4])[0]
                # byte x4 --- IR 2 sensor state
                self.input_state[device_header + 'analog_2_state'] = struct.unpack_from('H', msg[byte_offset+4:byte_offset+6])[0]

    def _compose_outgoing_msg(self, content):

        # NOTE: contents is two bytes offset for the header
        # max 60 bytes in content

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

        elif self.request_type == 'prgm':
            content[0] = self.output_param['program_teensy']

        elif self.request_type == 'low_level':

            device_offset = 0

            # ==== Fins ====
            # (8 bytes each)
            # >>>>> byte 2 to byte 9: Sound 0
            # >>>>> byte 10 to byte 17: Sound 1
            # >>>>> byte 18 to byte 25: Sound 2
            # >>>>> byte 26 to byte 33: Sound 3
            # >>>>> byte 34 to byte 41: Sound 4
            # >>>>> byte 42 to byte 49: Sound 5
            for j in range(self.NUM_SOUND):
                device_header = 'sound_%d_' % j
                byte_offset = 8*j + device_offset

                # byte x0 --- Sound PWM 0 output
                content[byte_offset+0] = self.output_param[device_header+'output_0_level']
                # byte x1 --- Sound PWM 1 output
                content[byte_offset+1] = self.output_param[device_header+'output_1_level']
                # byte x2 --- Sound Type Left
                content[byte_offset+2] = self.output_param[device_header+'sound_left_type']
                # byte x3 --- Sound Type Right
                content[byte_offset+3] = self.output_param[device_header+'sound_right_type']
                # byte x4 --- Sound Volume Left
                content[byte_offset+4] = self.output_param[device_header+'sound_left_volume']
                # byte x5 --- Sound Volume Right
                content[byte_offset+5] = self.output_param[device_header+'sound_right_volume']
                # byte x6 --- Sound Block Left
                content[byte_offset+6] = self.output_param[device_header+'sound_left_block']
                # byte x7 --- Sound Block Right
                content[byte_offset+7] = self.output_param[device_header+'sound_right_block']

        elif self.request_type == 'read_only':
            pass