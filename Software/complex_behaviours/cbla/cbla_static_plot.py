import os
from cbla_engine.cbla_data_plotter import CBLA_DataPlotter

if __name__ == '__main__':
    log_dir = os.path.join(os.getcwd(), 'cbla_log')

    plotter = CBLA_DataPlotter(log_dir=log_dir, log_header='cbla_mode')
    plotter.plot()
    # plotter.update_plot()
    plotter.save_all_plots(plotter.log_name)
    plotter.show_plots()