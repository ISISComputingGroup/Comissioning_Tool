from string import Template

START_AXIS = "SH$ax"
JOG = "JG$ax=$par0"
BEGIN = "BG$ax"
MESSAGE = "MG \"Axis $ax says $par0\" {P1}"
STOP = "ST$ax"
MOTOR_OFF = "MO$ax"
TELL_POSITION = "TP$ax"
TELL_STEPS = "TD$ax"
AFTER_MOVE = "AM$ax"
CONFIGURE_ENCODER = "CE$ax=$par0"
CONFIGURE = "CN -1,-1"
ENCODER_POSITION = "DE$ax"
HOME = "HM$ax"
TELL_SWITCHES = "TS$ax"

MOTOR_TYPE = "MT$ax=$par0"
DATA_RECORD = "QR$ax"
SPEED = "SP$ax=$par0"

DOWNLOAD = "DL"
END_DOWNLOAD = "EN"

EXECUTE_PROGRAM = "XQ$par0"
HALT_EXECUTE = "HX$par0"
LIST_PROGRAM = "LS"

STOP_ON_LIMITS = "#$par0;IF (_LF$ax = 0) | (_LR$ax = 0);" + STOP + ";ENDIF;JP #$par0;"


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


def format_command(command, axis_letter, *parameters):
    d = dict(ax=axis_letter)
    for i in range(len(parameters)):
        d["par{}".format(i)] = parameters[i]
    return Template(command).substitute(d)