'''Example of how to interface with a Teensy.

This is how you would iterface with the Teensy, not using CBLA.

THIS MAY NOT WORK. PLEASE TEST AND UPDATE THE COMMENTS.
'''

__author__ = 'Matthew'
from interactive_system import TeensyManager
from interactive_system.InteractiveCmd import InteractiveCmd
from interactive_system.InteractiveCmd import command_object

from time import clock

# class that polls the IR sensor
class read_ir_sensors(InteractiveCmd):
	'''Read the IR sensor values.
	
	Extends the InteractiveCmd class. InteractiveCommand is an emulated terminal to be able to control low-level sculptural functions and read data from the sculpture.
	'''

    def run(self):

        while True:

            t0 = clock()

            # if all the Teensy threads are dead, terminate the program
            if self.teensy_manager.get_num_teensy_thread() == 0:
                return

            # retrieve the names of all active Teensy devices
            teensy_names = self.teensy_manager.get_teensy_name_list()

            # request updated sensor measurements from all Teensy devices
            self.update_input_states(teensy_names)

            # specify the desired measurements
            input_type = ('tentacle_0_ir_0_state', 'tentacle_0_ir_1_state',
                           'tentacle_1_ir_0_state', 'tentacle_1_ir_1_state',
                           'tentacle_2_ir_0_state', 'tentacle_2_ir_1_state',)
            # retrieve the desired measurements
            input_states = self.get_input_states(teensy_names, input_types=input_type, timeout=1)

            for teensy_name in teensy_names:
                sample, is_new_update = input_states[teensy_name]
                print('[%s]\t'% teensy_name, end='\t')
                if is_new_update:
                    print('new*')
                else:
                    print('old')

                for j in range(3):
                    device_header = 'tentacle_%d_' % j
                    print("Tentacle %d" % j, end=" ---\t")
                    print("IR (", sample[device_header + 'ir_0_state'], ", ", sample[device_header + 'ir_1_state'], ")",
                          end="  \t")
                print('\n')

            print("Loop Time: %f" % (clock()-t0))


if __name__ == "__main__":

    # instantiate Teensy Monitor -> Monitor=Manager
    teensy_manager = TeensyManager(import_config=True)

    # find the number of Teensy devices
    print("Number of Teensy devices found: " + str(teensy_manager.get_num_teensy_thread()))

    # instantiate the IR polling thread
    read_ir_sensors(teensy_manager)

    # wait for all Teensy threads to terminate
    for teensy_thread in teensy_manager._get_teensy_thread_list():
        teensy_thread.join()

    print("All Teensy threads terminated.")
