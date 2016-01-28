__author__ = 'Matthew'
from collections import OrderedDict
import random
from time import perf_counter
from abstract_node import Var, DataLogger


class Prescripted_Base_Engine(object):

    def __init__(self, in_vars: dict, out_vars: dict, in_ranges: dict, out_ranges:dict):

        # setting input and output variables
        self.in_vars = OrderedDict()
        self.in_ranges = OrderedDict()
        self.out_vars = OrderedDict()
        self.out_ranges = OrderedDict()

        for name, input_var in in_vars.items():
            if isinstance(input_var, Var):
                self.in_vars[name] = input_var
            else:
                raise TypeError("Input %s is not a Var type!" % name)

            if name in in_ranges and isinstance(in_ranges[name], tuple):
                self.in_ranges[name] = in_ranges[name]

        for name, output_var in out_vars.items():
            if isinstance(output_var, Var):
                self.out_vars[name] = output_var
            else:
                raise TypeError("Input %s is not a Var type!" % name)

            if name in out_ranges and isinstance(out_ranges[name], tuple):
                self.out_ranges[name] = out_ranges[name]


    def update(self):

        data_packet = dict()
        data_packet[DataLogger.packet_time_key] = perf_counter()

        in_var_dict = dict()
        for name, input_var in self.in_vars.items():
            if name in self.in_ranges:
                in_var_dict[name] = self.normalize(input_var.val, self.in_ranges[name][0], self.in_ranges[name][1])
            else:
                in_var_dict[name] = input_var.val
        data_packet['in_vars'] = tuple(in_var_dict.values())

        out_var_dict = dict()
        for name, output_var in self.out_vars.items():
            if name in self.out_ranges:
                out_var_dict[name] = self.normalize(output_var.val, self.out_ranges[name][0], self.out_ranges[name][1])
            else:
                out_var_dict[name] = output_var.val
        data_packet['out_vars'] = tuple(out_var_dict.values())

        return data_packet

    @staticmethod
    def normalize(orig_val: float, low_bound: float, hi_bound: float) -> float:

        if low_bound >= hi_bound:
            raise ValueError("Lower Bound cannot be greater than or equal to the Upper Bound!")

        return (orig_val - low_bound)/(hi_bound - low_bound)

