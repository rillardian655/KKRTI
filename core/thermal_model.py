"""Estimates LiPo battery internal heat generation based on ohmic I^2*R dissipation."""

class BatteryThermalModel:
    def __init__(self, internal_res_ohm: float = 0.015, thermal_mass_j_k: float = 250.0, ambient_temp_c: float = 28.0):
        self.internal_res_ohm = internal_res_ohm
        self.thermal_mass = thermal_mass_j_k
        self.temp_c = ambient_temp_c
        self.ambient_temp_c = ambient_temp_c

    def update(self, current_amps: float, dt_sec: float) -> float:
        power_loss_watts = (current_amps ** 2) * self.internal_res_ohm
        heat_generated_j = power_loss_watts * dt_sec
        # Heat dissipation to ambient (convective constant)
        cooling_j = 0.5 * (self.temp_c - self.ambient_temp_c) * dt_sec
        self.temp_c += (heat_generated_j - cooling_j) / self.thermal_mass
        return self.temp_c
