import InteractiveCmd
from InteractiveCmd import command_object

from copy import copy
from time import clock
from time import sleep
import math

test_start_time = clock()
class Hardcoded_Behaviours(InteractiveCmd.InteractiveCmd):

    def run(self):
        pass


class Test_Behaviours(InteractiveCmd.InteractiveCmd):

    def run(self):

        teensy_names = self.teensy_manager.get_teensy_name_list()

        indicator_led_period = dict()
        indicator_led_on = dict()
        for teensy_name in teensy_names:
            indicator_led_period[teensy_name] = 0
            indicator_led_on[teensy_name] = 1

        loop = 0
        crash_count = 0
        num_loop = 10000
        while loop < num_loop:
            start_time = clock()

            if self.teensy_manager.get_num_teensy_thread() == 0:
                return

            for teensy_name in list(teensy_names):

                Teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)

                # check if the thread is still alive
                if Teensy_thread is not None:

                    #=== "Basic" commands"
                    cmd_obj = command_object(teensy_name, 'basic')


                    cmd_obj.add_param_change('indicator_led_on',  indicator_led_on[teensy_name])
                    cmd_obj.add_param_change('indicator_led_period', int(indicator_led_period[teensy_name])*50)


                    self.enter_command(cmd_obj)

                   # #=== change wave command====
                   #  cmd_obj = command_object(teensy_name, 'wave')
                   #
                   #  wave = ""
                   #  pt = 0
                   #  for i in range(32):
                   #      pt += int(255/32)
                   #      wave += (str(pt) + '_')
                   #
                   #  cmd_obj.add_param_change('indicator_led_wave', wave)
                   #  self.enter_command(cmd_obj)


            self.send_commands()

            all_input_states = self.get_input_states(teensy_names, ('all', ))
            for teensy_name, input_states in all_input_states.items():
                sample = input_states[0]
                is_new_update = input_states[1]
                #
                # if is_new_update:
                #     if sample['analog_0_state'] > 900:
                #         indicator_led_on[teensy_name] = 0
                #     else:
                #         indicator_led_on[teensy_name] = 1

                # print("[", teensy_name, "]")
                # print("Tentacle 0", end=" ---\t")
                # print("IR (", sample['tentacle_0_ir_0_state'], ", ", sample['tentacle_0_ir_1_state'], ")", end="  \t")
                # print("Accel (", sample['tentacle_0_acc_x_state'], ', ', sample['tentacle_0_acc_y_state'], ', ', sample['tentacle_0_acc_z_state'], ")" )
                #
                # print("Tentacle 1", end=" ---\t")
                # print("IR (", sample['tentacle_1_ir_0_state'], ", ", sample['tentacle_1_ir_1_state'], ")", end="  \t")
                # print("Accel (", sample['tentacle_1_acc_x_state'], ', ', sample['tentacle_1_acc_y_state'], ', ', sample['tentacle_1_acc_z_state'], ")" )
                #
                # print("Tentacle 2", end=" ---\t")
                # print("IR (", sample['tentacle_2_ir_0_state'], ", ", sample['tentacle_2_ir_1_state'], ")", end="  \t")
                # print("Accel (", sample['tentacle_2_acc_x_state'], ', ', sample['tentacle_2_acc_y_state'], ', ', sample['tentacle_2_acc_z_state'], ")" )
                #
                # print("Protocell", end=" ---\t")
                # print("ALS (", sample['protocell_0_ambient_light_sensor_state'], ", ", sample['protocell_1_ambient_light_sensor_state'], ")")
                # print('')

                # new blink period
                indicator_led_period[teensy_name] += 0.001
                indicator_led_period[teensy_name] %= 10


            #     if sample['tentacle_2_acc_x_state'] == 0:
            #         crash_count += 1
            #     else:
            #         crash_count = 0
            #
            # if crash_count > 20:
            #     break

            print("Loop Time:", clock() - start_time)
            loop += 1
           # sleep(0.5)

       # print("Crash Time: ", clock() - test_start_time)

class ProgrammUpload(InteractiveCmd.InteractiveCmd):

    def run(self):
        teensy_names = self.teensy_manager.get_teensy_name_list()

        if self.teensy_manager.get_num_teensy_thread() == 0:
            return

        for teensy_name in list(teensy_names):

            Teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)

            # check if the thread is still alive
            while Teensy_thread is not None:

                #=== programming command ===
                cmd_obj = command_object(teensy_name, 'prgm')
                cmd_obj.add_param_change('program_teensy', 1)

                self.enter_command(cmd_obj)

                self.send_commands()

                Teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)

            sleep(3)
