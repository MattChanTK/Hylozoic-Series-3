from interactive_system import InteractiveCmd
from interactive_system import Messenger
from node import *
from tentacle_node import *

from copy import copy
from collections import defaultdict

class Prescripted_Behaviour(InteractiveCmd.InteractiveCmd):

    # ========= the Run function for the prescripted behaviour system =====
    def run(self):

        for teensy_name in self.teensy_manager.get_teensy_name_list():
            # ------ set mode ------
            cmd_obj = InteractiveCmd.command_object(teensy_name, 'basic')
            cmd_obj.add_param_change('operation_mode', 3)
            self.enter_command(cmd_obj)

            # ------ configuration ------
            # set the Tentacle on/off periods
            cmd_obj = InteractiveCmd.command_object(teensy_name, 'tentacle_high_level')
            for j in range(3):
                device_header = 'tentacle_%d_' % j
                cmd_obj.add_param_change(device_header + 'arm_cycle_on_period', 15)
                cmd_obj.add_param_change(device_header + 'arm_cycle_off_period', 105)
            self.enter_command(cmd_obj)

        # initially update the Teensys with all the output parameters here
        self.update_output_params(self.teensy_manager.get_teensy_name_list())


        messenger = Messenger.Messenger(self, 0.03)
        messenger.start()

        teensy_0 = 'test_teensy_3'
        teensy_1 = 'HK_teensy_1'
        teensy_2 = 'HK_teensy_2'
        teensy_3 = 'HK_teensy_3'


        teensy_in_use = (teensy_2, )

        cluster = defaultdict(lambda: Cluster_Components())

        for teensy in teensy_in_use:

            # 3 tentacles
            for j in range(3):

                # 2 ir sensors each
                ir_sensor_0 = Input_Node(messenger, teensy, input='tentacle_%d_ir_0_state' % j)
                ir_sensor_1 = Input_Node(messenger, teensy, input='tentacle_%d_ir_1_state' % j)

                # 1 frond each
                frond = Output_Node(messenger, teensy, output='tentacle_%d_arm_motion_on' % j)

                # 2 reflex each
                reflex_0 = Output_Node(messenger, teensy, output='tentacle_%d_reflex_0_level' % j)
                reflex_1 = Output_Node(messenger, teensy, output='tentacle_%d_reflex_1_level' % j)


                # copy to Tentacle component set
                tentacle_internals = Tentacle_Internal_Components(ir_sensor_0, ir_sensor_1, frond, reflex_0, reflex_1)

                cluster[teensy].append_components(tentacle_internals=tentacle_internals)

                # create the Tentacle Node object
                tentacle = Tentacle(messenger, teensy_name=teensy,
                                    ir_0=cluster[teensy].tentacle_internals[j].ir_0.out_var['input'],
                                    ir_1=cluster[teensy].tentacle_internals[j].ir_0.out_var['input'],
                                    frond=cluster[teensy].tentacle_internals[j].frond.in_var['output'],
                                    reflex_0=cluster[teensy].tentacle_internals[j].reflex_0.in_var['output'],
                                    reflex_1=cluster[teensy].tentacle_internals[j].reflex_1.in_var['output'])

                # copy to cluster set
                cluster[teensy].append_node(tentacle_node=tentacle)

                # de-ref temp threads
                ir_sensor_0 = None
                ir_sensor_1 = None
                frond = None
                tentacle_internals = None
                tentacle = None

        for teensy in teensy_in_use:
            cluster[teensy].start()

        print('System Initialized')


class Tentacle_Internal_Components(object):

    def __init__(self, ir_sensor_0: Input_Node, ir_sensor_1: Input_Node,
                 frond: Output_Node, reflex_0: Output_Node, reflex_1: Output_Node):

        self.ir_0 = copy(ir_sensor_0)
        self.ir_1 = copy(ir_sensor_1)

        self.frond = copy(frond)
        self.reflex_0 = copy(reflex_0)
        self.reflex_1 = copy(reflex_1)

    def start_all(self):

        self.ir_0.start()
        self.ir_1.start()
        self.frond.start()
        self.reflex_0.start()
        self.reflex_1.start()

        print('components started')


class Cluster_Components(object):
    def __init__(self):

        self.tentacle_internals = []
        self.tentacle_node = []

    def append_node(self, tentacle_node: Tentacle):
        self.tentacle_node.append(copy(tentacle_node))

    def append_components(self, tentacle_internals: Tentacle_Internal_Components):
        self.tentacle_internals.append(copy(tentacle_internals))

    def start(self):

        for comp in self.tentacle_internals:
            comp.start_all()

        for node in self.tentacle_node:
            node.start()
            print('node started')





