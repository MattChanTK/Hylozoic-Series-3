from copy import copy
from time import clock
from time import sleep
import time
import math
import pickle
import os
import sys

from interactive_system import InteractiveCmd
from interactive_system.InteractiveCmd import command_object


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

                # first loop only
                if loop == 0:
                    cmd_obj = command_object(teensy_name, 'basic', write_only=True)
                    cmd_obj.add_param_change('operation_mode', 1)
                    self.enter_command(cmd_obj)

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
                    cmd_obj.add_param_change('tentacle_0_reflex_0_level',  125)#int((loop*6+40)%128))
                    cmd_obj.add_param_change('tentacle_0_reflex_1_level', 125)#int((loop*6+40)%128))
                    cmd_obj.add_param_change('tentacle_1_reflex_0_level', 125) #int((loop*6)%128))
                    cmd_obj.add_param_change('tentacle_1_reflex_1_level', 125)#int((loop*6)%128))
                    cmd_obj.add_param_change('tentacle_2_reflex_0_level',  125)#int((loop*6+80)%128))
                    cmd_obj.add_param_change('tentacle_2_reflex_1_level',125)# int((loop*6+80)%128))


                    self.enter_command(cmd_obj)

                    # === tentacle high-level commands"
                    cmd_obj = command_object(teensy_name, 'tentacle_high_level')

                    cmd_obj.add_param_change('tentacle_0_arm_motion_on', 3)#int(loop % 4))
                    cmd_obj.add_param_change('tentacle_1_arm_motion_on', 3)#int(loop % 4))
                    cmd_obj.add_param_change('tentacle_2_arm_motion_on', 3)#int(loop % 4))

                    self.enter_command(cmd_obj)

                    #=== protocell command====
                    cmd_obj = command_object(teensy_name, 'protocell')
                    cmd_obj.add_param_change('protocell_0_led_level', int((loop*30)%128))
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


class System_Identification_Behaviour(InteractiveCmd.InteractiveCmd):

    def run(self):

        teensy_names = self.teensy_manager.get_teensy_name_list()
        self.update_input_states(teensy_names)
        self.update_output_params(teensy_names)

        loop = 0
        num_loop = 10000
        tentacle_action = [0, 0, 0, 0]
        tentacle_time = [0, 0, 0, 0]
        protocell_brightness = [0, 0]
        protocell_time = [0,0]


        state_history = dict()

        t0 = clock()
        while loop < num_loop:


            if self.teensy_manager.get_num_teensy_thread() == 0:
                return

            #t_update = clock()
            #self.update_input_states(teensy_names)
            #print("t update", clock()-t_update)

            all_input_states = self.get_input_states(teensy_names, ('all', ), timeout=2)


            for teensy_name in list(teensy_names):

                # first loop only
                if loop == 0:
                    cmd_obj = command_object(teensy_name, 'basic', write_only=True)
                    cmd_obj.add_param_change('operation_mode', 2)
                    self.enter_command(cmd_obj)

                input_states = all_input_states[teensy_name]
                sample = input_states[0]
                is_new_update = input_states[1]



                print("[", teensy_name, "]")
                print('t = %f' % clock())
                print('delta t = %f'%(clock()-t0))

                # === tentacle high-level commands"
                cmd_obj_1 = command_object(teensy_name, 'tentacle_high_level', write_only=True)
                cmd_obj_2 = command_object(teensy_name, 'tentacle_low_level', write_only=True)
                for j in range(3):

                    t = clock()

                    device_header = 'tentacle_%d_' % j

                    # cycling the tentacle
                    if sample[device_header + 'cycling'] == 0:
                        cmd_obj_1.add_param_change('tentacle_%d_arm_motion_on' % j, tentacle_action[j]%4)

                    if t - tentacle_time[j] > 60 + j*3:
                        tentacle_action[j] += 1
                        tentacle_time[j] = t - j*3


                    # reflex sensor trigger LED and vibration motor
                    if (sample[device_header + 'ir_0_state']) > 1200:
                        cmd_obj_2.add_param_change('tentacle_%d_reflex_0_level' % j, 100)
                        cmd_obj_2.add_param_change('tentacle_%d_reflex_1_level' % j, 100)
                    else:
                        cmd_obj_2.add_param_change('tentacle_%d_reflex_0_level' % j, 0)
                        cmd_obj_2.add_param_change('tentacle_%d_reflex_1_level' % j, 0)


                    # output the reading
                    print("Tentacle %d" % j, end=" ---\t")
                    print("Action (", tentacle_action[j] % 4, ")", end="  \n")
                    print("Cycling (", sample[device_header + 'cycling'], ")", end="  \t")
                    print("IR (", sample[device_header + 'ir_0_state'], ", ", sample[device_header + 'ir_1_state'], ")",
                          end="  \t")
                    print("ACC (", sample[device_header + 'acc_x_state'], ', ', sample[device_header + 'acc_y_state'],
                          ', ', sample[device_header + 'acc_z_state'], ")")

                    state = [t, tentacle_action[j]%4, sample[device_header + 'cycling'],
                             sample[device_header + 'ir_0_state'], sample[device_header + 'ir_1_state'],
                             sample[device_header + 'acc_x_state'], sample[device_header + 'acc_y_state'], sample[device_header + 'acc_z_state']]

                    try:
                        state_history[teensy_name + '_tentacle_' + str(j)].append(copy(state))
                    except KeyError:
                        state_history[teensy_name + '_tentacle_' + str(j)] = []
                        state_history[teensy_name + '_tentacle_' + str(j)].append(copy(state))

                self.enter_command(cmd_obj_1)
                self.enter_command(cmd_obj_2)

                # ==== protocell low-level command
                cmd_obj = command_object(teensy_name, 'protocell', write_only=False)
                for j in range(1):

                    t = clock()

                    device_header = 'protocell_%d_' % j
                    # cycling the protocell
                    cmd_obj.add_param_change(device_header + 'led_level', protocell_brightness[j] % 255)

                    if t - protocell_time[j] > 1 + j:
                        protocell_brightness[j] += 1
                        protocell_time[j] = t - j

                    print("Protocell %d" % j, end=" ---\t")
                    #print("Brightness (%d)" % protocell_brightness[j]%255)
                    print("ALS (", sample[device_header + 'als_state'], ")")

                    state = [t, protocell_brightness[j]%255 , sample[device_header + 'als_state']]

                    try:
                        state_history[teensy_name + '_protocell_' + str(j)].append(copy(state))
                    except KeyError:
                        state_history[teensy_name + '_protocell_' + str(j)] = []
                        state_history[teensy_name + '_protocell_' + str(j)].append(copy(state))

                self.enter_command(cmd_obj)
                print('')

            #t_cmd = clock()
            self.send_commands()
            #print("t cmd", clock() - t_cmd)


            # output to files
            for device, states in state_history.items():
                curr_dir = os.getcwd()
                os.chdir(os.path.join(curr_dir, 'pickle_jar'))
                with open(str(device) + '_state_history.pkl', 'wb') as output:
                    pickle.dump(states, output, pickle.HIGHEST_PROTOCOL)
                os.chdir(curr_dir)

            t0 = clock()


class Internode_Test_Behaviour(InteractiveCmd.InteractiveCmd):

    def run(self):
        teensy_names = self.teensy_manager.get_teensy_name_list()
        self.update_input_states(teensy_names)
        self.update_output_params(teensy_names)

        loop = 0
        num_loop = 10000
        while loop < num_loop:

            if self.teensy_manager.get_num_teensy_thread() == 0:
                return

            self.update_input_states(teensy_names)

            all_input_states = self.get_input_states(teensy_names, ('all', ))

            teensy_names_list = list(teensy_names)

            for teensy_name in teensy_names_list:

                # first loop only
                if loop == 0:
                    cmd_obj = command_object(teensy_name, 'basic', write_only=True)
                    cmd_obj.add_param_change('operation_mode', 4)
                    self.enter_command(cmd_obj)

                input_states = all_input_states[teensy_name]
                sample = input_states[0]
                is_new_update = input_states[1]

                print("[", teensy_name, "]")


                next_teensy = teensy_names_list[(teensy_names_list.index(teensy_name)+1)%len(teensy_names)]
                print("Controlling --- [", next_teensy, "]")

                # === tentacle high-level commands"
                cmd_obj_1 = command_object(next_teensy, 'tentacle_high_level')
                cmd_obj_2 = command_object(next_teensy, 'tentacle_low_level')
                for j in range(3):

                    device_header = 'tentacle_%d_' % j
                    if (sample[device_header + 'ir_0_state']) > 1200:

                        cmd_obj_1.add_param_change('tentacle_%d_arm_motion_on' %j, 3)
                        cmd_obj_2.add_param_change('tentacle_%d_reflex_0_level' % j, 100)
                        cmd_obj_2.add_param_change('tentacle_%d_reflex_1_level' % j, 100)
                    else:
                        cmd_obj_1.add_param_change('tentacle_%d_arm_motion_on' %j, 0)
                        cmd_obj_2.add_param_change('tentacle_%d_reflex_0_level' % j, 0)
                        cmd_obj_2.add_param_change('tentacle_%d_reflex_1_level' % j, 0)

                    print("Tentacle %d" % j, end=" ---\t")
                    print("IR (", sample[device_header + 'ir_0_state'], ", ", sample[device_header + 'ir_1_state'], ")",
                          end="  \n")

                self.enter_command(cmd_obj_1)
                self.enter_command(cmd_obj_2)


            self.send_commands()


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

            for teensy_name in teensy_names:

                # first loop only
                if loop == 0:
                    cmd_obj = command_object(teensy_name, 'basic', write_only=True)
                    cmd_obj.add_param_change('operation_mode', 1)
                    self.enter_command(cmd_obj)

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


class Quality_Assurance(InteractiveCmd.InteractiveCmd):

    def run(self):

        # save to a text file
        now = time.strftime("%y-%m-%d %H-%M-%S", time.localtime())
        log_file_name = 'log (%s).txt' % now
        log_file = open(os.path.join(os.getcwd(), "qa_log", log_file_name), 'w')


        # get Teensy names
        teensy_names = self.teensy_manager.get_teensy_name_list()

        # initially update the Teensys with all the output parameters here
        self.update_output_params(teensy_names)

        if self.teensy_manager.get_num_teensy_thread() == 0:
            return

        tester_name = input("\nPlease enter your name: ")

        ## Display current date and time from now variable
        start_time = time.strftime("%c")
        print("Test's start time: %s" % start_time)

        for teensy_name in teensy_names:

           # set to QA mode
            cmd_obj = command_object(teensy_name, 'basic', write_only=True)
            cmd_obj.add_param_change('operation_mode', 6)
            self.enter_command(cmd_obj)

        self.send_commands()

        # testing each Tentacle one by one
        for teensy_name in teensy_names:

            print("\n........ Testing ", teensy_name, '........')

            for j in range(3):

                # turn on Tentacle arm
                cmd_obj = command_object(teensy_name, 'tentacle_high_level', write_only=True)
                cmd_obj.add_param_change('tentacle_%d_arm_motion_on' % j, 3)
                self.enter_command(cmd_obj)
                self.send_commands()

                # prompt user
                print("\nTentacle %d's frond is activated" % j)
                input("Enter [y] if passed and [f] if failed\t")

                # turn off Tentalce arm
                cmd_obj.add_param_change('tentacle_%d_arm_motion_on' % j, 0)
                self.enter_command(cmd_obj)
                self.send_commands()

                # turn on reflex actuators
                cmd_obj = command_object(teensy_name, 'tentacle_low_level', write_only=True)
                cmd_obj.add_param_change('tentacle_%d_reflex_0_level' % j, 100)
                cmd_obj.add_param_change('tentacle_%d_reflex_1_level' % j, 100)
                self.enter_command(cmd_obj)
                self.send_commands()

                # prompt user
                print("Tentacle %d's reflex actuators are activated" % j)
                input("Enter [y] if passed and [f] if failed\t")

                # turn off reflex actuator
                cmd_obj.add_param_change('tentacle_%d_reflex_0_level' % j, 0)
                cmd_obj.add_param_change('tentacle_%d_reflex_1_level' % j, 0)
                self.enter_command(cmd_obj)
                self.send_commands()



            cmd_obj = command_object(teensy_name, 'protocell', write_only=True)
            for j in range(1):

                # turn on protocell
                cmd_obj.add_param_change('protocell_%d_led_level' % j, 100)
                self.enter_command(cmd_obj)
                self.send_commands()

                print("\nProtocell %d's LED is activated" % j)
                input("Enter [y] if passed and [f] if failed\t")

                # turn off protocell
                cmd_obj.add_param_change('protocell_%d_led_level' % j, 0)
                self.enter_command(cmd_obj)
                self.send_commands()


        # terminate all threads
        print("\nTest Completed\n\n")
        for teensy_name in teensy_names:
            self.teensy_manager.kill_teensy_thread(teensy_name)





class ProgrammUpload(InteractiveCmd.InteractiveCmd):

    def run(self):
        teensy_names = self.teensy_manager.get_teensy_name_list()

        if self.teensy_manager.get_num_teensy_thread() == 0:
            return

        for teensy_name in list(teensy_names):

            Teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)

            # check if the thread is still alive
            counter = 0
            while Teensy_thread is not None:

                if counter > 5:
                    print("Cannot program ", teensy_name)
                    break

                #=== programming command ===
                cmd_obj = command_object(teensy_name, 'prgm')
                cmd_obj.add_param_change('program_teensy', 1)

                self.enter_command(cmd_obj)

                self.send_commands()

                Teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)
                counter += 1



            sleep(5)

