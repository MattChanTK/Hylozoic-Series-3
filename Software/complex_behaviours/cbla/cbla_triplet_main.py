import sys
from collections import defaultdict
from collections import OrderedDict

from interactive_system import CommunicationProtocol as CP
import interactive_system
from abstract_node import *

from cbla_spatial_node import *
from cbla_engine import cbla_data_collect, cbla_robot

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

class CBLA(interactive_system.InteractiveCmd):

    def __init__(self, Teensy_manager, auto_start=True, mode='spatial'):

        data_file = None
        if USE_SAVED_DATA:
            data_file, _ = cbla_data_collect.retrieve_data()

        self.data_collector = cbla_data_collect.DataCollector(data_file=data_file)
        self.node_list = OrderedDict()

        self.all_nodes_created = threading.Condition()

        self.mode = mode

        self.num_fin = 3
        self.num_light = 3

        super(CBLA, self).__init__(Teensy_manager, auto_start=auto_start)


    # ========= the Run function for the CBLA system based on the abstract node system=====
    def run(self):

        self.messenger = interactive_system.Messenger(self, 0.000)

        for teensy_name in self.teensy_manager.get_teensy_name_list():
            # ------ set mode ------
            cmd_obj = interactive_system.command_object(teensy_name, 'basic')
            cmd_obj.add_param_change('operation_mode', CP.CBLATestBed_Triplet_FAST.MODE_CBLA2_PRESCRIPTED)
            self.enter_command(cmd_obj)

            # ------ configuration ------
            # set the Fin on/off periods
            cmd_obj = interactive_system.command_object(teensy_name, 'fin_high_level')
            for j in range(3):
                device_header = 'fin_%d_' % j
                cmd_obj.add_param_change(device_header + 'arm_cycle_on_period', 15)
                cmd_obj.add_param_change(device_header + 'arm_cycle_off_period', 55)
            self.enter_command(cmd_obj)
        self.send_commands()

        # initially update the Teensys with all the output parameters here
        self.update_output_params(self.teensy_manager.get_teensy_name_list())

        # start the messenger
        self.messenger.start()

        teensy_in_use = tuple(self.teensy_manager.get_teensy_name_list())

        # instantiate all the basic components
        for teensy in teensy_in_use:

            # check if the teensy exists
            if teensy not in self.teensy_manager.get_teensy_name_list():
                print('%s does not exist!' % teensy)
                continue

            # ==== creating components related to the Light =====
            light_components = OrderedDict()
            for j in range(self.num_light):
               light_components.update(self.build_light_components(teensy_name=teensy, light_id=j))
            self.node_list.update(light_components)

            # ===== creating components for related to the Fins ====
            fin_components = OrderedDict()
            for j in range(self.num_fin):
                fin_components.update(self.build_fin_components(teensy_name=teensy, fin_id=j))
            self.node_list.update(fin_components)

        # ===== creating the CBLA Nodes ====
        if self.mode == 'spatial':
            for teensy in teensy_in_use:
                self.node_list.update(self.build_spatial_nodes(teensy, self.node_list))
        else:
            self.mode = 'spatial'
            for teensy in teensy_in_use:
                self.node_list.update(self.build_spatial_nodes(teensy, self.node_list))

        with self.all_nodes_created:
            self.all_nodes_created.notify_all()

        self.start_nodes()

        # wait for the nodes to destroy
        for node in self.node_list.values():
            node.join()

        return 0

    def build_fin_components(self, teensy_name, fin_id):

        fin_comps = OrderedDict()

        # 2 ir sensors each
        ir_s = Input_Node(self.messenger, teensy_name, node_name='f%d.ir-s' % fin_id, input='fin_%d_ir_0_state' % fin_id)
        ir_f = Input_Node(self.messenger, teensy_name, node_name='f%d.ir-f' % fin_id, input='fin_%d_ir_1_state' % fin_id)

        # 1 3-axis acceleromter each
        acc = Input_Node(self.messenger, teensy_name, node_name='f%d.acc' % fin_id,
                         x='fin_%d_acc_x_state' % fin_id,
                         y='fin_%d_acc_y_state' % fin_id,
                         z='fin_%d_acc_z_state' % fin_id)

        # acc diff
        acc_x_diff = Pseudo_Differentiation(self.messenger, node_name='%s.f%d.acc-x_diff' % (teensy_name, fin_id),
                                            input_var=acc.out_var['x'], diff_gap=5, smoothing=10,
                                            step_period=0.1)
        acc_y_diff = Pseudo_Differentiation(self.messenger, node_name='%s.f%d.acc-y_diff' % (teensy_name, fin_id),
                                            input_var=acc.out_var['y'], diff_gap=5, smoothing=10,
                                            step_period=0.1)
        acc_z_diff = Pseudo_Differentiation(self.messenger, node_name='%s.f%d.acc-z_diff' % (teensy_name, fin_id),
                                            input_var=acc.out_var['z'], diff_gap=5, smoothing=10,
                                            step_period=0.1)

        # acc running average
        acc_x_avg = Running_Average(self.messenger, node_name='%s.f%d.acc-x_avg' % (teensy_name, fin_id),
                                    input_var=acc.out_var['x'], avg_window=10, step_period=0.1)
        acc_y_avg = Running_Average(self.messenger, node_name='%s.f%d.acc-y_avg' % (teensy_name, fin_id),
                                    input_var=acc.out_var['y'], avg_window=10, step_period=0.1)
        acc_z_avg = Running_Average(self.messenger, node_name='%s.f%d.acc-z_avg' % (teensy_name, fin_id),
                                    input_var=acc.out_var['z'], avg_window=10, step_period=0.1)

        fin_comps[acc_x_avg.node_name] = acc_x_avg
        fin_comps[acc_y_avg.node_name] = acc_y_avg
        fin_comps[acc_z_avg.node_name] = acc_z_avg

        fin_comps[acc_x_diff.node_name] = acc_x_diff
        fin_comps[acc_y_diff.node_name] = acc_y_diff
        fin_comps[acc_z_diff.node_name] = acc_z_diff

        # 2 SMA wires each
        sma_l = Output_Node(self.messenger, teensy_name, node_name='f%d.sma-l' % fin_id, output='fin_%d_sma_0_level' % fin_id)
        sma_r = Output_Node(self.messenger, teensy_name, node_name='f%d.sma-r' % fin_id, output='fin_%d_sma_1_level' % fin_id)

        # 2 reflex each
        reflex_l = Output_Node(self.messenger, teensy_name, node_name='f%d.rfx-l' % fin_id, output='fin_%d_reflex_0_level' % fin_id)
        reflex_m = Output_Node(self.messenger, teensy_name, node_name='f%d.rfx-m' % fin_id, output='fin_%d_reflex_1_level' % fin_id)

        fin_comps[ir_s.node_name] = ir_s
        fin_comps[ir_f.node_name] = ir_f
        fin_comps[acc.node_name] = acc
        fin_comps[sma_l.node_name] = sma_l
        fin_comps[sma_r.node_name] = sma_r
        fin_comps[reflex_l.node_name] = reflex_l
        fin_comps[reflex_m.node_name] = reflex_m

        # 2 half-fin modules
        sma_temp_l = Var(0)
        half_fin_l = Half_Fin(self.messenger, node_name='%s.f%d.hf-l' % (teensy_name, fin_id),
                              sma=sma_l.in_var['output'], temp_ref=sma_temp_l)
        sma_temp_r = Var(0)
        half_fin_r = Half_Fin(self.messenger, node_name='%s.f%d.hf-r' % (teensy_name, fin_id),
                              sma=sma_r.in_var['output'], temp_ref=sma_temp_r)

        fin_comps[half_fin_l.node_name] = half_fin_l
        fin_comps[half_fin_r.node_name] = half_fin_r

        return fin_comps

    def build_light_components(self, teensy_name, light_id):

        light_comps = OrderedDict()

        # 1 LED per protocell
        led = Output_Node(self.messenger, teensy_name=teensy_name, node_name='l%d.led' % light_id,
                          output='light_%d_led_level' % light_id)

        light_comps[led.node_name] = led

        # 1 ambient light sensor per protocell
        als = Input_Node(self.messenger, teensy_name=teensy_name, node_name='l%d.als' % light_id,
                         input='light_%d_als_state' % light_id)

        light_comps[als.node_name] = als

        # 1 LED driver
        led_driver = LED_Driver(self.messenger, node_name="%s.l%d.led_driver" % (teensy_name, light_id),
                                led_out=led.in_var['output'], step_period=0.001)
        light_comps[led_driver.node_name] = led_driver

        return light_comps

    def build_spatial_nodes(self, teensy_name, components):

        cbla_nodes = OrderedDict()

        # ===== constructing the Light Node =====
        for j in range(self.num_light):
            in_vars = OrderedDict()
            in_vars['als'] = components['%s.l%d.als' % (teensy_name, j)].out_var['input']
            in_vars['ir-f'] = components['%s.f%d.ir-f' % (teensy_name, j)].out_var['input']

            out_vars = OrderedDict()
            out_vars['led'] = components['%s.l%d.led' % (teensy_name, j)].in_var['output']

            light_node = CBLA_Light_Node(messenger=self.messenger, data_collector=self.data_collector,
                                         cluster_name=teensy_name, node_type='light', node_id=j,
                                         in_vars=in_vars, out_vars=out_vars,
                                         s_keys=('als', 'ir-f'), s_ranges=((0,4095), (0, 4095)),
                                         s_names=('ambient light sensor', 'fin IR sensor'),
                                         m_keys=('led',), m_ranges=((0, 255),),
                                         m_names=('High-power LED', ),
                                         )

            cbla_nodes[light_node.node_name] = light_node

        # ===== constructing the Half-Fin Nodes =====
        for j in range(self.num_fin):

            # ===== constructing the shared part of the Half-Fin Nodes ====
            in_vars = OrderedDict()
            in_vars['ir-f'] = components['%s.f%d.ir-f' % (teensy_name, j)].out_var['input']
            in_vars['acc-x'] = components['%s.f%d.acc' % (teensy_name, j)].out_var['x']
            in_vars['acc-y'] = components['%s.f%d.acc' % (teensy_name, j)].out_var['y']
            in_vars['acc-z'] = components['%s.f%d.acc' % (teensy_name, j)].out_var['z']
            in_vars['acc-x_diff'] = components['%s.f%d.acc-x_diff' % (teensy_name, j)].out_var['output']
            in_vars['acc-y_diff'] = components['%s.f%d.acc-y_diff' % (teensy_name, j)].out_var['output']
            in_vars['acc-z_diff'] = components['%s.f%d.acc-z_diff' % (teensy_name, j)].out_var['output']
            in_vars['acc-x_avg'] = components['%s.f%d.acc-x_avg' % (teensy_name, j)].out_var['output']
            in_vars['acc-y_avg'] = components['%s.f%d.acc-y_avg' % (teensy_name, j)].out_var['output']
            in_vars['acc-z_avg'] = components['%s.f%d.acc-z_avg' % (teensy_name, j)].out_var['output']

            # ===== constructing the left Half-Fin Nodes ====
            in_vars_left = in_vars.copy()
            in_vars_left['ir-s'] = components['%s.f%d.ir-s' % (teensy_name, j)].out_var['input']

            out_vars_left = OrderedDict()
            out_vars_left['hf-l'] = components['%s.f%d.hf-l' % (teensy_name, j)].in_var['temp_ref']

            half_fin_left = CBLA_HalfFin_Node(messenger=self.messenger, data_collector=self.data_collector,
                                              cluster_name=teensy_name, node_type='halfFin', node_id=j, node_version='l',
                                              in_vars=in_vars_left, out_vars=out_vars_left,
                                              s_keys=('ir-f', 'ir-s', 'acc-x_diff', 'acc-y_diff', 'acc-z_diff'),
                                              s_ranges=((0, 4095), (0, 4095), (-6, 6), (-6, 6), (-6, 6)),
                                              s_names=('fin IR sensor', 'scout IR sensor',
                                                       'accelerometer (x-diff)', 'accelerometer (y-diff)', 'accelerometer (z-diff)',),
                                              m_keys=('hf-l', ), m_ranges=((0, 300), ), m_names=('Half Fin Input',)
                                              )

            cbla_nodes[half_fin_left.node_name] = half_fin_left

            # ===== constructing the right Half-Fin Nodes ====
            in_vars_right = in_vars.copy()
            in_vars_right['ir-s'] = components['%s.f%d.ir-s' % (teensy_name, (j + 1) % self.num_fin)].out_var['input']

            out_vars_right= OrderedDict()
            out_vars_right['hf-r'] = components['%s.f%d.hf-r' % (teensy_name, j)].in_var['temp_ref']

            half_fin_right = CBLA_HalfFin_Node(messenger=self.messenger, data_collector=self.data_collector,
                                               cluster_name=teensy_name, node_type='halfFin', node_id=j, node_version='r',
                                               in_vars=in_vars_right, out_vars=out_vars_right,
                                               s_keys=('ir-f', 'ir-s', 'acc-x_diff', 'acc-y_diff', 'acc-z_diff'),
                                               s_ranges=((0, 4095), (0, 4095), (-6, 6), (-6, 6), (-6, 6)),
                                               s_names=('fin IR sensor', 'scout IR sensor',
                                                        'accelerometer (x-diff)', 'accelerometer (y-diff)', 'accelerometer (z-diff)',),
                                               m_keys=('hf-r', ), m_ranges=((0, 300), ), m_names=('half-fin input',)
                                              )

            cbla_nodes[half_fin_right.node_name] = half_fin_right

        # ===== constructing the Reflex Nodes =====
        for j in range(self.num_fin):

            # ===== constructing the shared part of the Reflex Nodes ====
            in_vars = OrderedDict()
            in_vars['ir-s'] = components['%s.f%d.ir-s' % (teensy_name, j)].out_var['input']
            in_vars['sma-l'] = components['%s.f%d.sma-l' % (teensy_name, j)].in_var['output']
            in_vars['sma-r'] = components['%s.f%d.sma-r' % (teensy_name, j)].in_var['output']

            # ===== constructing the Reflex Motor Node ====
            out_vars_motor = OrderedDict()
            out_vars_motor['rfx-m'] = components['%s.f%d.rfx-m' % (teensy_name, j)].in_var['output']
            reflex_motor = CBLA_Reflex_Node(messenger=self.messenger, data_collector=self.data_collector,
                                            cluster_name=teensy_name, node_type='reflex', node_id=j, node_version='m',
                                            in_vars=in_vars, out_vars=out_vars_motor,
                                            s_keys=('ir-s', 'sma-l', 'sma-r'),
                                            s_ranges=((0, 4095), (0, 255), (0, 255)),
                                            s_names=('scout IR sensor', 'SMA output (left)', 'SMA output (right)'),
                                            m_keys=('rfx-m', ), m_ranges=((0, 255), ), m_names=('reflex motor',)
                                           )

            cbla_nodes[reflex_motor.node_name] = reflex_motor

            # ===== constructing the Reflex LED Node ====
            out_vars_led = OrderedDict()
            out_vars_led['rfx-l'] = components['%s.f%d.rfx-l' % (teensy_name, j)].in_var['output']
            reflex_led = CBLA_Reflex_Node(messenger=self.messenger, data_collector=self.data_collector,
                                            cluster_name=teensy_name, node_type='reflex', node_id=j, node_version='l',
                                            in_vars=in_vars, out_vars=out_vars_led,
                                            s_keys=('ir-s', 'sma-l', 'sma-r'),
                                            s_ranges=((0, 4095), (0, 255), (0, 255)),
                                            s_names=('scout IR sensor', 'SMA output (left)', 'SMA output (right)'),
                                            m_keys=('rfx-l', ), m_ranges=((0, 255), ), m_names=('reflex led',)
                                           )

            cbla_nodes[reflex_led.node_name] = reflex_led

        return cbla_nodes


    def start_nodes(self):

        if not isinstance(self.node_list, dict) or \
           not isinstance(self.data_collector, cbla_data_collect.DataCollector) or \
           not isinstance(self.messenger, interactive_system.Messenger):
            raise AttributeError("Nodes have not been created properly!")

        for name, node in self.node_list.items():
            node.start()
            print('%s initialized' % name)
        print('System Initialized with %d nodes' % len(self.node_list))

        # start the Data Collector
        self.data_collector.start()
        print('Data Collector initialized.')

    # loop that poll user's input from the console
    def termination_input_thread(self):

        if not isinstance(self.node_list, dict) or \
           not isinstance(self.data_collector, cbla_data_collect.DataCollector):
            raise AttributeError("Nodes have not been created properly!")

        input_str = ''
        while not input_str == 'exit':
            input_str = input("\nEnter 'exit' to terminate program: \t")

            if input_str == 'save_states':
                CBLA.save_cbla_node_states(self.node_list)
                print('state_saved')

            else:
                if not input_str == 'exit':
                    print('command does not exist!')

        self.terminate()

    def terminate(self):
        # killing each of the Node
        for node in self.node_list.values():
            node.alive = False
        for node in self.node_list.values():
            node.join()
            print('%s is terminated.' % node.node_name)

        # terminating the data_collection thread
        self.data_collector.end_data_collection()
        self.data_collector.join()
        print("Data Collector is terminated.")

        # killing each of the Teensy threads
        for teensy_name in list(self.teensy_manager.get_teensy_name_list()):
            self.teensy_manager.kill_teensy_thread(teensy_name)

    @staticmethod
    def save_cbla_node_states(node_list):

        for node in node_list.values():
            if isinstance(node, CBLA_Base_Node):
                node.save_states()



def hmi_init(hmi: tk_gui.Master_Frame, messenger: interactive_system.Messenger, node_list: dict):

    if not isinstance(hmi, tk_gui.Master_Frame):
        raise TypeError("HMI must be Master_Frame")
    if not isinstance(node_list, dict):
        raise TypeError("node_list must be a dictionary")

    hmi.wm_title('CBLA Mode')

    status_frame = tk_gui.Messenger_Status_Frame(hmi, messenger)
    content_frame = tk_gui.Content_Frame(hmi)
    nav_frame = tk_gui.Navigation_Frame(hmi, content_frame)

    cbla_display_vars = defaultdict(OrderedDict)
    device_display_vars = defaultdict(OrderedDict)

    if len(node_list) > 0:

        for name, node in node_list.items():
            node_name = name.split('.')
            teensy_name = node_name[0]
            device_name = node_name[1]

            if isinstance(node, CBLA_Base_Node):
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

    print('GUI initialized.')
    hmi.start(status_frame=status_frame,
              nav_frame=nav_frame,
              content_frame=content_frame,
              start_page_key=next(iter(page_frames.keys()), ''))


if __name__ == "__main__":

    mode_config = 'spatial'

    if len(sys.argv) > 1:
        mode_config = str(sys.argv[1])

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
        # -- this create all the abstract nodes
        behaviours = CBLA(teensy_manager, auto_start=True, mode='spatial')

        if not isinstance(behaviours, CBLA):
            raise TypeError("Behaviour must be CBLA type!")

        with behaviours.all_nodes_created:
            behaviours.all_nodes_created.wait()

        # initialize the gui
        hmi = tk_gui.Master_Frame()
        hmi_init(hmi, behaviours.messenger, behaviours.node_list)

        behaviours.terminate()

        for teensy_thread in teensy_manager._get_teensy_thread_list():
            teensy_thread.join()

        print("All Teensy threads terminated")

    main()
    print("\n===== Program Safely Terminated=====")