import InteractiveCmd
from InteractiveCmd import command_object

from copy import copy
from time import clock
from time import sleep
import math


class Hardcoded_Behaviours(InteractiveCmd.InteractiveCmd):

    def run(self):
        pass



class Test_Behaviours(InteractiveCmd.InteractiveCmd):


    def run(self):

        teensy_names = self.teensy_manager.get_teensy_name_list()

        # initially update the Teensys with all the output parameters here
        self.update_output_params(teensy_names)


        indicator_led_period = dict()
        indicator_led_on = dict()
        for teensy_name in teensy_names:
            indicator_led_period[teensy_name] = 0
            indicator_led_on[teensy_name] = 1

        loop = 0
        num_loop = 1000
        while loop < num_loop:
            start_time = clock()

            if self.teensy_manager.get_num_teensy_thread() == 0:
                return

            for teensy_name in list(teensy_names):

                Teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)

                # check if the thread is still alive
                if Teensy_thread is not None:

                    #=== basic commands"
                    cmd_obj = command_object(teensy_name, 'basic')

                    #
                    # cmd_obj.add_param_change('indicator_led_on',  indicator_led_on[teensy_name])
                    # cmd_obj.add_param_change('indicator_led_period', int(indicator_led_period[teensy_name])*50)

                    cmd_obj.add_param_change('reply_type_request', 0)

                    self.enter_command(cmd_obj)

                    #=== tentacle low-level commands"
                    cmd_obj = command_object(teensy_name, 'tentacle_low_level')


                    cmd_obj.add_param_change('tentacle_0_sma_0_level',  0)#int((loop*2)%255))
                    cmd_obj.add_param_change('tentacle_0_sma_1_level', 0)# int((loop*2)%255))
                    cmd_obj.add_param_change('tentacle_0_reflex_0_level',  int((loop*6+40)%128))
                    cmd_obj.add_param_change('tentacle_0_reflex_1_level', int((loop*6+40)%128))
                    cmd_obj.add_param_change('tentacle_1_reflex_0_level',  int((loop*6)%128))
                    cmd_obj.add_param_change('tentacle_1_reflex_1_level', int((loop*6)%128))
                    cmd_obj.add_param_change('tentacle_2_reflex_0_level',  int((loop*6+80)%128))
                    cmd_obj.add_param_change('tentacle_2_reflex_1_level', int((loop*6+80)%128))


                    self.enter_command(cmd_obj)
                    #=== protocell command====
                    cmd_obj = command_object(teensy_name, 'protocell')
                    cmd_obj.add_param_change('protocell_1_led_level', int((loop*30)%128))
                    self.enter_command(cmd_obj)


                    #=== change wave command====
                    cmd_obj = command_object(teensy_name, 'wave_change')

                    wave = ""
                    cmd_obj.add_param_change('wave_type', 1)
                    pt = 0
                    for i in range(32):
                        pt += int(255/32)
                        wave += (str(pt) + '_')
                    cmd_obj.add_param_change('new_wave', wave)
                    self.enter_command(cmd_obj)



            self.send_commands()

            all_input_states = self.get_input_states(teensy_names, ('all', ))
            for teensy_name, input_states in all_input_states.items():
                sample = input_states[0]
                is_new_update = input_states[1]

                print("[", teensy_name, "]")

                for j in range(4):
                    device_header = 'tentacle_%d_' % j
                    print("Tentacle %d" % j, end=" ---\t")
                    print("IR (", sample[device_header + 'ir_0_state'], ", ", sample[device_header + 'ir_1_state'], ")", end="  \t")
                    print("ACC (", sample[device_header + 'acc_x_state'], ', ', sample[device_header + 'acc_y_state'], ', ', sample[device_header + 'acc_z_state'], ")" )

                for j in range(2):
                    device_header = 'protocell_%d_' % j
                    print("Protocell %d" % j, end=" ---\t")
                    print("ALS (", sample[device_header + 'als_state'], ")")
                print('')

                # new blink period
                indicator_led_period[teensy_name] += 0.004
                indicator_led_period[teensy_name] %= 10

            print("Loop Time:", clock() - start_time)
            loop += 1
            sleep(0.1)

class Default_Behaviour(InteractiveCmd.InteractiveCmd):

    def run(self):
        teensy_names = self.teensy_manager.get_teensy_name_list()

        # initially update the Teensys with all the output parameters here
        self.update_output_params(teensy_names)

        # poll input
        loop = 0
        num_loop = 1000
        while loop < num_loop:
            start_time = clock()

            if self.teensy_manager.get_num_teensy_thread() == 0:
                return

            self.update_input_states(teensy_names)

            all_input_states = self.get_input_states(teensy_names, ('all', ))
            for teensy_name, input_states in all_input_states.items():
                sample = input_states[0]
                is_new_update = input_states[1]

                print("[", teensy_name, "]")

                for j in range(4):
                    device_header = 'tentacle_%d_' % j
                    print("Tentacle %d" % j, end=" ---\t")
                    print("IR (", sample[device_header + 'ir_0_state'], ", ", sample[device_header + 'ir_1_state'], ")", end="  \t")
                    print("ACC (", sample[device_header + 'acc_x_state'], ', ', sample[device_header + 'acc_y_state'], ', ', sample[device_header + 'acc_z_state'], ")" )

                for j in range(2):
                    device_header = 'protocell_%d_' % j
                    print("Protocell %d" % j, end=" ---\t")
                    print("ALS (", sample[device_header + 'als_state'], ")")
                print('')

            print("Loop Time:", clock() - start_time)
            loop += 1
            sleep(0.1)


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

            sleep(5)
