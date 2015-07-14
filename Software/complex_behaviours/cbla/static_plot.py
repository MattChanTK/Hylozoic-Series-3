
from abstract_node.simple_data_plot import *

if __name__ == '__main__':
    log_dir = os.path.join(os.getcwd(), 'cbla_log')

    plotter = Plotter(log_dir=log_dir, log_header='cbla_mode')
    plotter.plot()
    # plotter.update_plot()
    plotter.save_all_plots(plotter.log_name)
    plotter.show_plots()