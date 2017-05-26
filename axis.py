from comm_helper import *

class Axis():
    JOG_SPEED = 1000
    motor_type = 0
    encoder_type = 0
    STOP_LIM_PROG_NAME = "LIM"

    def __init__(self, g, axis_letter="A"):
        self.g = g
        self.axis_letter = axis_letter
        self.helper = Formatter(axis_letter)

    def setup(self):
        self.stop()
        self._send(CONFIGURE)
        self.motor_type = float(self._send(MOTOR_TYPE, "?"))
        self.encoder_type = int(self._send(CONFIGURE_ENCODER, "?"))

    def download_stop_on_all_limits(self):
        """
        Downloads a simple program into the controller that will stop the motor regardless of direction.
        This is useful if you do not trust that the limits are the correct way round. However, it will
        mean that it is impossible to drive off of a limit without code being erased.
        """
        program = self.helper.get_stop_on_limits(self.STOP_LIM_PROG_NAME)
        self.g.GProgramDownload(program, '')
        self._send(EXECUTE_PROGRAM, "#"+self.STOP_LIM_PROG_NAME+",0")

    def _send(self, command, parameter=None):
        to_send = self.helper.format_command(command, parameter)
        return self.g.GCommand(to_send)

    # Jogs the axis (forwards if not specified)
    # WARNING: If this is run without the STOP_ALL_LIMS program being in the controller it could physically crash
    def jog(self, forwards=True):
        self._send(START_AXIS)
        sign = 1 if forwards else -1
        self._send(JOG, sign*self.JOG_SPEED)
        self._send(BEGIN)

    def get_steps(self):
        return self._send(TELL_STEPS)

    def get_position(self):
        return self._send(TELL_POSITION)

    def stop(self):
        self._send(STOP)
        self._send(AFTER_MOVE)
        self._send(MOTOR_OFF)

    # Gets data once movement has stopped
    def get_switches_after_move(self):
        self.g.GMotionComplete(self.axis_letter)
        result = self._send(TELL_SWITCHES)
        result = translate_TS(int(result))
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