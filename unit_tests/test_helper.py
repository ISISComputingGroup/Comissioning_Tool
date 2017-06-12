import unittest

from test_program.comms.comms import translate_TS


class Test(unittest.TestCase):
    def test_translate_TS_all_zeros(self):
        # Act
        output = translate_TS(0)

        # Assert
        self.assertFalse(output["Latched"])
        self.assertFalse(output["Home"])
        self.assertTrue(output["Back Limit"])
        self.assertTrue(output["Forward Limit"])
        self.assertFalse(output["Motor Off"])
        self.assertFalse(output["Axis Error"])
        self.assertFalse(output["Axis Moving"])

    def test_translate_TS_all_ones(self):
        # Act
        output = translate_TS(255)

        # Assert
        self.assertTrue(output["Latched"])
        self.assertTrue(output["Home"])
        self.assertFalse(output["Back Limit"])
        self.assertFalse(output["Forward Limit"])
        self.assertTrue(output["Motor Off"])
        self.assertTrue(output["Axis Error"])
        self.assertTrue(output["Axis Moving"])