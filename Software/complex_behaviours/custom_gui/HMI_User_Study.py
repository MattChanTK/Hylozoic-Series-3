__author__ = 'Matthew'
from hmi_gui.tk_gui import *
from abstract_node import UserStudyPanel
from .HMI_Standard import *
from datetime import datetime

class HMI_User_Study(Page_Frame):

    def __init__(self, parent_frame: Content_Frame, page_name: str, page_key, display_var: OrderedDict):

        self.display_var = display_var

        # label style
        var_label_style = ttk.Style()
        var_label_style.configure("var_label.TLabel", foreground="black", font=('Helvetica', 12))

        super(HMI_User_Study, self).__init__(parent_frame, page_name, page_key)

    def _build_page(self):

        max_col_per_row = 1
        col = 0
        row = 0

        display_frames = dict()

        for var_name, var in self.display_var.items():

            # === var label ===
            var_label = ttk.Label(self, text=var_name, style="var_label.TLabel")
            var_label.grid(row=row, column=col, sticky='NW', pady=(0, 10))

            # === var display side ====
            display_frame = HMI_Standard_Display_Frame(self, var)
            display_frame.grid(row=row+1, column=col, sticky='NW', pady=(0, 20), padx=(0, 3))

            display_frames[var_name] = (display_frame, )

            col += 1
            if col == max_col_per_row:
                col = 0
                row += 2
