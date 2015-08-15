import os
from cbla_engine.cbla_data_plotter import CBLA_DataPlotter
from cbla_generic_node import *

if __name__ == '__main__':
    log_dir = os.path.join(os.getcwd(), 'cbla_log')

    plotter = CBLA_DataPlotter(log_dir=log_dir, log_header='cbla_mode',
                               packet_types=(CBLA_Base_Node.cbla_data_type_key,),
                               info_types=(CBLA_Base_Node.cbla_state_type_key, CBLA_Base_Node.cbla_label_name_key,))
    plotter.plot()
    # plotter.update_plot()
    plotter.save_all_plots(plotter.log_name)
    plotter.show_plots()