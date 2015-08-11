__author__ = 'Matthew'

import cbla_local_node as Local

class Spatial_Light_Node(Local.Local_Light_Node):
    def _get_learner_config(self):

        return super(Spatial_Light_Node, self)._get_learner_config()


class Spatial_HalfFin_Node(Local.Local_HalfFin_Node):
    def _get_learner_config(self):

        return super(Spatial_HalfFin_Node, self)._get_learner_config()


class Spatial_Reflex_Node(Local.Local_Reflex_Node):
    def _get_learner_config(self):

        return super(Spatial_Reflex_Node, self)._get_learner_config()
