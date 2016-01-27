__author__ = 'Matthew'

import interactive_system
import washington_protocol as CP
import abstract_node as Abs

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
            cmd_obj.add_param_change('operation_mode', protocol.MODE_CBLA)
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
            if isinstance(protocol, CP.WashingtonSoundModuleProtocol):
                self.node_list.update(self.build_sound_module_components(teensy_name))

            # -- operation mode ----
            # operation_mode_var = Abs.Output_Node(self.messenger, teensy_name, node_name="operation_mode_var",
            #                                      output='operation_mode')
            # self.node_list.update({operation_mode_var.node_name: operation_mode_var})

    def run(self):

        self.init_utilities()
        self.init_basic_components()
        self.init_cbla_nodes()

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

    def build_sound_module_components(self, teensy_name):

        components = OrderedDict()

        # Input Variables
        mic_0_max_freq = Abs.Input_Node(self.messenger, teensy_name, node_name='mic_mf-0', input='mic_0_max_freq')
        mic_1_max_freq = Abs.Input_Node(self.messenger, teensy_name, node_name='mic_mf-1', input='mic_1_max_freq')

        # Output Variables
        speaker_0_freq	= Abs.Output_Node(self.messenger, teensy_name, node_name='spk_frq-0', output='speaker_0_freq')
        speaker_1_freq	= Abs.Output_Node(self.messenger, teensy_name, node_name='spk_frq-1', output='speaker_1_freq')

        # Putting Input and Output Variables into a dictionary of components
        components[mic_0_max_freq.node_name] = mic_0_max_freq
        components[mic_1_max_freq.node_name] = mic_1_max_freq
        components[speaker_0_freq.node_name] = speaker_0_freq
        components[speaker_1_freq.node_name] = speaker_1_freq

        return components

    def init_cbla_nodes(self):

        print("warning: No CBLA Nodes defined")


