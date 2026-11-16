"""Calculates indicated (IAS) and true airspeed (TAS) from differential dynamic pressure."""

import math

def differential_pressure_to_airspeed(diff_pressure_pa: float, air_density_kg_m3: float = 1.225) -> float:
    """Applies Bernoulli principle to convert dynamic differential pressure into airspeed (m/s)."""
    if diff_pressure_pa <= 0.0 or air_density_kg_m3 <= 0.0:
        return 0.0
    return math.sqrt((2.0 * diff_pressure_pa) / air_density_kg_m3)
