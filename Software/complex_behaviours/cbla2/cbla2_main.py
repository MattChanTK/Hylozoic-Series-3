import sys
from collections import defaultdict
from collections import OrderedDict

from interactive_system import CommunicationProtocol as CP
import interactive_system
from abstract_node import *

#import old_gui
import cbla_node
from cbla_engine import cbla_data_collect

from complex_node import *

try:
    from custom_gui import *
except ImportError:
    import sys
    import os
    sys.path.insert(1, os.path.join(os.getcwd(), '..'))
    from custom_gui import *



USE_SAVED_DATA = False

if len(sys.argv) > 1:
    USE_SAVED_DATA = bool(sys.argv[1])

class CBLA2(interactive_system.InteractiveCmd):

    # ========= the Run function for the CBLA system based on the abstract node system=====
    def run(self):

        data_file = None
        if USE_SAVED_DATA:
            data_file, _ = cbla_data_collect.retrieve_data()

        data_collector = cbla_data_collect.DataCollector(data_file=data_file)

        for teensy_name in self.teensy_manager.get_teensy_name_list():
            # ------ set mode ------
            cmd_obj = interactive_system.command_object(teensy_name, 'basic')
            cmd_obj.add_param_change('operation_mode', CP.CBLATestBed_FAST.MODE_CBLA2)
            self.enter_command(cmd_obj)

            # ------ configuration ------
            # set the Tentacle on/off periods
            cmd_obj = interactive_system.command_object(teensy_name, 'tentacle_high_level')
            for j in range(3):
                device_header = 'tentacle_%d_' % j
                cmd_obj.add_param_change(device_header + 'arm_cycle_on_period', 15)
                cmd_obj.add_param_change(device_header + 'arm_cycle_off_period', 55)
            self.enter_command(cmd_obj)
        self.send_commands()

        # initially update the Teensys with all the output parameters here
        self.update_output_params(self.teensy_manager.get_teensy_name_list())

        # start the messenger
        messenger = interactive_system.Messenger(self, 0.000)
        messenger.start()

        teensy_0 = 'test_teensy_1'
        teensy_1 = 'test_teensy_3'
        teensy_2 = 'HK_teensy_1'
        teensy_3 = 'HK_teensy_2'
        teensy_4 = 'HK_teensy_3'

        teensy_in_use = (teensy_0, teensy_1, teensy_2, teensy_3, teensy_4,)

        node_list = OrderedDict()
        # instantiate all the basic components
        for teensy in teensy_in_use:

            # check if the teensy exists
            if teensy not in self.teensy_manager.get_teensy_name_list():
                print('%s does not exist!' % teensy)
                continue

            # ===== components for the 3 tentacles ====
            for j in range(3):

                # 2 ir sensors each
                ir_sensor_0 = Input_Node(messenger, teensy, node_name='tentacle_%d.ir_0' % j, input='tentacle_%d_ir_0_state' % j)
                ir_sensor_1 = Input_Node(messenger, teensy, node_name='tentacle_%d.ir_1' % j, input='tentacle_%d_ir_1_state' % j)

                # 1 3-axis acceleromter each
                acc = Input_Node(messenger, teensy, node_name='tentacle_%d.acc' % j, x='tentacle_%d_acc_x_state' % j,
                                                                                     y='tentacle_%d_acc_y_state' % j,
                                                                                     z='tentacle_%d_acc_z_state' % j)

                # 2 SMA wires each
                sma_0 = Output_Node(messenger, teensy, node_name='tentacle_%d.sma_0' % j, output='tentacle_%d_sma_0_level' % j)
                sma_1 = Output_Node(messenger, teensy, node_name='tentacle_%d.sma_1' % j, output='tentacle_%d_sma_1_level' % j)

                # 2 reflex each
                reflex_0 = Output_Node(messenger, teensy, node_name='tentacle_%d.reflex_0' % j, output='tentacle_%d_reflex_0_level' % j)
                reflex_1 = Output_Node(messenger, teensy, node_name='tentacle_%d.reflex_1' % j, output='tentacle_%d_reflex_1_level' % j)

                node_list[ir_sensor_0.node_name] = ir_sensor_0
                node_list[ir_sensor_1.node_name] = ir_sensor_1
                node_list[acc.node_name] = acc
                node_list[sma_0.node_name] = sma_0
                node_list[sma_1.node_name] = sma_1
                node_list[reflex_0.node_name] = reflex_0
                node_list[reflex_1.node_name] = reflex_1

                # 1 frond each
                motion_type = Var(0)
                frond = Frond(messenger, teensy, node_name='tentacle_%d.frond' % j, left_sma=sma_0.in_var['output'],
                              right_sma=sma_1.in_var['output'],
                              motion_type=motion_type)
                node_list[frond.node_name] = frond

            # ==== creating components for Protocell Node =====

            # 1 LED per protocell
            led = Output_Node(messenger, teensy_name=teensy, node_name='protocell.led',
                              output='protocell_0_led_level')

            node_list[led.node_name] = led

            # 1 ambient light sensor per protocell
            als = Input_Node(messenger, teensy, node_name='protocell.als',
                             input='protocell_0_als_state')

            node_list[als.node_name] = als

            shared_ir_0_var = node_list['%s.tentacle_2.ir_0' % teensy].out_var['input']

            # ===== constructing the tentacle ====
            for j in range(3):

                ir_sensor_0 = node_list['%s.tentacle_%d.ir_0' % (teensy, j)]
                ir_sensor_1 = node_list['%s.tentacle_%d.ir_1' % (teensy, j)]
                acc = node_list['%s.tentacle_%d.acc' % (teensy, j)]
                frond = node_list['%s.tentacle_%d.frond' % (teensy, j)]
                reflex_0 = node_list['%s.tentacle_%d.reflex_0' % (teensy, j)]
                reflex_1 = node_list['%s.tentacle_%d.reflex_1' % (teensy, j)]

                cbla_tentacle = cbla_node.CBLA_Tentacle(messenger, teensy, data_collector,
                                                        node_name='cbla_tentacle_%d' % j,
                                                        ir_0=ir_sensor_0.out_var['input'],
                                                        ir_1=ir_sensor_1.out_var['input'],
                                                        acc=Var([acc.out_var['x'], acc.out_var['y'], acc.out_var['z']]),
                                                        frond=frond.in_var['motion_type'],
                                                        reflex_0=reflex_0.in_var['output'],
                                                        reflex_1=reflex_1.in_var['output'],
                                                        shared_ir_0=shared_ir_0_var)
                node_list[cbla_tentacle.node_name] = cbla_tentacle

            # ===== constructing the Protocell ======
            als = node_list['%s.protocell.als' % teensy]
            led = node_list['%s.protocell.led' % teensy]
            cbla_protocell = cbla_node.CBLA_Protocell(messenger, teensy, data_collector,
                                                      node_name='cbla_protocell',
                                                      als=als.out_var['input'],
                                                      led=led.in_var['output'],
                                                      shared_ir_0=shared_ir_0_var)
            node_list[cbla_protocell.node_name] = cbla_protocell

        self.node_list = node_list
        self.messenger = messenger

        # initialize each node
        self.start_nodes()

        # initialize the gui
        self.hmi = tk_gui.Master_Frame()
        print('GUI initialized.')

        # start the Data Collector
        data_collector.start()
        print('Data Collector initialized.')

        # start thread that kill program with any input
        threading.Thread(target=self.termination_input_thread,
                         args=(node_list, data_collector, self.hmi),
                         daemon=True, name='termination_input').start()

        self.hmi_init()

    def start_nodes(self):

        for name, node in self.node_list.items():
            node.start()
            print('%s initialized' % name)
        print('System Initialized with %d nodes' % len(self.node_list))

    def hmi_init(self):

        self.hmi.wm_title('CBLA Mode')

        status_frame = tk_gui.Messenger_Status_Frame(self.hmi, self.messenger)
        content_frame = tk_gui.Content_Frame(self.hmi)
        nav_frame = tk_gui.Navigation_Frame(self.hmi, content_frame)

        cbla_display_vars = defaultdict(OrderedDict)
        device_display_vars = defaultdict(OrderedDict)

        if len(self.node_list) > 0:

            for name, node in self.node_list.items():

                node_name = name.split('.')
                teensy_name = node_name[0]
                device_name = node_name[1]

                if isinstance(node, cbla_node.CBLA_Node):
                    for var_name, var in node.in_var.items():

                        # specifying the displayable variables
                        if device_name not in cbla_display_vars[teensy_name]:
                            cbla_display_vars[teensy_name][device_name] = OrderedDict()

                        cbla_display_vars[teensy_name][device_name][var_name] = ({var_name: var}, 'input_node')

                    for var_name, var in node.out_var.items():

                        # specifying the displayable variables
                        if device_name not in cbla_display_vars[teensy_name]:
                            cbla_display_vars[teensy_name][device_name] = OrderedDict()

                        cbla_display_vars[teensy_name][device_name][var_name] = ({var_name: var}, 'output_node')

                else:
                    try:
                        output_name = node_name[2]
                    except IndexError:
                        output_name = "variables"

                    # specifying the displayable variables
                    if device_name not in device_display_vars[teensy_name]:
                        device_display_vars[teensy_name][device_name] = OrderedDict()

                    if isinstance(node, Input_Node):
                        device_display_vars[teensy_name][device_name][output_name] = (node.out_var, 'input_node')
                    elif isinstance(node, Output_Node):
                        device_display_vars[teensy_name][device_name][output_name] = (node.in_var, 'output_node')
                    else:
                        device_display_vars[teensy_name][device_name][output_name + "_input"] = (node.in_var, 'input_node')
                        device_display_vars[teensy_name][device_name][output_name + "_output"] = (node.out_var, 'output_node')

        page_frames = OrderedDict()
        for teensy_name, teensy_display_vars in device_display_vars.items():

            teensy_cbla_vars = OrderedDict()
            if teensy_name in cbla_display_vars.keys():
                teensy_cbla_vars = cbla_display_vars[teensy_name]
            frame = HMI_CBLA_Mode(content_frame, teensy_name, (teensy_name, 'cbla_display_page'),
                                         teensy_cbla_vars, teensy_display_vars)
            page_frames[frame.page_key] = frame

            content_frame.build_pages(page_frames)

            nav_frame.build_nav_buttons()

        self.hmi.start(status_frame=status_frame,
                       nav_frame=nav_frame,
                       content_frame=content_frame,
                       start_page_key=next(iter(page_frames.keys()), ''))

    def termination_input_thread(self, node_list, data_collector: cbla_data_collect.DataCollector, gui_root: tk_gui.Tk):

        input_str = ''
        while not input_str == 'exit':
            input_str = input("\nEnter 'exit' to terminate program: \t")

            if input_str == 'save_states':
                CBLA2.save_cbla_node_states(node_list)
                print('state_saved')

            else:
                if not input_str == 'exit':
                    print('command does not exist!')
        # terminate the gui
        gui_root.quit()
        print('GUI is terminated.')

        # killing each of the Node
        for node in node_list.values():
            node.alive = False
        for node in node_list.values():
            node.join()
            print('%s is terminated.' % node.node_name)

        # terminating the data_collection thread
        data_collector.end_data_collection()
        data_collector.join()
        print("Data Collector is terminated.")

        # killing each of the Teensy threads
        for teensy_name in list(self.teensy_manager.get_teensy_name_list()):
            self.teensy_manager.kill_teensy_thread(teensy_name)

    @staticmethod
    def save_cbla_node_states(node_list):

        for node in node_list.values():
            if isinstance(node, cbla_node.CBLA_Node):
                node.save_states()





if __name__ == "__main__":

    cmd = CBLA2

    # None means all Teensy's connected will be active; otherwise should be a tuple of names
    ACTIVE_TEENSY_NAMES = None  # ('test_teensy_88',)
    MANDATORY_TEENSY_NAMES = ACTIVE_TEENSY_NAMES

    def main():

        # instantiate Teensy Monitor
        teensy_manager = interactive_system.TeensyManager(import_config=True)

        # find all the Teensy
        print("Number of Teensy devices found: " + str(teensy_manager.get_num_teensy_thread()))

        # kill all and only leave those specified in ACTIVE_TEENSY_NAMES
        all_teensy_names = list(teensy_manager.get_teensy_name_list())
        if isinstance(ACTIVE_TEENSY_NAMES, tuple):
            for teensy_name in all_teensy_names:
                if teensy_name not in ACTIVE_TEENSY_NAMES:
                    teensy_manager.kill_teensy_thread(teensy_name)

        # check if all the mandatory ones are still there
        all_teensy_names = list(teensy_manager.get_teensy_name_list())
        if isinstance(MANDATORY_TEENSY_NAMES, tuple):
            for teensy_name in MANDATORY_TEENSY_NAMES:
                if teensy_name not in all_teensy_names:
                    raise Exception('%s is missing!!' % teensy_name)

        # find all the Teensy
        print("Number of active Teensy devices: %s\n" % str(teensy_manager.get_num_teensy_thread()))


        # interactive code
        behaviours = cmd(teensy_manager)

        for teensy_thread in teensy_manager._get_teensy_thread_list():
            teensy_thread.join()

        print("All Teensy threads terminated")

    main()

    print("\n===== Program Terminated =====")