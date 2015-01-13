import changePriority
from TeensyInterface import TeensyManager
import sys
import os
import cProfile
from pstats import Stats

behaviours_config = 4

# add CBLA folder to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'CBLA'))

if behaviours_config == 0:
    from InteractiveCmd import InteractiveCmd as cmd
elif behaviours_config == 1:
    from Behaviours import ProgrammUpload as cmd
elif behaviours_config == 2:
    from Behaviours import Default_Behaviour as cmd
elif behaviours_config == 3:
    from Behaviours import Test_Behaviours as cmd
elif behaviours_config == 4:
    from CBLA import CBLA_Behaviours as cmd
else:
    from InteractiveCmd import InteractiveCmd as cmd


packet_size_in = 64
packet_size_out = 64

def main():

    try:
        # change priority of the the Python process to HIGH
        changePriority.SetPriority(changePriority.Priorities.HIGH_PRIORITY_CLASS)
    except Exception:
        print("Cannot change priority; this is not a window machine")


    # instantiate Teensy Monitor
    teensy_manager = TeensyManager(import_config=True)

    # find all the Teensy

    print("Number of Teensy devices found: " + str(teensy_manager.get_num_teensy_thread()))


    # interactive code
    behaviours = cmd(teensy_manager)
    behaviours.run()

    if teensy_manager.get_num_teensy_thread() <= 0:
        print("All threads terminated")



if __name__ == '__main__':
    # pr = cProfile.Profile()
    #
    # pr.run('main()')
    # pr.print_stats(sort='cumtime')

    main()
