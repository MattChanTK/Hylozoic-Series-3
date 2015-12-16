__author__ = 'Matthew'

import os
import sys
from cbla_user_study_plotter import UserStudyPlotter
from cbla_generic_node import *

if __name__ == '__main__':

    for i in range(9, 11):
        log_dir = os.path.join(os.getcwd(), 'cbla_log', 'study_%d' % i)

        plotter = UserStudyPlotter(log_dir=log_dir, study_number=i, session_num=2,
                                   packet_types=(CBLA_Base_Node.cbla_data_type_key, CBLA_Base_Node.prescripted_data_type_key),
                                   info_types=(CBLA_Base_Node.cbla_state_type_key, CBLA_Base_Node.cbla_label_name_key,))

        win_periods = (30.0, 60.0, 120.0, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0)
        for win_period in win_periods:

            plotter.node_active_array = plotter.compute_node_activation_array(win_period=win_period)

            plotter.write_node_activation_array_to_excel(file_name="study_%d (%.2fs).xls" % (plotter.study_number, win_period),
                                                          save_to_dir="user_study_excel_data")


    # plotter.plot(win_period=2.0)
    # plotter.update_plot()
    # plotter.save_all_plots(plotter.log_name)
    # plotter.show_plots()
