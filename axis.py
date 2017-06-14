from Tkinter import IntVar, BooleanVar, DoubleVar

from test_program.comms.consts import *
from test_program.comms.comms import format_command, translate_TS


class Axis():
    high_limit = None  # The position of the high hard limit (steps)
    low_limit = None

    STOP_LIM_PROG_NAME = "LIM"
    MAX_SOFT_LIM = 2147483647

    def __init__(self, g, axis_letter="A"):

        self.g = g
        self.axis_letter = axis_letter

        self.JOG_SPEED = IntVar(value=3000)

        self.motor_type = DoubleVar()
        self.encoder_type = DoubleVar()

        self.offset = IntVar()  # The offset of the soft limits

        self.limits_found = BooleanVar(value=False)

    def setup(self):
        self.stop()
        self.send(CONFIGURE)
        self.motor_type.set(float(self.send(MOTOR_TYPE, "?")))
        self.encoder_type.set(int(self.send(CONFIGURE_ENCODER, "?")))
        self.send(FORWARD_LIMIT, self.MAX_SOFT_LIM)
        self.send(BACK_LIMIT, -self.MAX_SOFT_LIM)

    def download_program_and_execute(self, program):
        prog_name = "name"
        program = format_command(program, self.axis_letter, prog_name)
        self.g.GProgramDownload(program, '')
        self.send(EXECUTE_PROGRAM, "#"+prog_name+",0")

    def send(self, command, *parameters):
        to_send = format_command(command, self.axis_letter, *parameters)
        return self.g.GCommand(to_send)

    # Jogs the axis (forwards if not specified)
    # WARNING: If this is run without the STOP_ALL_LIMS program being in the controller it could physically crash
    def jog(self, forwards=True):
        self.send(START_AXIS)
        sign = 1 if forwards else -1
        self.send(JOG, sign*self.JOG_SPEED.get())
        self.send(BEGIN)

    def get_steps(self):
        return int(self.send(TELL_STEPS))

    def get_position(self):
        return int(self.send(TELL_POSITION))

    def set_position(self, steps, wait_for_motion=True):
        """
        Set the position of the axis in steps.
        """
        self.send(SPEED, self.JOG_SPEED.get())
        self.send(START_AXIS)
        self.send(SET_POSITION, steps)
        self.send(BEGIN)
        if wait_for_motion:
            self.wait_for_motion()

    def move_relative(self, steps, wait_for_motion=True):
        self.send(SPEED, self.JOG_SPEED.get())
        self.send(START_AXIS)
        self.send(POS_REL, steps)
        self.send(BEGIN)
        if wait_for_motion:
            self.wait_for_motion()

    def stop(self):
        self.send(STOP)
        self.send(AFTER_MOVE)
        self.send(MOTOR_OFF)

    # Gets data once movement has stopped
    def get_switches_after_move(self):
        self.wait_for_motion()
        result = self.send(TELL_SWITCHES)
        result = translate_TS(int(result))
        if result["Back Limit"]:
            self.low_limit = self.get_steps()
        elif result["Forward Limit"]:
            self.high_limit = self.get_steps()
        if self.low_limit is not None and self.high_limit is not None:
            self.limits_found.set(True)
        return result

    def _set_after_stop(self, comm, data):
        self.stop()
        self.wait_for_motion()
        self.send(comm, data)

    def set_motor_type(self, new_type):
        self._set_after_stop(MOTOR_TYPE, new_type)

    def set_encoder_type(self, new_type):
        self._set_after_stop(CONFIGURE_ENCODER, new_type)

    def wipe_program(self):
        self.g.GProgramDownload('', '')

    def set_soft_limits(self):
        if self.limits_found.get():
            self.send(FORWARD_LIMIT, self.high_limit - self.offset.get())
            self.send(BACK_LIMIT, self.low_limit + self.offset.get())

    def get_soft_limit(self, forwards=True):
        if self.limits_found.get():
            if forwards:
                return self.high_limit - self.offset.get()
            else:
                return self.low_limit + self.offset.get()
        else:
            return None

    def get_centre(self):
        return self.low_limit + (self.high_limit-self.low_limit)//2

    def get_step_range(self):
        return self.high_limit-self.low_limit-2*self.offset.get()

    def wait_for_motion(self):
        self.g.GMotionComplete(self.axis_letter)
