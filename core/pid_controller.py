"""Proportional-Integral-Derivative (PID) controller for UAV altitude and velocity tracking."""

class PIDController:
    def __init__(self, kp: float, ki: float, kd: float, output_min: float = -1.0, output_max: float = 1.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min = output_min
        self.output_max = output_max
        self.integral = 0.0
        self.prev_error = 0.0

    def reset(self):
        self.integral = 0.0
        self.prev_error = 0.0

    def compute(self, target: float, current: float, dt: float) -> float:
        if dt <= 0.0:
            return 0.0

        error = target - current
        self.integral += error * dt

        # Anti-windup clamping
        integral_max = abs(self.output_max) / (self.ki if self.ki > 0 else 1.0)
        self.integral = max(-integral_max, min(integral_max, self.integral))

        derivative = (error - self.prev_error) / dt
        self.prev_error = error

        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        return max(self.output_min, min(self.output_max, output))
