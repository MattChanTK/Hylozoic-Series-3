__author__ = 'Matthew'

import abstract_node as Abs
from abstract_node import Var, SMA_Controller
from interactive_system import Messenger
from time import sleep


class InteractiveFin(Abs.Node):

    MAX_T_ON_REF = 300

    def __init__(self, messenger: Messenger, node_name='interactiveFin',
                 # Input IR sensors
                 fin_ir: Var=Var(0), left_ir: Var=Var(0), right_ir: Var=Var(0),
                 # Output SMA wires
                 left_sma: Var=Var(0), right_sma: Var=Var(0), left_config=None, right_config=None,
                 # Control variables
                 fin_on_level: Var=Var(0)
                 ):

        super(InteractiveFin, self).__init__(messenger, node_name=node_name)

        # control variable
        self.in_var['fin_on_level'] = fin_on_level

        # output variables
        self.out_var['left_fin_level'] = Var(0)
        self.out_var['right_fin_level'] = Var(0)

        # input variables
        self.left_ir = left_ir
        self.right_ir = right_ir
        self.fin_ir = fin_ir

        # other internal variables
        self.left_ir_thres = 1000
        self.right_ir_thres = 1000
        self.fin_ir_thres = 1000

        # SMA controller
        self.left_sma = left_sma
        self.right_sma = right_sma
        if left_config is None:
            left_config = dict()
        if right_config is None:
            right_config = dict()
        self.ctrl_left = SMA_Controller(self.left_sma, **left_config)
        self.ctrl_right = SMA_Controller(self.right_sma, **right_config)

        self.print_to_term = False

    def run(self):

        while self.alive:

            # When fin sensor detects an object
            if self.fin_ir.val > self.fin_ir_thres:

                # if only the left sensor detects an object
                if self.left_ir.val > self.left_ir_thres and self.right_ir.val <= self.right_ir_thres:
                    self.out_var['left_fin_level'].val = self.in_var['fin_on_level'].val
                    self.out_var['right_fin_level'].val = 0

                # if only the right sensor detects an object
                elif self.right_ir.val > self.right_ir_thres and self.left_ir.val <= self.left_ir_thres:
                    self.out_var['right_fin_level'].val = self.in_var['fin_on_level'].val
                    self.out_var['left_fin_level'].val = 0

                # if both or neither left and right sensors detect something
                else:
                    self.out_var['left_fin_level'].val = self.in_var['fin_on_level'].val
                    self.out_var['right_fin_level'].val = self.in_var['fin_on_level'].val

            else:

                    self.out_var['left_fin_level'].val = 0
                    self.out_var['right_fin_level'].val = 0

            # making sure that the values are not over the limit
            self.out_var['left_fin_level'].val = max(0, min(self.out_var['left_fin_level'].val, self.MAX_T_ON_REF))
            self.out_var['right_fin_level'].val = max(0, min(self.out_var['right_fin_level'].val, self.MAX_T_ON_REF))

            # update the SMA controller
            self.ctrl_left.update(self.out_var['left_fin_level'].val)
            self.ctrl_right.update(self.out_var['right_fin_level'].val)

            sleep(self.messenger.estimated_msg_period*2)


class InteractiveReflex(Abs.Node):

    MAX_LED_LEVEL = 255
    MAX_MOTOR_LEVEL = 150

    def __init__(self, messenger: Messenger, node_name='interactiveReflex',
                 # Input IR sensor
                 reflex_ir: Var=Var(0),
                 # Output LED and motor
                 led_target: Var=Var(0), motor_target: Var=Var(0),
                 # Control variables
                 target_level: Var=Var(0)
                 ):

        super(InteractiveReflex, self).__init__(messenger, node_name=node_name)

        # control variable
        self.in_var['target_level'] = target_level

        # output variables
        self.out_var['led_target'] = led_target
        self.out_var['motor_target'] = motor_target

        # input variables
        self.reflex_ir = reflex_ir

        # other internal variables
        self.reflex_ir_thres = 1000

        self.print_to_term = False

    def run(self):

        while self.alive:

            # When IR sensor detects an object
            if self.reflex_ir.val > self.reflex_ir_thres:

                led_target_level = max(0, min(self.in_var['target_level'].val, self.MAX_LED_LEVEL))
                motor_target_level = max(0, min(self.in_var['target_level'].val, self.MAX_MOTOR_LEVEL))

                self.out_var['led_target'].val = led_target_level
                self.out_var['motor_target'].val = motor_target_level

            else:

                self.out_var['led_target'].val = 0
                self.out_var['motor_target'].val = 0

            sleep(self.messenger.estimated_msg_period*2)
