import numpy as np

class RepeatabilityTest():
    def __init__(self, logger):
        self.log = logger

    def _move_and_log(self, axis, steps):
        axis.move_relative(steps)
        return axis.get_steps(), axis.get_position()


    def perform_test(self, axis, steps, times):
        self.log("Moving to centre...")
        axis.set_position(axis.get_centre())

        begin = []
        end = []

        begin.append((axis.get_steps(), axis.get_position()))

        for i in range(times):
            end.append(self._move_and_log(axis, steps))
            begin.append(self._move_and_log(axis, -steps))

        d = np.array([begin[0], begin[1], end[0], end[1]])
        np.savetxt("data.txt", d, fmt="%d", delimiter=",")

        axis.stop()