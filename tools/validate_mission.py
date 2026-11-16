"""Validates mission waypoint files against safety and physical flight envelopes."""

import json
import sys
from typing import Dict, Any, List

def validate_mission_data(data: Dict[str, Any]) -> List[str]:
    issues = []
    waypoints = data.get("waypoints", [])
    if not waypoints:
        issues.append("Mission contains zero waypoints.")
    for idx, wp in enumerate(waypoints):
        alt = wp.get("alt", 0.0)
        if alt <= 0.0:
            issues.append(f"WP #{idx + 1}: Altitude must be positive (> 0m), got {alt}m")
        if alt > 120.0:
            issues.append(f"WP #{idx + 1}: Altitude exceeds legal ceiling limit (120m), got {alt}m")
        speed = wp.get("speed", 0.0)
        if speed > 25.0:
            issues.append(f"WP #{idx + 1}: Commanded speed ({speed}m/s) exceeds maximum safe airframe speed")
    return issues

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            errors = validate_mission_data(json.load(f))
            if errors:
                print("Validation issues found:")
                for e in errors:
                    print(f" - {e}")
                sys.exit(1)
            else:
                print("Mission passed all safety validation checks.")
