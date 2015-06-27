import interactive_system
from interactive_system import CommunicationProtocol as CP

from complex_node import *

try:
    from custom_gui import *
except ImportError:
    import sys
    import os
    sys.path.insert(1, os.path.join(os.getcwd(), '..'))
    from custom_gui import *


class Prescripted_Behaviour(interactive_system.InteractiveCmd):

    def __init__(self, Teensy_manager, auto_start=True, mode='default'):

        self.node_list = OrderedDict()
        #self.data_collector = None

        self.all_nodes_created = threading.Condition()

        self.num_fin = 3
        self.num_light = 3
        self.mode = mode

        super(Prescripted_Behaviour, self).__init__(Teensy_manager, auto_start=auto_start)

    # ========= the Run function for the prescripted behaviour system =====
    def run(self):

        self.messenger = interactive_system.Messenger(self, 0.000)

        for teensy_name in self.teensy_manager.get_teensy_name_list():
            # ------ set mode ------
            cmd_obj = interactive_system.command_object(teensy_name, 'basic')
            cmd_obj.add_param_change('operation_mode', CP.CBLATestBed_Triplet_FAST.MODE_CBLA2_PRESCRIPTED)
            self.enter_command(cmd_obj)

        self.send_commands()

        # initially update the Teensys with all the output parameters here
        self.update_output_params(self.teensy_manager.get_teensy_name_list())

        # start the messenger
        self.messenger.start()

        teensy_in_use = tuple(self.teensy_manager.get_teensy_name_list())

        # table of all data variables being collected
       # data_variables = dict()

        # instantiate all the basic components
        for teensy in teensy_in_use:

            # check if the teensy exists
            if teensy not in self.teensy_manager.get_teensy_name_list():
                print('%s does not exist!' % teensy)
                continue

             # ==== creating components related to the Light =====
            light_components = OrderedDict()
            for j in range(self.num_light):
                components, data_vars = self.build_light_components(teensy_name=teensy, light_id=j)
                light_components.update(components)
             #   data_variables.update(data_vars)
            self.node_list.update(light_components)


            # ===== creating components for related to the Fins ====
            fin_components = OrderedDict()
            for j in range(self.num_fin):
                components, data_vars = self.build_fin_components(teensy_name=teensy, fin_id=j)
                fin_components.update(components)
             #   data_variables.update(data_vars)
            self.node_list.update(fin_components)


         # ===== creating the CBLA Nodes ====
        if self.mode == 'default':
            for teensy in teensy_in_use:
                self.node_list.update(self.build_default_nodes(teensy, self.node_list))
        else:
            self.mode = 'default'
            for teensy in teensy_in_use:
                self.node_list.update(self.build_default_nodes(teensy, self.node_list))

        #self.data_collector = Data_Collector_Node(self.messenger, file_header='prescripted_mode_data', **data_variables)

        with self.all_nodes_created:
            self.all_nodes_created.notify_all()

        self.start_nodes()
        #self.data_collector.start()

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

        # 2 SMA wires each
        sma_r = Output_Node(self.messenger, teensy_name, node_name='f%d.sma-r' % fin_id, output='fin_%d_sma_0_level' % fin_id)
        sma_l = Output_Node(self.messenger, teensy_name, node_name='f%d.sma-l' % fin_id, output='fin_%d_sma_1_level' % fin_id)

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

        # collecting data
        data_variables = OrderedDict()
        # collecting their values
        data_variables['%s.fin_%d.ir-s' % (teensy_name, fin_id)] = ir_s.out_var['input']
        data_variables['%s.fin_%d.ir-f' % (teensy_name, fin_id)] = ir_f.out_var['input']

        data_variables['%s.fin_%d.acc-x' % (teensy_name, fin_id)] = acc.out_var['x']
        data_variables['%s.fin_%d.acc-y' % (teensy_name, fin_id)] = acc.out_var['y']
        data_variables['%s.fin_%d.acc-z' % (teensy_name, fin_id)] = acc.out_var['z']

        data_variables['%s.fin_%d.sma-l' % (teensy_name, fin_id)] = sma_l.in_var['output']
        data_variables['%s.fin_%d.sma-r' % (teensy_name, fin_id)] = sma_r.in_var['output']
        data_variables['%s.fin_%d.rfx-l' % (teensy_name, fin_id)] = reflex_l.in_var['output']
        data_variables['%s.fin_%d.rfx-m' % (teensy_name, fin_id)] = reflex_m.in_var['output']


        return fin_comps, data_variables

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

        # # 1 LED driver
        # led_driver = LED_Driver(self.messenger, node_name="%s.l%d.led_driver" % (teensy_name, light_id),
        #                         led_out=led.in_var['output'], step_period=0.001)
        # light_comps[led_driver.node_name] = led_driver

        # collecting data
        data_variables = OrderedDict()
        # collecting their values
        data_variables['%s.light_%d.led' % (teensy_name, light_id)] = led.in_var['output']
        data_variables['%s.light_%d.als' % (teensy_name, light_id)] = als.out_var['input']

        return light_comps, data_variables

    def build_default_nodes(self, teensy_name, components):

        interactive_nodes = OrderedDict()

        # configuration node
        local_action_prob = Var(0)
        local_cluster_input = []


        # ===== constructing the Light Node =====
        for j in range(self.num_light):
            als = components['%s.l%d.als' % (teensy_name, j)].out_var['input']
            ir_f = components['%s.f%d.ir-f' % (teensy_name, j)].out_var['input']

            led = components['%s.l%d.led' % (teensy_name, j)].in_var['output']

            light_node = Interactive_Light(messenger=self.messenger, node_name='%s.light%d' % (teensy_name, j),
                                           als=als, fin_ir=ir_f, led=led,
                                           local_action_prob=local_action_prob
                                           )

            # local_cluster_input.append(light_node.out_var['output'])
            interactive_nodes[light_node.node_name] = light_node

        # ===== constructing the Half-Fin Nodes =====
        for j in range(self.num_fin):

            # ===== constructing the left Half-Fin Nodes ====

            fin_ir_l = components['%s.f%d.ir-f' % (teensy_name, j)].out_var['input']
            scout_ir_l = components['%s.f%d.ir-s' % (teensy_name, j)].out_var['input']
            side_ir_l = components['%s.f%d.ir-s' % (teensy_name, (j - 1) % self.num_fin)].out_var['input']
            sma_l = components['%s.f%d.sma-l' % (teensy_name, j)].in_var['output']

            # left half-fin modules
            half_fin_l = Interactive_Half_Fin(self.messenger, node_name='%s.halfFin%d-l' % (teensy_name, j),
                                              output=sma_l, fin_ir=fin_ir_l,
                                              scout_ir=scout_ir_l, side_ir=side_ir_l,
                                              local_action_prob=local_action_prob
                                              )
            local_cluster_input.append(half_fin_l.out_var['output'])
            interactive_nodes[half_fin_l.node_name] = half_fin_l

            # ===== constructing the right Half-Fin Nodes ====
            fin_ir_r = components['%s.f%d.ir-f' % (teensy_name, j)].out_var['input']
            scout_ir_r = components['%s.f%d.ir-s' % (teensy_name, (j - 1) % self.num_fin)].out_var['input']
            side_ir_r = components['%s.f%d.ir-s' % (teensy_name, j)].out_var['input']
            sma_r = components['%s.f%d.sma-r' % (teensy_name, j)].in_var['output']

            # right half-fin modules
            half_fin_r = Interactive_Half_Fin(self.messenger, node_name='%s.halfFin%d-r' % (teensy_name, j),
                                              output=sma_r, fin_ir=fin_ir_r,
                                              scout_ir=scout_ir_r, side_ir=side_ir_r,
                                              local_action_prob=local_action_prob
                                              )

            local_cluster_input.append(half_fin_r.out_var['output'])
            interactive_nodes[half_fin_r.node_name] = half_fin_r



        # ===== constructing the Reflex Nodes =====
        for j in range(self.num_fin):

            # ===== constructing the shared part of the Reflex Nodes ====
            ir_s = components['%s.f%d.ir-s' % (teensy_name, j)].out_var['input']


            # ===== constructing the Reflex Motor Node ====
            rfx_m = components['%s.f%d.rfx-m' % (teensy_name, j)].in_var['output']
            reflex_motor = Interactive_Scout_Reflex(messenger=self.messenger,
                                                    node_name='%s.scoutReflex%d-m' % (teensy_name, j),
                                                    ir_sensor=ir_s, output=rfx_m,
                                                    max_val=100, step_period=0.05)


            interactive_nodes[reflex_motor.node_name] = reflex_motor

            # ===== constructing the Reflex LED Node ====
            rfx_l = components['%s.f%d.rfx-l' % (teensy_name, j)].in_var['output']
            reflex_light = Interactive_Scout_Reflex(messenger=self.messenger,
                                                    node_name='%s.scoutReflex%d-l' % (teensy_name, j),
                                                    ir_sensor=ir_s, output=rfx_l,
                                                    max_val=255, step_period=0.001)


            interactive_nodes[reflex_light.node_name] = reflex_light


        # setting up local activity node
        local_cluster = Cluster_Activity(self.messenger, node_name='%s.local_cluster' % teensy_name,
                                         output=local_action_prob, inputs=tuple(local_cluster_input))
        interactive_nodes[local_cluster.node_name] = local_cluster

        return interactive_nodes

    def start_nodes(self):

        if not isinstance(self.node_list, dict) or \
           not isinstance(self.messenger, interactive_system.Messenger):
            raise AttributeError("Nodes have not been created properly!")

        for name, node in self.node_list.items():
            node.start()
            print('%s initialized' % name)
        print('System Initialized with %d nodes' % len(self.node_list))

    def terminate(self):

        # terminate data collector
        #self.data_collector.alive = False
        #self.data_collector.join()
        print("Data Collector terminated")

        # killing each of the Node
        for node in self.node_list.values():
            node.alive = False
        for node in self.node_list.values():
            node.join()
            print('%s is terminated.' % node.node_name)

        print("All nodes are terminated")

        # killing each of the Teensy threads
        for teensy_name in list(self.teensy_manager.get_teensy_name_list()):
            self.teensy_manager.kill_teensy_thread(teensy_name)


def hmi_init(hmi: tk_gui.Master_Frame, messenger: interactive_system.Messenger, node_list: dict):

    if not isinstance(hmi, tk_gui.Master_Frame):
        raise TypeError("HMI must be Master_Frame")
    if not isinstance(node_list, dict):
        raise TypeError("node_list must be a dictionary")

    hmi.wm_title('Prescripted Mode')

    status_frame = tk_gui.Messenger_Status_Frame(hmi, messenger)
    content_frame = tk_gui.Content_Frame(hmi)
    nav_frame = tk_gui.Navigation_Frame(hmi, content_frame)

    control_vars = defaultdict(OrderedDict)
    display_vars = defaultdict(OrderedDict)

    if len(node_list) > 0:

        for name, node in node_list.items():

            node_name = name.split('.')
            teensy_name = node_name[0]
            device_name = node_name[1]
            try:
                output_name = node_name[2]
            except IndexError:
                output_name = "variables"

            # specifying the displayable variables
            if device_name not in display_vars[teensy_name]:
                display_vars[teensy_name][device_name] = OrderedDict()

            if isinstance(node, Input_Node):
                display_vars[teensy_name][device_name][output_name] = (node.out_var, 'input_node')
            elif isinstance(node, Output_Node):
                display_vars[teensy_name][device_name][output_name] = (node.in_var, 'output_node')
            else:
                display_vars[teensy_name][device_name][output_name + "_input"] = (node.in_var, 'input_node')
                display_vars[teensy_name][device_name][output_name + "_output"] = (node.out_var, 'output_node')

    page_frames = OrderedDict()
    for teensy_name, teensy_display_vars in display_vars.items():

        teensy_control_vars = OrderedDict()
        if teensy_name in control_vars.keys():
            teensy_control_vars = control_vars[teensy_name]
        frame = HMI_Prescripted_Mode(content_frame, teensy_name, (teensy_name, 'prescripted_display_page'),
                                teensy_control_vars, teensy_display_vars)
        page_frames[frame.page_key] = frame

        content_frame.build_pages(page_frames)

        nav_frame.build_nav_buttons()

    print('GUI initialized.')
    hmi.start(status_frame=status_frame,
              nav_frame=nav_frame,
              content_frame=content_frame,
              start_page_key=next(iter(page_frames.keys()), ''))


if __name__ == "__main__":

    cmd = Prescripted_Behaviour

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

        if not isinstance(behaviours, Prescripted_Behaviour):
            raise TypeError("Behaviour must be Prescripted_Behaviour type!")

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
