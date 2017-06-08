import time

import gclib

from axis import Axis
from direction_test.dir_test import DirectionTest
from encoder_test.enc_test import EncoderTest
from direction_test.file_writer import save_axis_data
from test_program.encoder_test.statistics import Statistics
from repeat_test.rep_test import RepeatabilityTest
from backlash_test.bl_test import BacklashTest
import serial.tools.list_ports


def log(message):
    print message

def check_connection(g):
    try:
        info = g.GInfo()
    except Exception as e:
        return False
    return isinstance(info, str)

# Searches all the ports for the galil
def open_connection(g):
    default_port = "COM34"
    open_str = "{} -b 115200"
    ports = []

    try:
        g.GOpen(open_str.format(default_port))
        if check_connection(g):
            return True
    except Exception as e:
        ports = [p[0] for p in serial.tools.list_ports.comports()]
        if default_port in ports:
            ports.remove(default_port)

    for p in ports:
        try:
            g.GOpen(open_str.format(p))
            if check_connection(g):
                return True
        except Exception as e:
            pass

    return False

def begin_test(g):
    option = -1
    axis_a = Axis(g)
    try:
        axis_a.setup()

        while option != 0:
            print "Axis A setup"
            print "What tests would you like to perform?"
            print "1. Directionality test"
            print "2. Encoder/steps accuracy test"
            print "3. Set soft limits"
            print "4. Analyse stats"
            print "5. Repeatability"
            print "6. Backlash"
            print "0. Exit"
            try:
                option = int(raw_input())
            except:
                option = 0

            if option == 1:
                test = DirectionTest(log)
                test.perform_test(axis_a)
                save_axis_data(axis_a)
            elif option == 2:
                test = EncoderTest(log, g)
                test.perform_test(axis_a)
            elif option == 3:
                log("Setting soft limits at 10000 steps from hard limits")
                axis_a.set_soft_limits(10000)
            elif option == 4:
                stats = Statistics()
                stats.analyse_whole_folder("data")
            elif option == 5:
                rep = RepeatabilityTest(log)
                rep.perform_test(axis_a, 10000, 2)
            elif option == 6:
                bl = BacklashTest(log, g, 10)
                bl.perform_test(axis_a)
    finally:
        axis_a.stop()

if __name__ == "__main__":
    g = gclib.py()

    if not open_connection(g):
        print "Error, cannot communicate with galil"
    else:
        begin_test(g)
        time.sleep(0.1)