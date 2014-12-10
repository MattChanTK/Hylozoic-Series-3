import threading
import queue
from time import clock

class InteractiveCmd():

    def __init__(self, Teensy_manager, multithread_mode=False):

        # command queue
        self.cmd_q = queue.Queue()
        self.teensy_manager = Teensy_manager
        self.multithread_mode = multithread_mode
        if self.multithread_mode:
            self.start_get_input_states_threads(self.teensy_manager.get_teensy_name_list())

    def update_output_params(self, teensy_names):

        for teensy_name in list(teensy_names):
            Teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)

            for request_type in Teensy_thread.param.request_types.keys():
                cmd_obj = command_object(teensy_name, request_type)
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
        #print("apply change request")
        teensy_thread = self.teensy_manager.get_teensy_thread(cmd_obj.teensy_name)
        if teensy_thread is None:
            print(cmd_obj.teensy_name + " does not exist!")
            return -1

        with teensy_thread.lock:

            teensy_thread.lock_received = False
            teensy_thread.inputs_sampled_event.clear()

            request_type = teensy_thread.param.set_request_type(cmd_obj.change_request_type)

            #cmd_obj.print()
            for param_type, param_val in cmd_obj.change_request.items():
                y = teensy_thread.param.set_output_param(param_type, param_val)
                if y == 1:
                    print(param_type, " is not a ", request_type, " request. Change request did not apply.")
                elif y == -1:
                    print("Request Type ", request_type, " does not exist! Change request did not apply.")
            teensy_thread.param_updated_event.set()
            #print(">>>>> sent command to Teensy #" + cmd_obj.teensy_name)

        if not teensy_thread.lock_received_event.wait(0.1):
            print("Teensy thread ", cmd_obj.teensy_name, " is not responding.")

        return 0

    def update_input_states(self, teensy_names):
        for teensy_name in teensy_names:
            teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)
            if teensy_thread is None:
                print(teensy_name + " does not exist!")
                return -1

            with teensy_thread.lock:
                teensy_thread.inputs_sampled_event.clear()

                teensy_thread.param_updated_event.set()

        return 0

    def start_get_input_states_threads(self, teensy_names, timeout=0.005):

        self.get_input_states_threads = dict()
        # for input results
        self.result_queue = queue.Queue()

        for teensy_name in list(teensy_names):
            teensy_thread = self.teensy_manager.get_teensy_thread(teensy_name)
            self.get_input_states_threads[teensy_name] = GetInputStateThread(self.result_queue, teensy_name, teensy_thread, timeout)

    def get_input_states(self, teensy_names, input_types='all', timeout=0.005):


        all_input_states = dict()

        for teensy_name in list(teensy_names):

             if not self.multithread_mode:

                result = self.__get_input_states_func(teensy_name, input_types, timeout)
                if result:
                    all_input_states[result[0]] = [result[1], result[2]]

             else:

                with self.get_input_states_threads[teensy_name].lock:
                    self.get_input_states_threads[teensy_name].input_types_requested = input_types
                    self.get_input_states_threads[teensy_name].get_inputs_requested_event.set()

        if self.multithread_mode:
            # wait until all thread have submitted their results
            while self.result_queue.qsize() < len(teensy_names):
                pass
            while not self.result_queue.empty():
                result = self.result_queue.get()
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
        #start_time = clock()
        new_sample_received = teensy_thread.inputs_sampled_event.wait(timeout=timeout)
        #print(clock()-start_time)

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


class GetInputStateThread(threading.Thread):

    def __init__(self, result_queue, teensy_name, teensy_thread, timeout):
        self.get_inputs_requested_event = threading.Event()
        self.lock = threading.Lock()

        self.teensy_name = teensy_name
        self.result_queue = result_queue
        self.timeout = timeout
        self.input_types_requested = None

        if not isinstance(teensy_name, str):
            raise TypeError("Teensy Name must be a string!")

        self.teensy_thread = teensy_thread

        # start thread
        threading.Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):

        while True:

            # wait for an input request event
            self.get_inputs_requested_event.wait()


            with self.lock:
                self.get_inputs_requested_event.clear()


            if self.teensy_thread is None:
                print(self.teensy_name + " does not exist!")
                return

            with self.lock:
                input_types = self.input_types_requested

            if input_types == 'all':
                input_types = ('all',)
            if not isinstance(input_types, tuple):
                raise TypeError("'Input Types' must be inputted as tuple of strings!")
            #start_time = clock()
            new_sample_received = self.teensy_thread.inputs_sampled_event.wait(timeout=self.timeout)
            #print(clock() - start_time)
            # clear the input_sampled_event flag
            if new_sample_received:
                # acquiring the lock for the Teensy thread, so that value cannot change while reading
                with self.teensy_thread.lock:
                    self.teensy_thread.inputs_sampled_event.clear()

            requested_inputs = dict()
            for input_type in input_types:
                if not isinstance(input_type, str):
                    raise TypeError("'Input type' must be a string!")

                with self.teensy_thread.lock:
                    if input_type == 'all':
                        requested_inputs = self.teensy_thread.param.input_state
                    else:
                        requested_inputs[input_type] = self.teensy_thread.param.get_input_state(input_type)

            self.result_queue.put([self.teensy_name, requested_inputs, new_sample_received])


class command_object():

    def __init__(self, teensy_name, change_request_type):
        if not isinstance(teensy_name, str):
            raise TypeError("Teensy Name must be a string!")

        if not isinstance(change_request_type, str):
            raise TypeError("Change Request Type must be a string!")

        self.teensy_name = teensy_name
        self.change_request = dict()
        self.change_request_type = change_request_type

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


