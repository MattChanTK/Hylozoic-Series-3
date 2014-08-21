import threading
import queue

class InteractiveCmd():

    def __init__(self, Teensy_manager):

        # command queue
        self.cmd_q = queue.Queue()
        self.teensy_manager = Teensy_manager


    def run(self):

        while True:
            self.enter_command()

            all_input_states = self.get_input_states(list(self.teensy_manager.get_teensy_name_list()))

            for teensy_name, input_states in all_input_states.items():
                sample = input_states[0]
                is_new_update = input_states[1]
                if is_new_update:
                    print(teensy_name, ": new* ", sample)
                else:
                    print(teensy_name, ": ", sample)

    def enter_command(self, cmd=None):

        if isinstance(cmd, command_object):
            self.cmd_q.put(cmd)

        # prompt users for inputs
        elif cmd is None:
            cmd = input("Enter--> [Teensy_name] [param_type]:[param_value] (separated by space).\n" +
                        "To apply changes, enter '>>apply'.\n")

            # tokenize the command
            param_cmd_list = cmd.split(" ")

            # check if it's the "apply" command
            try:
                applying_cmd = str(param_cmd_list[0])
                if applying_cmd == ">>apply" or applying_cmd == ">>Apply":
                    self.send_commands()
                    return 1
            except Exception as e:
                print(e)
                return -1

            # check if it's the "read" command
            try:
                applying_cmd = str(param_cmd_list[0])
                if applying_cmd == ">>read" or applying_cmd == ">>Read":
                    self.update_input_states(self.teensy_manager.get_teensy_name_list())
                    return 1
            except Exception as e:
                print(e)
                return -1

            # extract the Teensy ID
            try:
                if len(param_cmd_list) < 2:
                    raise Exception("Error: invalid command!")
                dev_name = param_cmd_list[0]

            except Exception as e:
                 print(e)
                 return -1

            # create a command object
            cmd_obj = command_object(dev_name)

            # extracts the parameters change requests
            try:
                for param_cmd in param_cmd_list[1:]:
                    param = param_cmd.split(":")
                    cmd_obj.add_param_change(param[0], param[1])
            except Exception:
                print("Invalid change request!")
                return -1

            self.cmd_q.put(cmd_obj)

        #print("Command Queue length: ", self.cmd_q.qsize())
        return 0

    def send_commands(self):
        while not self.cmd_q.empty():
            cmd_obj = self.cmd_q.get()
            t = threading.Thread(target=self.apply_change_request, args=(cmd_obj,))
            t.daemon = True
            t.start()

    def apply_change_request(self, cmd_obj):

        #print("apply change request")
        teensy_thread = self.teensy_manager.get_teensy_thread(cmd_obj.teensy_name)
        if teensy_thread is None:
            print(cmd_obj.teensy_name + " does not exist!")
            return -1
        teensy_thread.lock.acquire()
        teensy_thread.inputs_sampled_event.clear()

        try:
            #cmd_obj.print()
            for param_type, param_val in cmd_obj.change_request.items():
                teensy_thread.param.set_output_param(param_type, param_val)
            teensy_thread.param_updated_event.set()
            #print(">>>>> sent command to Teensy #" + str(cmd_obj.teensy_id))
        except Exception as e:
            print(e)

        finally:
            teensy_thread.lock.release()

        return 0

    def update_input_states(self, teensy_names):
        for teensy_name in teensy_names:
            t = threading.Thread(target=self.__update_input_states_thread, args=(teensy_name,))
            t.daemon = True
            t.start()

    def __update_input_states_thread(self, teensy_name):
        teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)
        if teensy_thread is None:
            print(teensy_name + " does not exist!")
            return -1
        teensy_thread.lock.acquire()
        teensy_thread.inputs_sampled_event.clear()

        try:
            teensy_thread.param_updated_event.set()
        except Exception as e:
            print(e)

        finally:
            teensy_thread.lock.release()

        return 0


    def get_input_states(self, teensy_names, input_types='all', timeout=0.005):
        t_list = []
        result_queue = queue.Queue()
        all_input_states = dict()

        for teensy_name in teensy_names:
            t = threading.Thread(target=self.__get_input_states_thread, args=(result_queue, teensy_name, input_types, timeout))
            t_list.append(t)
            t.daemon = True
            t.start()

        for t in t_list:
            t.join()

        while not result_queue.empty():
            result = result_queue.get()
            all_input_states[result[0]] = [result[1], result[2]]

        return all_input_states


    def __get_input_states_thread(self, result_queue, teensy_name, input_types, timeout):

        if input_types == 'all':
            input_types = ('all',)

        if not isinstance(teensy_name, str):
            raise TypeError("Teensy Name must be a string!")
        if not isinstance(input_types, tuple):
            raise TypeError("'Input Types' must be inputted as tuple of strings!")

        # wait for sample update
        teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)
        if teensy_thread is None:
            print(teensy_name + " does not exist!")
            return None

        new_sample_received = teensy_thread.inputs_sampled_event.wait(timeout=timeout)

        # acquiring the lock for the Teensy thread, so that value cannot change while reading
        teensy_thread.lock.acquire()

        # clear the input_sampled_event flag
        if new_sample_received:
            teensy_thread.inputs_sampled_event.clear()

        requested_inputs = dict()
        for input_type in input_types:
            if not isinstance(input_type, str):
                raise TypeError("'Input type' must be a string!")

            if input_type == 'all':
                requested_inputs = teensy_thread.param.input_state
            else:
                requested_inputs[input_type] = teensy_thread.param.get_input_state(input_type)

        # releasing the lock for the Teensy thread
        teensy_thread.lock.release()

        result_queue.put([teensy_name, requested_inputs, new_sample_received])


class command_object():

    def __init__(self, teensy_name):
        if not isinstance(teensy_name, str):
            raise TypeError("Teensy Name must be a string!")

        self.teensy_name = teensy_name
        self.change_request = dict()

    def add_param_change(self, type, value):
        if isinstance(type, str):
            self.change_request[type] = value
        else:
            raise TypeError("'State type' must be a string!")

    def print(self):
        print(self.teensy_name, end=': ')
        for type, value in self.change_request.items():
            print('(', type, '-', value, ') ', end="")
        print('')



if __name__ == '__main__':

    t = InteractiveCmd()


    t.join()

    while not t.cmd_q.empty():
        t.cmd_q.get().print()


