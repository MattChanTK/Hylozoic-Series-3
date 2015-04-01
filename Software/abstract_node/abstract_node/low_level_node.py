__author__ = 'Matthew'

from time import clock
from abstract_node.node import *
from interactive_system import Messenger


class Frond(Node):

    ON_LEFT = 1
    ON_RIGHT = 2
    ON_CENTRE = 3
    OFF = 0

    T_ON_REF = 300

    def __init__(self, messenger: Messenger.Messenger, teensy_name, node_name='frond', left_sma: Var=Var(0), right_sma: Var=Var(0), motion_type: Var=Var(0)):

        super(Frond, self).__init__(messenger, node_name='%s.%s' % (teensy_name, node_name))

        # output variables
        self.out_var['left_sma'] = left_sma
        self.out_var['right_sma'] = right_sma

        # input variable
        self.in_var['motion_type'] = motion_type

        # controller
        self.ctrl_left = Frond.Controller(self.out_var['left_sma'])
        self.ctrl_right = Frond.Controller(self.out_var['right_sma'])

        self.print_to_term = False

    def run(self):

        while True:

            if self.in_var['motion_type'].val == Frond.ON_LEFT:

                T_left_ref = Frond.T_ON_REF
                T_right_ref = 0

            elif self.in_var['motion_type'].val == Frond.ON_RIGHT:
                T_left_ref = 0
                T_right_ref = Frond.T_ON_REF

            elif self.in_var['motion_type'].val  == Frond.ON_CENTRE:
                T_left_ref = Frond.T_ON_REF
                T_right_ref = Frond.T_ON_REF

            else:
                T_left_ref = 0
                T_right_ref = 0

            self.ctrl_left.update(T_left_ref)
            self.ctrl_right.update(T_right_ref)

            sleep(self.messenger.estimated_msg_period*2)


    class Controller:

        def __init__(self, output: Var):

            self.KP = 15.0
            self.KI = 0.0005
            self.K_heating = 0.8
            self.K_dissipate = 0.1

            self.output = output
            self.T_model = 0
            self.T_err_sum = 0
            self.t0 = clock()

        def update(self, T_ref):

            self.T_model += (self.K_heating * self.output.val - self.K_dissipate * self.T_model) * (clock() - self.t0)

            T_err = (T_ref - self.T_model)
            output_p = self.KP * T_err
            self.T_err_sum += T_err
            output_i = self.KI*self.T_err_sum
            self.output.val = min(max(0, output_p + output_i), 255)

            self.t0=clock()
            return self.output.val
