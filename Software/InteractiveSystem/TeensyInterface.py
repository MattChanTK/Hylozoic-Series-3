import usb.core
import usb.util
import threading
import random
import struct
import changePriority
import sys
from time import clock

TEENSY_VENDOR_ID = 0x16C0
TEENSY_PRODUCT_ID = 0x0486

class TeensyManager(threading.Thread):

    def __init__(self):

        # find all connected Teensy
        self.__find_teensy_serial_number()

        self.Teensy_thread_list = []

        self.unit_config = 'SIMPLIFIED_TEST_UNIT'
        self.print_to_term = False

        # create all the initial Teensy Threads
        Teensy_id = 0
        for serial_num in self.serial_num_list:
            print("Teensy " + str(Teensy_id) + " --- " + str(serial_num))
            Teensy_id += 1

            # create a new thread for communicating with
            try:
                Teensy_thread = TeensyInterface(serial_num, unit_config=self.unit_config, print_to_term=self.print_to_term)
                self.Teensy_thread_list.append(Teensy_thread)
            except Exception as e:
                print(str(e))

        # start thread
        threading.Thread.__init__(self)
        self.daemon = False
        self.start()


    def run(self):

        # #wait for each thread to terminate
        for t in self.get_teensy_thread_list():
            t.join()

        print("All threads terminated")

    def get_teensy_serial_num(self):
        return self.serial_num_list

    def get_teensy_thread_list(self):
        return self.Teensy_thread_list

    def __find_teensy_serial_number(self, vendor_id=TEENSY_VENDOR_ID, product_id=TEENSY_PRODUCT_ID):

        # find our device
        dev_iter = usb.core.find(find_all=True, idVendor=vendor_id, idProduct=product_id)

        serialNum = []
        for iter in dev_iter:
            serialNum.append(iter.serial_number)

        self.serial_num_list = tuple(serialNum)





class TeensyInterface(threading.Thread):

    packet_size_in = 64
    packet_size_out = 64

    def __init__(self, serial_num, vendor_id=TEENSY_VENDOR_ID, product_id=TEENSY_PRODUCT_ID, print_to_term=False, unit_config='default'):

        if unit_config == 'FULL_TEST_UNIT':
            from TestUnitConfiguration import FullTestUnit as SysParam
        elif unit_config == 'SIMPLIFIED_TEST_UNIT':
            from TestUnitConfiguration import SimplifiedTestUnit as SysParam
        else:
            from SystemParameters import SimplifiedTestUnit as SysParam

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

        # instantiate the system parameters
        self.param = SysParam()

        # event is set when parameters are updated by the main thread
        self.param_updated_event = threading.Event()

        # event is set when the Teensy thread updated the inputs parameters
        self.inputs_sampled_event = threading.Event()

        self.lock = threading.Lock()

        # start thread
        threading.Thread.__init__(self)
        self.daemon = False
        self.start()


        # print to terminal or not
        self.print_to_term_enabled = print_to_term

    def run(self):
        # change priority of the the Python process to HIGH
        changePriority.SetPriority(changePriority.Priorities.REALTIME_PRIORITY_CLASS)

        while True:

            self.lock.acquire()

            if self.connected:
                self.lock.release()
            else:
                # release lock before terminating
                self.lock.release()
                # terminate itself
                return

            if self.param_updated_event.wait(timeout=1):

                self.param_updated_event.clear()

                self.lock.acquire()
                try:
                    self.inputs_sampled_event.clear()

                    self.print_to_term("Teensy thread: lock acquired, sampled event cleared")


                    # compose the data
                    out_msg, front_id, back_id = self.compose_msg()


                    # sending the data
                    # start_time = clock()
                    self.talk_to_Teensy(out_msg, timeout=0)
                    self.print_to_term("\n---Sent---")
                    self.print_data(out_msg, raw_dec=True)

                    # waiting for reply
                    received_reply = False
                    data = self.listen_to_Teensy(timeout=100, byte_num=TeensyInterface.packet_size_in)
                    invalid_reply_counter = 0
                    no_reply_counter = 0
                    while received_reply is False:
                        if data:
                            # check if reply matches sent message
                            if data[0] == front_id and data[-1] == back_id:
                                received_reply = True
                                self.param.parse_message_content(data)
                                self.inputs_sampled_event.set()
                                self.print_to_term("Teensy thread: input sampled")

                                self.print_to_term("---Received Reply---")
                                self.print_data(data, raw_dec=True)

                            else:
                                self.print_to_term("......Received invalid reply......")
                                self.print_data(data, raw_dec=True)

                                invalid_reply_counter += 1
                                if invalid_reply_counter > 5:
                                    print(str(self.serial_number) + "......Number of invalid replies exceeded 5! Stopped trying......")
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
                            print("Teensy (" + str(self.serial_number) + ")......Didn't receive any reply. Packet lost......." + str(no_reply_counter))
                            if no_reply_counter >= 5:
                                print("Teensy (" + str(self.serial_number) + ") has probably been disconnected.")

                                return
                finally:
                    self.lock.release()
                # print(self.serial_number, " - Echo time: ", clock() - start_time)
                self.print_to_term("Teensy thread: lock released")



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

        ep = usb.util.find_descriptor(
            self.intf,  # match the first IN endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN and \
                usb.util.endpoint_type(e.bEndpointAddress) == usb.util.ENDPOINT_TYPE_INTR)

        assert ep is not None

        try:
            data = ep.read(byte_num, timeout)
        except usb.core.USBError:
            #print("Timeout! Couldn't read anything")
            data = None

        return data

    def talk_to_Teensy(self, out_msg, timeout=10):

        ep = usb.util.find_descriptor(
            self.intf,
            # match the first OUT endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT and \
                usb.util.endpoint_type(e.bEndpointAddress) == usb.util.ENDPOINT_TYPE_CTRL)

        assert ep is not None

        try:
            ep.write(out_msg, timeout)
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


