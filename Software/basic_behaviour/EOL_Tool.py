from interactive_system import TeensyManager
from Behaviours import Quality_Assurance as QA

import os
import sys
import time


packet_size_in = 64
packet_size_out = 64

def main():


    # instantiate Teensy Monitor
    teensy_manager = TeensyManager(import_config=True)
    # find all the Teensy

    print("Number of Teensy devices found: " + str(teensy_manager.get_num_teensy_thread()))


    QA(teensy_manager)

    for teensy_thread in teensy_manager._get_teensy_thread_list():
        teensy_thread.join()

    print("All Teensy threads terminated.")



if __name__ == '__main__':


    main()
