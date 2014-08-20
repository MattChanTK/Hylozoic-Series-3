import SystemParameters as SysParam
from SystemParameters import enum_dict
import struct

class SimplifiedTestUnit(SysParam.SystemParameters):

    def __init__(self):

        #==== outputs ====
        self.output_param = dict()
        # ---defaults---
        self.output_param['indicator_led_on'] = True
        self.output_param['indicator_led_period'] = 100
        self.output_param['high_power_led_level'] = 5
        self.output_param['high_power_led_reflex_threshold'] = 100
        self.output_param['sma_0_level'] = 100
        self.output_param['sma_1_level'] = 100
        self.output_param['reflex_0_level'] = 100
        self.output_param['reflex_1_level'] = 100

        self.bool_var_list = ('indicator_led_on',)
        self.int8_var_list = ('high_power_led_level','sma_0_level', 'sma_1_level',
                              'reflex_0_level', 'reflex_1_level')
        self.int16_var_list = ('indicator_led_period', 'high_power_led_reflex_threshold')


        #==== inputs ====
        self.input_state = dict()
        # ---defaults---
        self.input_state['analog_0_state'] = 0
        self.input_state['ambient_light_state'] = 0
        self.input_state['ir_0_state'] = 0
        self.input_state['ir_1_state'] = 0

        #=== list of behaviours for selection ====
        self.behaviour_type = enum_dict('INTERACTIVE', 'AUTO')
        self.behaviour = self.behaviour_type['INTERACTIVE']

    def parse_message_content(self, msg):

        # byte 0 and byte 63: the msg signature; can ignore

        # byte 1 and 2: analog 0 state
        self.input_state['analog_0_state'] = struct.unpack_from('H', msg[1:3])[0]

        # byte 3 and 4: ambient light sensor state
        self.input_state['ambient_light_state'] = struct.unpack_from('H', msg[3:5])[0]

        # byte 5 and 6: ir sensor 0 state
        self.input_state['ir_0_state'] = struct.unpack_from('H', msg[5:7])[0]

        # byte 7 and 8: ir sensor 1 state
        self.input_state['ir_1_state'] = struct.unpack_from('H', msg[7:9])[0]

    def compose_message_content(self):

        # create an 64 bytes of zeros
        msg = bytearray(chr(0)*SysParam.SystemParameters.msg_length, 'utf-8')

        # byte 0 and byte 63: the msg signature; left as 0 for now

        # byte 1: type of behaviour
        msg[1] = self.behaviour

        # byte 2: indicator LED on or off
        msg[2] = self.output_param['indicator_led_on']

        # byte 3 to 4: blinking frequency of the indicator LED
        msg[3:5] = struct.pack('H', self.output_param['indicator_led_period'])

        # byte 5: high power LED level
        msg[5] = self.output_param['high_power_led_level']

        # byte 6 to 7: high power LED reflex threshold
        msg[6:8] = struct.pack('H', self.output_param['high_power_led_reflex_threshold'])

        # byte 8: SMA 0 level
        msg[8] = self.output_param['sma_0_level']

        # byte 9: SMA 1 level
        msg[9] = self.output_param['sma_1_level']

        # byte 10: Reflex 0 level
        msg[10] = self.output_param['reflex_0_level']

        # byte 11: Reflex 1 level
        msg[11] = self.output_param['reflex_1_level']

        return msg



class FullTestUnit(SysParam.SystemParameters):

    def __init__(self):

        #==== outputs ====
        self.output_param = dict()
        # ---defaults---
        self.output_param['indicator_led_on'] = False
        self.output_param['indicator_led_period'] = 0
        self.output_param['high_power_led_on'] = False
        self.output_param['high_power_led_level'] = 0
        self.output_param['vb_trigger_level'] = 300
        self.output_param['sma_0_on'] = False
        self.output_param['sma_1_on'] = False
        self.output_param['sma_2_on'] = False
        self.output_param['sma_3_on'] = False
        self.output_param['sma_4_on'] = False
        self.output_param['sma_5_on'] = False
        self.output_param['sound_type'] = 0

        self.bool_var_list = ('indicator_led_on', 'high_power_led_on',
                                'sma_0_on', 'sma_1_on', 'sma_2_on',
                                'sma_3_on', 'sma_4_on', 'sma_5_on')
        self.int8_var_list =('high_power_led_level', 'vb_trigger_level',
                                'sound_type')
        self.int16_var_list = ('indicator_led_period',
                                'sma_0_wait_time',  'sma_1_wait_time',  'sma_2_wait_time',
                                'sma_3_wait_time',  'sma_4_wait_time',  'sma_5_wait_time')


        #==== inputs ====
        self.input_state = dict()
        # ---defaults---
        self.input_state['analog_0_state'] = 0
        self.input_state['ir_stern_range'] = 0
        self.input_state['ir_tip_range'] = 0
        self.input_state['ir_acoustic_range'] = 0
        self.input_state['sound_detect_0'] = 0
        self.input_state['sound_detect_1'] = 0
        self.input_state['ambient_light_state'] = 0
        self.input_state['vb_voltage'] = 0

        #=== list of behaviours for selection ====
        self.behaviour_type = enum_dict('INTERACTIVE', 'AUTO')
        self.behaviour = self.behaviour_type['INTERACTIVE']

    def parse_message_content(self, msg):

        # byte 0 and byte 63: the msg signature; can ignore

        # byte 1: analog 0 state
        self.input_state['analog_0_state'] = struct.unpack_from('H', msg[1:3])[0]

    def compose_message_content(self):

        # create an 64 bytes of zeros
        msg = bytearray(chr(0)*SysParam.SystemParameters.msg_length, 'utf-8')

        # byte 0 and byte 63: the msg signature; left as 0 for now

        # byte 1: type of behaviour
        msg[1] = self.behaviour

        # byte 2: indicator LED on or off
        msg[2] = self.output_param['indicator_led_on']

        # byte 3 to 4: blinking frequency of the indicator LED
        msg[3:5] = struct.pack('H', self.output_param['indicator_led_period'])

        # byte 5: SMA 0 cycle on
        msg[5] = self.output_param['sma_0_on']

        # byte 5: SMA 0 cycle on
        msg[5] = self.output_param['sma_0_on']



        return msg

