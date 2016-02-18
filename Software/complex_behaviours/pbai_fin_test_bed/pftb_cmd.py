"""
The base class of PBAI Fin Test Bed (PFTB).
This class creates the basic components (Input and Output Node) of the PFTB.
"""

__author__ = 'Matthew'

import interactive_system
import pftb_protocol as CP
import abstract_node as Abs

from collections import OrderedDict
import  threading


class PFTB_Cmd(interactive_system.InteractiveCmd):

    """Base Command for the PBAI Fin Test Bed (PFTB)

    This class inherits the InteractiveCmd and creates all Input and Output Nodes that make up the PFTB.

    Parameters
    ------------

    Teensy Manager
        The Teensy Manager associated with the PFTB.

    auto_start: bool (default=True)
        With auto_start=False, the behaviour won't run until 'start' is called.


    """


    def __init__(self, Teensy_manager, auto_start=True):

        self.node_list = OrderedDict()

        self.all_nodes_created = threading.Condition()

        super(PFTB_Cmd, self).__init__(Teensy_manager, auto_start=auto_start)

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

            # -- PFTB Triplet Node ---
            if isinstance(protocol, CP.PFTB_Triplet_Protocol):

                self.NUM_LIGHT = protocol.NUM_LIGHT
                self.NUM_FIN = protocol.NUM_FIN

                # ==== creating components related to the Light =====
                light_components = OrderedDict()
                for j in range(self.NUM_LIGHT):
                    light_components.update(self.build_light_components(teensy_name=teensy_name, light_id=j))
                self.node_list.update(light_components)

                # ===== creating components for related to the Fins ====
                fin_components = OrderedDict()
                for j in range(self.NUM_FIN):
                    fin_components.update(self.build_fin_components(teensy_name=teensy_name, fin_id=j))
                self.node_list.update(fin_components)

            # -- operation mode ----
            # operation_mode_var = Abs.Output_Node(self.messenger, teensy_name, node_name="operation_mode_var",
            #                                      output='operation_mode')
            # self.node_list.update({operation_mode_var.node_name: operation_mode_var})

    def build_fin_components(self, teensy_name, fin_id):

        fin_comps = OrderedDict()

        # 2 ir sensors each
        ir_s = Abs.Input_Node(self.messenger, teensy_name, node_name='f%d.ir-s' % fin_id,
                            input='fin_%d_ir_0_state' % fin_id)
        ir_f = Abs.Input_Node(self.messenger, teensy_name, node_name='f%d.ir-f' % fin_id,
                            input='fin_%d_ir_1_state' % fin_id)

        # 1 3-axis acceleromter each
        acc = Abs.Input_Node(self.messenger, teensy_name, node_name='f%d.acc' % fin_id,
                             x='fin_%d_acc_x_state' % fin_id,
                             y='fin_%d_acc_y_state' % fin_id,
                             z='fin_%d_acc_z_state' % fin_id)

        # 2 SMA wires each
        sma_l = Abs.Output_Node(self.messenger, teensy_name, node_name='f%d.sma-l' % fin_id,
                                output='fin_%d_sma_0_level' % fin_id)
        sma_r = Abs.Output_Node(self.messenger, teensy_name, node_name='f%d.sma-r' % fin_id,
                                output='fin_%d_sma_1_level' % fin_id)

        # 2 reflex each
        reflex_l = Abs.Output_Node(self.messenger, teensy_name, node_name='f%d.rfx-l' % fin_id,
                                   output='fin_%d_reflex_0_level' % fin_id)
        reflex_m = Abs.Output_Node(self.messenger, teensy_name, node_name='f%d.rfx-m' % fin_id,
                                   output='fin_%d_reflex_1_level' % fin_id)

        fin_comps[ir_s.node_name] = ir_s
        fin_comps[ir_f.node_name] = ir_f
        fin_comps[acc.node_name] = acc
        fin_comps[sma_l.node_name] = sma_l
        fin_comps[sma_r.node_name] = sma_r
        fin_comps[reflex_l.node_name] = reflex_l
        fin_comps[reflex_m.node_name] = reflex_m

        return fin_comps

    def build_light_components(self, teensy_name, light_id):

        light_comps = OrderedDict()

        # 1 LED per protocell
        led = Abs.Output_Node(self.messenger, teensy_name=teensy_name, node_name='l%d.led' % light_id,
                              output='light_%d_led_level' % light_id)

        light_comps[led.node_name] = led

        # 1 ambient light sensor per protocell
        als = Abs.Input_Node(self.messenger, teensy_name=teensy_name, node_name='l%d.als' % light_id,
                             input='light_%d_als_state' % light_id)

        light_comps[als.node_name] = als

        return light_comps

    def init_routines(self):
        self.init_utilities()
        self.init_basic_components()

    def run(self):

        self.init_routines()

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
