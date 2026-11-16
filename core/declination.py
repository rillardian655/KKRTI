"""Magnetic declination offset lookup and true heading correction for Indonesia."""

# Approximate regional declination table for major Indonesian flight areas
REGIONAL_DECLINATION_DEG = {
    "yogyakarta": 0.75,
    "bandung": 0.50,
    "jakarta": 0.65,
    "madiun": 0.85,
    "malang": 0.95,
    "pekanbaru": -0.20
}

def magnetic_to_true_heading(magnetic_heading_deg: float, region_key: str = "yogyakarta") -> float:
    declination = REGIONAL_DECLINATION_DEG.get(region_key.lower(), 0.75)
    return (magnetic_heading_deg + declination + 360.0) % 360.0
