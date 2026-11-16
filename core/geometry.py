"""Geometric utilities for waypoint route line-segment and circular zone intersection."""

import math

def point_to_line_distance(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculates perpendicular shortest distance from a point to a 2D line segment."""
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(px - proj_x, py - proj_y)
