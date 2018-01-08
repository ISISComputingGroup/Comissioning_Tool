from datetime import date
import json

MTR_TYPE_STR = "Motor Type"
ENC_TYPE_STR = "Encoder Type"
MTR_RES_STR = "Motor Resolution (microns per full step)"
ENC_RES_STR = "Encoder Resolution (counts per micron)"
MICROSTEPS_STR = "Microsteps"
LAST_SPEED_STR = "Last tested speed"
LOW_LIMIT_STR = "Low Limit"
HIGH_LIMIT_STR = "High Limit"
LIM_DISTANCE_STR = "Distance between limits (steps)"
SOFT_LIM_OFF_STR = "Distance between soft limit and hard limit (steps)"
AXIS_LETTER_STR = "Axis letter"


def save_axes(filename, axes):
    """
    Saves the supplied axes as JSON under the given filename.
    :param filename: The filename to save the axes under
    :param axes: A dictionary containing the axes to save
    """
    out = {_: convert_axis_to_dict() for _, axis in axes.items()}
    out["Time of test"] = date.today().strftime("%d/%m/%y")

    with open(filename, mode="w") as f:
        f.write(json.dumps(out))


def load_axes(filename, axes):
    pass

def convert_axis_to_dict(axis):
    """
    Converts an axis into a dictionary describing it's state.
    :param axis: the axis to convert.
    :return: A dictionary describing the axis.
    """
    details = {MTR_TYPE_STR: axis.motor_type.get(),
               ENC_TYPE_STR: axis.encoder_type.get(),
               MTR_RES_STR: axis.motor_res.get(),
               ENC_RES_STR: axis.enc_res.get(),
               MICROSTEPS_STR: axis.microstep.get(),
               LAST_SPEED_STR: axis.JOG_SPEED.get()}

    if axis.limits_found.get():
        details.append({LOW_LIMIT_STR: axis.low_limit,
                        HIGH_LIMIT_STR: axis.high_limit,
                        LIM_DISTANCE_STR: axis.high_limit-axis.low_limit,
                        SOFT_LIM_OFF_STR: axis.offset.get()})
    return details


def convert_dict_to_axis(axis, axis_data_dict):
    """
    Populates an axis with information from a dictionary.
    :param axis_data_dict: the dict describing the axis
    :param axis: the axis object to populate
    """
    axis.set_motor_type(axis_data_dict[MTR_TYPE_STR])
    axis.set_encoder_type(axis_data_dict[ENC_TYPE_STR])
    axis.microstep.set(axis_data_dict[MICROSTEPS_STR])
    axis.motor_res.set(axis_data_dict[MTR_RES_STR])
    axis.enc_res.set(axis_data_dict[ENC_RES_STR])
    axis.JOG_SPEED.set(axis_data_dict[LAST_SPEED_STR])

    if LOW_LIMIT_STR in axis_data_dict:
        axis.low_limit = axis_data_dict[LOW_LIMIT_STR]
        axis.high_limit = axis_data_dict[HIGH_LIMIT_STR]
        axis.offset.set(axis_data_dict[SOFT_LIM_OFF_STR])
        axis.limits_found.set(True)