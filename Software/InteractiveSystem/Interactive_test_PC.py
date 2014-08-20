import changePriority
from TeensyInterface import TeensyManager

behaviours_config = 2

if behaviours_config == 0:
    from InteractiveCmd import InteractiveCmd as cmd
elif behaviours_config == 1:
    from Behaviours import HardcodedBehaviours_test as cmd
elif behaviours_config == 2:
    from Behaviours import HardcodedBehaviours as cmd
else:
    from InteractiveCmd import InteractiveCmd as cmd


packet_size_in = 64
packet_size_out = 64


if __name__ == '__main__':

    # change priority of the the Python process to HIGH
    changePriority.SetPriority(changePriority.Priorities.HIGH_PRIORITY_CLASS)

    # instantiate Teensy Monitor
    teensy_manager = TeensyManager()

    # find all the Teensy
    serial_num_list = teensy_manager.get_teensy_serial_num()
    print("Number of Teensy devices found: " + str(len(serial_num_list)))


    # interactive code
    behaviours = cmd(teensy_manager.get_teensy_thread_list())
    behaviours.run()



