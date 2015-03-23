from node import *

from time import sleep

class Tentacle(Node):

    def __init__(self, messenger: Messenger.Messenger, teensy_name: str, ir_0: Var, ir_1: Var, frond: Var):

        if not isinstance(teensy_name, str):
            raise TypeError('teensy_name must be a string!')

        self.teensy_name = teensy_name


        super(Tentacle, self).__init__(messenger)

        # defining the input variables
        self.in_var['ir_sensor_0'] = ir_0
        self.in_var['ir_sensor_1'] = ir_1

        # defining the output variables
        self.out_var['tentacle_out'] = frond
        self.out_var['reflex_out_0'] = Var(0)
        self.out_var['reflex_out_1'] = Var(0)




    def run(self):

        while True:
            if self.in_var['ir_sensor_1'].val > 1000 and self.out_var['tentacle_out'].val == 0:
                self.out_var['tentacle_out'].val = 3
                self.out_var['reflex_out_0'].val = 100
                self.out_var['reflex_out_1'].val = 100


            elif self.in_var['ir_sensor_1'].val <= 1000 and self.out_var['tentacle_out'].val > 0:

                self.out_var['tentacle_out'].val = 0
                self.out_var['reflex_out_0'].val = 0
                self.out_var['reflex_out_1'].val = 0

            sleep(self.messenger.estimated_msg_period*2)