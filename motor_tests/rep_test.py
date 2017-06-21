import numpy as np
from Tkinter import IntVar
from ttk import *

from motor_test import MotorTest


class RepeatabilityTest(MotorTest):
    def __init__(self, event_queue, logger, axis):
        MotorTest.__init__(self, axis, event_queue, logger, "Repeatability Test")
        self.axis = axis
        self.steps = IntVar(value=1000)
        self.repeats = IntVar(value=5)

    def _move_and_log(self, axis, steps):
        axis.move_relative(steps)
        return axis.get_steps(), axis.get_position()

    def perform_test(self):
        self.log("Moving to centre...")
        self.axis.set_position(self.axis.get_centre())

        begin = []
        end = []

        begin.append((self.axis.get_steps(), self.axis.get_position()))

        for i in range(self.repeats.get()):
            end.append(self._move_and_log(self.axis, self.steps.get()))
            begin.append(self._move_and_log(self.axis, -self.steps.get()))

        d = np.array([begin[0], begin[1], end[0], end[1]])
        fname = "data.txt"
        np.savetxt(fname, d, fmt="%d", delimiter=",")

        self.log("Saving in {}".format(fname))

    def get_settings_ui(self, frame):
        Label(frame, text="Move").grid(column=0, row=0)
        Entry(frame, textvariable=self.steps).grid(column=1, row=0)
        Label(frame, text="steps and repeat").grid(column=2, row=0)
        Entry(frame, textvariable=self.repeats).grid(column=3, row=0)
        Label(frame, text="times.").grid(column=4, row=0)
