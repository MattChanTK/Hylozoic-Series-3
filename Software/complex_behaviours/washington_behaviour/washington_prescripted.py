__author__ = 'Matthew'

import interactive_system
import washington_protocol as CP

from collections import OrderedDict
import  threading


class WashingtonManual(interactive_system.InteractiveCmd):

    def __init__(self, Teensy_manager, auto_start=True):

        self.node_list = OrderedDict()

        self.all_nodes_created = threading.Condition()

        self.num_cricket = 3
        self.num_light = 1

        super(WashingtonManual, self).__init__(Teensy_manager, auto_start=auto_start)

    def run(self):

        self.messenger = interactive_system.Messenger(self, 0.0)

        for teensy_name in self.teensy_manager.get_teensy_name_list():
            # ------ set mode ------
            cmd_obj = interactive_system.command_object(teensy_name, 'basic')
            protocol = self.teensy_manager.get_protocol(teensy_name)
            cmd_obj.add_param_change('operation_mode', protocol.MODE_MANUAL_CONTROL)
            self.enter_command(cmd_obj)




if __name__ == "__main__":

    cmd = WashingtonManual

    # None means all Teensy's connected will be active; otherwise should be a tuple of names
    ACTIVE_TEENSY_NAMES = None
    MANDATORY_TEENSY_NAMES = ACTIVE_TEENSY_NAMES

    def main():

        protocols = dict()
        protocols['WashingtonCricketProtocol'] = CP.WashingtonCricketProtocol()

        # instantiate Teensy Monitor
        teensy_manager = interactive_system.TeensyManager(import_config=True, protocols_dict=protocols)

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