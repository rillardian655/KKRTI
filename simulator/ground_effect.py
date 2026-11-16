"""Ground effect aerodynamic cushion lift multiplier for low altitude hovering."""

import math

def compute_ground_effect_multiplier(altitude_agl_m: float, rotor_diameter_m: float = 0.35) -> float:
    """Calculates thrust multiplier when hovering close to ground (Cheeseman-Bennett equation)."""
    if altitude_agl_m <= 0.05:
        altitude_agl_m = 0.05
    ratio = rotor_diameter_m / (4.0 * altitude_agl_m)
    # Clamp maximum ground effect factor to 1.25x
    factor = 1.0 / (1.0 - math.pow(ratio, 2))
    return max(1.0, min(1.25, factor))
