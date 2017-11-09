import unittest
from motor_tests.dir_test import DirectionTest
from mock import patch


class MockAxis():
    motor_type = 2.0
    forward_hit = False
    backward_hit = False

    def get_switches_after_move(self):
        return {"Forward Limit": self.forward_hit, "Back Limit": self.backward_hit}


class MockEventQueue():
    def put(self, *args):
        pass

    def put_and_get(self, *args):
        return True


class Test(unittest.TestCase):
    @patch("tkinter.Variable.__init__")
    def setUp(self, mock_tkinter):
        self.axis = MockAxis()
        self.dir = DirectionTest(MockEventQueue(), lambda x: None, self.axis, None)

    def test_GIVEN_equal_positions_WHEN_direction_calculated_THEN_error_raised(self):
        # Assert
        with self.assertRaises(Exception):
            self.dir._is_direction_correct(0, 0)

    def test_GIVEN_motor_going_forward_and_actually_forward_WHEN_direction_calculated_THEN_correct(self):
        # Arrange
        self.dir.actually_forward = True

        # Act
        correct = self.dir._is_direction_correct(0, 10)

        # Assert
        self.assertTrue(correct)

    def test_GIVEN_motor_going_forward_and_not_actually_forward_WHEN_direction_calculated_THEN_incorrect(self):
        # Arrange
        self.dir.actually_forward = False

        # Act
        correct = self.dir._is_direction_correct(0, 10)

        # Assert
        self.assertFalse(correct)

    def test_GIVEN_motor_not_going_forward_and_actually_forward_WHEN_direction_calculated_THEN_incorrect(self):
        # Arrange
        self.dir.actually_forward = True

        # Act
        correct = self.dir._is_direction_correct(10, 0)

        # Assert
        self.assertFalse(correct)

    def test_GIVEN_motor_not_going_forward_and_not_actually_forward_WHEN_direction_calculated_THEN_correct(self):
        # Arrange
        self.dir.actually_forward = False

        # Act
        correct = self.dir._is_direction_correct(10, 0)

        # Assert
        self.assertTrue(correct)

    def test_GIVEN_both_limits_hit_WHEN_switches_calculated_THEN_exception_raised(self):
        # Arrange
        self.axis.forward_hit = True
        self.axis.backward_hit = True

        # Assert
        with self.assertRaises(Exception):
            self.dir._are_switches_correct()

    def test_GIVEN_both_limits_not_hit_WHEN_switches_calculated_THEN_exception_raised(self):
        # Arrange
        self.axis.forward_hit = False
        self.axis.backward_hit = False

        # Assert
        with self.assertRaises(Exception):
            self.dir._are_switches_correct()

    def test_GIVEN_actually_forward_and_forward_limit_hit_WHEN_switches_calculated_THEN_correct(self):
        # Arrange
        self.dir.actually_forward = True
        self.axis.forward_hit = True

        # Act
        correct = self.dir._are_switches_correct()

        # Assert
        self.assertTrue(correct)

    def test_GIVEN_actually_forward_and_backward_limit_hit_WHEN_switches_calculated_THEN_incorrect(self):
        # Arrange
        self.dir.actually_forward = True
        self.axis.backward_hit = True

        # Act
        correct = self.dir._are_switches_correct()

        # Assert
        self.assertFalse(correct)

    def test_GIVEN_not_actually_forward_and_backward_limit_hit_WHEN_switches_calculated_THEN_correct(self):
        # Arrange
        self.dir.actually_forward = False
        self.axis.backward_hit = True

        # Act
        correct = self.dir._are_switches_correct()

        # Assert
        self.assertTrue(correct)

    def test_GIVEN_not_actually_forward_and_forward_limit_hit_WHEN_switches_calculated_THEN_incorrect(self):
        # Arrange
        self.dir.actually_forward = False
        self.axis.forward_hit = True

        # Act
        correct = self.dir._are_switches_correct()

        # Assert
        self.assertFalse(correct)

    def test_GIVEN_motor_type_2_WHEN_reverse_calculated_THEN_new_motor_type_is_2_and_half(self):
        self.assertEqual(2.5, self.dir._calc_reverse_motor(2.0))

    def test_GIVEN_motor_type_2_and_half_WHEN_reverse_calculated_THEN_new_motor_type_is_2(self):
        self.assertEqual(2.0, self.dir._calc_reverse_motor(2.5))

    def test_GIVEN_motor_type_minus_2_WHEN_reverse_calculated_THEN_new_motor_type_is_minus_2_and_half(self):
        self.assertEqual(-2.0, self.dir._calc_reverse_motor(-2.5))

    def test_GIVEN_motor_type_minus_2_and_half_WHEN_reverse_calculated_THEN_new_motor_type_is_minus_2(self):
        self.assertEqual(-2.5, self.dir._calc_reverse_motor(-2.0))

    def test_GIVEN_unrecognized_motor_type_WHEN_reverse_calculated_THEN_error_raised(self):
        with self.assertRaises(Exception):
            self.dir._calc_reverse_motor(1.0)

    def test_GIVEN_enc_type_13_and_motor_type_2_WHEN_reverse_calculated_THEN_new_enc_type_7(self):
        self.assertEqual(7, self.dir._calc_reverse_encoder(13, 2))

    def test_GIVEN_enc_type_6_and_motor_type_two_and_a_half_WHEN_reverse_calculated_THEN_new_enc_type_12(self):
        self.assertEqual(12, self.dir._calc_reverse_encoder(6, 2.5))

    def test_GIVEN_enc_type_3_and_motor_type_two_and_a_half_WHEN_reverse_calculated_THEN_new_enc_type_13(self):
        self.assertEqual(13, self.dir._calc_reverse_encoder(3, 2.5))