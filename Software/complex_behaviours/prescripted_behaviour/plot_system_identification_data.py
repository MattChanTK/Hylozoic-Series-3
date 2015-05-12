__author__ = 'Matthew'

import abstract_node.simple_data_collect as data_collect
from abstract_node.simple_data_plot import *

if __name__ == '__main__':
    data_file_name = None

    data_file, data_file_name = data_collect.retrieve_data(file_name=data_file_name, file_header='sys_id_data')

    plotter = Plotter(data_file)
    plotter.plot()
    # plotter.update_plot()
    plotter.save_all_plots(data_file_name.replace('.pkl', ''))
    plotter.show_plots()