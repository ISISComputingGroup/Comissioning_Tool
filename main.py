import serial
import time
from comms import *


class Axis():
    JOG_SPEED = 2000

    def __init__(self, ser, axis_letter="A"):
        self.ser = ser
        self.comms = Comms(ser, axis_letter)
        self.axis_letter = axis_letter

    # Jogs the axis (forwards if not specified)
    def jog(self, backwards=False):
        self.comms.send(START_AXIS)
        sign = -1 if backwards else 1
        self.comms.send(JOG, sign*self.JOG_SPEED)
        self.comms.send(BEGIN)

    def get_position(self):
        return self.comms.recv(TELL_POSITION)

    def stop(self):
        self.comms.send(STOP)
        self.comms.send(AFTER_MOVE)
        self.comms.send(MOTOR_OFF)

    # Gets data once movement has stopped
    def get_switches_after_move(self):
        pass

    def wait_for_move(self):
        move_message = "MV_FINISHED"
        program_name = "#A\r"
        program = [AFTER_MOVE, (MESSAGE, "MV_FINISHED")]
        self.comms.send_program(program_name, program)
        self.comms.send(EXECUTE_PROGRAM, program_name)
        output = ""
        while move_message not in output:
            output = self.comms.read_until_char(":")

def log(message):
    print message


# Searches all the ports for the galil
def check_connection(serial):
    ax = Axis(serial, "A")
    pos = ax.get_position()
    return isinstance(pos, float)


# Return true if forward (away from beam)
def ask_direction():
    opt = {"y": True, "n": False}
    while True:
        dir_inp = raw_input("Is the motor moving away from the beam? (Y/N)").lower()
        if dir_inp in opt:
            return opt[dir_inp]


def begin_test(ser):
    try:
        axis_a = Axis(ser)
        axis_a.stop()
        start_pos = axis_a.get_position()
        log("Starting position is: {}".format(start_pos))
        #axis_a.jog(True)

        fwd = ask_direction()
        end_pos = axis_a.get_position()
        log("Current position is: {}".format(end_pos))
        if start_pos < end_pos and fwd:
            log("Motor running correct direction (forward)")
        elif start_pos > end_pos and not fwd:
            log("Motor running correct direction (backward)")
        else:
            log("Motor running incorrect direction")

        axis_a.wait_for_move()

        time.sleep(1)
    finally:
        axis_a.stop()

if __name__ == "__main__":
    with serial.Serial('COM34', 19200, timeout=1) as ser:
        if not check_connection(ser):
            print "Error, cannot communicate with galil"
        else:
            begin_test(ser)
            time.sleep(0.1)