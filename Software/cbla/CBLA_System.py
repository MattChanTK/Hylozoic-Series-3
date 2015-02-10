import os
import threading


from interactive_system import InteractiveCmd
from interactive_system.InteractiveCmd import command_object
from cbla_engine import CBLA_Engine

import Robot
# from SimSystem import DiagonalPlane as Robot

class CBLA_Behaviours(InteractiveCmd.InteractiveCmd):

    # ========= the Run function for the entire CBLA behaviour =====
    def run(self):

        curr_dir = os.getcwd()
        os.chdir(os.path.join(curr_dir, "pickle_jar"))

        teensy_names = self.teensy_manager.get_teensy_name_list()

        # initially update the Teensys with all the output parameters here
        self.update_output_params(teensy_names)

        # synchonization barrier for all LEDs
        self.sync_barrier_led = Robot.Sync_Barrier(self, len(teensy_names) * 1,
                                                             node_type=Robot.Protocell_Node,
                                                             sample_interval=0, sample_period=0.05)
        # synchonization barrier for all SMAs
        self.sync_barrier_sma = Robot.Sync_Barrier(self, len(teensy_names) * 3,
                                                             node_type=Robot.Tentacle_Arm_Node,
                                                             sample_interval=5, sample_period=0.33)

        # semaphore for restricting only one thread to access this thread at any given time
        self.lock = threading.Lock()
        self.cbla_engine = dict()
        for teensy_name in teensy_names:

            # set mode
            cmd_obj = command_object(teensy_name, 'basic')
            cmd_obj.add_param_change('operation_mode', 3)
            self.enter_command(cmd_obj)

            # instantiate robots
            protocell_action = ((teensy_name, 'protocell_0_led_level'),)
            protocell_sensor = ((teensy_name, 'protocell_0_als_state'),)
            robot_led = Robot.Protocell_Node(protocell_action, protocell_sensor, self.sync_barrier_led,
                                                       name=(teensy_name + '_LED'), msg_setting=2)

            # -- raw accelerometer reading with all 3 arms ---
            # sma_action = ('tentacle_0_arm_motion_on','tentacle_1_arm_motion_on','tentacle_2_arm_motion_on',)
            #sma_sensor = ('tentacle_0_acc_z_state', 'tentacle_1_acc_z_state', 'tentacle_2_acc_z_state', 'tentacle_0_cycling', 'tentacle_1_cycling', 'tentacle_2_cycling'	)

            # --- one tentacle arm; derived acc features ---
            robot_sma = []
            for j in range(3):
                device_header = 'tentacle_%d_' % j
                sma_action = ((teensy_name, device_header + "arm_motion_on"),)
                sma_sensor = ((teensy_name, device_header + 'wave_mean_x'),
                              (teensy_name, device_header + 'wave_mean_y'),
                              (teensy_name, device_header + 'wave_mean_z'),
                              (teensy_name, device_header + 'cycling'))
                #sma_sensor = (device_header + 'wave_diff_x', device_header + 'wave_diff_y', device_header + 'wave_diff_z', device_header + 'cycling' )

                robot_sma.append(Robot.Tentacle_Arm_Node(sma_action, sma_sensor, self.sync_barrier_sma,
                                                                   name=(teensy_name + '_SMA_%d' % j), msg_setting=1))

            # instantiate CBLA Engines
            with self.lock:
                self.cbla_engine[teensy_name + '_LED'] = CBLA_Engine(robot_led, id=1,
                                                                                     sim_duration=float('inf'),
                                                                                     use_saved_expert=False,
                                                                                     split_thres=400,
                                                                                     mean_err_thres=30.0, kga_delta=5,
                                                                                     kga_tau=2, saving_freq=10)

                self.cbla_engine[teensy_name + '_SMA_0'] = CBLA_Engine(robot_sma[0], id=2,
                                                                                       sim_duration=float('inf'),
                                                                                       use_saved_expert=False,
                                                                                       split_thres=10,
                                                                                       mean_err_thres=2.0, kga_delta=1,
                                                                                       kga_tau=1, saving_freq=1)
                self.cbla_engine[teensy_name + '_SMA_1'] = CBLA_Engine(robot_sma[1], id=3,
                                                                                       sim_duration=float('inf'),
                                                                                       use_saved_expert=False,
                                                                                       split_thres=10,
                                                                                       mean_err_thres=2.0, kga_delta=1,
                                                                                       kga_tau=1, saving_freq=1)
                self.cbla_engine[teensy_name + '_SMA_2'] = CBLA_Engine(robot_sma[2], id=4,
                                                                                       sim_duration=float('inf'),
                                                                                       use_saved_expert=False,
                                                                                       split_thres=10,
                                                                                       mean_err_thres=2.0, kga_delta=1,
                                                                                       kga_tau=1, saving_freq=1)


        # waiting for all CBLA engines to terminate to do visualization
        name_list = []
        for name, engine in self.cbla_engine.items():
            name_list.append(name)
            engine.join()

