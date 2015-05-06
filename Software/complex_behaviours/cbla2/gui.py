__author__ = 'Matthew'

from abstract_node.gui import *

import cbla_node


class CBLA2_Main_GUI(Main_GUI):

    def pack_frames(self):
        super(CBLA2_Main_GUI, self).pack_frames()


class CBLA2_Learner_Frame(Display_Frame):

    def _construct_frame(self):

        self.status_text = OrderedDict()
        self.status_frame = tk.Frame(self)

        self.status_frame.pack(side=tk.LEFT)
        self.status_frame.columnconfigure(0, weight=1)

        # header label
        self.status_frame_label = tk.Label(self.status_frame, text="CBLA Status", font=("Helvetica", 14))
        self.status_frame_label.grid(row=0, columnspan=2)

        # contents
        for name, node in self.node_list.items():
            if isinstance(node, (cbla_node.CBLA_Tentacle, cbla_node.CBLA_Protocell)):
                for var_name in node.out_var_list:
                    if var_name in ('S', 'M', 'loop_time', 'idle_mode', 'node_step', 'best_val'):
                        self.status_text[(name, var_name)] = [tk.Label(self.status_frame, text="%s.%s" % (name, var_name),
                                                                       fg='black'),
                                                              tk.Label(self.status_frame,
                                                                       text="###",
                                                                       fg='black', width='20', anchor=tk.E, justify=tk.RIGHT)]

    def run(self):

        row_id = 2
        for label in self.status_text.values():
            label[0].grid(column=0, row=row_id, ipadx=10, sticky=tk.W)
            label[1].grid(column=1, row=row_id, ipadx=20, sticky=tk.E)
            row_id += 1

    def updateFrame(self):

        for name, label in self.status_text.items():
            val = self.node_list[name[0]].out_var[name[1]].val

            # formatting the string
            if isinstance(val, (tuple, list)):

                val_text = "("
                for element in val:
                    if isinstance(element, float):
                        val_text += '%0.5f, ' % element
                    elif isinstance(element, int):
                        val_text += '%d, ' % element
                    else:
                        val_text += '%s, ' % str(element)
                val_text += ")"

            else:
                val_text = str(val)[:6]

            msg = "%s" % val_text

            # setting the string
            label[1]["text"] = msg


        self.after(500, self.updateFrame)
        self.update()


if __name__ == '__main__':
    pass