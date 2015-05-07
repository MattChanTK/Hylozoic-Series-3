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

    # ========= the Run function for the prescripted behaviour system =====
    def run(self):

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

        messenger = interactive_system.Messenger(self, 0.001)
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

            local_action_prob = Var(0)

            # 3 tentacles
            half_frond_list = []
            reflex_actuator_list = []
            cluster_activity = Var(0)
            for j in range(3):

                # 2 ir sensors each
                ir_sensor_0 = Input_Node(messenger, teensy, node_name='tentacle_%d.ir_0' % j, input='tentacle_%d_ir_0_state' % j)
                ir_sensor_1 = Input_Node(messenger, teensy, node_name='tentacle_%d.ir_1' % j, input='tentacle_%d_ir_1_state' % j)

                node_list[ir_sensor_0.node_name] = ir_sensor_0
                node_list[ir_sensor_1.node_name] = ir_sensor_1

                # 1 3-axis acceleromter each
                acc = Input_Node(messenger, teensy, node_name='tentacle_%d.acc' % j,
                                         x='tentacle_%d_acc_x_state' % j,
                                         y='tentacle_%d_acc_y_state' % j,
                                         z='tentacle_%d_acc_z_state' % j)
                node_list[acc.node_name] = acc

                # 2 SMA wires each
                sma_0 = Output_Node(messenger, teensy, node_name='tentacle_%d.sma_0' % j, output='tentacle_%d_sma_0_level' % j)
                sma_1 = Output_Node(messenger, teensy, node_name='tentacle_%d.sma_1' % j, output='tentacle_%d_sma_1_level' % j)

                node_list[sma_0.node_name] = sma_0
                node_list[sma_1.node_name] = sma_1


                # 2 reflex each
                reflex_0 = Output_Node(messenger, teensy, node_name='tentacle_%d.reflex_0' % j, output='tentacle_%d_reflex_0_level' % j)
                reflex_1 = Output_Node(messenger, teensy, node_name='tentacle_%d.reflex_1' % j, output='tentacle_%d_reflex_1_level' % j)

                node_list[reflex_0.node_name] = reflex_0
                node_list[reflex_1.node_name] = reflex_1

                # 1 reflex actuator node
                scout_reflex_0 = Reflex_Actuator(messenger, node_name='%s.tentacle_%d.scout_reflex_0' % (teensy, j),
                                                 output=reflex_0.in_var['output'], ir_sensor=ir_sensor_0.out_var['input'])
                node_list[scout_reflex_0.node_name] = scout_reflex_0
                reflex_actuator_list.append(scout_reflex_0)

                # two half-fronds
                half_frond_left = Half_Frond(messenger, node_name='%s.tentacle_%d.half_frond_left' % (teensy, j),
                                             output=sma_0.in_var['output'], frond_ir=ir_sensor_1.out_var['input'],
                                             scout_ir=ir_sensor_0.out_var['input'], local_action_prob=local_action_prob)

                half_frond_right = Half_Frond(messenger, node_name='%s.tentacle_%d.half_frond_right' % (teensy, j),
                                              output=sma_1.in_var['output'], frond_ir=ir_sensor_1.out_var['input'],
                                              side_ir=ir_sensor_0.out_var['input'], local_action_prob=local_action_prob)

                node_list[half_frond_left.node_name] = half_frond_left
                node_list[half_frond_right.node_name] = half_frond_right
                half_frond_list.append(half_frond_left)
                half_frond_list.append(half_frond_right)

            # creating Protocell Node

            # 1 LED per protocell
            led = Output_Node(messenger, teensy_name=teensy, node_name='protocell.led',
                              output='protocell_0_led_level')
            protocell = Protocell2(messenger, node_name='%s.protocell' % teensy,
                                   led=led.in_var['output'],
                                   local_action_prob=local_action_prob)
            node_list[led.node_name] = led
            node_list[protocell.node_name] = protocell

            # == establishing relationship among devices ===

            # setting their side_ir to the neighbouring tentacle one
            half_frond_right_list = []
            half_frond_left_list = []
            for half_frond in half_frond_list:
                if isinstance(half_frond, Half_Frond):
                    if 'right' in half_frond.node_name:
                        half_frond_right_list.append(half_frond)
                    elif 'left' in half_frond.node_name:
                        half_frond_left_list.append(half_frond)

            for j in range(len(half_frond_right_list)):
                right_id = (j - 1) % len(half_frond_right_list)
                half_frond_right_list[j].in_var['scout_ir'] = half_frond_right_list[right_id].in_var['side_ir']
            for j in range(len(half_frond_left_list)):
                right_id = (j - 1) % len(half_frond_left_list)
                half_frond_left_list[j].in_var['side_ir'] = half_frond_left_list[right_id].in_var['scout_ir']

            # setting up local activity node
            local_cluster_input = []
            for device in half_frond_list + reflex_actuator_list:
                local_cluster_input.append(device.out_var['output'])

            local_cluster = Cluster_Activity(messenger, node_name='%s.local_cluster' % teensy,
                                             output=local_action_prob, inputs=tuple(local_cluster_input))


            node_list[local_cluster.node_name] = local_cluster

        self.node_list = node_list
        self.messenger = messenger

        self.start_nodes()
        self.hmi_init()

    def start_nodes(self):

        for name, node in self.node_list.items():
            node.start()
            print('%s initialized' % name)
        print('System Initialized with %d nodes' % len(self.node_list))

    def hmi_init(self):

        self.hmi = tk_gui.Master_Frame()
        self.hmi.wm_title('Prescripted Mode')

        status_frame = tk_gui.Messenger_Status_Frame(self.hmi, self.messenger)
        content_frame = tk_gui.Content_Frame(self.hmi)
        nav_frame = tk_gui.Navigation_Frame(self.hmi, content_frame)

        control_vars = defaultdict(OrderedDict)
        display_vars = defaultdict(OrderedDict)

        if len(self.node_list) > 0:

            for name, node in self.node_list.items():

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

        self.hmi.start(status_frame=status_frame,
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

        for teensy_thread in teensy_manager._get_teensy_thread_list():
            teensy_thread.join()

        print("All Teensy threads terminated")

    main()