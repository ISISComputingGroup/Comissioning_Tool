import string

from comms.comms import format_command, MOTOR_TYPE, CONFIGURE_ENCODER


EPICS_MTR_TYPE = "caput IN:%1:MTR%2{}_MTRTYPE_CMD {}"
EPICS_ENC_TYPE = "caput IN:%1:MTR%2{}_MENCTYPE_CMD {}"

def save_axis_data(axis):
    opt = 0
    while opt != 3:
        print "What format would you like to save the data as?"
        print "1. Galil Code"
        print "2. EPICS-friendly"
        print "3. Don't save"

        try:
            opt = int(raw_input())
        except:
            opt = 0
            continue
        if opt == 3:
            break

        print "Save as: "
        name = raw_input()

        suffixes = [".dmc", ".bat"]
        with open(name + suffixes[opt-1], "w+") as f:
            f.writelines([x + "\n" for x in _get_settings(axis, opt)])

        break


def _conv_motor_type(galil_type):
    conv = {-2.0: 2, 2.0: 3, -2.5: 4, 2.5: 5}
    return conv[galil_type]


def _get_settings(axis, opt):
    out = []
    if opt == 1:
        out.append(format_command(axis, MOTOR_TYPE, axis.motor_type))
        out.append(format_command(axis, CONFIGURE_ENCODER, axis.encoder_type))
    elif opt == 2:
        axis_number = "%02d" % (string.uppercase.index(axis.axis_letter) + 1)

        epics_mtr_type = _conv_motor_type(axis.motor_type)
        out.append("REM Run this with the instrument as the first argument and galil crate as the second")
        out.append(EPICS_MTR_TYPE.format(axis_number, epics_mtr_type))
        out.append(EPICS_ENC_TYPE.format(axis_number, axis.encoder_type % 4))
        out.append("")

    return out