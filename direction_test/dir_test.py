from test_program.comm_helper import STOP_ON_LIMITS

class DirectionTest():
    actually_forward = True

    def __init__(self, logger):
        self.log = logger

    def _ask_direction(self):
        opt = {"y": True, "n": False}
        while True:
            dir_inp = raw_input("Is the motor moving away from the beam? (Y/N)").lower()
            if dir_inp in opt:
                self.actually_forward = opt[dir_inp]
                return

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
        if start_value == end_value:
            raise Exception("Error: Motor not moving")
        else:
            moving_forward = float(start_value) < float(end_value)
            return self.actually_forward == moving_forward

    def _are_switches_correct(self, axis):
        switch_status = axis.get_switches_after_move()
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

    def perform_test(self, axis):
        """
        Tests the directionality of the axis.
        :param axis: The axis to test.
        """
        start_steps = axis.get_steps()
        start_pos = axis.get_position()

        switches = axis.get_switches_after_move()
        if switches["Forward Limit"] or switches["Back Limit"]:
            self.log("Error: Please drive off of limit before starting test")
            return

        """
        Downloads a simple program into the controller that will stop the motor regardless of direction.
        This is useful if you do not trust that the limits are the correct way round. However, it will
        mean that it is impossible to drive off of a limit without code being erased.
        """
        axis.download_program_and_execute(STOP_ON_LIMITS)

        self.log("Jogging forward...")
        axis.jog()

        self._ask_direction()

        motor_correct = self._log_dir_correct("Motor", start_steps, axis.get_steps())
        if not motor_correct:
            new_motor_type = self._calc_reverse_motor(axis.motor_type)
        else:
            new_motor_type = axis.motor_type
        self.log("MT should be: {}".format(new_motor_type))

        encoder_correct = self._log_dir_correct("Encoder", start_pos, axis.get_position())
        if not encoder_correct:
            new_encoder_type = self._calc_reverse_encoder(axis.encoder_type, axis.motor_type)
        else:
            new_encoder_type = axis.encoder_type
        self.log("CE should be: {}".format(new_encoder_type))

        if not self._are_switches_correct(axis):
            self.log("Limits incorrect, manually move motor off of limit and rewire them")
            raise Exception("Tests cannot continue until limits rewired")

        # Correct software config (CE/MT)
        self.log("Correcting controller configuration")
        axis.set_encoder_type(new_encoder_type)
        axis.set_motor_type(new_motor_type)

        # Will have to wipe the stop at all limits program here (scary)
        self.log("Moving to other limit to confirm")
        axis.wipe_program()

        self.actually_forward = not self.actually_forward
        axis.jog(self.actually_forward)

        if not self._are_switches_correct(axis):
            raise Exception("Both limits are the same?!?")

        axis.motor_type = new_motor_type
        axis.encoder_type = new_encoder_type
        
        axis.stop()


