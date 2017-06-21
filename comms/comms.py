from string import Template
import math
import serial.tools.list_ports
from test_program.mocks.mock_galil import MockGalil
from consts import *
import gclib


def start_recording(enc_name, steps_name, time_to_record, wait_for_speed=True):
    """
    Creates the galil program that will record encoder counts and step values
    :param enc_name: The name of the encoder count array
    :param steps_name: The name of the motor step array
    :param time_to_record: The time to record the array for
    :return: The program to load into the galil
    """
    # Set up arrays
    time_between_records = (time_to_record/4000.0) * 1000
    # TODO: This may only record half the motion due to the floor
    rec_num = int(math.floor(math.log(time_between_records, 2)))  # 2^n msec between records
    rec_num = min(rec_num, 8)  # 8 is maximum
    rec_num = max(rec_num, 1)  # 1 is minimum

    out = DEALLOCATE_ALL + ";"
    out += CREATE_ARR + ";" + REC_ARR + ";"
    out = _format_parameters(out, enc_name, steps_name)
    out += _format_parameters(REC_DATA, TELL_POSITION, GET_STEPS) + ";"
    if wait_for_speed:
        out += AFTER_SPEED + ";"
    out += _format_parameters(START_REC, rec_num) + ";"
    return "#$par0;" + out  # Add the program name on the beginning


def test_bit(int_type, offset):
    mask = 1 << offset
    return bool(int_type & mask)


def translate_TS(returned_data):
    out = dict()
    out["Latched"] = test_bit(returned_data, 0)
    out["Home"] = test_bit(returned_data, 1)
    out["Back Limit"] = not test_bit(returned_data, 2)
    out["Forward Limit"] = not test_bit(returned_data, 3)
    out["Motor Off"] = test_bit(returned_data, 5)
    out["Axis Error"] = test_bit(returned_data, 6)
    out["Axis Moving"] = test_bit(returned_data, 7)
    return out


def _format_parameters(command, *parameters):
    d = dict()
    for i in range(len(parameters)):
        d["par{}".format(i)] = parameters[i]
    return Template(command).safe_substitute(d)


def format_command(command, axis_letter, *parameters):
    d = dict(ax=axis_letter)
    command = _format_parameters(command, *parameters)
    return Template(command).substitute(d)


def _check_connection(g):
    try:
        info = g.GInfo()
    except Exception as e:
        return False
    return isinstance(info, str)


# Searches all the ports for the galil
def open_connection(g):
    #TODO: Use g.GAddresses

    default_port = "COM34"
    open_str = "{} -b 115200"
    ports = []

    try:
        g.GOpen(open_str.format(default_port))
        if _check_connection(g):
            return True
    except Exception as e:
        ports = [p[0] for p in serial.tools.list_ports.comports()]
        if default_port in ports:
            ports.remove(default_port)

    for p in ports:
        try:
            g.GOpen(open_str.format(p))
            if _check_connection(g):
                return True
        except Exception as e:
            pass

    return False


def create_connection(log):
    #g = MockGalil(log)
    g = gclib.py()

    if not open_connection(g):
        raise IOError("Error, cannot communicate with galil")

    return g