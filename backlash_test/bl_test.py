from test_program.comm_helper import start_recording, STOP_REC
from random import randint
import numpy as np

class BacklashTest():
    def __init__(self, log, g):
        self.log = log
        self.g = g
        self.enc_array = "enc"
        self.steps_array = "steps"

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

    def perform_test(self, axis, times):
        self.log("Moving to centre...")
        axis.set_position(axis.get_centre())

        # Have to move a little as not sure which way we came to the centre from
        axis.move_relative(700)

        fwd_bl = []
        back_bl = []

        for i in range(times+1):
            self.log("Testing forward")
            fwd_bl.append(self._do_one_test(axis))

            self.log("Testing backwards")
            back_bl.append(self._do_one_test(axis, False))

        fwd_bl = np.array(fwd_bl)
        back_bl = np.array(back_bl)

        print "Forward is {} +/- {}".format(np.mean(fwd_bl), np.std(fwd_bl))
        print "Back is {} +/- {}".format(np.mean(back_bl), np.std(back_bl))