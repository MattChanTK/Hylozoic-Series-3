from collections import OrderedDict
from collections import defaultdict

import interactive_system

import interactive_system.CommunicationProtocol as CP

from complex_node import *

# try:
#     from custom_gui import *
# except ImportError:
#     import sys
#     import os
#     sys.path.insert(1, os.path.join(os.getcwd(), '..'))
#     from custom_gui import *

class Manual_Control(interactive_system.InteractiveCmd):

    def __init__(self, Teensy_manager, auto_start=True):

        self.node_list = OrderedDict()

        self.all_nodes_created = threading.Condition()

        self.num_fin = 3
        self.num_light = 3

        super(Manual_Control, self).__init__(Teensy_manager, auto_start=auto_start)

    # ========= the Run function for the manual control =====
    def run(self):

        self.messenger = interactive_system.Messenger(self, 0.000)

        for teensy_name in self.teensy_manager.get_teensy_name_list():
            # ------ set mode ------
            cmd_obj = interactive_system.command_object(teensy_name, 'basic')
            cmd_obj.add_param_change('operation_mode', CP.CBLATestBed_Triplet_FAST.MODE_CBLA2_MANUAL)
            self.enter_command(cmd_obj)

        self.send_commands()

        # initially update the Teensys with all the output parameters here
        self.update_output_params(self.teensy_manager.get_teensy_name_list())

        # start the messenger
        self.messenger.start()

        teensy_in_use = tuple(self.teensy_manager.get_teensy_name_list())

        # instantiate all the basic components
        for teensy in teensy_in_use:

            # check if the teensy exists
            if teensy not in self.teensy_manager.get_teensy_name_list():
                print('%s does not exist!' % teensy)
                continue

            # 3 fins
            for j in range(self.num_fin):

                # 2 ir sensors each
                ir_sensor_0 = Input_Node(self.messenger, teensy, node_name='fin_%d.ir_0' % j, input='fin_%d_ir_0_state' % j)
                ir_sensor_1 = Input_Node(self.messenger, teensy, node_name='fin_%d.ir_1' % j, input='fin_%d_ir_1_state' % j)

                self.node_list[ir_sensor_0.node_name] = ir_sensor_0
                self.node_list[ir_sensor_1.node_name] = ir_sensor_1

                # 1 3-axis acceleromter each
                acc = Input_Node(self.messenger, teensy, node_name='fin_%d.acc' % j,
                                         x='fin_%d_acc_x_state' % j,
                                         y='fin_%d_acc_y_state' % j,
                                         z='fin_%d_acc_z_state' % j)
                self.node_list[acc.node_name] = acc

                # 2 SMA wires each
                sma_0 = Output_Node(self.messenger, teensy, node_name='fin_%d.sma_0' % j, output='fin_%d_sma_0_level' % j)
                sma_1 = Output_Node(self.messenger, teensy, node_name='fin_%d.sma_1' % j, output='fin_%d_sma_1_level' % j)

                self.node_list[sma_0.node_name] = sma_0
                self.node_list[sma_1.node_name] = sma_1

                # 1 fin
                motion_type = Var(0)
                #sma_param = {'KP': 15, 'K_heating': 0.00, 'K_dissipate': 0.05}
                fin = Fin(self.messenger, teensy, node_name='fin_%d.fin' % j, left_sma=sma_0.in_var['output'],
                              right_sma=sma_1.in_var['output'], motion_type=motion_type,)
                              #left_config=sma_param, right_config=sma_param)
                self.node_list[fin.node_name] = fin


                # 2 reflex each
                reflex_0 = Output_Node(self.messenger, teensy, node_name='fin_%d.reflex_0' % j, output='fin_%d_reflex_0_level' % j)
                reflex_1 = Output_Node(self.messenger, teensy, node_name='fin_%d.reflex_1' % j, output='fin_%d_reflex_1_level' % j)


                self.node_list[reflex_0.node_name] = reflex_0
                self.node_list[reflex_1.node_name] = reflex_1

            # for Interactive_Light
            for j in range(self.num_light):
                # 1 ambient light sensor
                als = Input_Node(self.messenger, teensy, node_name='light_%d.als' % j,
                                 input='light_%d_als_state' % j)
                self.node_list[als.node_name] = als
                # 1 led
                led = Output_Node(self.messenger, teensy_name=teensy, node_name='light_%d.led' % j,
                                  output='light_%d_led_level' % j)
                self.node_list[led.node_name] = led

        with self.all_nodes_created:
            self.all_nodes_created.notify_all()

        self.start_nodes()

        # wait for the nodes to destroy
        for node in self.node_list.values():
            node.join()

        return 0

    def start_nodes(self):

        if not isinstance(self.node_list, dict) or \
           not isinstance(self.messenger, interactive_system.Messenger):
            raise AttributeError("Nodes have not been created properly!")

        for name, node in self.node_list.items():
            node.start()
            print('%s initialized' % name)
        print('System Initialized with %d nodes' % len(self.node_list))

    def terminate(self):
        # killing each of the Node
        for node in self.node_list.values():
            node.alive = False
        for node in self.node_list.values():
            node.join()
            print('%s is terminated.' % node.node_name)

        print("All nodes are terminated")

        # killing each of the Teensy threads
        for teensy_name in list(self.teensy_manager.get_teensy_name_list()):
            self.teensy_manager.kill_teensy_thread(teensy_name)


def hmi_init(hmi: tk_gui.Master_Frame, messenger: interactive_system.Messenger, node_list: dict):

    if not isinstance(hmi, tk_gui.Master_Frame):
        raise TypeError("HMI must be Master_Frame")
    if not isinstance(node_list, dict):
        raise TypeError("node_list must be a dictionary")

    hmi.wm_title('Manual Control Mode')

    status_frame = tk_gui.Messenger_Status_Frame(hmi, messenger)
    content_frame = tk_gui.Content_Frame(hmi)
    nav_frame = tk_gui.Navigation_Frame(hmi, content_frame)

    control_vars = OrderedDict()
    display_vars = OrderedDict()

    if len(node_list) > 0:

        for name, node in node_list.items():
            node_name = name.split('.')
            teensy_name = node_name[0]
            device_name = node_name[1]
            try:
                output_name = node_name[2]
            except IndexError:
                output_name = "variables"

            if teensy_name not in control_vars:
                control_vars[teensy_name] = OrderedDict()

            if teensy_name not in display_vars:
                display_vars[teensy_name] = OrderedDict()

            # specifying the controlable variables
            if device_name not in control_vars[teensy_name]:
                control_vars[teensy_name][device_name] = OrderedDict()

            if isinstance(node, Fin):
                control_vars[teensy_name][device_name][output_name] = node.in_var['motion_type']
            elif isinstance(node, Output_Node) and 'sma' not in name:
                control_vars[teensy_name][device_name][output_name] = node.in_var['output']

            # specifying the displayable variables
            if device_name not in display_vars[teensy_name]:
                display_vars[teensy_name][device_name] = OrderedDict()

            if isinstance(node, Input_Node):
                display_vars[teensy_name][device_name][output_name] = (node.out_var, 'input_node')
            elif isinstance(node, Output_Node):
                display_vars[teensy_name][device_name][output_name] = (node.in_var, 'output_node')
            else:
                display_vars[teensy_name][device_name][output_name + "_input"] = (node.in_var, 'input_node')
                display_vars[teensy_name][device_name][output_name + "_output"] = (node.out_var, 'output_node')

    page_frames = OrderedDict()
    for teensy_name, teensy_display_vars in display_vars.items():

        teensy_control_vars = OrderedDict()
        if teensy_name in control_vars.keys():
            teensy_control_vars = control_vars[teensy_name]
        frame = HMI_Manual_Mode(content_frame, teensy_name, (teensy_name, 'manual_ctrl_page'),
                                teensy_control_vars, teensy_display_vars)
        page_frames[frame.page_key] = frame

        content_frame.build_pages(page_frames)

        nav_frame.build_nav_buttons()

    print('GUI initialized.')
    hmi.start(status_frame=status_frame,
              nav_frame=nav_frame,
              content_frame=content_frame,
              start_page_key=next(iter(page_frames.keys()), ''))




if __name__ == "__main__":

    cmd = Manual_Control

    # None means all Teensy's connected will be active; otherwise should be a tuple of names
    ACTIVE_TEENSY_NAMES = None  # ('test_teensy_88',)
    MANDATORY_TEENSY_NAMES = ACTIVE_TEENSY_NAMES

    def main():

        # instantiate Teensy Monitor
        teensy_manager = interactive_system.TeensyManager(import_config=True)

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
        # -- this create all the abstract nodes
        behaviours = cmd(teensy_manager)

        if not isinstance(behaviours, Manual_Control):
            raise TypeError("Behaviour must be Manual Control type!")

        with behaviours.all_nodes_created:
            behaviours.all_nodes_created.wait()

        # initialize the gui
        hmi = tk_gui.Master_Frame()
        hmi_init(hmi, behaviours.messenger, behaviours.node_list)

        behaviours.terminate()

        for teensy_thread in teensy_manager._get_teensy_thread_list():
            teensy_thread.join()

        print("All Teensy threads terminated")

    main()
    print("\n===== Program Safely Terminated=====")