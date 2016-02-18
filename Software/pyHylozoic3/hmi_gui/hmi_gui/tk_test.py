__author__ = 'Matthew'

import tk_gui
from collections import OrderedDict

hmi = tk_gui.Master_Frame()
status_frame = tk_gui.Status_Frame(hmi)
content_frame = tk_gui.Content_Frame(hmi)
nav_frame = tk_gui.Navigation_Frame(hmi, content_frame)


page_frames = OrderedDict()
page_frames['page_1'] = tk_gui.Page_Frame(content_frame, 'Page 1', 'page_1')
page_frames['page_2'] = tk_gui.Page_Frame(content_frame, 'Page 2', 'page_2')

content_frame.build_pages(page_frames)
content_frame.set_curr_page(page_key='page_1')

nav_frame.build_nav_buttons()


hmi.start(status_frame=status_frame,
          nav_frame=nav_frame,
          content_frame=content_frame)