from comm_helper import *


class Axis():
    JOG_SPEED = 3000
    motor_type = 0
    encoder_type = 0

    high_limit = 411587  # The position of the high hard limit (steps)
    low_limit = 151502
    offset = 10000  # The offset of the soft limits

    STOP_LIM_PROG_NAME = "LIM"

    def __init__(self, g, axis_letter="A"):
        self.g = g
        self.axis_letter = axis_letter

    def setup(self):
        self.stop()
        self._send(CONFIGURE)
        self.motor_type = float(self._send(MOTOR_TYPE, "?"))
        self.encoder_type = int(self._send(CONFIGURE_ENCODER, "?"))

    def download_program_and_execute(self, program):
        prog_name = "name"
        program = format_command(program, self.axis_letter, prog_name)
        self.g.GProgramDownload(program, '')
        self._send(EXECUTE_PROGRAM, "#"+prog_name+",0")

    def _send(self, command, *parameters):
        to_send = format_command(command, self.axis_letter, *parameters)
        return self.g.GCommand(to_send)

    # Jogs the axis (forwards if not specified)
    # WARNING: If this is run without the STOP_ALL_LIMS program being in the controller it could physically crash
    def jog(self, forwards=True):
        self._send(START_AXIS)
        sign = 1 if forwards else -1
        self._send(JOG, sign*self.JOG_SPEED)
        self._send(BEGIN)

    def get_steps(self):
        return int(self._send(TELL_STEPS))

    def get_position(self):
        return int(self._send(TELL_POSITION))

    def set_position(self, steps):
        """
        Set the position of the axis in steps.
        """
        self._send(SPEED, self.JOG_SPEED)
        self._send(START_AXIS)
        self._send(SET_POSITION, steps)
        self._send(BEGIN)

    def stop(self):
        self._send(STOP)
        self._send(AFTER_MOVE)
        self._send(MOTOR_OFF)

    # Gets data once movement has stopped
    def get_switches_after_move(self):
        self.g.GMotionComplete(self.axis_letter)
        result = self._send(TELL_SWITCHES)
        result = translate_TS(int(result))
        if result["Back Limit"]:
            self.low_limit = self.get_steps()
        elif result["Forward Limit"]:
            self.high_limit = self.get_steps()
        return result

    def set_motor_type(self, new_type):
        self.stop()
        self.g.GMotionComplete(self.axis_letter)
        self._send(MOTOR_TYPE, new_type)

    def set_encoder_type(self, new_type):
        self.stop()
        self.g.GMotionComplete(self.axis_letter)
        self._send(CONFIGURE_ENCODER, new_type)

    def wipe_program(self):
        self.g.GProgramDownload('', '')

    def set_soft_limits(self, offset):
        # TODO: Ensure high/low limit defined
        self.offset = offset
        self._send(FORWARD_LIMIT, self.high_limit - offset)
        self._send(BACK_LIMIT, self.low_limit + offset)

    def get_soft_limit(self, forwards=True):
        if forwards:
            return self.high_limit - self.offset
        else:
            return self.low_limit + self.offset

    def get_centre(self):
        return (self.high_limit-self.low_limit)//2

    def get_step_range(self):
        return self.high_limit-self.low_limit-2*self.offset
