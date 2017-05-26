import time
import gclib
from axis import Axis
from direction_test.dir_test import DirectionTest
from direction_test.file_writer import save_axis_data


def log(message):
    print message


# Searches all the ports for the galil
def check_connection(g):
    try:
        info = g.GInfo()
    except Exception as e:
        return False
    return isinstance(info, str)


def encoder_test(axis):
    pass

def speed_test(axis):
    pass

def begin_test(g):
    option = 0
    axis_a = Axis(g)
    try:
        axis_a.setup()

        while option != 4:
            print "Axis A setup"
            print "What tests would you like to perform?"
            print "1. Directionality test"
            print "2. Encoder/steps accuracy test "
            print "3. Motor speed test"
            print "4. Exit"
            try:
                option = int(raw_input())
            except:
                option = 0

            if option == 1:
                test = DirectionTest(log)
                test.perform_test(axis_a)
                save_axis_data(axis_a)
            elif option == 2:
                encoder_test(axis_a)
            elif option == 3:
                speed_test(axis_a)

    finally:
        axis_a.stop()

if __name__ == "__main__":
    g = gclib.py()

    g.GOpen("COM34 -b 19200")

    if not check_connection(g):
        print "Error, cannot communicate with galil"
    else:
        begin_test(g)
        time.sleep(0.1)