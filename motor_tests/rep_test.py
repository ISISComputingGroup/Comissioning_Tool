import numpy as np

class RepeatabilityTest():
    def __init__(self, logger, axis):
        self.log = logger
        self.axis = axis

    def _move_and_log(self, axis, steps):
        axis.move_relative(steps)
        return axis.get_steps(), axis.get_position()

    def perform_test(self, steps, times):
        self.log("Moving to centre...")
        self.axis.set_position(self.axis.get_centre())

        begin = []
        end = []

        begin.append((self.axis.get_steps(), self.axis.get_position()))

        for i in range(times):
            end.append(self._move_and_log(self.axis, steps))
            begin.append(self._move_and_log(self.axis, -steps))

        d = np.array([begin[0], begin[1], end[0], end[1]])
        fname = "data.txt"
        np.savetxt(fname, d, fmt="%d", delimiter=",")

        self.log("Saving in {}".format(fname))

        self.log("Repeatability test finished")