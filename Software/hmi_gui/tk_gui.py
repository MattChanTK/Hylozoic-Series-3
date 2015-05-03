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

    def start(self, status_frame=None, nav_frame=None, content_frame=None):

        if isinstance(status_frame, ttk.Frame):
            self.status_panel = status_frame
        else:
            self.status_panel = ttk.Frame(self)

        if isinstance(content_frame, ttk.Frame):
            self.content_panel = content_frame
        else:
            self.content_panel = ttk.Frame(self)

        if isinstance(nav_frame, ttk.Frame):
            self.nav_panel = nav_frame
        else:
            self.nav_panel = ttk.Frame(self)

        self.__construct_gui()
        self.run()

    def run(self):
        self.__construct_gui()

        self.mainloop()

    def __construct_gui(self):

        self.status_panel.grid(row=1, column=0, columnspan=2)
        self.content_panel.grid(row=0, column=1)
        self.nav_panel.grid(row=0, column=0)


class Status_Frame(ttk.Frame):

    def __init__(self, tk_master: Tk):
        super(Status_Frame, self).__init__(tk_master)

        self.status_label = ttk.Label(self, text="Status: Running")

        self.build_frame()

    def build_frame(self):
        self.status_label.pack()


class Content_Frame(ttk.Frame):

    def __init__(self, tk_master: Tk):
        super(Content_Frame, self).__init__(tk_master)

        self.page_frames = defaultdict(ttk.Frame)

    def build_pages(self, page_dict: dict):

        self.page_frames = page_dict

        for page in self.page_frames.values():
            page.grid(row=0, column=0)

    def set_curr_page(self, page_key):
        if page_key in self.page_frames and isinstance(self.page_frames[page_key], ttk.Frame):
            self.page_frames[page_key].tkraise()


class Page_Frame(ttk.Frame):

    def __init__(self, parent_frame: Content_Frame, page_name: str, page_key):
        super(Page_Frame, self).__init__(parent_frame)

        if not isinstance(page_name, str):
            raise TypeError("Page name must be a string!")

        self.page_name = page_name
        self.page_key = page_key

        self.page_label = ttk.Label(self, text="This page is called ==%s==" % page_name)
        self.page_label.pack()


class Navigation_Frame(ttk.Frame):

    def __init__(self, tk_master: Tk, content_frame: Content_Frame):

        super(Navigation_Frame, self).__init__(tk_master)

        self.content_panel = content_frame

        # list of all the buttons
        self.button_list = []

    def build_nav_buttons(self, max_per_col: int=8):

        if isinstance(max_per_col, int):
            raise TypeError("max_per_col must be an integer!")

        self.button_list = []

        for page_key, page_frame in self.content_panel.page_frames.items():

            self.button_list.append(Nav_Button(self, page_frame.page_name, page_key))

        col_id = -1
        for i in range(len(self.button_list)):
            row_id = i % max_per_col
            if row_id == 0:
                col_id += 1
            self.button_list[i].grid(row=row_id, column=col_id)

    def set_curr_page(self, page_key):
        if page_key in self.content_panel.page_frames \
                and isinstance(self.content_panel.page_frames[page_key], ttk.Frame):
            self.content_panel.page_frames[page_key].tkraise()


class Nav_Button(ttk.Button):

    def __init__(self, nav_frame: Navigation_Frame, page_label, page_key):
        self.nav_panel = nav_frame
        self.page_key = page_key
        super(Nav_Button, self).__init__(master=nav_frame, text=page_label,
                                         command=self.button_action)

    def button_action(self):

        self.nav_panel.set_curr_page(self.page_key)