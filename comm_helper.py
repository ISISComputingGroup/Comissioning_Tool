from string import Template

START_AXIS = "SH$ax"
JOG = "JG$ax=$par"
BEGIN = "BG$ax"
MESSAGE = "MG \"Axis $ax says $par\" {P1}"
STOP = "ST$ax"
MOTOR_OFF = "MO$ax"
TELL_POSITION = "TP$ax"
TELL_STEPS = "TD$ax"
AFTER_MOVE = "AM$ax"
CONFIGURE_ENCODER = "CE$ax=$par"
CONFIGURE = "CN -1,-1"
ENCODER_POSITION = "DE$ax"
HOME = "HM$ax"
TELL_SWITCHES = "TS$ax"

MOTOR_TYPE = "MT$ax=$par"
DATA_RECORD = "QR$ax"
SPEED = "SP$ax=$par"

DOWNLOAD = "DL"
END_DOWNLOAD = "EN"

EXECUTE_PROGRAM = "XQ$par"
HALT_EXECUTE = "HX$par"
LIST_PROGRAM = "LS"

STOP_ON_LIMITS = "$prog;IF (_LF$ax = 0) | (_LR$ax = 0);" + STOP + ";ENDIF;JP $prog;"

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


class Formatter():
    def __init__(self, axis_letter):
        self.axis_letter = axis_letter

    def format_command(self, command, parameter=None):
        d = dict(ax=self.axis_letter, par=parameter)
        return Template(command).substitute(d)

    def get_stop_on_limits(self, program_name):
        if not program_name[0] == "#":
            program_name = "#" + program_name
        d = dict(ax=self.axis_letter, prog=program_name)
        return Template(STOP_ON_LIMITS).substitute(d)