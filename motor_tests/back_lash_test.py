from random import randint

import numpy as np
from tkinter import IntVar, ttk

from comms.comms import start_recording
from comms.consts import STOP_REC
from motor_tests.generic_test import MotorTest


class BacklashTest(MotorTest):
    name = "Backlash Test"

    def __init__(self, event_queue, log, axis, g):
        super().__init__(axis, event_queue, log)
        self.g = g
        self.enc_array = "enc"
        self.steps_array = "steps"

        self.repeats = IntVar(value=5)

        self.prog = start_recording(self.enc_array, self.steps_array, 1, False)

    def _get_arr(self, arr_name):
        arr = self.g.GArrayUpload(arr_name, -1, 200)
        return [int(x) for x in arr]

    def _calc_backlash(self, enc, motor):
        steps = 0
        for i in range(1, len(motor)):
            steps += abs(motor[i] - motor[i-1])
            if enc[i] != enc[i-1] and steps > 0:
                return steps

    def _do_one_test(self, axis, forwards=True):
        direct = 1 if forwards else -1

        axis.download_program_and_execute(self.prog)

        mag = randint(100, 300)  # Random movement gives a better statistic

        axis.move_relative(direct*mag)

        axis.stop()

        axis.send(STOP_REC)

        self.log("Gathering data")

        cnts = self._get_arr(self.enc_array)
        steps = self._get_arr(self.steps_array)

        return self._calc_backlash(cnts, steps)

    def perform_test(self):
        self.log("Moving to centre...")
        self.axis.set_position(self.axis.get_centre())

        # Have to move a little as not sure which way we came to the centre from
        self.axis.move_relative(700)

        fwd_bl = []
        back_bl = []

        for i in range(self.repeats.get()+1):
            self.log("Testing forward")
            fwd_bl.append(self._do_one_test(self.axis))

            self.log("Testing backwards")
            back_bl.append(self._do_one_test(self.axis, False))

        fwd_bl = np.array(fwd_bl)
        back_bl = np.array(back_bl)

        self.log("Forward is {} +/- {}".format(np.mean(fwd_bl), np.std(fwd_bl)))
        self.log("Back is {} +/- {}".format(np.mean(back_bl), np.std(back_bl)))

    def get_settings_ui(self, frame):
        ttk.Label(frame, text="Repeat backlash test: ").grid(column=0, row=0)
        ttk.Entry(frame, textvariable=self.repeats).grid(column=1, row=0)
        ttk.Label(frame, text="times").grid(column=2, row=0)
