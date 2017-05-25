from string import Template
import re

START_AXIS = "SH$ax\r"
JOG = "JG$ax=$par\r"
BEGIN = "BG$ax\r"
MESSAGE = "MG \"Axis $ax says $par\" {P1}\r"
STOP = "ST$ax\r"
MOTOR_OFF = "MO$ax\r"
TELL_POSITION = "TP$ax\r"
AFTER_MOVE = "AM$ax\r"
CONFIGURE_ENCODER = "CE$ax=$par\r"
CONFIGURE = "CN -1,-1\r"
ENCODER_POSITION = "DE$ax\r"
HOME = "HM$ax\r"
TELL_SWITCHES = "TS$ax\r"

MOTOR_TYPE = "MT$ax=$par\r"
DATA_RECORD = "QR$ax\r"
SPEED = "SP$ax=$par\r"

DOWNLOAD = "DL\r"
END_DOWNLOAD = "EN\r" + chr(26)

EXECUTE_PROGRAM = "XQ$par;"

class Comms():
    def __init__(self, serial, axis_letter):
        self.ser = serial
        self.axis_letter = axis_letter

    def read_until_char(self, c, wait=False):
        output = ""
        while c not in output:
            read = self.ser.read()
            if read:
                output += read
            else:
                if not wait:
                    raise RuntimeError("Reading timed out")
        print "READ: " + output
        return output

    def parse_returned(self, data, as_number):
        if as_number:
            # Strip all chars
            data = float(re.sub(r'[^\d\-\+.]', "", data))
        return data

    def recv(self, command, parameter="?", as_number=True):
        data = self.send(command, parameter)
        return self.parse_returned(data, as_number)

    def _format_command(self, command, parameter=None):
        d = dict(ax=self.axis_letter, par=parameter)
        return Template(command).substitute(d)

    def send(self, command, parameter=None):
        sub = self._format_command(command, parameter)
        self.ser.write(sub)
        print "SENT: " + sub
        return self.read_until_char(":")

    def send_program(self, program_name, commands):
        program = DOWNLOAD + program_name
        for c in commands:
            if isinstance(c, str):
                program += c
            elif isinstance(c, tuple):
                program += self._format_command(c[0], c[1])
        program += END_DOWNLOAD
        self.send(program)