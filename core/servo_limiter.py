"""Safety limiter for PWM servo actuation signals."""

class ServoLimiter:
    def __init__(self, pwm_min: int = 1000, pwm_max: int = 2000, deadband: int = 20):
        self.pwm_min = pwm_min
        self.pwm_max = pwm_max
        self.deadband = deadband

    def clamp(self, pwm_cmd: int) -> int:
        return max(self.pwm_min, min(self.pwm_max, pwm_cmd))

    def in_deadband(self, pwm_cmd: int, center: int = 1500) -> bool:
        return abs(pwm_cmd - center) <= self.deadband
