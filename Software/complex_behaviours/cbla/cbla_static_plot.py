import os
import sys
from cbla_engine.cbla_data_plotter import CBLA_DataPlotter
from cbla_generic_node import *

if __name__ == '__main__':


    log_dir = os.path.join(os.getcwd(), 'cbla_log',) # 'study_1')

    if len(sys.argv) > 1:
        log_header = str(sys.argv[1])
    else:
        log_header = None

    if len(sys.argv) > 2:
        log_timestamp = str(sys.argv[2])
    else:
        log_timestamp = None

    plotter = CBLA_DataPlotter(log_dir=log_dir, log_header=log_header, log_timestamp=log_timestamp,
                               packet_types=(CBLA_Base_Node.cbla_data_type_key, CBLA_Base_Node.prescripted_data_type_key),
                               info_types=(CBLA_Base_Node.cbla_state_type_key, CBLA_Base_Node.cbla_label_name_key,))
    plotter.plot()
    # plotter.update_plot()
    plotter.save_all_plots(plotter.log_name)
    # plotter.show_plots()