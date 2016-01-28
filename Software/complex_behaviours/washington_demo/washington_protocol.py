__author__ = 'Matthew'

from interactive_system import SystemParameters

import struct
import re
import os

class WashingtonSoundModuleProtocol(SystemParameters):

    MODE_SELF_RUNNING_TEST = 0
    MODE_MANUAL_CONTROL = 1
    MODE_CBLA = 2
    MODE_INACTIVE = 255

    def __init__(self):
        super(WashingtonSoundModuleProtocol, self).__init__()

    def additional_config_routine(self):

        # import parameters from files
        self.output_param_config_filename = 'washington_sound_module_output_config'
        self.input_param_config_filename = 'washington_sound_module_input_config'
        self._import_param_from_file(directory=os.path.join(os.getcwd(), 'protocol_variables'))

    def parse_message_content(self, msg):

        # byte 0 and byte 63: the msg signature; can ignore

        # byte 1: reply type
        self.reply_type = msg[1]

        # === Default reply type =====
        if self.reply_type == 0:

            byte_offset = 2

            # byte x0 --- mic
            self.input_state['mic_0_max_freq'] = struct.unpack_from('H', msg[byte_offset+0:byte_offset+2])[0]
            # byte x2 --- IR 1 sensor state
            self.input_state['mic_1_max_freq'] = struct.unpack_from('H', msg[byte_offset+2:byte_offset+4])[0]



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

        elif self.request_type == 'freq_ctrl':

            # byte x0-x1 --- Speaker 0 frequency output
            content[0:2] = struct.pack('H', self.output_param['speaker_0_freq'])

            # byte x2-x3 --- Speaker 1 frequency output
            content[2:4] = struct.pack('H', self.output_param['speaker_1_freq'])


        elif self.request_type == 'read_only':
            pass