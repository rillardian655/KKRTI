"""Simplified Dubins path curve generator for fixed-wing UAV turns."""

import math
from typing import List, Tuple

def generate_arc(start_x: float, start_y: float, start_heading_rad: float,
                 turn_angle_rad: float, turn_radius_m: float, steps: int = 10) -> List[Tuple[float, float]]:
    """Generates discrete 2D coordinates along a circular arc turn."""
    points = []
    # Center of turn circle
    cx = start_x - turn_radius_m * math.sin(start_heading_rad)
    cy = start_y + turn_radius_m * math.cos(start_heading_rad)

    for i in range(steps + 1):
        fraction = i / float(steps)
        curr_angle = (start_heading_rad - math.pi / 2.0) + (fraction * turn_angle_rad)
        px = cx + turn_radius_m * math.cos(curr_angle)
        py = cy + turn_radius_m * math.sin(curr_angle)
        points.append((px, py))
    return points
