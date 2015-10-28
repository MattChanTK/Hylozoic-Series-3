__author__ = 'Matthew'

from interactive_system import SystemParameters

import struct
import re
import os


class WashingtonCricketProtocol(SystemParameters):

    MODE_SELF_RUNNING_TEST = 0
    MODE_MANUAL_CONTROL = 1
    MODE_INACTIVE = 255

    def __init__(self):
        super(WashingtonCricketProtocol, self).__init__()

    def additional_config_routine(self):

        # import parameters from files
        self.output_param_config_filename = 'washington_cricket_node_output_config'
        self.input_param_config_filename = 'washington_cricket_node_input_config'
        self._import_param_from_file(directory=os.path.join(os.getcwd(), 'protocol_variables'))

    def parse_message_content(self, msg):

        # byte 0 and byte 63: the msg signature; can ignore

        # byte 1: reply type
        self.reply_type = msg[1]

        #=== Default reply type =====
        if self.reply_type == 0:

            # (8 bytes each)
            # >>>>> byte 2 to byte 9: Cricket 0
            # >>>>> byte 10 to byte 17: Cricket 1
            # >>>>> byte 18 to byte 25: Cricket 2
            for j in range(3):
                device_header = 'cricket_%d_' % j
                byte_offset = 8*j + 2

                # byte x0 --- IR 0 sensor state
                self.input_state[device_header + 'ir_state'] = struct.unpack_from('H', msg[byte_offset+0:byte_offset+2])[0]

            # (8 bytes each)
            # >>>>> byte 26 to byte 33: Light 0
            for j in range(1):
                device_header = 'light_%d_' % j
                byte_offset = 8*j + 26

                # byte x0 --- IR 0 sensor state
                self.input_state[device_header + 'ir_0_state'] = struct.unpack_from('H', msg[byte_offset+0:byte_offset+2])[0]
                # byte x1 --- IR 1 sensor state
                self.input_state[device_header + 'ir_1_state'] = struct.unpack_from('H', msg[byte_offset+0:byte_offset+2])[0]



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

            # ==== Crickets ====
            # (8 bytes each)
            # >>>>> byte 2 to byte 9: Cricket 0
            # >>>>> byte 10 to byte 17: Cricket 1
            # >>>>> byte 18 to byte 25: Cricket 2

            for j in range(3):
                device_header = 'cricket_%d_' % j
                byte_offset = 8*j

                # byte x0 --- Cricket actuator 0 output
                content[byte_offset+0] = self.output_param[device_header+'output_0_level']
                # byte x1 --- Cricket actuator 1 output
                content[byte_offset+1] = self.output_param[device_header+'output_1_level']
                # byte x2 --- Cricket actuator 2 output
                content[byte_offset+2] = self.output_param[device_header+'output_2_level']
                # byte x3--- Cricket actuator 3 output
                content[byte_offset+3] = self.output_param[device_header+'output_3_level']

            # ==== Lights ====
            # (8 bytes each)
            # >>>>> byte 26 to byte 33: Light 0

            for j in range(1):
                device_header = 'light_%d_' % j
                byte_offset = 8*j + 24

                # byte x0 --- Light LED 0 output
                content[byte_offset+0] = self.output_param[device_header+'led_0_level']
                # byte x1 --- Light LED 1 output
                content[byte_offset+1] = self.output_param[device_header+'led_1_level']
                # byte x2 --- Light LED 2 output
                content[byte_offset+2] = self.output_param[device_header+'led_2_level']
                # byte x3 --- Light LED 3 output
                content[byte_offset+3] = self.output_param[device_header+'led_3_level']

        elif self.request_type == 'read_only':
            pass

class WashingtonFinCricketProtocol(SystemParameters):

    pass

class WashingtonFinProtocol(SystemParameters):

    pass

class WashingtonSoundProtocol(SystemParameters):

    pass
