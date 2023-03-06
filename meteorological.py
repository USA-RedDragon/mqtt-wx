import math

from units import convert_k_to_f


def dew_point(temp_f, relative_humidity):
    """
    Calculates the dew point using Arden Buck's methods with parameters that provide the lowest maximum errors.

    Args:
        dry_bulb_temp_f (float): The dry-bulb temperature in degrees Fahrenheit.
        relative_humidity (float): The relative humidity as a percentage (e.g. 50 for 50%).

    Returns:
        float: The dew point temperature in degrees Fahrenheit.
    """
    import math

    # Convert temperature to Celsius
    dry_bulb_temp_c = (temp_f - 32) * 5 / 9

    # Calculate the vapor pressure in kPa
    t = dry_bulb_temp_c
    rh = relative_humidity
    if t >= 0:
        a, b, c = 6.1121, 17.368, 238.88
    else:
        a, b, c = 6.1121, 17.966, 247.15
    p_vapor_saturation = a * math.exp((b * t) / (c + t))
    p_vapor_actual = (rh / 100) * p_vapor_saturation

    # Calculate the dew point temperature in Celsius
    dew_point_temp_c = (c * math.log(p_vapor_actual / a)) / (b - math.log(p_vapor_actual / a))

    # Convert dew point temperature back to Fahrenheit
    dew_point_temp_f = dew_point_temp_c * 9 / 5 + 32

    return dew_point_temp_f


# Heat Index <https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml>
HEAT_INDEX_C1 = -42.379
HEAT_INDEX_C2 = 2.04901523
HEAT_INDEX_C3 = 10.14333127
HEAT_INDEX_C4 = 0.22475541
HEAT_INDEX_C5 = 0.00683783
HEAT_INDEX_C6 = 0.05481717
HEAT_INDEX_C7 = 0.00122874
HEAT_INDEX_C8 = 0.00085282
HEAT_INDEX_C9 = 0.00000199


# Returns heat index in Fahrenheit
def heat_index(temp_f, relative_humidity):
    HI = (HEAT_INDEX_C1 +
          HEAT_INDEX_C2 * temp_f +
          HEAT_INDEX_C3 * relative_humidity -
          HEAT_INDEX_C4 * temp_f * relative_humidity -
          HEAT_INDEX_C5 * temp_f**2 -
          HEAT_INDEX_C6 * relative_humidity**2 +
          HEAT_INDEX_C7 * temp_f**2 * relative_humidity +
          HEAT_INDEX_C8 * temp_f * relative_humidity**2 -
          HEAT_INDEX_C9 * temp_f**2 * relative_humidity**2)

    if relative_humidity < 13 and 80 <= temp_f <= 112:
        HI -= ((13 - relative_humidity) / 4) * math.sqrt((17 - abs(temp_f - 95)) / 17)
    elif relative_humidity > 85 and 80 <= temp_f <= 87:
        HI += ((relative_humidity - 85) / 10) * ((87 - temp_f) / 5)
    else:
        HI = 0.5 * (temp_f + 61.0 + ((temp_f-68.0)*1.2) + (relative_humidity*0.094))

    return HI


# Returns wind chill in Fahrenheit
def wind_chill(temp_f, wind_speed_mph):
    wc = 35.74+0.6215*(temp_f)-35.75*(wind_speed_mph)**0.16+0.4275*(temp_f)*(wind_speed_mph)**0.16

    # Check if the input values are within the accepted range
    if temp_f > 50 or wind_speed_mph < 3:
        return temp_f

    return wc


# Returns frost point in Fahrenheit
def frost_point(temp_k, dewpoint_k):
    return convert_k_to_f(
            dewpoint_k - temp_k + 2671.02 / ((2954.61 / temp_k) + 2.193665 * math.log(temp_k) - 13.3448)
        )
