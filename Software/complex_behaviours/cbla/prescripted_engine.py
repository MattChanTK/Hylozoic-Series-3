__author__ = 'Matthew'
from collections import OrderedDict
from abstract_node import Var


class Prescripted_Base_Engine(object):

    def __init__(self, in_vars: dict, out_vars: dict, **config):

        # setting the configurations
        self.config = dict()
        if isinstance(config, dict):
            for name, arg in config.items():
                self.config[name] = arg

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

        pass


class Interactive_Light_Engine(Prescripted_Base_Engine):

    def __init__(self, fin_ir: Var=Var(0), led: Var=Var(0),
                 local_action_prob: Var=Var(0),
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

        out_vars = OrderedDict()
        if isinstance(led, Var):
            out_vars['led'] = led
        else:
            raise TypeError("led is not a Var type!")


        # initialize
        super(Interactive_Light_Engine, self).__init__(in_vars=in_vars, out_vars=out_vars, **config)

    def update(self):

        if self.in_vars['fin_ir'].val > 1000:
            self.out_vars['led'].val = 100
        else:
            self.out_vars['led'].val = 0


class Interactive_Reflex_Engine(Prescripted_Base_Engine):

     def __init__(self, scout_ir: Var=Var(0), actuator: Var=Var(0), **config):

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

        super(Interactive_Reflex_Engine, self).__init__(in_vars=in_vars, out_vars=out_vars, **config)


class Interactive_Fin_Engine(Prescripted_Base_Engine):

    def __init__(self, fin_ir: Var=Var(0), scout_ir: Var=Var(0), side_ir: Var=Var(0),
                 local_action_prob: Var=Var(0), actuator=Var(0), **config):

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

        out_vars = OrderedDict()
        if isinstance(actuator, Var):
            out_vars['actuator'] = actuator
        else:
            raise TypeError("actuator is not a Var type!")

        super(Interactive_Fin_Engine, self).__init__(in_vars=in_vars, out_vars=out_vars, **config)

