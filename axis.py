from tkinter import IntVar, BooleanVar, DoubleVar

from comms.consts import *
from comms.comms import format_command, translate_TS

from file_writer import convert_axis_to_dict


class Axis:
    """
    A class that represents a single axis on the controller.

    This class should be used as an abstraction instead of talking directly to the controller.
    """
    high_limit = None  # The position of the high hard limit (steps)
    low_limit = None

    safe_to_move = True

    STOP_LIM_PROG_NAME = "LIM"
    MAX_SOFT_LIM = 2147483647

    def __init__(self, g, axis_letter="A"):
        self.g = g
        self.axis_letter = axis_letter

        self.motor_type = DoubleVar()
        self.encoder_type = DoubleVar()

        self.JOG_SPEED = IntVar()

        self.microstep = IntVar()
        self.motor_res = DoubleVar()
        self.enc_res = DoubleVar()

        self.offset = IntVar()  # The offset of the soft limits
        self.limits_found = BooleanVar(value=False)

        self.JOG_SPEED.set(3000)

        self.microstep.set(16)
        self.motor_res.set(1.0)  # Microns per full step
        self.enc_res.set(2.5)  # Counts per micron

    def setup(self):
        """
        Sets up the motor on first start up.
        """
        self.stop()
        self.send(CONFIGURE)
        self.motor_type.set(float(self.send(MOTOR_TYPE, "?")))
        self.encoder_type.set(int(self.send(CONFIGURE_ENCODER, "?")))
        self.send(FORWARD_LIMIT, self.MAX_SOFT_LIM)
        self.send(BACK_LIMIT, -self.MAX_SOFT_LIM)

    def download_program_and_execute(self, program):
        """
        Downloads a galil program into the controller and executes it.
        :param program: The program to download
        """
        prog_name = "name"
        program = format_command(program, self.axis_letter, prog_name)
        self.g.GProgramDownload(program, '')
        self.send(EXECUTE_PROGRAM, "#"+prog_name+",0")

    def send(self, command, *parameters):
        if command not in SAFE_COMMS and not self.safe_to_move:
            raise Exception("Motor has been manually stopped, all tests stopped.")
        to_send = format_command(command, self.axis_letter, *parameters)
        return self.g.GCommand(to_send)

    def jog(self, forwards=True):
        """
        Jogs the axis (forwards if not specified)
        WARNING: If this is run without the STOP_ALL_LIMS program being in the controller it could physically crash
        :param forwards: The direction to jog the motor in, True to jog forwards w.r.t the internal motor direction
                        (default: True)
        """
        self.send(START_AXIS)
        sign = 1 if forwards else -1
        self.send(JOG, sign*self.JOG_SPEED.get())
        self.send(BEGIN)

    def get_steps(self):
        """
        Get the number of motor steps the axis is currently at.
        :return The number of motor steps
        """
        return int(self.send(TELL_STEPS))

    def get_position(self):
        """
        Get the position of the encoder on the motor.
        :return The position of the encoder in counts.
        """
        return int(self.send(TELL_POSITION))

    def set_position(self, steps, wait_for_motion=True):
        """
        Set the position of the axis in steps.
        :param steps: The step position to go to.
        :param wait_for_motion: True if the function should block waiting for the motion to finish
        """
        current_pos = self.get_position()
        if steps != current_pos:
            self.send(SPEED, self.JOG_SPEED.get())
            self.send(START_AXIS)
            self.send(SET_POSITION, steps)
            self.send(BEGIN)
            if wait_for_motion:
                self.wait_for_motion()

    def move_relative(self, steps, wait_for_motion=True):
        """
        Move a number of steps relative to the current position.
        :param steps: The number of steps to move away from the current position.
        :param wait_for_motion: True if the function should block waiting for the motion to finish
        """
        self.send(SPEED, self.JOG_SPEED.get())
        self.send(START_AXIS)
        self.send(POS_REL, steps)
        self.send(BEGIN)
        if wait_for_motion:
            self.wait_for_motion()

    def stop(self):
        """
        Stop this axis.
        """
        self.send(STOP)
        self.send(AFTER_MOVE)
        self.send(MOTOR_OFF)

    def get_switches_after_move(self):
        """
        Waits form motion to stop then gets the data for the limit switches
        :return: Dictionary containing the information from the galil about switches
        """
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
        """
        Set the motor type of the axis.
        :param new_type: The new motor type.
        """
        self.send(MOTOR_TYPE, new_type)
        self.motor_type.set(new_type)

    def set_encoder_type(self, new_type):
        """
        Set the encoder type of the axis.
        :param new_type: The new encoder type.
        """
        self.send(CONFIGURE_ENCODER, new_type)
        self.encoder_type.set(new_type)

    def wipe_program(self):
        """
        Wipes the program inside the controller by sending an empty program.
        """
        self.g.GProgramDownload('', '')

    def set_soft_limits(self):
        """
        Sets the soft limits of the motor based on the already discovered hard limits and the user set offset.
        """
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

    def __str__(self):
        """
        :return: What is printed to file when this axis is saved.
        """
        return str(convert_axis_to_dict(self))


class LoggingAxis(Axis):
    """
    An axis that also logs every command that it sends to the controller.
    """
    def __init__(self, g, axis_letter="A", old_axis=None):
        super().__init__(g, axis_letter, old_axis)

    def download_program_and_execute(self, program):
        prog_name = "name"
        print("Downloading: {}".format(format_command(program, self.axis_letter, prog_name)))
        Axis.download_program_and_execute(self, program)

    def send(self, command, *parameters):
        sent = format_command(command, self.axis_letter, *parameters)
        print("Sending {}".format(sent))
        return Axis.send(self, command, *parameters)
