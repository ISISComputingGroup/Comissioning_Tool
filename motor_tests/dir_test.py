from tkinter import messagebox

from comms.consts import STOP_ON_LIMITS
from motor_tests.generic_test import MotorTest


class DirectionTest(MotorTest):
    name = "Setup"
    actually_forward = None

    def __init__(self, event_queue, logger, axis, g):
        super().__init__(axis, event_queue, logger)
        self.log = logger

    def _limits_connected(self):
        """
        Confirms with the user that they have checked the limits
        """
        msg = "Have you confirmed that both limits are wired into the controller?"
        return messagebox.askyesno("Physical Limits Connection", msg)

    def _ask_direction(self):
        """
        Asks the user which direction the motor is moving (needed to establish outside reference)
        """
        return messagebox.askyesno("Direction", "Is the motor moving away from the beam?")

    def _calc_reverse_encoder(self, old_encoder_type, new_motor_type):
        main = old_encoder_type % 4
        if main < 2:
            main += 2
        else:
            main -= 2

        if abs(new_motor_type) == 2.0:
            return main + 4
        else:
            return main + 12

    def _calc_reverse_motor(self, old_type):
        """
        Calculates what the new motor type will be when reversed.
        :param old_type: The old motor type that needs reversing
        :return: The new motor type
        """
        if abs(old_type) == 2.5:
            new_type = 2.0
        elif abs(old_type) == 2.0:
            new_type = 2.5
        else:
            raise Exception("Error: Motor type not recognized")
        if old_type < 0:
            new_type *= -1
        return new_type

    def _is_direction_correct(self, start_value, end_value):
        """
        Calculates whether the direction is correct based on the outside reference value.
        :param start_value: The starting position of the motor/encoder
        :param end_value: The end position of the motor/encoder
        :return:
        """
        if start_value == end_value:
            raise Exception("Error: Motor not moving")
        else:
            moving_forward = float(start_value) < float(end_value)
            return self.actually_forward == moving_forward

    def _are_switches_correct(self):
        switch_status = self.axis.get_switches_after_move()
        forward_hit = switch_status["Forward Limit"]
        backward_hit = switch_status["Back Limit"]

        if forward_hit == backward_hit:
            if forward_hit:
                raise Exception("Error: both limit switches hit")
            else:
                raise Exception("Error: tried to run to limit but failed")

        correct = (self.actually_forward and forward_hit) or (not self.actually_forward and backward_hit)

        if correct:
            if self.actually_forward:
                self.log("Forward limit correct")
            else:
                self.log("Backward limit correct")

        return correct

    def _log_dir_correct(self, name, start_val, end_val):
        """
        Calculate whether item is in correct direction and log the result.
        :param name: The item we are checking (e.g. motor/encoder)
        :param start_val: The starting value (e.g. steps/counts)
        :param end_val: The ending value (e.g. steps/counts)
        :return: Whether the direction is correct
        """
        self.log("{} went from {} to {}".format(name, start_val, end_val))
        correct = self._is_direction_correct(start_val, end_val)
        if correct:
            self.log(name + " running correct direction")
        else:
            self.log(name + " running incorrect direction")
        return correct

    def perform_test(self):
        """
        Tests the directionality of the axis.
        """

        if not self.event_queue.put_and_get(self._limits_connected):
            raise Exception("Cannot continue until limits are connected.")

        start_steps = self.axis.get_steps()
        start_pos = self.axis.get_position()

        self.axis.download_program_and_execute(STOP_ON_LIMITS)

        switches = self.axis.get_switches_after_move()
        if switches["Forward Limit"] or switches["Back Limit"]:
            self.log("Error: Please drive off of limit before starting test")
            return

        self.log("Jogging forward...")
        self.axis.jog()

        self.actually_forward = self.event_queue.put_and_get(self._ask_direction)

        motor_correct = self._log_dir_correct("Motor", start_steps, self.axis.get_steps())
        if not motor_correct:
            new_motor_type = self._calc_reverse_motor(self.axis.motor_type.get())
        else:
            new_motor_type = self.axis.motor_type.get()
        self.log("MT should be: {}".format(new_motor_type))

        encoder_correct = self._log_dir_correct("Encoder", start_pos, self.axis.get_position())
        if not encoder_correct:
            new_encoder_type = self._calc_reverse_encoder(self.axis.encoder_type.get(), self.axis.motor_type.get())
        else:
            new_encoder_type = self.axis.encoder_type.get()
        self.log("CE should be: {}".format(new_encoder_type))

        self.log("Running to check limit...")

        if not self._are_switches_correct():
            self.log("Limits incorrect, manually move motor off of limit and rewire them")
            raise Exception("Tests cannot continue until limits rewired")

        # Correct software config (CE/MT)
        if not encoder_correct or not motor_correct:
            self.log("Correcting controller configuration")
            self.axis.set_encoder_type(new_encoder_type)
            self.axis.set_motor_type(new_motor_type)

        # Will have to wipe the stop at all limits program here (scary)
        self.log("Moving to other limit to confirm")
        self.axis.wipe_program()

        self.actually_forward = not self.actually_forward
        self.axis.jog(self.actually_forward)

        if not self._are_switches_correct():
            raise Exception("Both limits are the same?!?")

        self.log("Axis forward limit at: " + str(self.axis.high_limit))
        self.log("Axis back limit at: " + str(self.axis.low_limit))


