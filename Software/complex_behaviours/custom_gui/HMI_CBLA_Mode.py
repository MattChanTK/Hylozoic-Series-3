__author__ = 'Matthew'
from .HMI_Standard import *
import matplotlib

class HMI_CBLA_Mode(tk_gui.Page_Frame):

    def __init__(self, parent_frame: tk_gui.Content_Frame, page_name: str, page_key,
                 cbla_var: OrderedDict, display_var: OrderedDict):

        self.display_var = display_var
        self.cbla_var = cbla_var

        # label styles
        device_label_style = ttk.Style()
        device_label_style.configure("device_label.TLabel", foreground="black", font=('Helvetica', 12))

        super(HMI_CBLA_Mode, self).__init__(parent_frame, page_name, page_key)

    def _build_page(self):

        max_col_per_row = 4
        col = 0
        row = 0

        device_frames = dict()
        cbla_frames = dict()
        for device_name, device in self.display_var.items():

            # === device label ===
            device_label = ttk.Label(self, text=device_name, style="device_label.TLabel")
            device_label.grid(row=row, column=col, sticky='NW', pady=(0, 10))

            # === device display side ====
            display_frame = HMI_Standard_Display_Frame(self, device)
            display_frame.grid(row=row+1, column=col, sticky='NW', pady=(0, 20), padx=(0, 3))

            device_frames[device_name] = (display_frame, )

            col += 1
            if col == max_col_per_row:
                col = 0
                row += 2

        for node_name, node in self.cbla_var.items():
            # === cbla node label ===
            node_label = ttk.Label(self, text=node_name, style="device_label.TLabel")
            node_label.grid(row=row, column=col, sticky='NW', pady=(0, 10))

            # === cbla display side ====
            cbla_frame = HMI_Standard_Display_Frame(self, node)
            cbla_frame.grid(row=row+1, column=col, sticky='NW', pady=(0, 2), padx=(0, 3))

            cbla_frames[node_name] = (cbla_frame, )

            col += 1

            if col == max_col_per_row:
                col = 0
                row += 2


class HMI_CBLA_Plot_Page(tk_gui.Page_Frame):

    def __init__(self, parent_frame: tk_gui.Content_Frame, page_name: str, page_key):

        # label styles
        device_label_style = ttk.Style()
        device_label_style.configure("device_label.TLabel", foreground="black", font=('Helvetica', 12))

        super(HMI_CBLA_Plot_Page, self).__init__(parent_frame, page_name, page_key)



