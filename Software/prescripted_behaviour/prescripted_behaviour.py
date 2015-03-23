from interactive_system import InteractiveCmd
from interactive_system import Messenger
import node
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



        messenger = Messenger.Messenger(self, 0.03)
        messenger.start()


        ir_sensor_0 = node.IR_Proximity_Sensor(messenger, 'test_teensy_3', 'tentacle_0_ir_0_state')
        ir_sensor_0.start()

        ir_sensor_1 = node.IR_Proximity_Sensor(messenger, 'test_teensy_3', 'tentacle_0_ir_1_state')
        ir_sensor_1.start()


        # test_node = node.Test_Node(messenger, ir_sensor_0.out_var['sensor_raw'])
        # test_node.start()

        tentacle_0 = node.Tentacle(messenger, teensy_name='test_teensy_3', tentacle_num=0,
                                   ir_0=ir_sensor_0.out_var['sensor_raw'], ir_1=ir_sensor_0.out_var['sensor_raw'])
        tentacle_0.start()
        print('System Initialized')

