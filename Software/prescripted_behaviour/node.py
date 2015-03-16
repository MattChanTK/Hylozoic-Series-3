import threading


class Node(threading.Thread):

    def __init__(self, output_vars: list, input_vars: list):

        super(Node, self).__init__(daemon=True)

        if not isinstance(output_vars, list) or not isinstance(input_vars, list):
            raise TypeError('output_vars and input_vars must both be tuple!')

        # constructing the list of output variables
        self.out_var = output_vars

        # constructing the list of input variables
        self.in_var = input_vars

    def run(self):

        raise SystemError('Run must be defined in the child class')


class Tentacle(Node):

    def run(self):

        pass

class IR_Proximity_Sensor(Node):

    def run(self):

        pass







