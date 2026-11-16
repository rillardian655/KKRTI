"""Quality assurance filter for GPS fixes based on HDOP and satellite count."""

class GPSFilter:
    def __init__(self, max_hdop: float = 2.0, min_satellites: int = 8):
        self.max_hdop = max_hdop
        self.min_satellites = min_satellites

    def is_fix_acceptable(self, fix_type: int, satellites: int, eph_cm: int) -> bool:
        """Validates 3D fix status, HDOP (eph in centimeters), and satellite visibility."""
        if fix_type < 3:
            return False
        if satellites < self.min_satellites:
            return False
        hdop = eph_cm / 100.0
        return hdop <= self.max_hdop
