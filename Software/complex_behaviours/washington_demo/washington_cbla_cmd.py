__author__ = 'Matthew'

import interactive_system
import washington_protocol as CP
import abstract_node as Abs
from abstract_node import *

try:
    from custom_gui import *
except ImportError:
    import sys
    import os
    sys.path.insert(1, os.path.join(os.getcwd(), '..'))
    from custom_gui import *

try:
    from cbla_engine import *
except ImportError:
    import sys
    import os
    sys.path.insert(1, os.path.join(os.getcwd(), '..'))
    from cbla_engine import *

from collections import OrderedDict
import  threading


class WashingtonCBLA(interactive_system.InteractiveCmd):

    def __init__(self, Teensy_manager, auto_start=True):

        self.node_list = OrderedDict()

        self.all_nodes_created = threading.Condition()

        super(WashingtonCBLA, self).__init__(Teensy_manager, auto_start=auto_start)

    def init_utilities(self):

        self.messenger = interactive_system.Messenger(self, 0.0)

        for teensy_name in self.teensy_manager.get_teensy_name_list():
            # ------ set mode ------
            cmd_obj = interactive_system.command_object(teensy_name, 'basic')
            protocol = self.teensy_manager.get_protocol(teensy_name)
            cmd_obj.add_param_change('operation_mode', protocol.MODE_MANUAL_CONTROL)
            self.enter_command(cmd_obj)
        self.send_commands()

         # initially update the Teensys with all the output parameters here
        self.update_output_params(self.teensy_manager.get_teensy_name_list())

        # start the messenger
        self.messenger.start()

        return 0

    def init_basic_components(self):

        teensy_in_use = tuple(self.teensy_manager.get_teensy_name_list())

         # instantiate all the basic components
        for teensy_name in teensy_in_use:

            # check if the teensy exists
            if teensy_name not in self.teensy_manager.get_teensy_name_list():
                print('%s does not exist!' % teensy_name)
                continue

            # check the type of node
            protocol = self.teensy_manager.get_protocol(teensy_name)

            # -- Sound Node ---
            if isinstance(protocol, CP.WashingtonSoundProtocol):
                self.node_list.update(self.build_sound_node_components(teensy_name, protocol.NUM_SOUND))

            # -- operation mode ----
            operation_mode_var = Abs.Output_Node(self.messenger, teensy_name, node_name="operation_mode_var",
                                                 output='operation_mode')
            self.node_list.update({operation_mode_var.node_name: operation_mode_var})

    def run(self):

        self.init_utilities()
        self.init_basic_components()

        self.start_nodes()

        with self.all_nodes_created:
            self.all_nodes_created.notify_all()

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

    def build_sound_node_components(self, teensy_name, num_sound):

        components = OrderedDict()
        fin_comps = OrderedDict()

        for j in range(num_sound):

            # 2 ir sensors each
            ir_s = Abs.Input_Node(self.messenger, teensy_name, node_name='f%d.ir-s' % j, input='fin_%d_ir_0_state' % j)
            ir_f = Abs.Input_Node(self.messenger, teensy_name, node_name='f%d.ir-f' % j, input='fin_%d_ir_1_state' % j)

            # 1 3-axis acceleromter each
            acc = Abs.Input_Node(self.messenger, teensy_name, node_name='f%d.acc' % j,
                             x='fin_%d_acc_x_state' % j,
                             y='fin_%d_acc_y_state' % j,
                             z='fin_%d_acc_z_state' % j)

            # 2 SMA wires each
            sma_r = Abs.Output_Node(self.messenger, teensy_name, node_name='f%d.sma-r' % j, output='fin_%d_sma_0_level' % j)
            sma_l = Abs.Output_Node(self.messenger, teensy_name, node_name='f%d.sma-l' % j, output='fin_%d_sma_1_level' % j)

            # 2 reflex each
            reflex_l = Abs.Output_Node(self.messenger, teensy_name, node_name='f%d.rfx-l' % j, output='fin_%d_reflex_0_level' % j)
            reflex_m = Abs.Output_Node(self.messenger, teensy_name, node_name='f%d.rfx-m' % j, output='fin_%d_reflex_1_level' % j)

            fin_comps[ir_s.node_name] = ir_s
            fin_comps[ir_f.node_name] = ir_f
            fin_comps[acc.node_name] = acc
            fin_comps[sma_l.node_name] = sma_l
            fin_comps[sma_r.node_name] = sma_r
            fin_comps[reflex_l.node_name] = reflex_l
            fin_comps[reflex_m.node_name] = reflex_m

            components.update(fin_comps)
        return components

def hmi_init(hmi: tk_gui.Master_Frame, messenger: interactive_system.Messenger, node_list: dict, monitor_only=False):

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
            if not monitor_only:
                if  device_name not in control_vars[teensy_name]:
                    control_vars[teensy_name][device_name] = OrderedDict()

                if isinstance(node, Output_Node) and 'sma' not in name:
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

    cmd = WashingtonManual

    # None means all Teensy's connected will be active; otherwise should be a tuple of names
    ACTIVE_TEENSY_NAMES = None
    MANDATORY_TEENSY_NAMES = ACTIVE_TEENSY_NAMES

    def main():

        protocols = dict()
        protocols['WashingtonCricketProtocol'] = CP.WashingtonCricketProtocol
        protocols['WashingtonFinCricketProtocol'] = CP.WashingtonFinCricketProtocol
        protocols['WashingtonFinProtocol'] = CP.WashingtonFinProtocol
        protocols['WashingtonSoundProtocol'] = CP.WashingtonSoundProtocol

        # instantiate Teensy Monitor
        teensy_manager = interactive_system.TeensyManager(import_config=True, protocols_dict=protocols, print_to_term=False)

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
        behaviour = cmd(teensy_manager)

        if not isinstance(behaviour, WashingtonManual):
            raise TypeError("Behaviour must be WashingtonBehaviour type!")

        with behaviour.all_nodes_created:
            behaviour.all_nodes_created.wait()

        # initialize the gui
        hmi = tk_gui.Master_Frame()
        hmi_init(hmi, behaviour.messenger, behaviour.node_list)

        behaviour.terminate()

        behaviour.join()

        for teensy_thread in teensy_manager._get_teensy_thread_list():
            teensy_thread.join()

        print("All Teensy threads terminated")

    main()
    print("\n===== Program Safely Terminated=====")