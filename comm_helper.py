from string import Template
import math

START_AXIS = "SH$ax"
JOG = "JG$ax=$par0"
BEGIN = "BG$ax"
MESSAGE = "MG \"Axis $ax says $par0\" {P1}"
STOP = "ST$ax"
MOTOR_OFF = "MO$ax"
TELL_POSITION = "TP$ax"
SET_POSITION = "PA$ax=$par0"
TELL_STEPS = "TD$ax"

AFTER_MOVE = "AM$ax"
AFTER_SPEED = "AS$ax"
CONFIGURE_ENCODER = "CE$ax=$par0"
CONFIGURE = "CN -1,-1"
ENCODER_POSITION = "DE$ax"
HOME = "HM$ax"
TELL_SWITCHES = "TS$ax"

FORWARD_LIMIT = "FL$ax=$par0"
BACK_LIMIT = "BL$ax=$par0"

MOTOR_TYPE = "MT$ax=$par0"
DATA_RECORD = "QR$ax"
SPEED = "SP$ax=$par0"

DOWNLOAD = "DL"
END_DOWNLOAD = "EN"

EXECUTE_PROGRAM = "XQ$par0"
HALT_EXECUTE = "HX$par0"
LIST_PROGRAM = "LS"

DEALLOCATE_ALL = "DA *[0]"
CREATE_ARR = "DM ${par0}[4000], ${par1}[4000]"
REC_ARR = "RA ${par0}[], ${par1}[]"
REC_DATA = "RD _${par0}, _${par1}"
START_REC = "RC ${par0}"
STOP_REC = "RC 0"

WAIT = "WT ${par0}"
GET_STEPS = "DE${ax}"

STOP_ON_LIMITS = "#$par0;IF (_LF$ax = 0) | (_LR$ax = 0);" + STOP + ";ENDIF;JP #$par0;"

def start_recording(enc_name, steps_name, time_to_record):
    # Set up arrays
    time_between_records = (time_to_record/4000.0) * 1000
    # TODO: This may only record half the motion due to the floor
    rec_num = int(math.floor(math.log(time_between_records, 2)))  # 2^n msec between records
    rec_num = min(rec_num, 8)  # 8 is maximum

    print "REC NUM: " + str(rec_num)
    out = DEALLOCATE_ALL + ";"
    out += CREATE_ARR + ";" + REC_ARR + ";"
    out = _format_parameters(out, enc_name, steps_name)
    out += _format_parameters(REC_DATA, TELL_POSITION, GET_STEPS) + ";"
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