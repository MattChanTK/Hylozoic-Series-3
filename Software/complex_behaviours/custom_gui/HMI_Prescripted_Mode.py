__author__ = 'Matthew'
from .HMI_Standard import *


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


class HMI_Prescripted_Mode_Display_Frame(HMI_Standard_Display_Frame):
    pass

