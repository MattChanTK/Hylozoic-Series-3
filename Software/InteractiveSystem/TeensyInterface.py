import usb.core
import usb.util
import threading
import random
import struct
import changePriority
import sys
import re
from time import clock

TEENSY_VENDOR_ID = 0x16C0
TEENSY_PRODUCT_ID = 0x0486


class TeensyManager():

    def __init__(self, import_config=True):

        # table that store all the Teensy threads
        self.teensy_thread_table = dict()

        # configuration of the Teensy threads
        self.unit_config_default = 'SIMPLIFIED_TEST_UNIT'
        self.print_to_term_default = True
        self.import_config = import_config

        self.create_teensy_threads()


    def create_teensy_threads(self):

        # find all connected Teensy
        serial_num_list = self.__find_teensy_serial_number()

        # import config file
        teensy_config_table = dict()

        try:
            if self.import_config is True:
                # read from file
                with open("teensy_config", mode='r') as f:
                    teensy_config = [line.rstrip() for line in f]

                for line in teensy_config:
                    entry = re.split('\W*', line)
                    try:
                        if len(entry) != 3:
                            raise Exception("Invalid configuration at line -> " + line)
                        teensy_config_table[entry[0]] = (entry[1], entry[2])
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)


        # create all the initial Teensy Threads
        unknown_Teensy_id = 0

        for serial_num in serial_num_list:


            # if the serial_num appears in the config file
            if serial_num in teensy_config_table:
                Teensy_name = teensy_config_table[serial_num][0]
                Teensy_unit_config = teensy_config_table[serial_num][1]

            # else mark it as unknown Teensy
            else:
                unknown_Teensy_id += 1
                Teensy_name = "Unknown_" + str(unknown_Teensy_id)
                Teensy_unit_config = self.unit_config_default

            print(Teensy_name + " --- " + str(serial_num))

            # create a new thread for communicating with

            Teensy_thread = TeensyInterface(serial_num, unit_config=Teensy_unit_config, print_to_term=self.print_to_term_default)
            self.teensy_thread_table[Teensy_name] = Teensy_thread

    def _get_teensy_serial_num_list(self):
        serial_num_list = []
        for teensy_name, teensy_thread in self.teensy_thread_table.items():
            serial_num_list.append(teensy_thread.serial_number)
        return serial_num_list

    def _get_teensy_thread_list(self):
        teensy_thread_list = []
        for teensy_name, teensy_thread in self.teensy_thread_table.items():
            teensy_thread_list.append(teensy_thread)
        return teensy_thread_list

    def get_teensy_thread(self, teensy_name):

        try:
            if not self.teensy_thread_table[teensy_name].is_alive():
                self.remove_teensy_thread(teensy_name)
                return None
            return self.teensy_thread_table[teensy_name]
        except KeyError:
            return None

    def get_num_teensy_thread(self):
        return len(self.teensy_thread_table)

    def get_teensy_name_list(self):
        return self.teensy_thread_table.keys()

    def remove_teensy_thread(self, teensy_name):
        try:
            del self.teensy_thread_table[teensy_name]
            return 0
        except KeyError:
            print(teensy_name + ' does not exist!')
            return -1

    def is_teensy_thread_alive(self, teensy_name):
        try:
            return self.teensy_thread_table[teensy_name].is_alive()
        except KeyError:
            print(teensy_name + ' does not exist!')
            return -1


    def __find_teensy_serial_number(self, vendor_id=TEENSY_VENDOR_ID, product_id=TEENSY_PRODUCT_ID):

        # find our device
        dev_iter = usb.core.find(find_all=True, idVendor=vendor_id, idProduct=product_id)

        serialNum = []
        for iter in dev_iter:
            serialNum.append(iter.serial_number)

        return tuple(serialNum)


class TeensyInterface(threading.Thread):

    packet_size_in = 64
    packet_size_out = 64

    def __init__(self, serial_num, vendor_id=TEENSY_VENDOR_ID, product_id=TEENSY_PRODUCT_ID, print_to_term=False, unit_config='default'):

        if unit_config == 'SIMPLIFIED_TEST_UNIT':
            from TestUnitConfiguration import SimplifiedTestUnit as SysParam
        else:
            from SystemParameters import SystemParameters as SysParam

        # find our device
        dev = usb.core.find(idVendor=vendor_id, idProduct=product_id, serial_number=serial_num)
        # was it found?
        if dev is None:
            raise ValueError('Device not found')

        self.serial_number = serial_num
        self.connected = True

        # set the active configuration. With no arguments, the first
        # configuration will be the active one
        dev.set_configuration()

        # get an endpoint instance
        cfg = dev.get_active_configuration()

        interface_iter = usb.util.find_descriptor(cfg, find_all=True)
        interface = []
        for iter in interface_iter:
            interface.append(iter)
        self.intf = interface[0]

        # release device
        #usb.util.release_interface(dev, self.intf)
        # claiming device
        usb.util.claim_interface(dev, self.intf)

        # get OUT endpoint
        self.ep_out = usb.util.find_descriptor(
            self.intf,
            # match the first OUT endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT and \
                usb.util.endpoint_type(e.bEndpointAddress) == usb.util.ENDPOINT_TYPE_CTRL)

        assert self.ep_out is not None

        # get IN endpoint
        self.ep_in = usb.util.find_descriptor(
            self.intf,  # match the first IN endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN and \
                usb.util.endpoint_type(e.bEndpointAddress) == usb.util.ENDPOINT_TYPE_INTR)

        assert self.ep_in is not None

        # instantiate the system parameters
        self.param = SysParam()

        # event is set when parameters are updated by the main thread
        self.param_updated_event = threading.Event()

        # event is set when the Teensy thread updated the inputs parameters
        self.inputs_sampled_event = threading.Event()

        self.lock = threading.Lock()
        self.lock_received_event = threading.Event()

        # start thread
        threading.Thread.__init__(self)
        self.daemon = True
        self.start()


        # print to terminal or not
        self.print_to_term_enabled = print_to_term

    def run(self):

        # change priority of the the Python process to HIGH
        changePriority.SetPriority(changePriority.Priorities.REALTIME_PRIORITY_CLASS)

        no_reply_counter = 0
        while True:

            if self.param_updated_event.wait(timeout=1):
                self.param_updated_event.clear()

                with self.lock:
                    self.lock_received_event.set()
                    self.inputs_sampled_event.clear()
                    self.print_to_term("Teensy thread: sampled event cleared")

                    # compose the data
                    out_msg, front_id, back_id = self.compose_msg()
                self.lock_received_event.clear()

                # sending the data
                #start_time = clock()
                self.talk_to_Teensy(out_msg, timeout=0)
                self.print_to_term("\n---Sent---")
                self.print_data(out_msg, raw_dec=True)
                #print("Talk time: ", clock()-start_time)

                # waiting for reply
                received_reply = False
                #start_time = clock()
                data = self.listen_to_Teensy(timeout=100, byte_num=TeensyInterface.packet_size_in)
                #print("Listen time: ", clock()-start_time)
                invalid_reply_counter = 0

                while received_reply is False:
                    if data:
                        no_reply_counter = 0
                        #print("Echo Time:", clock() - start_time)
                        # check if reply matches sent message
                        if data[0] == front_id and data[-1] == back_id:
                            received_reply = True

                            with self.lock:
                                self.param.parse_message_content(data)
                                self.inputs_sampled_event.set()

                            self.print_to_term("Teensy thread: input sampled")

                            self.print_to_term("---Received Reply---")
                            self.print_data(data, raw_dec=True)

                        else:

                            self.print_to_term("Teensy (" + str(self.serial_number) + ") ---- Received invalid reply......" + str(invalid_reply_counter))
                            self.print_data(data, raw_dec=True)

                            invalid_reply_counter += 1
                            if invalid_reply_counter > 5:
                                print("Teensy (" + str(self.serial_number) + ") ---- Number of invalid replies exceeded 5! Packet lost......")
                                print("Sent:")
                                self.print_data(out_msg, raw_dec=True)
                                print("Received:")
                                self.print_data(data, raw_dec=True)
                                break
                            else:
                                # request another reply
                                data = self.listen_to_Teensy(timeout=100, byte_num=TeensyInterface.packet_size_in)
                    else:
                        no_reply_counter += 1

                        if no_reply_counter >= 5:
                            print("Teensy (" + str(self.serial_number) + ") has probably been disconnected.")
                            return
                        else:
                            print("Teensy (" + str(self.serial_number) + ") ---- Didn't receive any reply. Packet lost......." + str(no_reply_counter))


                # print(self.serial_number, " - Echo time: ", clock() - start_time)



    def compose_msg(self, rand_signature=True):

        content = self.param.compose_message_content()

        # check if content is in valid format
        if not isinstance(content, bytearray):
            raise TypeError("Content must be bytearray.")
        if len(content) is not 64:
            raise ValueError("Content must be 64 byte long.")


        # unique id for each message
        if rand_signature:
            front_id_dec = random.randint(0, 255)
            back_id_dec = random.randint(0, 255)
            if sys.version_info.major is 2:
                front_id = struct.pack('c', chr(front_id_dec))
                back_id = struct.pack('c', chr(back_id_dec))
            else:
                front_id = front_id_dec
                back_id = back_id_dec
            content[0] = front_id
            content[-1] = back_id
        else:
            front_id_dec = 0
            back_id_dec = 0

        return content, front_id_dec, back_id_dec

    def listen_to_Teensy(self, timeout=100, byte_num=64):

        try:
            data = self.ep_in.read(byte_num, timeout)
        except usb.core.USBError:
            #print("Timeout! Couldn't read anything")
            data = None

        return data

    def talk_to_Teensy(self, out_msg, timeout=10):

        try:
            self.ep_out.write(out_msg, timeout)
        except usb.core.USBError:
            pass
            #print("Timeout! Couldn't write")

    def print_data(self, data, raw_dec=False):
        if data and self.print_to_term_enabled:
            i = 0
            print("Serial Number: " + str(self.serial_number))
            print("Number of byte: " + str(len(data)))
            while i < len(data):
                if raw_dec:
                    char = int(data[i])
                else:
                    char = chr(data[i])
                print(char, end=' ')
                i +=1

            print('\n')

    def print_to_term(self, string):
        if self.print_to_term_enabled:
            print(string)


class TeensyMonitor(threading.Thread):

    def __init__(self, teensy_thread_table):

        self.teensy_thread_table = teensy_thread_table

        # start thread
        threading.Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):

        while True:

            for teensy_name in list(self.teensy_thread_table.keys()):
                if not self.teensy_thread_table[teensy_name].is_alive():
                    del self.teensy_thread_table[teensy_name]



if __name__ == '__main__':
    tm = TeensyManager()
