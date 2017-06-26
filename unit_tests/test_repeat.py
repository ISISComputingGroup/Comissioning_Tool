import unittest
from test_program.motor_tests.rep_test import RepeatabilityTest
from mock import patch
import numpy as np

class MockAxis():
    pass

class MockEventQueue():
    def put(self, *args):
        pass

    def put_and_get(self, *args):
        return True

class Test(unittest.TestCase):
    def log(self, message):
        print message

    @patch("test_program.motor_tests.dir_test.MotorTest.__init__")
    def setUp(self, mock_parent_init):
        mock_parent_init.return_value = None
        self.axis = MockAxis()
        self.test = RepeatabilityTest(MockEventQueue(), self.log, self.axis, None)

    def test_calculating_forward_difference_of_one_move(self):
        # Arrange
        beg = np.array([0, 10])
        end = np.array([10, 100])

        # Act
        ans = self.test.calculate_forward_diff(beg, end)

        # Assert
        self.assertEqual(ans[0], 10)
        self.assertEqual(ans[1], 90)