import time
import gclib
from axis import Axis
from direction_test.dir_test import DirectionTest
from encoder_test.enc_test import EncoderTest
from direction_test.file_writer import save_axis_data
from statistics import Statistics

def log(message):
    print message


# Searches all the ports for the galil
def check_connection(g):
    try:
        info = g.GInfo()
    except Exception as e:
        return False
    return isinstance(info, str)

def speed_test(axis):
    pass

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
            print "3. Motor speed test"
            print "4. Set soft limits"
            print "5. Analyse stats"
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
                speed_test(axis_a)
            elif option == 4:
                log("Setting soft limits at 50000 steps from hard limits")
                axis_a.set_soft_limits(50000)
            elif option == 5:
                stats = Statistics()
                stats.analyse_whole_folder("data")


    finally:
        axis_a.stop()

if __name__ == "__main__":
    g = gclib.py()

    g.GOpen("COM34 -b 115200")

    if not check_connection(g):
        print "Error, cannot communicate with galil"
    else:
        begin_test(g)
        time.sleep(0.1)