"""Generates realistic Gaussian sensor noise for GPS and IMU simulations."""

import random

class SensorNoise:
    def __init__(self, gps_noise_std_m: float = 0.4, imu_noise_std_deg: float = 0.15):
        self.gps_std = gps_noise_std_m
        self.imu_std = imu_noise_std_deg

    def apply_gps_noise(self, lat: float, lon: float) -> tuple[float, float]:
        dlat = random.gauss(0, self.gps_std) / 111320.0
        dlon = random.gauss(0, self.gps_std) / 111320.0
        return (lat + dlat, lon + dlon)

    def apply_attitude_noise(self, deg: float) -> float:
        return deg + random.gauss(0, self.imu_std)
