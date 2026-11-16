"""Nonlinear LiPo battery discharge and internal resistance voltage sag model."""

class BatteryModel:
    def __init__(self, cell_count: int = 4, capacity_mah: float = 5000.0, internal_res_ohm: float = 0.015):
        self.cell_count = cell_count
        self.capacity_mah = capacity_mah
        self.internal_res_ohm = internal_res_ohm
        self.remaining_mah = capacity_mah

    @property
    def percentage(self) -> float:
        return max(0.0, min(100.0, (self.remaining_mah / self.capacity_mah) * 100.0))

    def update(self, current_amps: float, dt_sec: float) -> float:
        used_mah = (current_amps * 1000.0) * (dt_sec / 3600.0)
        self.remaining_mah = max(0.0, self.remaining_mah - used_mah)
        fraction = self.percentage / 100.0
        ocv_per_cell = 3.27 + (0.93 * fraction)
        pack_ocv = ocv_per_cell * self.cell_count
        v_loaded = pack_ocv - (current_amps * self.internal_res_ohm)
        return max(0.0, v_loaded)
