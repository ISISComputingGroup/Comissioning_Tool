import time
import numpy as np

from test_program.comms.comms import start_recording
from motor_test import MotorTest

GALIL_ARRAY_MAX = 8000


class EncoderTest(MotorTest):
    def __init__(self, event_queue, logger, axis, g):
        MotorTest.__init__(self, axis, event_queue, logger, "Encoder Test")
        self.axis = axis
        self.g = g

    def _get_arr(self, arr_name):
        arr = self.g.GArrayUpload(arr_name, -1, -1)
        return [int(x) for x in arr]

    def _take_full_data_and_save(self, axis, name, forward=True):
        data = self.record_data_between(axis, axis.get_soft_limit(not forward), axis.get_soft_limit(forward))

        name = "data\\test_data_{}_{}_{}.txt".format(axis.axis_letter, axis.JOG_SPEED.get(), name)

        self.log("Saving data in {}".format(name))
        np.savetxt(name, data, fmt="%d", delimiter=",")

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
        self._take_full_data_and_save(self.axis, "forward", True)

        self._take_full_data_and_save(self.axis, "back", False)