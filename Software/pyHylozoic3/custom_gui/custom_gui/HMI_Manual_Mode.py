__author__ = 'Matthew'

from .HMI_Standard import *


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

        max_row_per_col = 3
        row = 0
        col = 0

        device_frames = dict()

        for device_name, device in self.display_var.items():

            # === device label ===
            device_label = ttk.Label(self, text=device_name, style="device_label.TLabel")
            device_label.grid(row=row, column=col, sticky='NW')
            row += 1

            # === control input side ======
            control_frame = None
            if device_name in self.control_var.keys():
                control_frame = HMI_Manual_Mode_Control_Frame(self, self.control_var[device_name])
                control_frame.grid(row=row, column=col, sticky='NW', pady=(5, 30))

            # === display side ====
            display_frame = HMI_Manual_Mode_Display_Frame(self, device)
            display_frame.grid(row=row, column=col+1, sticky='NW', pady=(5, 10), padx=(30, 0))

            device_frames[device_name] = (display_frame, control_frame)
            row += 1

            if row/2 == max_row_per_col:
                row = 0
                col +=2


class HMI_Manual_Mode_Display_Frame(HMI_Standard_Display_Frame):

    def __init__(self, tk_master: HMI_Manual_Mode, display_vars: OrderedDict):
        super(HMI_Manual_Mode_Display_Frame, self).__init__(tk_master, display_vars, max_col_per_row=5)


class HMI_Manual_Mode_Control_Frame(HMI_Standard_Control_Frame):

    def __init__(self, tk_master: HMI_Manual_Mode, display_vars: OrderedDict):

        super(HMI_Manual_Mode_Control_Frame, self).__init__(tk_master, display_vars, max_col_per_row=5)

