from interactive_system import InteractiveCmd
from interactive_system import Messenger
from node import *
from tentacle_node import *
import gui

from copy import copy
from collections import defaultdict

class Prescripted_Behaviour(InteractiveCmd.InteractiveCmd):

    # ========= the Run function for the prescripted behaviour system =====
    def run(self):

        for teensy_name in self.teensy_manager.get_teensy_name_list():
            # ------ set mode ------
            cmd_obj = InteractiveCmd.command_object(teensy_name, 'basic')
            cmd_obj.add_param_change('operation_mode', 3)
            self.enter_command(cmd_obj)

            # ------ configuration ------
            # set the Tentacle on/off periods
            cmd_obj = InteractiveCmd.command_object(teensy_name, 'tentacle_high_level')
            for j in range(3):
                device_header = 'tentacle_%d_' % j
                cmd_obj.add_param_change(device_header + 'arm_cycle_on_period', 15)
                cmd_obj.add_param_change(device_header + 'arm_cycle_off_period', 105)
            self.enter_command(cmd_obj)

        # initially update the Teensys with all the output parameters here
        self.update_output_params(self.teensy_manager.get_teensy_name_list())


        messenger = Messenger.Messenger(self, 0.03)
        messenger.start()

        teensy_0 = 'test_teensy_3'
        teensy_1 = 'HK_teensy_1'
        teensy_2 = 'HK_teensy_2'
        teensy_3 = 'HK_teensy_3'


        teensy_in_use = (teensy_0, )

        node_list = dict()

        for teensy in teensy_in_use:

            # check if the teensy exists
            if teensy not in self.teensy_manager.get_teensy_name_list():
                print('%s does not exist!' % teensy)
                continue

            # 3 tentacles
            for j in range(3):

                # 2 ir sensors each
                ir_sensor_0 = Input_Node(messenger, teensy, node_name='tentacle_%d.ir_0' % j, input='tentacle_%d_ir_0_state' % j)
                ir_sensor_1 = Input_Node(messenger, teensy, node_name='tentacle_%d.ir_1' % j, input='tentacle_%d_ir_1_state' % j)

                # 1 frond each
                frond = Output_Node(messenger, teensy, node_name='tentacle_%d.frond' % j, output='tentacle_%d_arm_motion_on' % j)

                # 2 reflex each
                reflex_0 = Output_Node(messenger, teensy, node_name='tentacle_%d.reflex_0' % j, output='tentacle_%d_reflex_0_level' % j)
                reflex_1 = Output_Node(messenger, teensy, node_name='tentacle_%d.reflex_1' % j, output='tentacle_%d_reflex_1_level' % j)

                # create the Tentacle Node object
                tentacle = Tentacle(messenger, teensy_name=teensy,
                                    node_name='tentacle_%d' % j,
                                    ir_0=ir_sensor_0.out_var['input'],
                                    ir_1=ir_sensor_1.out_var['input'],
                                    frond=frond.in_var['output'],
                                    reflex_0=reflex_0.in_var['output'],
                                    reflex_1=reflex_1.in_var['output'])

                node_list[ir_sensor_0.node_name] = ir_sensor_0
                node_list[ir_sensor_1.node_name] = ir_sensor_1
                node_list[frond.node_name] = frond
                node_list[reflex_0.node_name] = reflex_0
                node_list[reflex_1.node_name] = reflex_1
                node_list[tentacle.node_name] = tentacle



        for name, node in node_list.items():
            node.start()
            print('%s initialized' % name)

        print('System Initialized with %d nodes' % len(node_list))

        app = gui.GUI(node_list)

        app.run()





