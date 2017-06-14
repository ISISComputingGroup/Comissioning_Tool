START_AXIS = "SH$ax"
JOG = "JG$ax=$par0"
BEGIN = "BG$ax"
MESSAGE = "MG \"Axis $ax says $par0\" {P1}"
STOP = "ST$ax"
MOTOR_OFF = "MO$ax"
TELL_POSITION = "TP$ax"
SET_POSITION = "PA$ax=$par0"
POS_REL = "PR$ax=$par0"
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