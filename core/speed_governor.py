"""Ensures commanded accelerations and velocities respect physical vehicle limits."""

class SpeedGovernor:
    def __init__(self, max_speed_m_s: float = 12.0, max_accel_m_s2: float = 3.0):
        self.max_speed = max_speed_m_s
        self.max_accel = max_accel_m_s2
        self.current_speed = 0.0

    def compute_step(self, target_speed: float, dt: float) -> float:
        clamped_target = max(0.0, min(self.max_speed, target_speed))
        diff = clamped_target - self.current_speed
        max_step = self.max_accel * dt
        if abs(diff) <= max_step:
            self.current_speed = clamped_target
        else:
            self.current_speed += max_step if diff > 0 else -max_step
        return self.current_speed
