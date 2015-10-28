__author__ = 'Matthew'

import interactive_system
import washington_protocol as CP
import abstract_node as Abs

from collections import OrderedDict
import  threading


class WashingtonManual(interactive_system.InteractiveCmd):

    def __init__(self, Teensy_manager, auto_start=True):

        self.node_list = OrderedDict()

        self.all_nodes_created = threading.Condition()

        super(WashingtonManual, self).__init__(Teensy_manager, auto_start=auto_start)

    def run(self):

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

        teensy_in_use = tuple(self.teensy_manager.get_teensy_name_list())

         # instantiate all the basic components
        for teensy_name in teensy_in_use:

            # check if the teensy exists
            if teensy_name not in self.teensy_manager.get_teensy_name_list():
                print('%s does not exist!' % teensy_name)
                continue

            # check the type of node
            protocol = self.teensy_manager.get_protocol(teensy_name)

            # -- Cricket Node
            if isinstance(protocol, CP.WashingtonCricketProtocol):
                components  = self.build_cricket_components(teensy_name)


    def build_cricket_components(self, teensy_name, cricket_id):

        cricket_comps = OrderedDict()

        # 1 ir sensor each
        ir = Abs.Input_Node(self.messenger, teensy_name, node_name='c%d.ir' % cricket_id, input='cricket_%d_ir_state' % cricket_id)
        cricket_comps[ir.node_name] = ir

        # 4 motor output each
        motor_0 = Abs.Output_Node(self.messenger, teensy_name, node_name='c%d.motor_0' % cricket_id, output='cricket_%d_output_0' % cricket_id)
        motor_1 = Abs.Output_Node(self.messenger, teensy_name, node_name='c%d.motor_1' % cricket_id, output='cricket_%d_output_1' % cricket_id)
        motor_2 = Abs.Output_Node(self.messenger, teensy_name, node_name='c%d.motor_2' % cricket_id, output='cricket_%d_output_2' % cricket_id)
        motor_3 = Abs.Output_Node(self.messenger, teensy_name, node_name='c%d.motor_3' % cricket_id, output='cricket_%d_output_3' % cricket_id)

        cricket_comps[motor_0.node_name] = motor_0
        cricket_comps[motor_1.node_name] = motor_1
        cricket_comps[motor_2.node_name] = motor_2
        cricket_comps[motor_3.node_name] = motor_3

        return cricket_comps

    def build_light_components(self, teensy_name, light_id):

        light_comps = OrderedDict()

        # 1 ir sensor each
        ir = Abs.Input_Node(self.messenger, teensy_name, node_name='c%d.ir' % cricket_id, input='cricket_%d_ir_state' % cricket_id)
        cricket_comps[ir.node_name] = ir

        # 4 motor output each
        motor_0 = Abs.Output_Node(self.messenger, teensy_name, node_name='c%d.motor_0' % cricket_id, output='cricket_%d_output_0' % cricket_id)
        motor_1 = Abs.Output_Node(self.messenger, teensy_name, node_name='c%d.motor_1' % cricket_id, output='cricket_%d_output_1' % cricket_id)
        motor_2 = Abs.Output_Node(self.messenger, teensy_name, node_name='c%d.motor_2' % cricket_id, output='cricket_%d_output_2' % cricket_id)
        motor_3 = Abs.Output_Node(self.messenger, teensy_name, node_name='c%d.motor_3' % cricket_id, output='cricket_%d_output_3' % cricket_id)

        cricket_comps[motor_0.node_name] = motor_0
        cricket_comps[motor_1.node_name] = motor_1
        cricket_comps[motor_2.node_name] = motor_2
        cricket_comps[motor_3.node_name] = motor_3

        return cricket_comps

if __name__ == "__main__":

    cmd = WashingtonManual

    # None means all Teensy's connected will be active; otherwise should be a tuple of names
    ACTIVE_TEENSY_NAMES = None
    MANDATORY_TEENSY_NAMES = ACTIVE_TEENSY_NAMES

    def main():

        protocols = dict()
        protocols['WashingtonCricketProtocol'] = CP.WashingtonCricketProtocol()

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

        # with behaviour.all_nodes_created:
        #     behaviours.all_nodes_created.wait()
        #
        # # initialize the gui
        # hmi = tk_gui.Master_Frame()
        # hmi_init(hmi, behaviours.messenger, behaviours.node_list)

        # behaviour.terminate()

        behaviour.join()

        for teensy_thread in teensy_manager._get_teensy_thread_list():
            teensy_thread.join()

        print("All Teensy threads terminated")

    main()
    print("\n===== Program Safely Terminated=====")