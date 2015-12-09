__author__ = 'Matthew'
from cbla_engine import cbla_data_plotter as cdp
from collections import defaultdict
import numpy as np
import xlwt
import xlrd
import os


class UserStudyPlotter(cdp.CBLA_DataPlotter):

    def __init__(self, log_dir, study_number, session_num=2, log_header='cbla', packet_types=(), info_types=(),):

        self.node_active_array = None
        self.win_period = None
        self.study_number = study_number

        self.session_num = session_num
        super(UserStudyPlotter, self).__init__(log_dir=log_dir, log_header=log_header,
                                               packet_types=packet_types, info_types=info_types)

    def _construct_plot_objects(self):
        pass

    def plot(self):

        pass

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

            # check if it is prescripted first or CBLA first
            cbla_first = node_data['M']['x'][0] < node_data['out_vars']['x'][0]
            # print("CBLA first?  ", cbla_first)

            if cbla_first:
                data_types = ('M', 'out_vars')
            else:
                data_types = ('out_vars', 'M')

            # extracting the data in the right order

            window_t = 0.0
            for data_type in data_types:
                k = 0

                data_val = node_data[data_type]

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

    def write_node_activation_array_to_excel(self, file_name=None, save_to_dir=None):

        book = xlwt.Workbook(encoding="utf-8")

        sheet = book.add_sheet("Node Activation", cell_overwrite_ok=True)

        cur_row_id = 2
        cur_col_id = 1

        # sort the node_active_array
        self.sorted_array_list = []
        for node_name, node_data in self.node_active_array.items():
            self.sorted_array_list.append((node_name, node_data))
        self.sorted_array_list = sorted(self.sorted_array_list, key=lambda x: x[0])

        sheet.write(1, 0, 'time (s)')
        for node_name, node_data in self.sorted_array_list:

            sheet.write(0, cur_col_id, node_name)
            sheet.write(1, cur_col_id, 'output level')

            for t, output in node_data:

                sheet.write(cur_row_id, 0, t)
                sheet.write(cur_row_id, cur_col_id, output)

                cur_row_id += 1

            cur_row_id = 2
            cur_col_id += 1

        # remember current directory
        cur_dir = os.getcwd()

        # if the directory is specified
        if isinstance(save_to_dir, str):
            # If the directory does not exist, create it
            if not os.path.exists(save_to_dir):
                os.makedirs(save_to_dir)

            os.chdir(save_to_dir)

        # if a file name is specified
        if isinstance(file_name, str):
            book.save(file_name)
        else:
            book.save("study_data.xls")

        # go back to the "current directory"
        os.chdir(cur_dir)