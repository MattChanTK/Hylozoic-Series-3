__author__ = 'Matthew'

import cbla_local_node as Local
from abstract_node import *

class Spatial_Light_Node(Local.Local_Light_Node):
    def _get_learner_config(self):

        return super(Spatial_Light_Node, self)._get_learner_config()


class Spatial_HalfFin_Node(Local.Local_HalfFin_Node):
    def _get_learner_config(self):

        return super(Spatial_HalfFin_Node, self)._get_learner_config()


class Spatial_Reflex_Node(Local.Local_Reflex_Node):
    def _get_learner_config(self):

        return super(Spatial_Reflex_Node, self)._get_learner_config()

class Spatial_Sum(Simple_Node):

    def __init__(self, messenger: Messenger, node_name='spatial_sum', output: Var=Var(0), **input_var):

        for var in input_var.values():
            if not isinstance(var, Var):
                raise TypeError("Every input variable must be a Var type.")

            if not isinstance(var.val, (float, int)):
                raise TypeError("Every input variable must be a Var of float.")

        super(Spatial_Sum, self).__init__(messenger, node_name, output, **input_var)


    def run(self):

        while self.alive:

            val_arr = []
            for var in self.in_var.values():
                val_arr.append(var.val)

            self.out_var['output'].val = sum(val_arr)

            sleep(self.messenger.estimated_msg_period * 2)

