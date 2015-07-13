__author__ = 'Matthew'

import os
from abstract_node.simple_data_plot import *

if __name__ == '__main__':
    log_dir = os.path.join(os.getcwd(), 'data_log')

    plotter = Plotter(log_dir=log_dir, log_header='prescripted_mode', log_name='prescripted_mode_data_2015-07-13_12-39-30')
    plotter.plot()
    # plotter.update_plot()
    plotter.save_all_plots(plotter.log_name)
    plotter.show_plots()