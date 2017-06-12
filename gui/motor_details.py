from Tkinter import *
from ttk import *


class Settings(Frame):
    SOFT_LABEL = "Soft"
    HARD_LABEL = "Hard"

    def __init__(self, axis, backlash_reps, master=None):
        Frame.__init__(self, master)
        self.axis = axis

        self.create_widgets(backlash_reps)

    def _conv_limit_repr(self, limit):
        return "Unknown" if limit is None else limit

    def _update_lims(self, *args):
        if self.axis.limits_found.get():
            self.set_lims.configure(state=NORMAL)
        self.limits_tree.set(self.HARD_LABEL, column=0, value=self._conv_limit_repr(self.axis.low_limit))
        self.limits_tree.set(self.HARD_LABEL, column=1, value=self._conv_limit_repr(self.axis.high_limit))

    def _set_soft_limits(self):
        self.axis.set_soft_limits()
        self.limits_tree.set(self.SOFT_LABEL, column=0, value=self._conv_limit_repr(self.axis.get_soft_limit(False)))
        self.limits_tree.set(self.SOFT_LABEL, column=1, value=self._conv_limit_repr(self.axis.get_soft_limit(True)))

    def create_widgets(self, backlash_reps):
        heading_txt = "Motor Details for Axis {}".format(self.axis.axis_letter)
        Label(self, text=heading_txt, font="Times 20").grid(column=0, row=0, columnspan=3, pady="10")

        Label(self, text="Default speed: ").grid(column=0, row=1)
        Entry(self, textvariable=self.axis.JOG_SPEED).grid(column=1, row=1)

        Label(self, text="Soft Limit Offset: ").grid(column=0, row=2)
        Entry(self, textvariable=self.axis.offset).grid(column=1, row=2)

        self.set_lims = Button(self, text="Set Limits", state=DISABLED, command=self._set_soft_limits)
        self.set_lims.grid(column=2, row=2)
        self.axis.limits_found.trace("w", self._update_lims)

        self.limits_tree = Treeview(self, columns=("Lower Limit", "Upper Limit"))
        self.limits_tree.heading('#0', text="Limit Type")
        self.limits_tree.heading('#1', text="Lower Limit")
        self.limits_tree.heading('#2', text="Upper Limit")
        self.limits_tree.insert('', 0, iid=self.HARD_LABEL, text=self.HARD_LABEL)
        self.limits_tree.insert('', 1, iid=self.SOFT_LABEL, text=self.SOFT_LABEL)
        self.limits_tree.grid(column=0, row=3, columnspan=3, padx="40", pady="10")

        self._update_lims()

        Label(self, text="Repeat backlash test: ").grid(column=0, row=4)
        Entry(self, textvariable=backlash_reps).grid(column=1, row=4)
        Label(self, text="times").grid(column=2, row=4)

