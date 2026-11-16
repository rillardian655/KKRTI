"""Complementary filter combining gyroscope integration with accelerometer tilt."""

import math

class ComplementaryFilter:
    def __init__(self, alpha: float = 0.96):
        self.alpha = alpha
        self.pitch_deg = 0.0
        self.roll_deg = 0.0

    def update(self, gyro_pitch_rate: float, gyro_roll_rate: float,
               accel_x: float, accel_y: float, accel_z: float, dt: float):
        # Accelerometer angles
        accel_pitch = math.degrees(math.atan2(-accel_x, math.sqrt(accel_y*accel_y + accel_z*accel_z)))
        accel_roll = math.degrees(math.atan2(accel_y, accel_z))

        # Filter fusion: high-pass on gyro, low-pass on accel
        self.pitch_deg = self.alpha * (self.pitch_deg + gyro_pitch_rate * dt) + (1.0 - self.alpha) * accel_pitch
        self.roll_deg = self.alpha * (self.roll_deg + gyro_roll_rate * dt) + (1.0 - self.alpha) * accel_roll
        return self.pitch_deg, self.roll_deg
