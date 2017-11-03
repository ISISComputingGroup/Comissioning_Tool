import time
import numpy as np
from tkinter import StringVar, W, E, ttk, messagebox

from comms.comms import start_recording
from motor_tests.motor_test import MotorTest

GALIL_ARRAY_MAX = 8000


class EncoderTest(MotorTest):
    name = "Encoder Test"
    enc_name = "Encoder Counts"
    motor_name = "Motor Steps"

    dir_opts = ["FORWARDS", "BACKWARDS", "BOTH"]

    def __init__(self, event_queue, logger, axis, g):
        MotorTest.__init__(self, axis, event_queue, logger)

        self.save_path = StringVar(value="data\\test_data_{axis}_{velo}_{dir}")
        self.direction = StringVar()

        self.g = g

    def _get_arr(self, arr_name):
        arr = self.g.GArrayUpload(arr_name, -1, -1)
        return [int(x) for x in arr]

    def _format_save_path(self, axis, forward):
        direct = "forwards" if forward else "backwards"
        path = self.save_path.get()

        if "." not in path:
            path += ".csv"

        return path.format(axis=axis.axis_letter, velo=axis.JOG_SPEED.get(), dir=direct)

    def _take_full_data_and_save(self, axis, forward=True):
        data = self.record_data_between(axis, axis.get_soft_limit(not forward), axis.get_soft_limit(forward))

        name = self._format_save_path(axis, forward)
        self.log("Saving data in {}".format(name))
        np.savetxt(name, data.T, fmt="%d", delimiter=",", header="{}, {}".format(self.enc_name, self.motor_name))

    def record_data_between(self, axis, start, stop):
        axis.wipe_program()

        self.log("Moving to start")
        axis.set_position(start)

        self.log("At start")

        enc_array = "enc"
        steps_array = "steps"

        est_data_trans_time = 6*8*GALIL_ARRAY_MAX/115200
        est_time = (axis.get_step_range() / axis.JOG_SPEED.get())

        self.log("Running test, this will take approx. {} seconds".format(est_time+est_data_trans_time))
        prog = start_recording(enc_array, steps_array, est_time)

        axis.download_program_and_execute(prog)

        start = time.time()

        axis.set_position(stop)

        self.log("Finished Motion, gathering data")

        data = np.array([self._get_arr(enc_array), self._get_arr(steps_array)])

        self.log("Took " + str(time.time()-start) + " secs")

        return data

    def perform_test(self):
        idx = self.dir_opts.index(self.direction.get())
        if idx == 0 or idx == 2:
            self._take_full_data_and_save(self.axis, True)
        if idx == 1 or idx == 2:
            self._take_full_data_and_save(self.axis, False)

    def _path_help(self):
        help_msg = "The path can include the following macros:"
        help_msg += "\n  " + chr(2022) + "  {axis}: The name of the axis the test was run on"
        help_msg += "\n  " + chr(2022) + "  {velo}: The speed the test was run at"
        help_msg += "\n  " + chr(2022) + "  {dir}: The direction the test was run in"
        help_msg += '\n\n e.g. "data_{axis}_{velo}_{dir}" becomes "data_A_3000_forwards"'
        help_msg += "\n\n Unless otherwise specified data is saved as a csv file"
        messagebox.showinfo("Path Help", help_msg)

    def get_settings_ui(self, frame):
        frame.grid_columnconfigure(1, weight=1)
        ttk.Label(frame, text="Save as: ").grid(column=0, row=0)
        ttk.Entry(frame, textvariable=self.save_path).grid(column=1, row=0, padx=5, sticky=W+E)
        ttk.Button(frame, text="?", command=self._path_help, width=5).grid(column=2, row=0, sticky=E)

        ttk.Label(frame, text="Test direction: ").grid(column=0, row=1)
        ttk.OptionMenu(frame, self.direction, self.dir_opts[2], *self.dir_opts).grid(column=1, row=1, sticky=W)
