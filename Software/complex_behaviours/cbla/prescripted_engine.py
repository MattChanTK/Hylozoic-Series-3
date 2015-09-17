__author__ = 'Matthew'
from collections import OrderedDict
import random
from time import perf_counter
from abstract_node import Var, DataLogger


class Prescripted_Base_Engine(object):

    def __init__(self, in_vars: dict, out_vars: dict):

        # setting input and output variables
        self.in_vars = OrderedDict()
        self.out_vars = OrderedDict()

        for name, input_var in in_vars.items():
            if isinstance(input_var, Var):
                self.in_vars[name] = input_var
            else:
                raise TypeError("Input %s is not a Var type!" % name)

        for name, output_var in out_vars.items():
            if isinstance(output_var, Var):
                self.out_vars[name] = output_var
            else:
                raise TypeError("Input %s is not a Var type!" % name)

    def update(self):

        data_packet = dict()
        data_packet[DataLogger.packet_time_key] = perf_counter()

        in_var_dict = dict()
        for name, input_var in self.in_vars.items():
            in_var_dict[name] = input_var.val
        data_packet['in_vars'] = in_var_dict

        out_var_dict = dict()
        for name, output_var in self.out_vars.items():
            out_var_dict[name] = output_var.val
        data_packet['out_vars'] = out_var_dict

        return data_packet

class Interactive_Light_Engine(Prescripted_Base_Engine):

    def __init__(self, fin_ir: Var=Var(0), led: Var=Var(0),
                 local_action_prob: Var=Var(0), neighbour_active: Var=Var(0),
                 **config):

        # setting the input and output variables
        in_vars = OrderedDict()
        if isinstance(fin_ir, Var):
            in_vars['fin_ir']  = fin_ir
        else:
            raise TypeError("fin_ir is not a Var type!")

        if isinstance(local_action_prob, Var):
            in_vars['local_action_prob'] = local_action_prob
        else:
            raise TypeError("local_action_prob is not a Var type!")

        if isinstance(neighbour_active, Var):
            in_vars['neighbour_active'] = neighbour_active
        else:
            raise TypeError("neighbour_active is not a Var type!")

        out_vars = OrderedDict()
        if isinstance(led, Var):
            out_vars['led'] = led
        else:
            raise TypeError("led is not a Var type!")

        # setting the configurations
        self.config = dict()

        # default configuration
        self.config['ir_on_thres'] = 1000
        self.config['ir_off_thres'] = 800
        self.config['led_max_output'] = 100
        self.config['random_check_period'] = 1.0
        self.config['activation_period'] = 3.0
        self.config['neighbour_action_k'] = 0.05

        # custom configuration
        if isinstance(config, dict):
            for name, arg in config.items():
                self.config[name] = arg

        # initialize
        super(Interactive_Light_Engine, self).__init__(in_vars=in_vars, out_vars=out_vars)

        # variables
        self.random_check_time = perf_counter()
        self.activation_time = perf_counter()

    def update(self):

        # activate for a fixed period
        if perf_counter() - self.activation_time > self.config['activation_period']:
            # might activate based on random check
            if perf_counter() - self.random_check_time > self.config['random_check_period']:
                do_local_action = random.random() < self.in_vars['local_action_prob'].val
                self.random_check_time = perf_counter()
            else:
                do_local_action = False

            if do_local_action or self.in_vars['fin_ir'].val > self.config['ir_on_thres']:
                self.out_vars['led'].val = self.config['led_max_output']
                self.activation_time = perf_counter()

            elif self.in_vars['neighbour_active'].val:
                self.out_vars['led'].val = self.config['led_max_output'] * self.config['neighbour_action_k']

            elif self.in_vars['fin_ir'].val < self.config['ir_off_thres']:
                self.out_vars['led'].val = 0

        return super(Interactive_Light_Engine, self).update()


class Interactive_Reflex_Engine(Prescripted_Base_Engine):

    def __init__(self, scout_ir: Var=Var(0), actuator: Var=Var(0),
                 **config):

        in_vars = OrderedDict()
        if isinstance(scout_ir, Var):
            in_vars['scout_ir']  = scout_ir
        else:
            raise TypeError("scout_ir is not a Var type!")

        out_vars = OrderedDict()
        if isinstance(actuator, Var):
            out_vars['actuator'] = actuator
        else:
            raise TypeError("actuator is not a Var type!")

        # setting the configurations
        self.config = dict()

        # default configuration
        self.config['ir_on_thres'] = 1000
        self.config['ir_off_thres'] = 800
        self.config['max_output'] = 100
        self.config['pulsing_period'] = 2.0

        # custom configuration
        if isinstance(config, dict):
            for name, arg in config.items():
                self.config[name] = arg

        # initialize
        super(Interactive_Reflex_Engine, self).__init__(in_vars=in_vars, out_vars=out_vars)

        # variables
        self.on_time = perf_counter()
        self.off_time = perf_counter()
        self.activating = False

    def update(self):

        if self.in_vars['scout_ir'].val > self.config['ir_on_thres']:

            if not self.activating and perf_counter() - self.off_time > self.config['pulsing_period']/2:
                self.activating = True
                self.on_time = perf_counter()
            elif self.activating and perf_counter() - self.on_time > self.config['pulsing_period']/2:
                self.activating = False
                self.off_time = perf_counter()

            if self.activating:
                self.out_vars['actuator'].val = self.config['max_output']
            else:
                self.out_vars['actuator'].val = 0
        elif self.in_vars['scout_ir'].val < self.config['ir_off_thres']:
            self.out_vars['actuator'].val = 0

        return super(Interactive_Reflex_Engine, self).update()


class Interactive_HalfFin_Engine(Prescripted_Base_Engine):

    def __init__(self, fin_ir: Var=Var(0), scout_ir: Var=Var(0), side_ir: Var=Var(0),
                 actuator=Var(0), local_action_prob: Var=Var(0), neighbour_active: Var=Var(0),
                 **config):

        in_vars = OrderedDict()
        if isinstance(fin_ir, Var):
            in_vars['fin_ir'] = fin_ir
        else:
            raise TypeError("fin_ir is not a Var type!")

        if isinstance(scout_ir, Var):
            in_vars['scout_ir']  = scout_ir
        else:
            raise TypeError("scout_ir is not a Var type!")

        if isinstance(side_ir, Var):
            in_vars['side_ir'] = side_ir
        else:
            raise TypeError("side_ir is not a Var type!")

        if isinstance(local_action_prob, Var):
            in_vars['local_action_prob'] = local_action_prob
        else:
            raise TypeError("local_action_prob is not a Var type!")

        if isinstance(neighbour_active, Var):
            in_vars['neighbour_active'] = neighbour_active
        else:
            raise TypeError("neighbour_active is not a Var type!")

        out_vars = OrderedDict()
        if isinstance(actuator, Var):
            out_vars['actuator'] = actuator
        else:
            raise TypeError("actuator is not a Var type!")

        # setting the configurations
        self.config = dict()

         # default configuration
        self.config['ir_on_thres'] = 1000
        self.config['ir_off_thres'] = 1200
        self.config['on_output'] = 300
        self.config['off_output'] = 0
        self.config['random_check_period'] = 1.0
        self.config['activation_period'] = 2.0
        self.config['neighbour_action_k'] = 0.2

        # custom configuration
        if isinstance(config, dict):
            for name, arg in config.items():
                self.config[name] = arg

        super(Interactive_HalfFin_Engine, self).__init__(in_vars=in_vars, out_vars=out_vars)

        # variables
        self.random_check_time = perf_counter()
        self.activation_time = perf_counter()

    def update(self):

        # activate for a fixed period
        if perf_counter() - self.activation_time > self.config['activation_period']:

            # might activate based on random check
            if perf_counter() - self.random_check_time > self.config['random_check_period']:
                do_local_action = random.random() < self.in_vars['local_action_prob'].val
                self.random_check_time = perf_counter()
            else:
                do_local_action = False

            if self.in_vars['fin_ir'].val > self.config['ir_on_thres']:

                # turn on unless scout ir doesn't detect anything and side ir does
                if self.in_vars['scout_ir'].val < self.config['ir_off_thres'] and \
                   self.in_vars['side_ir'].val > self.config['ir_on_thres']:

                    self.out_vars['actuator'].val = self.config['off_output']
                else:
                    self.out_vars['actuator'].val = self.config['on_output']

            elif self.in_vars['fin_ir'].val < self.config['ir_off_thres'] and \
                self.out_vars['actuator'].val > self.config['off_output'] and not do_local_action:

                self.out_vars['actuator'].val = self.config['off_output']

            else:

                if do_local_action:
                    self.out_vars['actuator'].val = self.config['on_output']
                    self.activation_time = perf_counter()

                elif self.in_vars['neighbour_active'].val:
                    self.out_vars['actuator'].val = self.config['on_output'] * self.config['neighbour_action_k']
                    self.activation_time = perf_counter()

        return super(Interactive_HalfFin_Engine, self).update()
