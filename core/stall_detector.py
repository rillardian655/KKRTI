"""Monitors airspeed and angle of attack to warn of approaching aerodynamic stall."""

class StallDetector:
    def __init__(self, stall_speed_m_s: float = 11.0, critical_pitch_deg: float = 18.0):
        self.stall_speed = stall_speed_m_s
        self.critical_pitch = critical_pitch_deg

    def evaluate(self, airspeed_m_s: float, pitch_deg: float) -> tuple[bool, str]:
        if airspeed_m_s < self.stall_speed and pitch_deg > (self.critical_pitch / 2.0):
            return True, f"STALL WARNING: Low airspeed ({airspeed_m_s:.1f} m/s) with pitch {pitch_deg:.1f} deg"
        if pitch_deg > self.critical_pitch:
            return True, f"CRITICAL PITCH: Exceeded max safe pitch envelope ({pitch_deg:.1f} deg)"
        return False, "Nominal aerodynamic state"
