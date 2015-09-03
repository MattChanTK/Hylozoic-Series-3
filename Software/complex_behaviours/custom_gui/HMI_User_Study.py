__author__ = 'Matthew'
from hmi_gui.tk_gui import *
from .HMI_Standard import *
from abstract_node import CSV_Snapshot
from tkinter import CENTER


class HMI_User_Study(Page_Frame):

    def __init__(self, parent_frame: Content_Frame, page_name: str, page_key, display_var: OrderedDict,
                 snapshot_taker: CSV_Snapshot, switch_mode_var: Var):

        # type checking
        if not isinstance(display_var, dict):
            raise TypeError("display_var must be a dictionary!")
        self.display_var = display_var

        if not isinstance(snapshot_taker, CSV_Snapshot):
            raise TypeError("Snapshot Taker not found!")
        self.snapshot_taker = snapshot_taker

        if not isinstance(switch_mode_var, Var):
            raise TypeError("switch_mode variable not found!")
        self.switch_mode_var = switch_mode_var

        # set up the display window for the participant facing window
        self.public_window = Tk()
        self.public_window.title('Current Number')
        self.public_sample_num_label = ttk.Label(self.public_window, text='0', anchor=CENTER)
        self.public_sample_num_label.config(foreground="black", background="white", font=('Helvetica', 500))
        self.public_sample_num_label.grid(row=0, column=0,  sticky='nsew')
        self.public_window.columnconfigure(0, weight=1)
        self.public_window.rowconfigure(0, weight=1)

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


        # === control panel ===
        row += 1
        # control frame
        control_frame = ttk.Frame(self)
        control_frame.grid(row=row, column=0)

        # sample button
        sample_button = ttk.Button(control_frame, text='Sample Now', command=self.__sample_action)
        sample_button.grid(row=0, column=0, sticky='NW')

        switch_mode_button = ttk.Button(control_frame, text='Switch Mode', command=self.__switch_mode_action)
        switch_mode_button.grid(row=1, column=0, sticky='NW')

    def __sample_action(self):

        self.snapshot_taker.take_snapshot()
        self.public_sample_num_label.configure(text=self.snapshot_taker.row_info['sample_number'].val)

    def __switch_mode_action(self):

        if self.switch_mode_var.val:
            self.switch_mode_var.val = False
        else:
            self.switch_mode_var.val = True
