import SystemParameters as SysParam
from SystemParameters import enum_dict
import struct

class SimplifiedTestUnit(SysParam.SystemParameters):

    input_param_config_filename = 'param_config_input_simplified'
    output_param_config_filename = 'param_config_output_simplified'

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

    def __compose_outgoing_msg(self, content):

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
