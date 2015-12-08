__author__ = 'Matthew'
from cbla_engine import cbla_data_plotter as cdp
from collections import defaultdict
import numpy as np


class UserStudyPlotter(cdp.CBLA_DataPlotter):

    def __init__(self, log_dir, log_header='cbla', packet_types=(), info_types=(), session_num=1):

        self.node_active_array = None

        self.session_num = session_num
        super(UserStudyPlotter, self).__init__(log_dir=log_dir, log_header=log_header,
                                               packet_types=packet_types, info_types=info_types)

    def _construct_plot_objects(self):

        session_data = self.data[self.session_num-1]
        #
        # for node_name, node_data in session_data.items():
        #
        #     self.plot_objects[(self.session_num, node_name, 'history')] = cdp.CBLA_PlotObject(fig_title='History Plot - %s (S%d)' % (node_name, self.session_num))
        #
        # self.plot_objects[(self.session_num, 'metrics')]  = cdp.PlotObject(fig_num=len(self.plot_objects)+1,
        #                                                               fig_title='S%d - Metrics' % self.session_num)

    def plot(self):

        self.node_active_array = self.compute_node_activation_array()

        for node_name, node_data in self.node_active_array.items():
            print(node_name)
            print(node_data)
            print(np.mean(node_data, axis=0))
            print()

    # Compute an array of outputs for each Node wit the specified window period
    # if multiple samples are in one window, the average will be taken.
    # if no sample is in a window, value of the previous window will be used.
    # return a dictionary with name of the node as key and array of outputs as value
    def compute_node_activation_array(self, win_period=1.0):

        if not isinstance(win_period, (int, float)):
            raise TypeError("win_period must be a float or an integer!")

        # pick out the data of the relevant session
        session_data = self.data[self.session_num-1]

        # creating the activation array which will be returned at the end of this function
        active_arrays = dict()

        # iterating through each node type and construct the array
        for node_name, node_data in session_data.items():

            node_array = []

            # only extract the data types that represent output
            for data_type, data_val in node_data.items():

                if data_type == 'M' or data_type == 'out_vars':

                    k = 0
                    window_t = 0.0

                    # number of data points for this variable
                    num_data_pt = len(data_val['x'])

                    # temporary data buffer for a window
                    win_data = []


                    # iterate through every data point
                    while k < num_data_pt:

                        # if the time for this data point is within the current window
                        if data_val['x'][k] < window_t + win_period:
                            # append the value of the data point to the data buffer
                            win_data.append(data_val['y'][k])
                            # increment k to move onto the next data point
                            k += 1
                        # if the time for this data point is beyond this window
                        else:
                            # average the data in the buffer
                            if len(win_data) > 0:
                                # save the average in the node_array
                                node_array.append((window_t, np.mean(win_data)))
                            else:  # if there's no value in that window
                                if len(node_array) > 0:
                                    prev_win_avg = node_array[-1][1]
                                else: # if there isn't any previous value
                                    prev_win_avg = 0.0
                                # save the previous average in the node_array
                                node_array.append((window_t, prev_win_avg))

                            # increment the current window's time
                            window_t += win_period
                            # empty the win_data buffer
                            win_data = []

            # sort the array
            node_array = sorted(node_array, key=lambda x: x[0] )

            # convert it to numpy array and save to the class instance
            active_arrays[node_name] = np.asarray(node_array)

        return active_arrays
