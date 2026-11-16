"""Parses flight telemetry CSV to generate max altitude, speed, and duration statistics."""

import csv
import sys
from typing import Dict, Any

def generate_summary(csv_file_path: str) -> Dict[str, Any]:
    max_alt = 0.0
    max_speed = 0.0
    start_time = None
    end_time = None
    count = 0

    with open(csv_file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            count += 1
            t = float(row.get("timestamp", 0.0))
            if start_time is None:
                start_time = t
            end_time = t
            alt = float(row.get("alt_rel", 0.0))
            spd = float(row.get("groundspeed", 0.0))
            max_alt = max(max_alt, alt)
            max_speed = max(max_speed, spd)

    duration = (end_time - start_time) if (start_time and end_time) else 0.0
    return {
        "records": count,
        "duration_sec": duration,
        "max_altitude_m": max_alt,
        "max_speed_m_s": max_speed
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        s = generate_summary(sys.argv[1])
        print(f"Flight Summary: Duration={s['duration_sec']:.1f}s, Max Alt={s['max_altitude_m']:.1f}m, Max Speed={s['max_speed_m_s']:.1f}m/s")
    else:
        print("Usage: python flight_summary.py <path_to_csv>")
