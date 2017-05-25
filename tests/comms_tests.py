from comms import *
import unittest
from collections import deque


class MockGalil():
    NUMBER_RETURNED = 100
    DATA_RETURNED = "number_is_" + str(NUMBER_RETURNED)
    last_written = ""
    to_return = deque()

    def write(self, data):
        self.last_written = data
        if "?" in data:
            self.to_return.append(self.DATA_RETURNED)
        self.to_return.append(":")

    def get_last_written(self):
        t_last_written = self.last_written
        self.last_written = ""
        return t_last_written

    def read(self):
        return self.to_return.popleft()


class TestComms(unittest.TestCase):
    def setUp(self):
        self.ser = MockGalil()
        self.comms = Comms(self.ser, "A")

    def assertLastWritten(self, message):
        self.assertEqual(self.ser.last_written, message)

    def test_send_command_no_params(self):
        # Act
        self.comms.send(DOWNLOAD)

        # Assert
        self.assertLastWritten(DOWNLOAD)

    def test_send_command_with_axis(self):
        # Act
        self.comms.send(BEGIN)

        # Assert
        self.assertLastWritten("BGA;")

    def test_send_command_with_axis_and_param(self):
        # Act
        self.comms.send(JOG, 100)

        # Assert
        self.assertLastWritten("JGA=100;")

    def test_send_command_without_expected_params_throws(self):
        # Assert
        self.assertRaises(Exception, self.comms.send(JOG))

    def test_send_recv_command(self):
        # Act
        self.comms.recv(JOG)

        # Assert
        self.assertLastWritten("JGA=?;")

    def test_get_recv_data_raw(self):
        # Act
        returned = self.comms.recv(JOG, False)

        # Assert
        self.assertEqual(returned, self.ser.DATA_RETURNED + ":")

    def test_get_recv_data_as_number(self):
        # Act
        returned = self.comms.recv(JOG)

        # Assert
        self.assertEqual(returned, self.ser.NUMBER_RETURNED)

    def test_get_recv_after_previous_sends(self):
        # Arrange
        self.comms.send(BEGIN)

        # Act
        returned = self.comms.recv(JOG)

        # Assert
        self.assertEqual(returned, self.ser.NUMBER_RETURNED)