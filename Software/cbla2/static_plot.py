__author__ = 'Matthew'
from cbla_engine import cbla_data_plot, cbla_data_collect
from time import clock

if __name__ == '__main__':

    data_file_name = None #'cbla_data_15-04-27_11-41-51 (1).pkl'

    data_file, data_file_name = cbla_data_collect.retrieve_data(file_name=data_file_name)

    plotter = cbla_data_plot.Plotter(data_file)
    plotter.plot()
    # plotter.update_plot()
    plotter.save_all_plots(data_file_name.replace('.pkl', ''))
    plotter.show_plots()
