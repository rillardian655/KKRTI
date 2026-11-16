"""Calculates estimated UAV flight endurance based on battery capacity and hover power."""

def calculate_endurance(battery_mah: float, cell_count: int, hover_current_amps: float, reserve_pct: float = 20.0) -> float:
    usable_mah = battery_mah * (1.0 - (reserve_pct / 100.0))
    if hover_current_amps <= 0:
        return 0.0
    hours = (usable_mah / 1000.0) / hover_current_amps
    return hours * 60.0  # Return minutes

if __name__ == "__main__":
    minutes = calculate_endurance(battery_mah=5000, cell_count=4, hover_current_amps=18.0)
    print(f"Estimated safe hover endurance: {minutes:.1f} minutes")
