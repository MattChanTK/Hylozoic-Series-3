__author__ = 'Matthew'

from interactive_system import *
import sys

class ListTeensy(InteractiveCmd):

    def run(self):

        teensy_names = self.get_teensy_list()

        if self.teensy_manager.get_num_teensy_thread() == 0:
            return

        input("Press any key to exit.")

    def get_teensy_list(self):

        return self.teensy_manager.get_teensy_name_list()



packet_size_in = 64
packet_size_out = 64




if __name__ == '__main__':

    try:
        node_type = sys.argv[1]
    except IndexError:
        node_type = None

    teensy_manager = TeensyManager(import_config=True)

    program = ListTeensy(teensy_manager)

    if program:
        program.join()

    print("===Program terminated safely====")

    sleep(5)

