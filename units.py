# Define the conversion functions
def convert_f_to_c(temp_f):
    return (temp_f - 32) * 5/9


def convert_c_to_k(temp_f):
    return temp_f + 273.15


def convert_k_to_f(temp_k):
    return temp_k * 9/5 - 459.67


def convert_mps_to_mph(wind_mps):
    return wind_mps * 2.23694
