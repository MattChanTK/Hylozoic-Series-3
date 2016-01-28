__author__ = 'Matthew'

import math

class NodeSpatialMap(object):

    def __init__(self):

        self.node_dict = dict()

    def add_node(self, node_name, x, y, z=0):

        if isinstance(node_name, str) and \
            isinstance(x, (int, float)) and \
            isinstance(y, (int, float)) and \
                isinstance(z, (int, float)):

            self.node_dict[node_name] = (x, y, z)

        else:
            raise ValueError('Invalid node_name or coordinates.')

    def get_position(self, node_name):

        if node_name in self.node_dict:
            return self.node_dict[node_name]
        else:
            return None

    def get_displacement(self, from_node, to_node):

        if isinstance(from_node, (tuple, list)) and len(from_node) == 3:
            pos_1 = tuple(from_node)
        else:
            pos_1 = self.get_position(from_node)

        if isinstance(to_node, (tuple, list)) and len(to_node) == 3:
            pos_2 = tuple(to_node)
        else:
            pos_2 = self.get_position(to_node)

        if isinstance(pos_2, (tuple, list)) and \
                isinstance(pos_2, (tuple, list))\
                and (len(pos_1) == len(pos_2)):

            displacement = []
            for i in range(len(pos_1)):
                displacement.append(pos_2[i] - pos_1[i])

            return tuple(displacement)
        else:
            return None

    def get_distance(self, node_1, node_2):

        displacement = self.get_displacement(node_1, node_2)

        if displacement:
            return math.sqrt(sum([x**2 for x in displacement]))

        return None


if __name__ == "__main__":

    node_map = NodeSpatialMap()

    node_map.add_node("A", 1, 2, 3)
    node_map.add_node("B", 1, 2, 3)
    node_map.add_node("C", 1, 0, 0)

    print(node_map.get_displacement("A", "B"))
    print(node_map.get_displacement("A", "C"))
    print(node_map.get_distance("A", "C"))
    print(node_map.get_distance("C", "A"))



