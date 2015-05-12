from copy import copy
from time import clock
from time import sleep
import time
import math
import pickle
import os

import sys
import numpy as np
import random
from interactive_system import InteractiveCmd
from interactive_system.InteractiveCmd import command_object

ACC_MG_PER_LSB = 3.9
ADC_RES = 2**12

class Test_Behaviours(InteractiveCmd):

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
                    cmd_obj = command_object(teensy_name, msg_setting=1)
                    cmd_obj.add_param_change('operation_mode', 1)
                    self.enter_command(cmd_obj)

                Teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)

                # check if the thread is still alive
                if Teensy_thread is not None:

                    #=== basic commands"
                    cmd_obj = command_object(teensy_name, msg_setting=1)

                    #
                    # cmd_obj.add_param_change('indicator_led_on',  indicator_led_on[teensy_name])
                    # cmd_obj.add_param_change('indicator_led_period', int(indicator_led_period[teensy_name])*50)

                    cmd_obj.add_param_change('reply_type_request', 0)

                    #=== tentacle low-level commands"
                    # cmd_obj.add_param_change('tentacle_0_sma_0_level',  int((loop*2)%255))
                    # cmd_obj.add_param_change('tentacle_0_sma_1_level', int((loop*2)%255))
                    cmd_obj.add_param_change('tentacle_0_reflex_0_level',  int((loop*6+40)%128))
                    cmd_obj.add_param_change('tentacle_0_reflex_1_level', int((loop*6+40)%128))
                    cmd_obj.add_param_change('tentacle_1_reflex_0_level', int((loop*6)%128))
                    cmd_obj.add_param_change('tentacle_1_reflex_1_level', int((loop*6)%128))
                    cmd_obj.add_param_change('tentacle_2_reflex_0_level',  int((loop*6+80)%128))
                    cmd_obj.add_param_change('tentacle_2_reflex_1_level', int((loop*6+80)%128))

                    # === tentacle high-level commands"
                    cmd_obj.add_param_change('tentacle_0_arm_motion_on', 3)#int(loop % 4))
                    cmd_obj.add_param_change('tentacle_1_arm_motion_on', 3)#int(loop % 4))
                    cmd_obj.add_param_change('tentacle_2_arm_motion_on', 3)#int(loop % 4))

                    #=== protocell command====
                    cmd_obj.add_param_change('protocell_0_led_level', int((loop*30)%128))
                    self.enter_command(cmd_obj)

                    #=== change wave command====
                    cmd_obj = command_object(teensy_name, msg_setting=0)

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
                    ir_percent = tuple(np.array((sample[device_header + 'ir_0_state'],
                                                 sample[device_header + 'ir_1_state'])) / ADC_RES * 100)
                    print("IR ( %.2f%%, %.2f%% )" % ir_percent, end="  \t")
                    acc_g = tuple(np.array((sample[device_header + 'acc_x_state'],
                                            sample[device_header + 'acc_y_state'],
                                            sample[device_header + 'acc_z_state'])) * ACC_MG_PER_LSB)
                    print("ACC ( %.2f, %.2f, %.2f ) " % acc_g)

                for j in range(2):
                    device_header = 'protocell_%d_' % j
                    print("Protocell %d" % j, end=" ---\t")
                    als_percent = sample[device_header + 'als_state'] / ADC_RES * 100
                    print("ALS ( %.2f%% )" % als_percent)
                print('')



                # new blink period
                indicator_led_period[teensy_name] += 0.004
                indicator_led_period[teensy_name] %= 10

            print("Loop Time:", clock() - start_time)
            loop += 1
            sleep(0.1)


class System_Identification_Behaviour(InteractiveCmd):

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
        t_pre_output = 0
        while loop < num_loop:


            if self.teensy_manager.get_num_teensy_thread() == 0:
                return

            #t_update = clock()
            self.update_input_states(teensy_names)
            #print("t update", clock()-t_update)

            all_input_states = self.get_input_states(teensy_names, ('all', ), timeout=2)


            for teensy_name in list(teensy_names):

                # first loop only
                if loop == 0:
                    cmd_obj = command_object(teensy_name, msg_setting=1)
                    cmd_obj.add_param_change('operation_mode', 2)
                    self.enter_command(cmd_obj)

                    # ------ configuration ------
                    # set the Tentacle on/off periods
                    cmd_obj = command_object(teensy_name, 'tentacle_high_level')
                    for j in range(3):
                        device_header = 'tentacle_%d_' % j
                        cmd_obj.add_param_change(device_header + 'arm_cycle_on_period', 15)
                        cmd_obj.add_param_change(device_header + 'arm_cycle_off_period', 105)
                    self.enter_command(cmd_obj)
                    self.send_commands()
                input_states = all_input_states[teensy_name]
                sample = input_states[0]
                is_new_update = input_states[1]


                print("[", teensy_name, "]")
                print('t = %f' % clock())
                print('delta t = %f'%(clock()-t0))

                # === tentacle high-level commands"
                cmd_obj = command_object(teensy_name, msg_setting=1)
                for j in range(3):

                    t = clock()


                    device_header = 'tentacle_%d_' % j

                    # cycling the tentacle
                    #if sample[device_header + 'cycling'] == :
                    cmd_obj.add_param_change('tentacle_%d_arm_motion_on' % j, tentacle_action[j]%4)


                    # reflex sensor trigger LED and vibration motor
                    if (sample[device_header + 'ir_0_state']) > 1400:
                        cmd_obj.add_param_change('tentacle_%d_reflex_0_level' % j, 100)
                        cmd_obj.add_param_change('tentacle_%d_reflex_1_level' % j, 100)
                    else:
                        cmd_obj.add_param_change('tentacle_%d_reflex_0_level' % j, 0)
                        cmd_obj.add_param_change('tentacle_%d_reflex_1_level' % j, 0)


                    # output the reading
                    print("Tentacle %d" % j, end=" ---\t")
                    print("Action (", tentacle_action[j] % 4, ")", end="  \n")
                    print("Cycling (", sample[device_header + 'cycling'], ")", end="  \t")

                    ir_percent = tuple(np.array((sample[device_header + 'ir_0_state'],
                                                 sample[device_header + 'ir_1_state'])) / ADC_RES * 100)
                    print("IR ( %.2f%%, %.2f%% )" % ir_percent, end="  \t")
                    acc_g = tuple(np.array((sample[device_header + 'acc_x_state'],
                                            sample[device_header + 'acc_y_state'],
                                            sample[device_header + 'acc_z_state'])) * ACC_MG_PER_LSB)
                    print("ACC ( %.2f, %.2f, %.2f ) " % acc_g)


                    state = [t, tentacle_action[j]%4, sample[device_header + 'cycling'],
                             sample[device_header + 'ir_0_state'], sample[device_header + 'ir_1_state'],
                             sample[device_header + 'acc_x_state'], sample[device_header + 'acc_y_state'], sample[device_header + 'acc_z_state']]

                    try:
                        state_history[teensy_name + '_tentacle_' + str(j)].append(copy(state))
                    except KeyError:
                        state_history[teensy_name + '_tentacle_' + str(j)] = []
                        state_history[teensy_name + '_tentacle_' + str(j)].append(copy(state))

                    if t - tentacle_time[j] > 60:
                        tentacle_action[j] += 1
                        tentacle_time[j] = t

                self.enter_command(cmd_obj)

                # ==== protocell low-level command
                cmd_obj = command_object(teensy_name, msg_setting=1)
                for j in range(1):

                    t = clock()

                    device_header = 'protocell_%d_' % j
                    # cycling the protocell
                    cmd_obj.add_param_change(device_header + 'led_level', protocell_brightness[j] % 256)

                    print("Protocell %d" % j, end=" ---\t")

                    print("Brightness (%d)" % (protocell_brightness[j]%256))
                    als_state = sample[device_header + 'als_state'] #/ ADC_RES * 100
                    print("ALS ( %d )" % als_state)


                    state = [t, protocell_brightness[j]%256 , sample[device_header + 'als_state']]

                    try:
                        state_history[teensy_name + '_protocell_' + str(j)].append(copy(state))
                    except KeyError:
                        state_history[teensy_name + '_protocell_' + str(j)] = []
                        state_history[teensy_name + '_protocell_' + str(j)].append(copy(state))

                    if True:#t - protocell_time[j] > 1.0:
                        protocell_brightness[j] = random.randint(0, 255)
                        #protocell_brightness[j] += 1
                        protocell_time[j] = t

                self.enter_command(cmd_obj)
                print('')



            #t_cmd = clock()
            self.send_commands()
            #print("t cmd", clock() - t_cmd)


            # output to files
            if t0 - t_pre_output > 3:
                t_pre_output = clock()
                for device, states in state_history.items():
                    curr_dir = os.getcwd()
                    os.chdir(os.path.join(curr_dir, 'pickle_jar'))
                    with open(str(device) + '_state_history.pkl', 'wb') as output:
                        pickle.dump(states, output, protocol=3)
                    os.chdir(curr_dir)

            t0 = clock()
            #sleep(0.5)


class Internode_Test_Behaviour(InteractiveCmd):

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
                    cmd_obj = command_object(teensy_name)
                    cmd_obj.add_param_change('operation_mode', 4)
                    self.enter_command(cmd_obj)

                input_states = all_input_states[teensy_name]
                sample = input_states[0]
                is_new_update = input_states[1]

                print("[", teensy_name, "]")


                next_teensy = teensy_names_list[(teensy_names_list.index(teensy_name)+1)%len(teensy_names)]
                print("Controlling --- [", next_teensy, "]")

                # === tentacle high-level commands"
                cmd_obj = command_object(next_teensy)
                for j in range(3):

                    device_header = 'tentacle_%d_' % j
                    if (sample[device_header + 'ir_0_state']) > 1200:

                        cmd_obj.add_param_change('tentacle_%d_arm_motion_on' %j, 3)
                        cmd_obj.add_param_change('tentacle_%d_reflex_0_level' % j, 100)
                        cmd_obj.add_param_change('tentacle_%d_reflex_1_level' % j, 100)
                    else:
                        cmd_obj.add_param_change('tentacle_%d_arm_motion_on' %j, 0)
                        cmd_obj.add_param_change('tentacle_%d_reflex_0_level' % j, 0)
                        cmd_obj.add_param_change('tentacle_%d_reflex_1_level' % j, 0)

                    print("Tentacle %d" % j, end=" ---\t")
                    print("IR (", sample[device_header + 'ir_0_state'], ", ", sample[device_header + 'ir_1_state'], ")",
                          end="  \n")

                self.enter_command(cmd_obj)

            self.send_commands()


class Default_Behaviour(InteractiveCmd):

    def run(self):
        teensy_names = self.teensy_manager.get_teensy_name_list()

        # initially update the Teensys with all the output parameters here
        self.update_output_params(teensy_names)

        # poll input
        loop = 0
        num_loop = 10000
        while loop < num_loop:
            start_time = clock()

            if self.teensy_manager.get_num_teensy_thread() == 0:
                return

            for teensy_name in teensy_names:

                # first loop only
                if loop == 0:
                    cmd_obj = command_object(teensy_name)
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
                    ir_percent = tuple(np.array((sample[device_header + 'ir_0_state'],
                                                 sample[device_header + 'ir_1_state']))/ADC_RES*100)
                    print("IR ( %.2f%%, %.2f%% )" % ir_percent, end="  \t")
                    acc_g = tuple(np.array((sample[device_header + 'acc_x_state'],
                                            sample[device_header + 'acc_y_state'],
                                            sample[device_header + 'acc_z_state']))*ACC_MG_PER_LSB)
                    print("ACC ( %.2f, %.2f, %.2f ) " % acc_g)

                for j in range(2):
                    device_header = 'protocell_%d_' % j
                    print("Protocell %d" % j, end=" ---\t")
                    als_percent = sample[device_header + 'als_state'] / ADC_RES * 100
                    print("ALS ( %.2f%% )" % als_percent)
                print('')

            print("Loop Time:", clock() - start_time)
            loop += 1
            sleep(0.1)


class ProgrammUpload(InteractiveCmd):

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
                cmd_obj = command_object(teensy_name, 'prgm', msg_setting=1)
                cmd_obj.add_param_change('program_teensy', 1)

                self.enter_command(cmd_obj)

                self.send_commands()

                sleep(2)

                Teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)
                counter += 1
