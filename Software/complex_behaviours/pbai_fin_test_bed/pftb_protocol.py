"""
The communication protocol that communicates with the PBAI Fin Test Bed.
"""

__author__ = 'Matthew'

from interactive_system import SystemParameters

import struct
import re
import os


class PFTB_Triplet_Protocol(SystemParameters):

    """Communication Protocol for the PBAI Fin Test Bed (PFTB)

    This class inherits the SystemParameters.

    """

    MODE_SELF_RUNNING_TEST = 0
    MODE_MANUAL_CONTROL = 1
    MODE_CBLA = 9
    MODE_INACTIVE = 255

    NUM_FIN = 3
    NUM_LIGHT = 3

    def __init__(self):
        super(PFTB_Triplet_Protocol, self).__init__()

    def additional_config_routine(self):

        # import parameters from files
        self.output_param_config_filename = 'pftb_triplet_output_config'
        self.input_param_config_filename = 'pftb_triplet_input_config'
        self._import_param_from_file(directory=os.path.join(os.getcwd(), 'protocol_variables'))

    def parse_message_content(self, msg):

        # byte 0 and byte 63: the msg signature; can ignore

        # byte 1: reply type
        self.reply_type = msg[1]

        #=== Default reply type =====
        if self.reply_type == 0:

            # === FIN =====

            device_offset = 2
            # >>>>> byte 2 to byte 15: FIN 0
            # >>>>> byte 16 to byte 29: FIN 1
            # >>>>> byte 30 to byte 43: FIN 2

            for j in range(self.NUM_FIN):
                device_header = 'fin_%d_' % j
                byte_offset = 14*j + device_offset

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
                # byte x10 -- Cycling
                self.input_state[device_header + 'cycling'] =  msg[byte_offset+10]

            # === LIGHT ====

            device_offset += 14*self.NUM_FIN
            # >>>>> byte 2 to byte 5: Light 0
            # >>>>> byte 6 to byte 9: Light 0
            # >>>>> byte 10 to byte 13: Light 0

            for j in range(self.NUM_LIGHT):

                device_header = 'light_%d_' % j
                byte_offset = 4*j + device_offset

                # byte 2 to 4: ambient light sensor state
                self.input_state[device_header + 'als_state'] = struct.unpack_from('H', msg[byte_offset+0:byte_offset+2])[0]


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

        elif self.request_type == 'fin_high_level':

            # (14 bytes each)
            # >>>>> byte 2 to byte 15: TENTACLE 0
            # >>>>> byte 16 to byte 29: TENTACLE 1
            # >>>>> byte 30 to byte 43: TENTACLE 2

            for j in range(self.NUM_FIN):
                device_header = 'fin_%d_' % j
                byte_offset = 14*j

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

                # byte x10 --- fin motion activation
                content[byte_offset+10] = self.output_param[device_header+'arm_motion_on']

                # byte x11 --- reflex channel 1 wave type
                content[byte_offset+11] = self.output_param[device_header+'reflex_0_wave_type']
                # byte x12 --- reflex channel 2 wave type
                content[byte_offset+12] = self.output_param[device_header+'reflex_1_wave_type']

        elif self.request_type == 'fin_low_level':

            # (14 bytes each)
            # >>>>> byte 2 to byte 15: TENTACLE 0
            # >>>>> byte 16 to byte 29: TENTACLE 1
            # >>>>> byte 30 to byte 43: TENTACLE 2
            for j in range(self.NUM_FIN):
                device_header = 'fin_%d_' % j
                byte_offset = 14*j

                # byte x0 --- fin SMA wire 0
                content[byte_offset+0] = self.output_param[device_header+'sma_0_level']
                # byte x1 --- fin SMA wire 1
                content[byte_offset+1] = self.output_param[device_header+'sma_1_level']
                # byte x2 --- reflex actuation level
                content[byte_offset+2] = self.output_param[device_header+'reflex_0_level']
                # byte x4 --- reflex actuation level
                content[byte_offset+3] = self.output_param[device_header+'reflex_1_level']

        elif self.request_type == 'light':
            # (14 bytes each)
            # >>>>> byte 2 to byte 15: LIGHT 0
            # >>>>> byte 16 to byte 29: LIGHT 1
            # >>>>> byte 30 to byte 43: LIGHT 2
            for j in range(self.NUM_LIGHT):
                device_header = 'light_%d_' % j
                byte_offset = 14*j

                # byte x0 --- Ambient light sensor threshold
                content[byte_offset+0:byte_offset+2] = struct.pack('H', self.output_param[device_header+'als_threshold'])
                # byte x2 --- high-power LED cycle period
                content[byte_offset+2:byte_offset+4] = struct.pack('H', self.output_param[device_header+'cycle_period'])
                # byte x4 --- high-power LED level
                content[byte_offset+4] = self.output_param[device_header+'led_level']
                # byte x5 --- high-power led wave type
                content[byte_offset+5] = self.output_param[device_header+'led_wave_type']

        elif self.request_type == 'composite_1':

            # === FIN ===
            device_offset = 0
            # >>>>> byte 2 to byte 9 : FIN 0
            # >>>>> byte 10 to byte 17 : FIN 1
            # >>>>> byte 18 to byte 25 : FIN 2
            for j in range(self.NUM_FIN):
                device_header = 'fin_%d_' % j
                byte_offset = 8*j + device_offset

                # byte x0 --- fin motion activation
                content[byte_offset] = self.output_param[device_header + 'arm_motion_on']
                # byte x1 --- reflex actuation level
                content[byte_offset+1] = self.output_param[device_header+'reflex_0_level']
                # byte x2 --- reflex actuation level
                content[byte_offset+2] = self.output_param[device_header+'reflex_1_level']
                # byte x3 --- fin SMA wire 0
                content[byte_offset+3] = self.output_param[device_header+'sma_0_level']
                # byte x4 --- fin SMA wire 1
                content[byte_offset+4] = self.output_param[device_header+'sma_1_level']

            # === LIGHT ===
            device_offset += 8*self.NUM_FIN + device_offset
            # (4 bytes each)
            # >>>>> byte 26 to byte 29: LIGHT 0
            # >>>>> byte 30 to byte 33: LIGHT 1
            # >>>>> byte 34 to byte 37: LIGHT 2
            for j in range(self.NUM_LIGHT):
                device_header = 'light_%d_' % j
                byte_offset = 4*j + device_offset

                # byte x0 --- high-power LED level
                content[byte_offset] = self.output_param[device_header + 'led_level']

        elif self.request_type == 'read_only':
            pass

            pass