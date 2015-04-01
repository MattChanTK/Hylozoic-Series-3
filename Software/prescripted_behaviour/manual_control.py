from collections import OrderedDict
from time import clock

from interactive_system import InteractiveCmd
from interactive_system import CommunicationProtocol as CP

from abstract_node.low_level_node import *
from complex_node import *
import gui


class Manual_Control(InteractiveCmd.InteractiveCmd):

    # ========= the Run function for the manual control =====
    def run(self):

        for teensy_name in self.teensy_manager.get_teensy_name_list():
            # ------ set mode ------
            cmd_obj = InteractiveCmd.command_object(teensy_name, 'basic')
            cmd_obj.add_param_change('operation_mode', CP.CBLATestBed_FAST.MODE_CBLA2)
            self.enter_command(cmd_obj)

        self.send_commands()

        # initially update the Teensys with all the output parameters here
        self.update_output_params(self.teensy_manager.get_teensy_name_list())

        messenger = Messenger.Messenger(self, 0.000)
        messenger.start()

        teensy_0 = 'test_teensy_1'
        teensy_1 = 'test_teensy_3'
        teensy_2 = 'HK_teensy_1'
        teensy_3 = 'HK_teensy_2'
        teensy_4 = 'HK_teensy_3'

        teensy_in_use = (teensy_0, teensy_1,)

        node_list = OrderedDict()

        # instantiate all the basic components
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

                node_list[ir_sensor_0.node_name] = ir_sensor_0
                node_list[ir_sensor_1.node_name] = ir_sensor_1

                # 1 3-axis acceleromter each
                acc = Input_Node(messenger, teensy, node_name='tentacle_%d.acc' % j,
                                         x='tentacle_%d_acc_x_state' % j,
                                         y='tentacle_%d_acc_y_state' % j,
                                         z='tentacle_%d_acc_z_state' % j)
                node_list[acc.node_name] = acc

                # 2 SMA wires each
                sma_0 = Output_Node(messenger, teensy, node_name='tentacle_%d.sma_0' % j, output='tentacle_%d_sma_0_level' % j)
                sma_1 = Output_Node(messenger, teensy, node_name='tentacle_%d.sma_1' % j, output='tentacle_%d_sma_1_level' % j)

                node_list[sma_0.node_name] = sma_0
                node_list[sma_1.node_name] = sma_1

                # 1 frond
                motion_type = Var(0)
                frond = Frond(messenger, teensy, node_name='tentacle_%d.frond' % j, left_sma=sma_0.in_var['output'],
                              right_sma=sma_1.in_var['output'],
                              motion_type=motion_type)
                node_list[frond.node_name] = frond


                # 2 reflex each
                reflex_0 = Output_Node(messenger, teensy, node_name='tentacle_%d.reflex_0' % j, output='tentacle_%d_reflex_0_level' % j)
                reflex_1 = Output_Node(messenger, teensy, node_name='tentacle_%d.reflex_1' % j, output='tentacle_%d_reflex_1_level' % j)


                node_list[reflex_0.node_name] = reflex_0
                node_list[reflex_1.node_name] = reflex_1

            # 1 led
            led = Output_Node(messenger, teensy_name=teensy, node_name='protocell.led',
                              output='protocell_0_led_level')
            node_list[led.node_name] = led

        for name, node in node_list.items():
            node.start()
            print('%s initialized' % name)


        if len(node_list) > 0:

            # initialize the gui
            main_gui = gui.Main_GUI(messenger)
            main_gui.root.title = 'Manual Control'
            # adding the data display frame
            display_gui = gui.Display_Frame(main_gui.root, node_list)

            # adding the control frame
            entries = OrderedDict()
            for name, node in node_list.items():

                if isinstance(node, Frond):
                    entries[name] = node.in_var['motion_type']
                elif isinstance(node, Output_Node) and 'sma' not in name:
                    entries[name] = node.in_var['output']

            control_gui = gui.Manual_Control_GUI(main_gui.root, entries)

            main_gui.add_frame(control_gui)
            main_gui.add_frame(display_gui)

            main_gui.start()

        print('System Initialized with %d nodes' % len(node_list))




if __name__ == "__main__":

    from interactive_system import TeensyManager
    cmd = Manual_Control

    # None means all Teensy's connected will be active; otherwise should be a tuple of names
    ACTIVE_TEENSY_NAMES = None  # ('test_teensy_88',)
    MANDATORY_TEENSY_NAMES = ACTIVE_TEENSY_NAMES

    def main():

        # instantiate Teensy Monitor
        teensy_manager = TeensyManager(import_config=True)

        # find all the Teensy
        print("Number of Teensy devices found: " + str(teensy_manager.get_num_teensy_thread()))

        # kill all and only leave those specified in ACTIVE_TEENSY_NAMES
        all_teensy_names = list(teensy_manager.get_teensy_name_list())
        if isinstance(ACTIVE_TEENSY_NAMES, tuple):
            for teensy_name in all_teensy_names:
                if teensy_name not in ACTIVE_TEENSY_NAMES:
                    teensy_manager.kill_teensy_thread(teensy_name)

        # check if all the mandatory ones are still there
        all_teensy_names = list(teensy_manager.get_teensy_name_list())
        if isinstance(MANDATORY_TEENSY_NAMES, tuple):
            for teensy_name in MANDATORY_TEENSY_NAMES:
                if teensy_name not in all_teensy_names:
                    raise Exception('%s is missing!!' % teensy_name)

        # find all the Teensy
        print("Number of active Teensy devices: %s\n" % str(teensy_manager.get_num_teensy_thread()))


        # interactive code
        behaviours = cmd(teensy_manager)

        for teensy_thread in teensy_manager._get_teensy_thread_list():
            teensy_thread.join()

        print("All Teensy threads terminated")

    main()