__author__ = 'Matthew'

from abstract_node import *
import interactive_system
from custom_gui import *
from cbla import CBLA_Generic_Node, CBLA_Base_Node

def hmi_init(hmi: tk_gui.Master_Frame, messenger: interactive_system.Messenger, node_list: dict, monitor_only=False):

    if not isinstance(hmi, tk_gui.Master_Frame):
        raise TypeError("HMI must be Master_Frame")
    if not isinstance(node_list, dict):
        raise TypeError("node_list must be a dictionary")

    hmi.wm_title('Manual Control Mode')

    status_frame = tk_gui.Messenger_Status_Frame(hmi, messenger)
    content_frame = tk_gui.Content_Frame(hmi)
    nav_frame = tk_gui.Navigation_Frame(hmi, content_frame)

    control_vars = OrderedDict()
    display_vars = OrderedDict()

    if len(node_list) > 0:

        for name, node in node_list.items():
            node_name = name.split('.')
            teensy_name = node_name[0]
            device_name = node_name[1]
            try:
                output_name = node_name[2]
            except IndexError:
                output_name = "variables"

            if teensy_name not in control_vars:
                control_vars[teensy_name] = OrderedDict()

            if teensy_name not in display_vars:
                display_vars[teensy_name] = OrderedDict()

            # specifying the controlable variables
            if not monitor_only:
                if  device_name not in control_vars[teensy_name]:
                    control_vars[teensy_name][device_name] = OrderedDict()

                if isinstance(node, Output_Node): #and 'sma' not in name:
                     control_vars[teensy_name][device_name][output_name] = node.in_var['output']

            # specifying the displayable variables
            if device_name not in display_vars[teensy_name]:
                display_vars[teensy_name][device_name] = OrderedDict()

            if isinstance(node, Input_Node):
                display_vars[teensy_name][device_name][output_name] = (node.out_var, 'input_node')
            elif isinstance(node, Output_Node):
                display_vars[teensy_name][device_name][output_name] = (node.in_var, 'output_node')
            else:
                display_vars[teensy_name][device_name][output_name + "_input"] = (node.in_var, 'input_node')
                display_vars[teensy_name][device_name][output_name + "_output"] = (node.out_var, 'output_node')

    page_frames = OrderedDict()
    for teensy_name, teensy_display_vars in display_vars.items():

        teensy_control_vars = OrderedDict()
        if teensy_name in control_vars.keys():
            teensy_control_vars = control_vars[teensy_name]
        frame = HMI_Manual_Mode(content_frame, teensy_name, (teensy_name, 'manual_ctrl_page'),
                                teensy_control_vars, teensy_display_vars)
        page_frames[frame.page_key] = frame

        content_frame.build_pages(page_frames)

        nav_frame.build_nav_buttons()

    print('GUI initialized.')
    hmi.start(status_frame=status_frame,
              nav_frame=nav_frame,
              content_frame=content_frame,
              start_page_key=next(iter(page_frames.keys()), ''))


def cbla_hmi_init(hmi: tk_gui.Master_Frame, messenger: interactive_system.Messenger, node_list: dict, in_user_study=False):
    if not isinstance(hmi, tk_gui.Master_Frame):
        raise TypeError("HMI must be Master_Frame")
    if not isinstance(node_list, dict):
        raise TypeError("node_list must be a dictionary")

    hmi.wm_title('CBLA Mode')

    status_frame = tk_gui.Messenger_Status_Frame(hmi, messenger)
    content_frame = tk_gui.Content_Frame(hmi)
    nav_frame = tk_gui.Navigation_Frame(hmi, content_frame)

    # constructing the list of cbla and device display variables
    panel_display_vars = OrderedDict()
    cbla_display_vars = OrderedDict()
    device_display_vars = OrderedDict()

    snapshot_taker = None
    switch_mode_var = None

    if len(node_list) > 0:

        for name, node in node_list.items():

            node_name = name.split('.')
            try:
                teensy_name = node_name[0]
                device_name = node_name[1]

            # non-device based node
            except IndexError:
                if isinstance(node, UserStudyPanel):
                    page_name = 'User Study'
                    for var_name, var in node.out_var.items():
                        if page_name not in panel_display_vars:
                            panel_display_vars[page_name] = OrderedDict()

                        panel_display_vars[page_name][var_name] = ({var_name: var}, 'panel')

                    snapshot_taker = node.snapshot_taker
                    switch_mode_var = node.out_var['prescripted_mode_active']

            # device based node
            else:

                footer = '\nMisc.'
                if isinstance(node, CBLA_Generic_Node):
                    footer = '\nCBLA'

                page_name = teensy_name + footer

                if isinstance(node, CBLA_Base_Node):

                    for var_name, var in node.in_var.items():

                        if page_name not in cbla_display_vars:
                            cbla_display_vars[page_name] = OrderedDict()

                        # specifying the displayable variables
                        if device_name not in cbla_display_vars[page_name]:
                            cbla_display_vars[page_name][device_name] = OrderedDict()

                        cbla_display_vars[page_name][device_name][var_name] = ({var_name: var}, 'input_node')

                    for var_name, var in node.out_var.items():

                        # specifying the displayable variables
                        if device_name not in cbla_display_vars[page_name]:
                            cbla_display_vars[page_name][device_name] = OrderedDict()

                        cbla_display_vars[page_name][device_name][var_name] = ({var_name: var}, 'output_node')

                    for var_name, var in node.cbla_robot.internal_state.items():

                        # specifying the displayable variables
                        if device_name not in cbla_display_vars[page_name]:
                            cbla_display_vars[page_name][device_name] = OrderedDict()

                        cbla_display_vars[page_name][device_name][var_name] = ({var_name: var}, 'robot_internal')

                    # for the special "in_prescripted_mode" variables
                    var_name = 'in_prescripted_mode'
                    cbla_display_vars[page_name][device_name][var_name] = ({var_name: node.prescripted_mode_active}, 'robot_internal')

                else:
                    try:
                        output_name = node_name[2]
                    except IndexError:
                        output_name = "variables"

                    # specifying the displayable variables
                    if page_name not in device_display_vars:
                        device_display_vars[page_name] = OrderedDict()

                    if device_name not in device_display_vars[page_name]:
                        device_display_vars[page_name][device_name] = OrderedDict()

                    if isinstance(node, Input_Node):
                        device_display_vars[page_name][device_name][output_name] = (node.out_var, 'input_node')
                    elif isinstance(node, Output_Node):
                        device_display_vars[page_name][device_name][output_name] = (node.in_var, 'output_node')
                    else:
                        device_display_vars[page_name][device_name][output_name + "_input"] = (node.in_var, 'input_node')
                        device_display_vars[page_name][device_name][output_name + "_output"] = (node.out_var, 'output_node')

    # Putting the variables into the pages
    page_frames = OrderedDict()

    # page for the User study control panel
    if in_user_study:
        page_name = 'User Study'
        user_study_frame = HMI_User_Study(content_frame, page_name=page_name, page_key=page_name,
                                          display_var=panel_display_vars,
                                          snapshot_taker=snapshot_taker, switch_mode_var=switch_mode_var)
        page_frames[page_name] = user_study_frame

    # page for the cbla and device variables
    for page_name, page_vars in tuple(cbla_display_vars.items()) + tuple(device_display_vars.items()):

        teensy_display_vars = OrderedDict()
        teensy_cbla_vars = OrderedDict()

        if page_name in device_display_vars.keys():
            teensy_display_vars = device_display_vars[page_name]
        elif page_name in cbla_display_vars.keys():
            teensy_cbla_vars = cbla_display_vars[page_name]

        frame = HMI_CBLA_Mode(content_frame, page_name, (page_name, 'cbla_display_page'),
                              teensy_cbla_vars, teensy_display_vars)
        page_frames[frame.page_key] = frame

        content_frame.build_pages(page_frames)

        nav_frame.build_nav_buttons(max_per_col=15)

    print('GUI initialized.')
    hmi.start(status_frame=status_frame,
              nav_frame=nav_frame,
              content_frame=content_frame,
              start_page_key=next(iter(page_frames.keys()), ''))