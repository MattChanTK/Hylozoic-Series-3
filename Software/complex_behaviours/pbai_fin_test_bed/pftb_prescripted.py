__author__ = 'Matthew'

from pftb_cmd import PFTB_Cmd, CP
from collections import OrderedDict
from pftb_prescripted_nodes import *
from abstract_node import Var, LED_Driver

class PFTB_Prescripted(PFTB_Cmd):
    log_dir = 'cbla_log'
    log_header = 'pftb_cbla'

    def init_routines(self):

        super(PFTB_Prescripted, self).init_routines()
        self.init_prescripted_components()

    def init_prescripted_components(self):

        teensy_in_use = tuple(self.teensy_manager.get_teensy_name_list())

         # instantiate all the basic components
        for teensy_name in teensy_in_use:

            # check if the teensy exists
            if teensy_name not in self.teensy_manager.get_teensy_name_list():
                print('%s does not exist!' % teensy_name)
                continue

            # check the type of node
            protocol = self.teensy_manager.get_protocol(teensy_name)

            # -- PFTB Triplet Node ---
            if isinstance(protocol, CP.PFTB_Triplet_Protocol):

                # ===== creating components related to the Fins =====
                fin_components = OrderedDict()
                for j in range(protocol.NUM_FIN):
                    fin_components.update(self.build_interactive_fin(teensy_name=teensy_name, fin_id=j))
                    fin_components.update(self.build_interactive_reflex(teensy_name=teensy_name, fin_id=j))
                self.node_list.update(fin_components)

    def build_interactive_fin(self, teensy_name, fin_id):

        fin_components = OrderedDict()

        # specifying the ir sensors
        fin_ir = self.node_list['%s.f%d.ir-f' % (teensy_name, fin_id)].out_var['input']
        left_ir = self.node_list['%s.f%d.ir-s' % (teensy_name, (fin_id + 1) % self.NUM_FIN)].out_var['input']
        right_ir = self.node_list['%s.f%d.ir-s' % (teensy_name, fin_id)].out_var['input']

        # specifying the sma wires
        left_sma = self.node_list['%s.f%d.sma-l' % (teensy_name, fin_id)].in_var['output']
        right_sma = self.node_list['%s.f%d.sma-r' % (teensy_name, fin_id)].in_var['output']


        # fin on level as a Var
        fin_on_level = Var(300)

        interactive_fin = InteractiveFin(self.messenger, node_name='%s.f%d.iFin' % (teensy_name, fin_id),
                                         # Input IR sensors
                                         fin_ir=fin_ir, left_ir=left_ir, right_ir=right_ir,
                                         # Output SMA wires
                                         left_sma=left_sma, right_sma=right_sma,
                                         left_config=None, right_config=None,
                                         # Control variables
                                         fin_on_level=fin_on_level
                                         )

        fin_components[interactive_fin.node_name] = interactive_fin

        return fin_components

    def build_interactive_reflex(self, teensy_name, fin_id):

        reflex_components = OrderedDict()

        led_target = Abs.Var(0)
        motor_target = Abs.Var(0)

        # Reflex Driver
        led = self.node_list['%s.f%d.rfx-l' % (teensy_name, fin_id)].in_var['output']
        motor = self.node_list['%s.f%d.rfx-m' % (teensy_name, fin_id)].in_var['output']

        reflex_l_driver = LED_Driver(self.messenger,  node_name="%s.f%d.rfx_driver-l" % (teensy_name, fin_id),
                                     led_ref=led_target,
                                     led_out=led, step_period=0.0005)
        reflex_m_driver = LED_Driver(self.messenger,  node_name="%s.f%d.rfx_driver-m" % (teensy_name, fin_id),
                                     led_ref=motor_target,
                                     led_out=motor, step_period=0.0005)

        reflex_components[reflex_l_driver.node_name] = reflex_l_driver
        reflex_components[reflex_m_driver.node_name] = reflex_m_driver

        reflex_ir = self.node_list['%s.f%d.ir-s' % (teensy_name, fin_id)].out_var['input']
        reflex_target_level = Abs.Var(255)

        interactive_reflex = InteractiveReflex(self.messenger, node_name='%s.f%d.iReflex' % (teensy_name, fin_id),
                                                 # Input IR sensor
                                                 reflex_ir=reflex_ir,
                                                 # Output LED and motor
                                                 led_target=led_target, motor_target=motor_target,
                                                 # Control variables
                                                 target_level = reflex_target_level
                                                 )

        reflex_components[interactive_reflex.node_name] = interactive_reflex

        return reflex_components