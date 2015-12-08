__author__ = 'Matthew'

import os
import sys
from cbla_user_study_plotter import UserStudyPlotter
from cbla_generic_node import *

if __name__ == '__main__':

    log_dir = os.path.join(os.getcwd(), 'cbla_log', 'study_1')

    plotter = UserStudyPlotter(log_dir=log_dir,
                               packet_types=(CBLA_Base_Node.cbla_data_type_key, CBLA_Base_Node.prescripted_data_type_key),
                               info_types=(CBLA_Base_Node.cbla_state_type_key, CBLA_Base_Node.cbla_label_name_key,))
    plotter.plot()
    # plotter.update_plot()
    plotter.save_all_plots(plotter.log_name)
    # plotter.show_plots()