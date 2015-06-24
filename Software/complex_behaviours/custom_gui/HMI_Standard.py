__author__ = 'Matthew'
from collections import OrderedDict
from collections import defaultdict

from tkinter import ttk

from hmi_gui import tk_gui
from abstract_node import Var


class HMI_Standard_Display_Frame(ttk.Frame):

    def __init__(self, tk_master: tk_gui.Page_Frame, display_vars: OrderedDict, **kwargs):
        super(HMI_Standard_Display_Frame, self).__init__(tk_master)

        self.root = tk_master

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

                value_label_string = to_tuple_string(var.val)

            else:
                value_label_string = HMI_Standard_Display_Frame.get_var_string(output_name, output_var[0])

            label_width = max([len(string) for string in value_label_string.split('\n')]) + 1
            value_label = ttk.Label(self, text=value_label_string, width=-label_width)

            value_label.grid(row=row, column=col + 1, sticky='NW', pady=(2, 2))

            row += 1

            self.var_dict[output_name] = (output_label, value_label)

        self.updateFrame()

    @staticmethod
    def get_var_string(output_name, output_var: dict, max_num_per_row=1):

        if not isinstance(output_var, dict):
            raise TypeError("output_var must be a dictionary!")

        if output_name in ('acc',):
            return to_tuple_string(output_var)
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
                val_string = to_tuple_string(var.val)
                var_string += "%s=%s%s" % (var_name, val_string, end_string)
                var_num += 1

            return var_string

    def updateFrame(self):
        for output_name, output_var in self.var_dict.items():
            label = output_var[0]
            val = output_var[1]

            curr_vals = self.display_vars[output_name][0]

            if len(curr_vals) == 1:
                val['text'] = to_tuple_string(next(iter(curr_vals.values())).val)
            else:
                value_label_string = HMI_Standard_Display_Frame.get_var_string(output_name, curr_vals)
                val['text'] = value_label_string
            label_width = max([len(string) for string in val['text'].split('\n')]) + 4
            val.configure(width=max(val['width'], label_width))

        self.update()
        self.after(500, self.updateFrame)
        #updateRecursive(self)

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

        self.update()
        self.after(500, self.updateFrame)


def to_tuple_string(output_var):

    if not isinstance(output_var, (float, int, list, tuple, dict)):
        raise TypeError("output_var must be a int, float, list, a tuple or a dict")

    if isinstance(output_var, dict):
        var_list = tuple(output_var.values())
    elif isinstance(output_var, (int, float)):
        var_list = tuple([output_var])
    else:
        var_list = tuple(output_var)

    text_string = ""
    for var in var_list:
        if isinstance(var, Var):
            var = var.val
        if isinstance(var, int):
            text_string += '%d' % var
        elif isinstance(var, float):
            text_string += '%.4f' % var
        else:
            text_string += str(var)
        text_string += ', '

    if len(var_list) > 1:
        text_string = '(' + text_string[:-2] + ')'
    else:
        text_string = text_string[:-2]
    return text_string


def updateRecursive(tk_root):
    tk_root.update()
    try:
        updateRecursive(tk_root.root)
    except AttributeError:
        pass