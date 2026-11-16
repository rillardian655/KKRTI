"""Standard International Atmosphere (ISA) barometric density and temperature model."""

import math

def get_air_density_at_altitude(altitude_msl_m: float) -> float:
    """Estimates air density (kg/m3) up to troposphere (11,000m) based on ISA standard."""
    t0 = 288.15     # Sea level standard temp in K
    p0 = 101325.0   # Sea level standard pressure in Pa
    l = 0.0065      # Temp lapse rate (K/m)
    r = 287.05      # Specific gas constant (J/(kg*K))
    g = 9.80665     # Gravity

    t = t0 - l * altitude_msl_m
    if t <= 0:
        t = 1.0
    p = p0 * math.pow(t / t0, g / (r * l))
    density = p / (r * t)
    return density
