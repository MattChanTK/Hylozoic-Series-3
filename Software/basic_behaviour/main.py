from interactive_system import TeensyManager
import sys
import os
import cProfile
from pstats import Stats

behaviours_config = 2

if len(sys.argv) > 1:
    behaviours_config = int(sys.argv[1])
#
# # add CBLA folder to path
# sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'CBLA'))

if behaviours_config == 0:
    from interactive_system.InteractiveCmd import InteractiveCmd as cmd
elif behaviours_config == 1:
    from Behaviours import ProgrammUpload as cmd
elif behaviours_config == 2:
    from Behaviours import Default_Behaviour as cmd
elif behaviours_config == 3:
    from Behaviours import Test_Behaviours as cmd
elif behaviours_config == 4:
    from Behaviours import Internode_Test_Behaviour as cmd
elif behaviours_config == 5:
    from Behaviours import System_Identification_Behaviour as cmd
else:
    from interactive_system.InteractiveCmd import InteractiveCmd as cmd


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
