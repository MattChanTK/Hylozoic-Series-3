from collections import OrderedDict
from collections import defaultdict
from time import clock
import sys
import os

import interactive_system
import interactive_system.CommunicationProtocol as CP

from complex_node import *
from abstract_node import *

from tkinter import ttk
import tk_gui


class Manual_Control(interactive_system.InteractiveCmd):

    # ========= the Run function for the manual control =====
    def run(self):

        for teensy_name in self.teensy_manager.get_teensy_name_list():
            # ------ set mode ------
            cmd_obj = interactive_system.command_object(teensy_name, 'basic')
            cmd_obj.add_param_change('operation_mode', CP.CBLATestBed_FAST.MODE_CBLA2)
            self.enter_command(cmd_obj)

        self.send_commands()

        # initially update the Teensys with all the output parameters here
        self.update_output_params(self.teensy_manager.get_teensy_name_list())

        messenger = Messenger(self, 0.000)
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

            # 3 tentacles
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

                # 1 frond
                motion_type = Var(0)
                #sma_param = {'KP': 15, 'K_heating': 0.00, 'K_dissipate': 0.05}
                frond = Frond(messenger, teensy, node_name='tentacle_%d.frond' % j, left_sma=sma_0.in_var['output'],
                              right_sma=sma_1.in_var['output'], motion_type=motion_type,)
                              #left_config=sma_param, right_config=sma_param)
                node_list[frond.node_name] = frond


                # 2 reflex each
                reflex_0 = Output_Node(messenger, teensy, node_name='tentacle_%d.reflex_0' % j, output='tentacle_%d_reflex_0_level' % j)
                reflex_1 = Output_Node(messenger, teensy, node_name='tentacle_%d.reflex_1' % j, output='tentacle_%d_reflex_1_level' % j)


                node_list[reflex_0.node_name] = reflex_0
                node_list[reflex_1.node_name] = reflex_1

            # for Protocell
            # 1 ambient light sensor
            als = Input_Node(messenger, teensy, node_name='protocell.als', input='protocell_0_als_state')
            node_list[als.node_name] = als
            # 1 led
            led = Output_Node(messenger, teensy_name=teensy, node_name='protocell.led',
                              output='protocell_0_led_level')
            node_list[led.node_name] = led

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
        self.hmi.wm_title('Manual Control Mode')

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
                output_name = node_name[2]

                # specifying the controlable variables
                if device_name not in control_vars[teensy_name]:
                    control_vars[teensy_name][device_name] = OrderedDict()

                if isinstance(node, Frond):
                    control_vars[teensy_name][device_name][output_name] = node.in_var['motion_type']
                elif isinstance(node, Output_Node) and 'sma' not in name:
                    control_vars[teensy_name][device_name][output_name] = node.in_var['output']

                # specifying the displayable variables
                if device_name not in display_vars[teensy_name]:
                    display_vars[teensy_name][device_name] = OrderedDict()

                if isinstance(node, Input_Node):
                    display_vars[teensy_name][device_name][output_name] = (node.out_var, 'input_node')
                elif isinstance(node, Output_Node):
                    display_vars[teensy_name][device_name][output_name] = (node.in_var, 'output_node')


        page_frames = OrderedDict()
        for teensy_name, teensy_display_vars in display_vars.items():

            teensy_control_vars = OrderedDict()
            if teensy_name in control_vars.keys():
                teensy_control_vars = control_vars[teensy_name]
            frame = HMI_Manual_Mode(content_frame, teensy_name, (teensy_name, 'manual_ctrl_page'),
                                    teensy_control_vars, teensy_display_vars)
            page_frames[frame.page_key] = frame

            content_frame.build_pages(page_frames)

            nav_frame.build_nav_buttons()

        self.hmi.start(status_frame=status_frame,
                       nav_frame=nav_frame,
                       content_frame=content_frame,
                       start_page_key=next(iter(page_frames.keys()), ''))


class HMI_Manual_Mode(tk_gui.Page_Frame):

    def __init__(self, parent_frame: tk_gui.Content_Frame, page_name: str, page_key,
                 control_var: OrderedDict, display_var: OrderedDict):

        self.control_var = control_var
        self.display_var = display_var

        # label styles
        device_label_style = ttk.Style()
        device_label_style.configure("device_label.TLabel", foreground="black", font=('Helvetica', 12))

        super(HMI_Manual_Mode, self).__init__(parent_frame, page_name, page_key)

    def _build_page(self):

        row = 0

        device_frames = dict()

        for device_name, device in self.display_var.items():

            # === device label ===
            device_label = ttk.Label(self, text=device_name, style="device_label.TLabel")
            device_label.grid(row=row, column=0, sticky='NW')
            row += 1

            # === control input side ======
            control_frame = None
            if device_name in self.control_var.keys():
                control_frame = HMI_Manual_Mode_Control_Frame(self, self.control_var[device_name])
                control_frame.grid(row=row, column=0, sticky='NW', pady=(5, 30))

            # === display side ====
            display_frame = HMI_Manual_Mode_Display_Frame(self, device)
            display_frame.grid(row=row, column=1, sticky='NW', pady=(5, 10), padx=(30, 0))

            device_frames[device_name] = (display_frame, control_frame)
            row += 1


class HMI_Manual_Mode_Control_Frame(ttk.Frame):

    def __init__(self, tk_master: HMI_Manual_Mode, control_vars: OrderedDict):
        super(HMI_Manual_Mode_Control_Frame, self).__init__(tk_master)

        # label styles
        invalid_style = ttk.Style()
        invalid_style.configure("invalid.TLabel", foreground="red")
        valid_style = ttk.Style()
        valid_style.configure("valid.TLabel", foreground="black")

        self.control_vars = control_vars
        self.output_dict = dict()

        max_col_per_row = 3
        row = 0
        col = 0
        # specifying the output label and entry box
        for output_name, output_var in control_vars.items():
            output_label = ttk.Label(self, text=output_name.replace('_', ' '), width=15)
            output_entry = ttk.Entry(self, width=5)
            output_entry.insert(0, '0')

            if col >= max_col_per_row:
                col = 0
                row += 2
            output_label.grid(row=row, column=col, sticky='NW')
            output_entry.grid(row=row + 1, column=col, padx=(0, 5), sticky='nsew')

            self.output_dict[output_name] = (output_label, output_entry)

            col += 1

        self.updateFrame()

    def updateFrame(self):

        for output_name, output_var in self.output_dict.items():
            label = output_var[0]
            entry = output_var[1]

            try:
                curr_val = int(entry.get())
                if curr_val > 255 or curr_val < 0:
                    raise ValueError

                if curr_val != self.control_vars[output_name].val:
                    self.control_vars[output_name].val = curr_val

            except ValueError:
                label.configure(style="invalid.TLabel")
            else:
                label.configure(style="valid.TLabel")

        self.after(500, self.updateFrame)
        self.update()


class HMI_Manual_Mode_Display_Frame(ttk.Frame):

    def __init__(self, tk_master: HMI_Manual_Mode, display_vars: OrderedDict):
        super(HMI_Manual_Mode_Display_Frame, self).__init__(tk_master)

        # label styles
        input_style = ttk.Style()
        input_style.configure("input_var.TLabel", foreground="magenta")
        output_style = ttk.Style()
        output_style.configure("output_var.TLabel", foreground="blue")

        self.display_vars = display_vars
        self.var_dict = defaultdict(dict)

        max_col_per_row = 8
        row = 0
        col = 0

        # specifying the output label and entry box
        for output_name, output_var in display_vars.items():

            if col >= max_col_per_row:
                col = 0
                row += 2

            output_label = ttk.Label(self, text=output_name.replace('_', ' '))
            if output_var[1] == 'input_node':
                output_label.configure(style="input_var.TLabel")
            elif output_var[1] == 'output_node':
                output_label.configure(style="output_var.TLabel")

            if len(output_var[0]) == 1:

                output_label.grid(row=row, column=col, sticky='NW', padx=(0, 5))

                var = next(iter(output_var[0].values()))
                value_label = ttk.Label(self, text='%d' % var.val, width=8)
            else:
                output_label.grid(row=row, column=col, sticky='NW', padx=(0, 5))

                value_tuple = []
                for var_name, var in output_var[0].items():
                    value_tuple.append(var.val)
                value_tuple = tuple(value_tuple)

                value_label = ttk.Label(self, text=str(value_tuple), width=15)

            value_label.grid(row=row + 1, column=col, sticky='NW', pady=(0, 5))

            col += 1

            self.var_dict[output_name] = (output_label, value_label)

        self.updateFrame()

    def updateFrame(self):
        for output_name, output_var in self.var_dict.items():
            label = output_var[0]
            val = output_var[1]

            curr_vals = self.display_vars[output_name][0]

            if len(curr_vals) == 1:
                val['text'] = '%d' % next(iter(curr_vals.values())).val
            else:
                value_tuple = []
                for var_name, var in curr_vals.items():
                    value_tuple.append(var.val)
                value_tuple = tuple(value_tuple)

                val['text'] = str(value_tuple)


        self.after(500, self.updateFrame)
        self.update()


if __name__ == "__main__":

    cmd = Manual_Control

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

        print('done')
        for teensy_thread in teensy_manager._get_teensy_thread_list():
            teensy_thread.join()

        print("All Teensy threads terminated")

    main()