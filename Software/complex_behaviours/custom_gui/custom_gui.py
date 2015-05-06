__author__ = 'Matthew'
from collections import OrderedDict
from collections import defaultdict

from tkinter import ttk

from hmi_gui import tk_gui



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


class HMI_Prescripted_Mode(tk_gui.Page_Frame):

    def __init__(self, parent_frame: tk_gui.Content_Frame, page_name: str, page_key,
                 control_var: OrderedDict, display_var: OrderedDict):

        self.display_var = display_var

        # label styles
        device_label_style = ttk.Style()
        device_label_style.configure("device_label.TLabel", foreground="black", font=('Helvetica', 12))

        super(HMI_Prescripted_Mode, self).__init__(parent_frame, page_name, page_key)

    def _build_page(self):

        col = 0

        device_frames = dict()

        for device_name, device in self.display_var.items():

            row = 0
            # === device label ===
            device_label = ttk.Label(self, text=device_name, style="device_label.TLabel")
            device_label.grid(row=row, column=col, sticky='NW')
            row += 1

            # === display side ====
            display_frame = HMI_Prescripted_Mode_Display_Frame(self, device)
            display_frame.grid(row=row, column=col, sticky='NW', pady=(0, 2), padx=(0, 3))

            device_frames[device_name] = (display_frame, )
            col += 1


class HMI_Standard_Display_Frame(ttk.Frame):

    def __init__(self, tk_master: tk_gui.Page_Frame, display_vars: OrderedDict, **kwargs):
        super(HMI_Standard_Display_Frame, self).__init__(tk_master)

        # label styles
        input_style = ttk.Style()
        input_style.configure("input_var.TLabel", foreground="magenta", font=('Helvetica', 10))
        output_style = ttk.Style()
        output_style.configure("output_var.TLabel", foreground="blue", font=('Helvetica', 10))
        default_style = ttk.Style()
        default_style.configure("default_var.TLabel", foreground="green", font=('Helvetica', 10))

        self.display_vars = display_vars
        self.var_dict = defaultdict(dict)

        self.max_col_per_row = 20
        if 'max_col_per_row' in kwargs:
            if isinstance(kwargs['max_col_per_row'], int):
                self.max_col_per_row = kwargs['max_col_per_row']

        row = 0
        col = 0

        # specifying the output label and entry box
        for output_name, output_var in display_vars.items():

            if row >= self.max_col_per_row:
                row = 0
                col += 2

            output_label = ttk.Label(self, text=output_name.replace('_', ' '), style="default_var.TLabel")
            if output_var[1] == 'input_node':
                output_label.configure(style="input_var.TLabel")
            elif output_var[1] == 'output_node':
                output_label.configure(style="output_var.TLabel")

            output_label.grid(row=row, column=col, sticky='NW', padx=(0, 3))

            if len(output_var[0]) == 1:
                var = next(iter(output_var[0].values()))
                value_label = ttk.Label(self, text='%d' % var.val, width=8)
            else:
                value_label_string = HMI_Prescripted_Mode_Display_Frame.get_var_string(output_name, output_var[0])
                label_width = max([len(string) for string in value_label_string.split('\n')]) + 1
                value_label = ttk.Label(self, text=value_label_string, width=label_width)

            value_label.grid(row=row, column=col + 1, sticky='NW', pady=(2, 2))

            row += 1

            self.var_dict[output_name] = (output_label, value_label)

        self.updateFrame()

    @staticmethod
    def get_var_string(output_name, output_var: dict, max_num_per_row=1):

        if not isinstance(output_var, dict):
            raise TypeError("output_var must be a dictionary!")

        if output_name in ('acc',):

            value_tuple = []
            for var_name, var in output_var.items():
                value_tuple.append(var.val)
            value_tuple = tuple(value_tuple)

            return str(value_tuple)
        else:
            var_string = ""
            var_num = 1
            for var_name, var in output_var.items():
                if var_num % max_num_per_row:
                    end_string = '; '
                elif var_num == len(output_var):
                    end_string = ''
                else:
                    end_string = '\n'
                var_string += "%s=%d%s" % (var_name, var.val, end_string)
                var_num += 1

            return var_string

    def updateFrame(self):
        for output_name, output_var in self.var_dict.items():
            label = output_var[0]
            val = output_var[1]

            curr_vals = self.display_vars[output_name][0]

            if len(curr_vals) == 1:
                val['text'] = '%d' % next(iter(curr_vals.values())).val
            else:
                value_label_string = HMI_Prescripted_Mode_Display_Frame.get_var_string(output_name, curr_vals)
                val['text'] = value_label_string

        self.after(500, self.updateFrame)
        self.update()


class HMI_Prescripted_Mode_Display_Frame(HMI_Standard_Display_Frame):
    pass


class HMI_Manual_Mode_Display_Frame(HMI_Standard_Display_Frame):

    def __init__(self, tk_master: HMI_Manual_Mode, display_vars: OrderedDict):
        super(HMI_Manual_Mode_Display_Frame, self).__init__(tk_master, display_vars, max_col_per_row=5)


class HMI_Standard_Control_Frame(ttk.Frame):

    def __init__(self, tk_master: tk_gui.Page_Frame, control_vars: OrderedDict, **kwargs):
        super(HMI_Standard_Control_Frame, self).__init__(tk_master)

        # label styles
        invalid_style = ttk.Style()
        invalid_style.configure("invalid.TLabel", foreground="red")
        valid_style = ttk.Style()
        valid_style.configure("valid.TLabel", foreground="black")

        self.control_vars = control_vars
        self.output_dict = dict()

        self.max_col_per_row = 20
        if 'max_col_per_row' in kwargs:
            if isinstance(kwargs['max_col_per_row'], int):
                self.max_col_per_row = kwargs['max_col_per_row']

        row = 0
        col = 0
        # specifying the output label and entry box
        for output_name, output_var in control_vars.items():
            output_label = ttk.Label(self, text=output_name.replace('_', ' '), width=15)
            output_entry = ttk.Entry(self, width=5)
            output_entry.insert(0, '0')

            if row >= self.max_col_per_row:
                row = 0
                col += 2
            output_label.grid(row=row, column=col, sticky='NW')
            output_entry.grid(row=row, column=col+1, padx=(0, 5), sticky='nsew')

            self.output_dict[output_name] = (output_label, output_entry)

            row += 1

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


class HMI_Manual_Mode_Control_Frame(HMI_Standard_Control_Frame):

    def __init__(self, tk_master: HMI_Manual_Mode, display_vars: OrderedDict):

        super(HMI_Manual_Mode_Control_Frame, self).__init__(tk_master, display_vars, max_col_per_row=5)