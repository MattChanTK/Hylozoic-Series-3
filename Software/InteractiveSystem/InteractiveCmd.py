import threading
import queue
from time import clock
import inspect

class InteractiveCmd(threading.Thread):

    def __init__(self, Teensy_manager):

        # command queue
        self.cmd_q = queue.Queue()
        self.teensy_manager = Teensy_manager

        # start thread
        threading.Thread.__init__(self)
        self.daemon = False
        self.start()


    def update_output_params(self, teensy_names):

        for teensy_name in list(teensy_names):
            Teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)

            for request_type, vars in Teensy_thread.param.request_types.items():
                cmd_obj = command_object(teensy_name, request_type, write_only=True)
                for var in vars:
                    cmd_obj.add_param_change(var, Teensy_thread.param.output_param[var])
                self.enter_command(cmd_obj)

        self.send_commands()

    def run(self):


        while self.teensy_manager.get_num_teensy_thread() > 0:
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
            cmd = input("Enter--> [Teensy_name] [request_type] [param_type]:[param_value] (separated by space).\n" +
                        "To apply changes, enter '>>apply'.\n")

            # tokenize the command
            param_cmd_list = cmd.split(" ")

            # check if it's the "apply" command

            applying_cmd = str(param_cmd_list[0])
            if applying_cmd == ">>apply" or applying_cmd == ">>Apply":
                self.send_commands()
                return 1


            # check if it's the "read" command

            applying_cmd = str(param_cmd_list[0])
            if applying_cmd == ">>read" or applying_cmd == ">>Read":
                self.update_input_states(self.teensy_manager.get_teensy_name_list())
                return 1

            # check if it's the "update" command

            applying_cmd = str(param_cmd_list[0])
            if applying_cmd == ">>update" or applying_cmd == ">>Update":
                self.update_output_params(self.teensy_manager.get_teensy_name_list())
                return 1

            # extract the Teensy ID
            try:
                if len(param_cmd_list) < 3:
                    raise Exception("Error: invalid command!")
                dev_name = param_cmd_list[0]

            except Exception as e:
                 print(e)
                 return -1

            # create a command object
            cmd_type = param_cmd_list[1]
            cmd_obj = command_object(dev_name, cmd_type)

            # extracts the parameters change requests
            try:
                for param_cmd in param_cmd_list[2:]:
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

            self.apply_change_request(cmd_obj)

    def apply_change_request(self, cmd_obj):

        #print("applying change request")
        teensy_thread = self.teensy_manager.get_teensy_thread(cmd_obj.teensy_name)
        if teensy_thread is None:
            print(cmd_obj.teensy_name + " does not exist!")
            return -1

        with teensy_thread.lock:
            # print("sending... ", end="")
            # cmd_obj.print()

            #teensy_thread.lock_received = False
            teensy_thread.inputs_sampled_event.clear()

            request_type = teensy_thread.param.set_request_type(cmd_obj.change_request_type)
            teensy_thread.param.set_write_only(cmd_obj.write_only)

            #cmd_obj.print()
            for param_type, param_val in cmd_obj.change_request.items():
                y = teensy_thread.param.set_output_param(param_type, param_val)
                if y == 1:
                    print(param_type, " is not a ", request_type, " request. Change request did not apply.")
                elif y == -1:
                    print("Request Type ", request_type, " does not exist! Change request did not apply.")
            #print("set event updated")
            teensy_thread.param_updated_event.set()
            #print(">>>>> sent command to Teensy #" + cmd_obj.teensy_name)

        if not teensy_thread.lock_received_event.wait(0.5):
            print("Teensy thread ", cmd_obj.teensy_name, " is not responding.")
        else:
            teensy_thread.lock_received_event.clear()

        return 0

    def update_input_states(self, teensy_names, derive_param=None):
        for teensy_name in teensy_names:
            teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)
            if teensy_thread is None:
                print(teensy_name + " does not exist!")
                return -1

            # send in an empty read_only command object
            cmd_obj = command_object(teensy_name, 'read_only')
            if derive_param is not None and isinstance(derive_param, dict):
                cmd_obj.add_param_change('derive_inputs', True)
                for key in derive_param.keys():
                    cmd_obj.add_param_change(key, derive_param[key])

            self.enter_command(cmd_obj)

        self.send_commands()

        return 0

    def get_input_states(self, teensy_names, input_types='all', timeout=0.005):


        all_input_states = dict()

        for teensy_name in list(teensy_names):

            result = self.__get_input_states_func(teensy_name, input_types, timeout)
            if result:
                all_input_states[result[0]] = [result[1], result[2]]


        return all_input_states

    def __get_input_states_func(self,teensy_name, input_types, timeout):

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
        # start_time = clock()

        new_sample_received = teensy_thread.inputs_sampled_event.wait(timeout=timeout)

        # print(input_types)
        # print(clock()-start_time)

        # clear the input_sampled_event flag
        if new_sample_received:
            # acquiring the lock for the Teensy thread, so that value cannot change while reading
            with teensy_thread.lock:
                teensy_thread.inputs_sampled_event.clear()

        requested_inputs = dict()
        for input_type in input_types:
            if not isinstance(input_type, str):
                raise TypeError("'Input type' must be a string!")

            with teensy_thread.lock:
                if input_type == 'all':
                    requested_inputs = teensy_thread.param.input_state
                else:
                    requested_inputs[input_type] = teensy_thread.param.get_input_state(input_type)

        return teensy_name, requested_inputs, new_sample_received



class command_object():

    def __init__(self, teensy_name, change_request_type, write_only=False):
        if not isinstance(teensy_name, str):
            raise TypeError("Teensy Name must be a string!")

        if not isinstance(change_request_type, str):
            raise TypeError("Change Request Type must be a string!")

        self.teensy_name = teensy_name
        self.change_request = dict()
        self.change_request_type = change_request_type
        self.write_only = write_only

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


