from interactive_system import TeensyManager
# import sys
# import os
# import cProfile

from CBLA_System import CBLA_Behaviours as cmd


packet_size_in = 64
packet_size_out = 64

def main():


    # instantiate Teensy Monitor
    teensy_manager = TeensyManager(import_config=True)
    # teensy_manager.kill_teensy_thread('HK_teensy_2')
    # teensy_manager.kill_teensy_thread('HK_teensy_3')

    # find all the Teensy

    print("Number of Teensy devices found: " + str(teensy_manager.get_num_teensy_thread()))


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
