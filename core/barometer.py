"""Hypsometric formula for barometric altitude estimation."""

import math

def pressure_to_altitude(pressure_hpa: float, sea_level_pressure_hpa: float = 1013.25, temp_celsius: float = 25.0) -> float:
    """Calculates altitude above sea level using standard hypsometric barometric equation."""
    if pressure_hpa <= 0.0 or sea_level_pressure_hpa <= 0.0:
        return 0.0
    temp_kelvin = temp_celsius + 273.15
    # Standard lapse rate model
    altitude = ((math.pow(sea_level_pressure_hpa / pressure_hpa, 1.0 / 5.257) - 1.0) * temp_kelvin) / 0.0065
    return max(0.0, altitude)
