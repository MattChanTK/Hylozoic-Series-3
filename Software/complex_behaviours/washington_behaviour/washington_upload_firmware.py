__author__ = 'Matthew'
from interactive_system import *
import sys

class ProgramUpload(InteractiveCmd):

    def run(self):

        teensy_names = self.get_teensy_list()

        if self.teensy_manager.get_num_teensy_thread() == 0:
            return

        for teensy_name in list(teensy_names):
            print("Programming %s" % teensy_name)
            Teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)

            # check if the thread is still alive
            counter = 0
            while Teensy_thread is not None:

                if counter > 5:
                    print("Cannot program ", teensy_name)
                    break

                #=== programming command ===
                cmd_obj = command_object(teensy_name, 'prgm', msg_setting=1)
                cmd_obj.add_param_change('program_teensy', 1)

                self.enter_command(cmd_obj)

                self.send_commands()

                sleep(2)

                #self.teensy_manager.kill_teensy_thread(teensy_name)
                Teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)
                counter += 1

    def get_teensy_list(self):

        return self.teensy_manager.get_teensy_name_list()


class ProgramCrickets(ProgramUpload):

    def get_teensy_list(self):

        print("Programming Cricket Nodes")
        cricket_names = ("cricket_node_a", "cricket_node_b", "cricket_node_c", "cricket_node_d")

        # kill all and only leave those specified
        all_teensy_names = list(self.teensy_manager.get_teensy_name_list())
        if isinstance(cricket_names, tuple):
            for teensy_name in all_teensy_names:
                if teensy_name not in cricket_names:
                    self.teensy_manager.kill_teensy_thread(teensy_name)

        sleep(3.0)
        return list(self.teensy_manager.get_teensy_name_list())

class ProgramFinCrickets(ProgramUpload):

    def get_teensy_list(self):

        print("Programming Cricket Nodes")
        cricket_names = ("fin_cricket_node_C", "fin_cricket_node_D")

        # kill all and only leave those specified
        all_teensy_names = list(self.teensy_manager.get_teensy_name_list())
        if isinstance(cricket_names, tuple):
            for teensy_name in all_teensy_names:
                if teensy_name not in cricket_names:
                    self.teensy_manager.kill_teensy_thread(teensy_name)

        sleep(3.0)
        return list(self.teensy_manager.get_teensy_name_list())

class ProgramFins(ProgramUpload):

    def get_teensy_list(self):

        print("Programming Cricket Nodes")
        cricket_names = ("fin_node_A", "fin_node_B", )

        # kill all and only leave those specified
        all_teensy_names = list(self.teensy_manager.get_teensy_name_list())
        if isinstance(cricket_names, tuple):
            for teensy_name in all_teensy_names:
                if teensy_name not in cricket_names:
                    self.teensy_manager.kill_teensy_thread(teensy_name)

        sleep(3.0)
        return list(self.teensy_manager.get_teensy_name_list())

class ProgramSounds(ProgramUpload):

    def get_teensy_list(self):

        print("Programming Cricket Nodes")
        cricket_names = ("sound_node", )

        # kill all and only leave those specified
        all_teensy_names = list(self.teensy_manager.get_teensy_name_list())
        if isinstance(cricket_names, tuple):
            for teensy_name in all_teensy_names:
                if teensy_name not in cricket_names:
                    self.teensy_manager.kill_teensy_thread(teensy_name)

        sleep(3.0)
        return list(self.teensy_manager.get_teensy_name_list())

packet_size_in = 64
packet_size_out = 64




if __name__ == '__main__':

    try:
        node_type = sys.argv[1]
    except IndexError:
        node_type = None

    teensy_manager = TeensyManager(import_config=True)

    if node_type == "crickets":
        program = ProgramCrickets(teensy_manager)
    elif node_type == "fin_crickets":
        program = ProgramFinCrickets(teensy_manager)
    elif node_type == "fins":
        program = ProgramFins(teensy_manager)
    elif node_type == "sounds":
        program = ProgramSounds(teensy_manager)
    else:
        program = None
        print("Not a valid node type!")
    if program:
        program.join()

    print("===Program terminated safely====")

    sleep(5)

