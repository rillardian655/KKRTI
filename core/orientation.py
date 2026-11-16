"""Quaternion and Euler angle transformation utilities for UAV orientation."""

import math
from typing import Tuple

def euler_to_quaternion(roll_deg: float, pitch_deg: float, yaw_deg: float) -> Tuple[float, float, float, float]:
    """Converts roll, pitch, and yaw (in degrees) to normalized quaternion (w, x, y, z)."""
    phi = math.radians(roll_deg) / 2.0
    theta = math.radians(pitch_deg) / 2.0
    psi = math.radians(yaw_deg) / 2.0

    w = math.cos(phi) * math.cos(theta) * math.cos(psi) + math.sin(phi) * math.sin(theta) * math.sin(psi)
    x = math.sin(phi) * math.cos(theta) * math.cos(psi) - math.cos(phi) * math.sin(theta) * math.sin(psi)
    y = math.cos(phi) * math.sin(theta) * math.cos(psi) + math.sin(phi) * math.cos(theta) * math.sin(psi)
    z = math.cos(phi) * math.cos(theta) * math.sin(psi) - math.sin(phi) * math.sin(theta) * math.cos(psi)

    norm = math.sqrt(w*w + x*x + y*y + z*z)
    if norm > 0:
        w /= norm
        x /= norm
        y /= norm
        z /= norm
    return (w, x, y, z)

def quaternion_to_euler(w: float, x: float, y: float, z: float) -> Tuple[float, float, float]:
    """Converts quaternion (w, x, y, z) to roll, pitch, yaw (in degrees)."""
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    sinp = 2.0 * (w * y - z * x)
    if abs(sinp) >= 1.0:
        pitch = math.copysign(math.pi / 2.0, sinp)
    else:
        pitch = math.asin(sinp)

    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return (math.degrees(roll), math.degrees(pitch), (math.degrees(yaw) + 360.0) % 360.0)
