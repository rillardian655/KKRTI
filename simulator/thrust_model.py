"""Rotor thrust-to-weight scaling equation for quadcopter motor simulation."""

def calculate_thrust_force_n(rpm: float, prop_diameter_m: float = 0.30, ct: float = 0.11, air_density: float = 1.225) -> float:
    """Calculates aerodynamic thrust force in Newtons: T = Ct * rho * n^2 * D^4."""
    n_rev_per_sec = rpm / 60.0
    thrust = ct * air_density * (n_rev_per_sec ** 2) * (prop_diameter_m ** 4)
    return max(0.0, thrust)
