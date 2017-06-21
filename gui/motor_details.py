from Tkinter import *
from ttk import *
import tkMessageBox


class MotorSettings(Frame):
    SOFT_LABEL = "Soft"
    HARD_LABEL = "Hard"

    def __init__(self, axis, parent):
        Frame.__init__(self, parent, padding="10")
        self.axis = axis

        self.create_widgets()

    def _conv_limit_repr(self, limit):
        return "Unknown" if limit is None else limit

    def _update_lims(self, *args):
        if self.axis.limits_found.get():
            self.set_lims.configure(state=NORMAL)
        self.limits_grid.set(self.HARD_LABEL, column=0, value=self._conv_limit_repr(self.axis.low_limit))
        self.limits_grid.set(self.HARD_LABEL, column=1, value=self._conv_limit_repr(self.axis.high_limit))

    def _set_soft_limits(self):
        self.axis.set_soft_limits()
        self.limits_grid.set(self.SOFT_LABEL, column=0, value=self._conv_limit_repr(self.axis.get_soft_limit(False)))
        self.limits_grid.set(self.SOFT_LABEL, column=1, value=self._conv_limit_repr(self.axis.get_soft_limit(True)))

    def jog_axis(self, forwards):
        msg = "The motor has not yet been setup. This means the limits could be wrong and cause a crash."
        msg += " Continue anyway?"
        if self.axis.limits_found.get() or tkMessageBox.askyesno("Motor Not Setup", msg):
            self.axis.jog(forwards)

    def create_widgets(self):
        heading_txt = "Motor Details for Axis {}".format(self.axis.axis_letter)
        Label(self, text=heading_txt, font="Times 20").grid(column=0, row=0, columnspan=4, pady="10")

        Label(self, text="Speed: ").grid(column=0, row=1)
        Entry(self, textvariable=self.axis.JOG_SPEED).grid(column=1, row=1)

        Button(self, text="Jog Forward", command=lambda: self.jog_axis(True)).grid(column=2, row=1)
        Button(self, text="Jog Backward", command=lambda: self.jog_axis(False)).grid(column=3, row=1)

        Label(self, text="Soft Limit Offset: ").grid(column=0, row=2)
        Entry(self, textvariable=self.axis.offset).grid(column=1, row=2)

        self.set_lims = Button(self, text="Set Limits", state=DISABLED, command=self._set_soft_limits)
        self.set_lims.grid(column=2, row=2)
        self.axis.limits_found.trace("w", self._update_lims)

        self.limits_grid = Treeview(self, columns=("Lower Limit", "Upper Limit"))
        self.limits_grid.heading('#0', text="Limit Type")
        self.limits_grid.heading('#1', text="Lower Limit")
        self.limits_grid.heading('#2', text="Upper Limit")
        self.limits_grid.insert('', 0, iid=self.HARD_LABEL, text=self.HARD_LABEL)
        self.limits_grid.insert('', 1, iid=self.SOFT_LABEL, text=self.SOFT_LABEL)
        self.limits_grid.grid(column=0, row=3, columnspan=4, padx="40", pady="10")

        self._update_lims()

        Label(self, text="Motor Type: ").grid(column=0, row=4)
        self.mot_type = Entry(self, textvariable=self.axis.motor_type, state=DISABLED).grid(column=1, row=4)

        Label(self, text="Encoder Type: ").grid(column=2, row=4)
        self.enc_type = Entry(self, textvariable=self.axis.encoder_type, state=DISABLED).grid(column=3, row=4)

