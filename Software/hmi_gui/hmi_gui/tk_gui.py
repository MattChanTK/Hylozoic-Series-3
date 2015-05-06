__author__ = 'Matthew'

from tkinter import *
from tkinter import ttk
from collections import OrderedDict
from collections import defaultdict

class Master_Frame(Tk):

    def __init__(self):

        super(Master_Frame, self).__init__()

        # messenger status panel
        self.status_panel = None

        # navigation panel
        self.nav_panel = None

        # content panel
        self.content_panel = None

    def start(self, status_frame=None, nav_frame=None, content_frame=None, start_page_key=None):

        if isinstance(status_frame, Status_Frame):
            self.status_panel = status_frame
        else:
            self.status_panel = Status_Frame(self)

        if isinstance(content_frame, Content_Frame):
            self.content_panel = content_frame
        else:
            self.content_panel = Content_Frame(self)

        if isinstance(nav_frame, Navigation_Frame):
            self.nav_panel = nav_frame
        else:
            self.nav_panel = Navigation_Frame(self, self.content_panel)

        if start_page_key in self.content_panel.page_frames:
            if start_page_key in self.nav_panel.button_dict:
                self.nav_panel.set_curr_page(page_key=start_page_key)
            else:
                self.content_panel.set_curr_page(page_key=start_page_key)

        self.__construct_gui()
        self.run()

    def run(self):
        self.__construct_gui()

        self.mainloop()

    def __construct_gui(self):

        self.status_panel.grid(row=1, column=0, columnspan=2, sticky=SE, padx=5)
        self.content_panel.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        self.nav_panel.grid(row=0, column=0, sticky=NW, padx=10, pady=10)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)


class Status_Frame(ttk.Frame):

    def __init__(self, tk_master: Tk):
        super(Status_Frame, self).__init__(tk_master, name='status_panel')

        self._build_frame()

    def _build_frame(self):
        self.status_label = ttk.Label(self, text="Status: Running")
        self.status_label.grid(column=0, row=0)


class Messenger_Status_Frame(Status_Frame):

    def __init__(self, tk_master: Tk, messenger):
        self.messenger = messenger
        super(Messenger_Status_Frame, self).__init__(tk_master)

    def _build_frame(self):

        self.status_label = ttk.Label(self, text="Messenger Update Period: ###")
        self.status_label.grid(column=0, row=0)
        self._update_frame()

    def _update_frame(self):

        try:
            self.status_label["text"] = "Messenger Update Period: %.2fms" % (self.messenger.estimated_msg_period*1000)
        except AttributeError:
            return

        self.after(250, self._update_frame)
        self.update()


class Content_Frame(ttk.Frame):

    def __init__(self, tk_master: Tk):
        super(Content_Frame, self).__init__(tk_master, name='content_panel')

        self.page_frames = defaultdict(ttk.Frame)

    def build_pages(self, page_dict: dict):

        self.page_frames = page_dict

        for page in self.page_frames.values():
            page.grid(row=0, column=0, sticky='nsew')

    def set_curr_page(self, page_key):
        if page_key in self.page_frames and isinstance(self.page_frames[page_key], ttk.Frame):
            self.page_frames[page_key].tkraise()


class Page_Frame(ttk.Frame):

    def __init__(self, parent_frame: Content_Frame, page_name: str, page_key, page_builder_args=()):
        super(Page_Frame, self).__init__(parent_frame)

        if not isinstance(page_name, str):
            raise TypeError("Page name must be a string!")

        self.page_name = page_name
        self.page_key = page_key

        self._build_page(*page_builder_args)

    def _build_page(self, *args):

        self.page_label = ttk.Label(self, text="This page is called %s" % self.page_name)
        self.page_label.pack()


class Navigation_Frame(ttk.Frame):

    def __init__(self, tk_master: Tk, content_panel: Content_Frame):

        super(Navigation_Frame, self).__init__(tk_master, name='nav_panel')

        self.content_panel = content_panel

        # list of all the buttons
        self.button_dict = OrderedDict()

    def build_nav_buttons(self, max_per_col: int=8):

        if not isinstance(max_per_col, int):
            raise TypeError("max_per_col must be an integer!")

        for page_key, page_frame in self.content_panel.page_frames.items():

            self.button_dict[page_key] = Nav_Button(self, page_frame.page_name, page_key)

        col_id = 0
        row_id = 0
        for button in self.button_dict.values():
            if row_id >= max_per_col:
                col_id += 1
                row_id = 0

            button.grid(row=row_id, column=col_id, sticky='nsew')
            row_id += 1

    def set_curr_page(self, page_key):
        if page_key in self.content_panel.page_frames \
                and isinstance(self.content_panel.page_frames[page_key], ttk.Frame):
            self.content_panel.page_frames[page_key].tkraise()

        for button in self.button_dict.values():
            if button.page_key == page_key:
                button.set_active()
            else:
                button.set_inactive()

class Nav_Button(ttk.Button):

    def __init__(self, nav_frame: Navigation_Frame, page_label, page_key):
        self.nav_panel = nav_frame
        self.page_key = page_key

      # style
        active_style = ttk.Style()
        active_style.configure("active_nav.TButton", background="yellow", font=('Helvetica', 10, 'bold'))
        inactive_style = ttk.Style()
        inactive_style.configure("inactive_nav.TButton", foreground="grey", font=('Helvetica', 10))

        super(Nav_Button, self).__init__(master=nav_frame, text=page_label,
                                         style="inactive_nav.TButton", width=16,
                                         command=self.button_action)


    def button_action(self):
        self.nav_panel.set_curr_page(self.page_key)

    def set_active(self):
        self.configure(style="active_nav.TButton")

    def set_inactive(self):
        self.configure(style="inactive_nav.TButton")