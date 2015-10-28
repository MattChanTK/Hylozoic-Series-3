__author__ = 'Matthew'

from interactive_system import SystemParameters

import struct
import re
import os


class WashingtonCricketProtocol(SystemParameters):

    MODE_SELF_RUNNING_TEST = 0
    MODE_MANUAL_CONTROL = 1
    MODE_INACTIVE = 255

    NUM_CRICKET = 3
    NUM_LIGHT = 1

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
            for j in range(self.NUM_CRICKET):
                device_header = 'cricket_%d_' % j
                byte_offset = 8*j + 2

                # byte x0 --- IR 0 sensor state
                self.input_state[device_header + 'ir_state'] = struct.unpack_from('H', msg[byte_offset+0:byte_offset+2])[0]

            # (8 bytes each)
            # >>>>> byte 26 to byte 33: Light 0
            for j in range(self.NUM_LIGHT):
                device_header = 'light_%d_' % j
                byte_offset = 8*j + 26

                # byte x0 --- IR 0 sensor state
                self.input_state[device_header + 'ir_0_state'] = struct.unpack_from('H', msg[byte_offset+0:byte_offset+2])[0]
                # byte x1 --- IR 1 sensor state
                self.input_state[device_header + 'ir_1_state'] = struct.unpack_from('H', msg[byte_offset+2:byte_offset+4])[0]



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

            for j in range(self.NUM_CRICKET):
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

            for j in range(self.NUM_LIGHT):
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
    MODE_SELF_RUNNING_TEST = 0
    MODE_MANUAL_CONTROL = 1
    MODE_INACTIVE = 255

    NUM_CRICKET = 3
    NUM_FIN = 3

    def __init__(self):
        super(WashingtonFinCricketProtocol, self).__init__()

    def additional_config_routine(self):

        # import parameters from files
        self.output_param_config_filename = 'washington_fin_cricket_node_output_config'
        self.input_param_config_filename = 'washington_fin_cricket_node_input_config'
        self._import_param_from_file(directory=os.path.join(os.getcwd(), 'protocol_variables'))

    def parse_message_content(self, msg):

        # byte 0 and byte 63: the msg signature; can ignore

        # byte 1: reply type
        self.reply_type = msg[1]

        #=== Default reply type =====
        if self.reply_type == 0:

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

            device_offset += 14*self.NUM_FIN

            # (4 bytes each)
            # >>>>> byte 44 to byte 47: Cricket 0
            # >>>>> byte 48 to byte 51: Cricket 1
            # >>>>> byte 52 to byte 55: Cricket 2

            for j in range(self.NUM_CRICKET):
                device_header = 'cricket_%d_' % j
                byte_offset = 4*j + device_offset

                # byte x0 --- IR 0 sensor state
                self.input_state[device_header + 'ir_state'] = struct.unpack_from('H', msg[byte_offset+0:byte_offset+2])[0]

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
            # >>>>> byte 2 to byte 9: Fin 0
            # >>>>> byte 10 to byte 17: Fin 1
            # >>>>> byte 18 to byte 25: Fin 2
            for j in range(self.NUM_FIN):
                device_header = 'fin_%d_' % j
                byte_offset = 8*j + device_offset

                # byte x0 --- Fin SMA 0 output
                content[byte_offset+0] = self.output_param[device_header+'sma_0_level']
                # byte x1 --- Fin SMA 1 output
                content[byte_offset+1] = self.output_param[device_header+'sma_1_level']
                # byte x2 --- Fin reflex 0 output
                content[byte_offset+2] = self.output_param[device_header+'reflex_0_level']
                # byte x3 --- Fin reflex 1 output
                content[byte_offset+3] = self.output_param[device_header+'reflex_1_level']

            device_offset += 8*self.NUM_FIN

            # ==== Crickets ====
            # (8 bytes each)
            # >>>>> byte 2 to byte 9: Cricket 0
            # >>>>> byte 10 to byte 17: Cricket 1
            # >>>>> byte 18 to byte 25: Cricket 2

            for j in range(self.NUM_CRICKET):
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

        elif self.request_type == 'read_only':
            pass


class WashingtonFinProtocol(SystemParameters):
    MODE_SELF_RUNNING_TEST = 0
    MODE_MANUAL_CONTROL = 1
    MODE_INACTIVE = 255

    NUM_FIN = 3

    def __init__(self):
        super(WashingtonFinProtocol, self).__init__()

    def additional_config_routine(self):

        # import parameters from files
        self.output_param_config_filename = 'washington_fin_node_output_config'
        self.input_param_config_filename = 'washington_fin_node_input_config'
        self._import_param_from_file(directory=os.path.join(os.getcwd(), 'protocol_variables'))


    def parse_message_content(self, msg):

        # byte 0 and byte 63: the msg signature; can ignore

        # byte 1: reply type
        self.reply_type = msg[1]

        # === Default reply type =====
        if self.reply_type == 0:

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

            device_offset += 14*self.NUM_FIN

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
            # >>>>> byte 2 to byte 9: Fin 0
            # >>>>> byte 10 to byte 17: Fin 1
            # >>>>> byte 18 to byte 25: Fin 2
            for j in range(self.NUM_FIN):
                device_header = 'fin_%d_' % j
                byte_offset = 8*j + device_offset

                # byte x0 --- Fin SMA 0 output
                content[byte_offset+0] = self.output_param[device_header+'sma_0_level']
                # byte x1 --- Fin SMA 1 output
                content[byte_offset+1] = self.output_param[device_header+'sma_1_level']
                # byte x2 --- Fin reflex 0 output
                content[byte_offset+2] = self.output_param[device_header+'reflex_0_level']
                # byte x3 --- Fin reflex 1 output
                content[byte_offset+3] = self.output_param[device_header+'reflex_1_level']

            device_offset += 8*self.NUM_FIN

        elif self.request_type == 'read_only':
            pass

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
                content[byte_offset+5] = self.output_param[device_header+'sound_right_right']
                # byte x6 --- Sound Block Left
                content[byte_offset+6] = self.output_param[device_header+'sound_left_block']
                # byte x7 --- Sound Block Right
                content[byte_offset+7] = self.output_param[device_header+'sound_right_block']

        elif self.request_type == 'read_only':
            pass