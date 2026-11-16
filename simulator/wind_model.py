"""Simulated wind vector and gust dynamics for UAV environment testing."""

import math
import random
from dataclasses import dataclass

@dataclass
class WindVector:
    speed_m_s: float = 0.0
    direction_deg: float = 0.0
    gust_intensity: float = 0.0

    def get_components(self) -> tuple[float, float]:
        """Returns (north_component, east_component) in m/s."""
        rad = math.radians(self.direction_deg)
        total_speed = self.speed_m_s + random.uniform(-self.gust_intensity, self.gust_intensity)
        vn = total_speed * math.cos(rad)
        ve = total_speed * math.sin(rad)
        return (vn, ve)
