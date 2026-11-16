"""Monitors takeoff rate of climb and attitude bounds to abort failed launches."""

class TakeoffAbortDetector:
    def __init__(self, min_climb_rate_m_s: float = 0.5, max_tilt_deg: float = 35.0, timeout_sec: float = 5.0):
        self.min_climb_rate = min_climb_rate_m_s
        self.max_tilt = max_tilt_deg
        self.timeout_sec = timeout_sec

    def evaluate(self, climb_rate: float, roll_deg: float, pitch_deg: float, elapsed_sec: float) -> tuple[bool, str]:
        if abs(roll_deg) > self.max_tilt or abs(pitch_deg) > self.max_tilt:
            return True, f"Excessive tilt during takeoff: roll={roll_deg:.1f}, pitch={pitch_deg:.1f}"
        if elapsed_sec > self.timeout_sec and climb_rate < self.min_climb_rate:
            return True, f"Insufficient climb rate after {elapsed_sec:.1f}s ({climb_rate:.2f} m/s)"
        return False, "Nominal takeoff profile"
