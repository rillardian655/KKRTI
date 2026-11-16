"""Vector field guidance law for cross-track error correction."""

import math

def compute_course_correction(cross_track_error_m: float, path_heading_rad: float, k_path: float = 0.05) -> float:
    """Calculates desired heading angle to converge smoothly onto the intended flight path."""
    # Limit max correction angle to 45 degrees
    chi_inf = math.pi / 4.0
    correction = -chi_inf * (2.0 / math.pi) * math.atan(k_path * cross_track_error_m)
    desired_heading = (path_heading_rad + correction) % (2.0 * math.pi)
    return desired_heading
