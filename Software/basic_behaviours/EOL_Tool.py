import numpy as np
import os
import time

from interactive_system import TeensyManager
from interactive_system import InteractiveCmd
from interactive_system.InteractiveCmd import command_object

ACC_MG_PER_LSB = 3.9
ADC_RES = 2**12

def main():


    # instantiate Teensy Monitor
    teensy_manager = TeensyManager(import_config=True)
    # find all the Teensy

    print("Number of Teensy devices found: " + str(teensy_manager.get_num_teensy_thread()))


    Quality_Assurance(teensy_manager)

    for teensy_thread in teensy_manager._get_teensy_thread_list():
        teensy_thread.join()

    print("All Teensy threads terminated.")



class Quality_Assurance(InteractiveCmd):

    def run(self):

        NUM_FIN = 3
        NUM_LIGHT = 3

        # save to a text file
        now = time.strftime("%y-%m-%d %H-%M-%S", time.localtime())
        log_file_name = 'log (%s).txt' % now
        if not os.path.exists("qa_log"):
            os.makedirs("qa_log")
        log_file = open(os.path.join(os.getcwd(), "qa_log", log_file_name), 'w')


        # get Teensy names
        teensy_names = self.teensy_manager.get_teensy_name_list()

        # initially update the Teensys with all the output parameters here
        self.update_output_params(teensy_names)

        if self.teensy_manager.get_num_teensy_thread() == 0:
            return

        tester_name = input("\nPlease enter your name: ")
        log_file.write("Tester: %s\n" % tester_name)

        ## Display current date and time from now variable
        start_time = time.strftime("%c")
        print("Test's start time: %s" % start_time)
        log_file.write("Date: %s\n" % start_time)

        for teensy_name in teensy_names:

           # set to QA mode
            cmd_obj = command_object(teensy_name)
            cmd_obj.add_param_change('operation_mode', 6)
            self.enter_command(cmd_obj)

           # ------ configuration ------
           # set the Fin on/off periods
            cmd_obj = command_object(teensy_name, 'fin_high_level')
            for j in range(NUM_FIN):
                device_header = 'fin_%d_' % j
                cmd_obj.add_param_change(device_header + 'arm_cycle_on_period', 15)
                cmd_obj.add_param_change(device_header + 'arm_cycle_off_period', 105)
            self.enter_command(cmd_obj)
        self.send_commands()

        log_file.write("\n====== Test Results =======\n")
        # testing each Fin one by one
        for teensy_name in teensy_names:

            print("\n........ Testing ", teensy_name, '........')
            log_file.write("\n------ %s ------" % teensy_name)

            for j in range(NUM_FIN):

                # turn on Fin arm
                cmd_obj = command_object(teensy_name)
                cmd_obj.add_param_change('fin_%d_arm_motion_on' % j, 3)
                self.enter_command(cmd_obj)
                self.send_commands()

                # prompt user
                print("\nFin %d's arm is activated" % j)
                result = input("Enter [y] if passed and [f] if failed\t")
                log_file.write("\nFin %d's arm:\t%s" % (j, result))

                # turn off Tentalce arm
                cmd_obj.add_param_change('fin_%d_arm_motion_on' % j, 0)
                self.enter_command(cmd_obj)
                self.send_commands()

                # turn on reflex actuators
                cmd_obj = command_object(teensy_name)
                cmd_obj.add_param_change('fin_%d_reflex_0_level' % j, 100)
                cmd_obj.add_param_change('fin_%d_reflex_1_level' % j, 100)
                self.enter_command(cmd_obj)
                self.send_commands()

                # prompt user
                print("Fin %d's reflex actuators are activated" % j)
                result = input("Enter [y] if passed and [f] if failed\t")
                log_file.write("\nFin %d's reflex actuators:\t%s" % (j, result))

                # turn off reflex actuator
                cmd_obj.add_param_change('fin_%d_reflex_0_level' % j, 0)
                cmd_obj.add_param_change('fin_%d_reflex_1_level' % j, 0)
                self.enter_command(cmd_obj)
                self.send_commands()

                # +++testing the IR sensors++++
                result = 's'
                while result is 's':
                    self.update_input_states((teensy_name,))

                    # specify the desired measurements
                    input_type = ('fin_%d_ir_0_state'%j, 'fin_%d_ir_1_state'%j)

                    # retrieve the desired measurements
                    input_states = self.get_input_states((teensy_name,), input_types=input_type, timeout=1)
                    sample, is_new_update = input_states[teensy_name]

                    device_header = 'fin_%d_' % j
                    print("Sampled Fin %d's IR sensors" % j, end=":\t")
                    ir_percent = tuple(np.array((sample[device_header + 'ir_0_state'],
                                                 sample[device_header + 'ir_1_state'])) / ADC_RES * 100)

                    print("( %.2f%%, %.2f%% )" % ir_percent, end="\n")


                    result = input("Enter [y] if passed or [f] if failed; [s] to re-sample\t")

                log_file.write("\nFin %d's IR Sensors (%.2f%%, %.2f%%):\t%s" % ((j,) + ir_percent + (result,)))


                # +++testing the Accelerometers++++
                result = 's'
                while result is 's':
                    self.update_input_states((teensy_name,))

                    # specify the desired measurements
                    input_type = ('fin_%d_acc_x_state' % j, 'fin_%d_acc_y_state' % j,
                                  'fin_%d_acc_z_state' % j)

                    # retrieve the desired measurements
                    input_states = self.get_input_states((teensy_name,), input_types=input_type, timeout=1)
                    sample, is_new_update = input_states[teensy_name]

                    device_header = 'fin_%d_' % j

                    print("Sampled Fin %d's Accelerometers" % j, end=":\t")
                    acc_g = tuple(np.array((sample[device_header + 'acc_x_state'],
                                            sample[device_header + 'acc_y_state'],
                                            sample[device_header + 'acc_z_state'])) * ACC_MG_PER_LSB)

                    print("( %.2f, %.2f, %.2f ) " % acc_g)
                    result = input("Enter [y] if passed or [f] if failed; [s] to re-sample\t")

                log_file.write("\nFin %d's Accelerometers (%.2f, %.2f, %.2f):\t%s" % ((j,) +acc_g + (result,)))

            cmd_obj = command_object(teensy_name)
            for j in range(NUM_LIGHT):

                # turn on light
                cmd_obj.add_param_change('light_%d_led_level' % j, 100)
                self.enter_command(cmd_obj)
                self.send_commands()

                print("\nLight %d's LED is activated" % j)
                result = input("Enter [y] if passed or [f] if failed\t")
                log_file.write("\nLight %d's LED:\t%s" % (j, result))

                # turn off light
                cmd_obj.add_param_change('light_%d_led_level' % j, 0)
                self.enter_command(cmd_obj)
                self.send_commands()

                # +++testing the Ambient light sensors++++
                result = 's'
                while result is 's':
                    self.update_input_states((teensy_name,))

                    # specify the desired measurements
                    input_type = ('light_%d_als_state' % j,)

                    # retrieve the desired measurements
                    input_states = self.get_input_states((teensy_name,), input_types=input_type, timeout=1)
                    sample, is_new_update = input_states[teensy_name]

                    device_header = 'light_%d_' % j
                    print("Sampled Light %d's ambient light sensors" % j, end=":\t")
                    als_percent = sample[device_header + 'als_state'] / ADC_RES * 100
                    print("ALS ( %.2f%% )" % als_percent)

                    result = input("Enter [y] if passed or [f] if failed; [s] to re-sample\t")
                log_file.write("\nLight %d's Ambient Light Sensors (%.2f%%):\t%s" % ((j,) + (als_percent,) + (result,)))


        # terminate all threads
        # Display current date and time from now variable
        end_time = time.strftime("%c")
        print("\nTest Completed at %s \n\n" % end_time)

        log_file.write("\nTest Completed at %s \n\n" % end_time)
        for teensy_name in list(teensy_names):
            self.teensy_manager.kill_teensy_thread(teensy_name)
        log_file.close()

if __name__ == '__main__':


    main()
