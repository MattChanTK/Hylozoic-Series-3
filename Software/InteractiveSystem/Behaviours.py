import InteractiveCmd
from InteractiveCmd import command_object

from copy import copy
from time import clock

class Hardcoded_Behaviours(InteractiveCmd.InteractiveCmd):

    def run(self):

        teensy_names = self.teensy_manager.get_teensy_name_list()

        indicator_led_period = dict()
        indicator_led_on = dict()
        for teensy_name in teensy_names:
            indicator_led_period[teensy_name] = 0
            indicator_led_on[teensy_name] = 0

        while True:
            #start_time = clock()

            if self.teensy_manager.get_num_teensy_thread() == 0:
                return

            for teensy_name in list(teensy_names):

                Teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)

                # check if the thread is still alive
                if Teensy_thread is not None:

                    cmd_obj = command_object(teensy_name)

                    cmd_obj.add_param_change('indicator_led_on',  indicator_led_on[teensy_name])
                    cmd_obj.add_param_change('indicator_led_period', int(indicator_led_period[teensy_name])*25)

                    self.enter_command(cmd_obj)

            self.send_commands()

            all_input_states = self.get_input_states(teensy_names, ('all', ))
            for teensy_name, input_states in all_input_states.items():
                sample = input_states[0]
                is_new_update = input_states[1]

                if is_new_update:
                    if sample['analog_0_state'] > 850:
                        indicator_led_on[teensy_name] = 0
                    else:
                        indicator_led_on[teensy_name] = 1

                print(teensy_name, ": ", sample)

                # new blink period
                indicator_led_period[teensy_name] += 0.002
                indicator_led_on[teensy_name] %= 10

            #print("Loop Time:", clock() - start_time)


class Test_Behaviours(InteractiveCmd.InteractiveCmd):

    def run(self):

        teensy_names = self.teensy_manager.get_teensy_name_list()

        indicator_led_period = dict()
        indicator_led_on = dict()
        for teensy_name in teensy_names:
            indicator_led_period[teensy_name] = 0
            indicator_led_on[teensy_name] = 0

        while True:
            start_time = clock()

            if self.teensy_manager.get_num_teensy_thread() == 0:
                return

            for teensy_name in list(teensy_names):

                Teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)

                # check if the thread is still alive
                if Teensy_thread is not None:

                    cmd_obj = command_object(teensy_name, 'basic')

                    cmd_obj.add_param_change('indicator_led_on',  indicator_led_on[teensy_name])
                    cmd_obj.add_param_change('indicator_led_period', int(indicator_led_period[teensy_name])*25)

                    self.enter_command(cmd_obj)

            self.send_commands()

            all_input_states = self.get_input_states(teensy_names, ('all', ))
            for teensy_name, input_states in all_input_states.items():
                sample = input_states[0]
                is_new_update = input_states[1]

                if is_new_update:
                    if sample['analog_0_state'] > 900:
                        indicator_led_on[teensy_name] = 0
                    else:
                        indicator_led_on[teensy_name] = 1

                print(teensy_name, ": ", sample)

                # new blink period
                indicator_led_period[teensy_name] += 0.002
                indicator_led_period[teensy_name] %= 10

            print("Loop Time:", clock() - start_time)
