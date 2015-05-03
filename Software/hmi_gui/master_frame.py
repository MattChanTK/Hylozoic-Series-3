__author__ = 'Matthew'

from tkinter import *
from tkinter import ttk
from collections import OrderedDict
from collections import defaultdict
from queue import Queue
from copy import copy
import gc


class Master_Frame(Tk):

    def __init__(self, start_page='home'):

        super(Master_Frame, self).__init__()

        # messenger status panel
        self.status_panel = None

        # navigation panel
        self.nav_panel = None

        # content panel
        self.content_panel = None
        # the contents are stored in the page_dict
        self.curr_page = start_page

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

    def set_curr_content(self, page_key):

        print(page_key)
        self.content_panel.page_frames[page_key].tkraise()

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


class Navigation_Frame(ttk.Frame):

    class Nav_Button(ttk.Button):

        def __init__(self, nav_frame, page_label, page_key):
            self.page_key = page_key
            super(Navigation_Frame.Nav_Button, self).__init__(master=nav_frame, text=page_label,
                                                              command=lambda: nav_frame.controller.set_curr_content(self.page_key))

    def __init__(self, tk_master: Tk, page_dict: dict):

        super(Navigation_Frame, self).__init__(tk_master)

        self.controller = tk_master

        if not isinstance(page_dict, dict):
            raise TypeError("page_dict must be a list or tuple!")

        # list of all the buttons
        self.page_dict = page_dict
        self.button_list = []
        self._build_nav_buttons()

    def _build_nav_buttons(self, max_per_col=8):

        for page_label, page_key in self.page_dict.items():
            self.button_list.append(Navigation_Frame.Nav_Button(self, page_label, page_key))

        col_id = -1
        for i in range(len(self.button_list)):
            row_id = i % max_per_col
            if row_id == 0:
                col_id += 1
            self.button_list[i].grid(row=row_id, column=col_id)


class Content_Frame(ttk.Frame):

    def __init__(self, tk_master: Tk, page_dict: dict):
        super(Content_Frame, self).__init__(tk_master)

        self.page_frames = defaultdict(ttk.Frame)
        for page_key in page_dict.values():
            page_frame = ttk.Frame(self)
            page_label = ttk.Label(page_frame, text="This page is called ==%s==" % page_key)
            page_label.pack()
            self.page_frames[page_key] = page_frame

        self._build_frame()

    def _build_frame(self):

        for page in self.page_frames.values():
            page.grid(row=0, column=0)







