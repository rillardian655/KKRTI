"""Calculates total specific energy, kinetic energy, and potential energy of the airframe."""

GRAVITY = 9.80665

def calculate_flight_energy(mass_kg: float, groundspeed_m_s: float, altitude_agl_m: float) -> tuple[float, float, float]:
    """Returns (kinetic_joules, potential_joules, total_energy_joules)."""
    ke = 0.5 * mass_kg * (groundspeed_m_s ** 2)
    pe = mass_kg * GRAVITY * max(0.0, altitude_agl_m)
    return (ke, pe, ke + pe)
