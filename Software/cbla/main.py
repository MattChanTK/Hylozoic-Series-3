# import sys
# import os
# import cProfile

from interactive_system import TeensyManager
from CBLA_System import CBLA_Behaviours as cmd

# None means all Teensy's connected will be active; otherwise should be a tuple of names
ACTIVE_TEENSY_NAMES = None  #('test_teensy_88',)
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


if __name__ == '__main__':
    # pr = cProfile.Profile()
    #
    # pr.run('main()')
    # pr.print_stats(sort='cumtime')

    main()
