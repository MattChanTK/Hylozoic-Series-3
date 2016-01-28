__author__ = 'Matthew'


if __name__ != "__main__":

    quit()

from washington_cbla_cmd import *
from washington_cbla_sound_test_bed import WashingtonCBLASoundTestBed
import washington_hmi_generic as HMI

from custom_gui import tk_gui

cmd = WashingtonCBLASoundTestBed

# None means all Teensy's connected will be active; otherwise should be a tuple of names
ACTIVE_TEENSY_NAMES = None
MANDATORY_TEENSY_NAMES = ACTIVE_TEENSY_NAMES

def main():

    protocols = dict()
    protocols['WashingtonSoundModuleProtocol'] = CP.WashingtonSoundModuleProtocol


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

    if not isinstance(behaviour, WashingtonCBLA):
        raise TypeError("Behaviour must be WashingtonCBLA type!")

    with behaviour.all_nodes_created:
        behaviour.all_nodes_created.wait()

    # initialize the gui
    hmi = tk_gui.Master_Frame()
    HMI.cbla_hmi_init(hmi, behaviour.messenger, behaviour.node_list)

    behaviour.terminate()

    behaviour.join()

    for teensy_thread in teensy_manager._get_teensy_thread_list():
        teensy_thread.join()

    print("All Teensy threads terminated")

main()
