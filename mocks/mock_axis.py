from comms.comms import *
from axis import Axis


class MockAxis(Axis):

    current_pos = 0
    current_steps = 0

    actual_high_lim = 10000
    actual_low_lim = -10000

    def __init__(self, g, axis_letter="A", old_axis=None):
        Axis.__init__(self, g, axis_letter, old_axis)
        if axis_letter == "B":
            self.actual_high_lim *= 2
            self.actual_low_lim *= 2

    def _mock_switches(self):
        if self.current_pos == self.actual_high_lim:
            return 37
        elif self.current_pos == self.actual_low_lim:
            return 41
        else:
            return 45

    def send(self, command, *parameters):
        Axis.send(self, command, *parameters)
        if command is TELL_SWITCHES:
            return self._mock_switches()

    def setup(self):
        self.stop()
        self.send(CONFIGURE)
        self.motor_type.set(2.5)
        self.encoder_type.set(14)

    def jog(self, forwards=True):
        Axis.jog(self, forwards)
        if forwards:
            self.current_steps = self.actual_high_lim
            self.current_pos = self.actual_high_lim
        else:
            self.current_steps = self.actual_low_lim
            self.current_pos = self.actual_low_lim

    def get_steps(self):
        return self.current_steps

    def get_position(self):
        return self.current_pos

    def set_position(self, steps, wait_for_motion=True):
        Axis.set_position(self, steps, wait_for_motion)
        self.current_pos = steps

    def move_relative(self, steps, wait_for_motion=True):
        Axis.move_relative(self, steps, wait_for_motion)
        self.current_pos += steps
