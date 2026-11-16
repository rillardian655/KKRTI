"""Exports waypoint CSV lists to standard QGroundControl .plan JSON format."""

import csv
import json
import sys

def convert_to_qgc_plan(csv_path: str, output_plan_path: str):
    items = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        seq = 1
        for row in reader:
            items.append({
                "autoContinue": True,
                "command": 16,  # MAV_CMD_NAV_WAYPOINT
                "doJumpId": seq,
                "frame": 3,     # MAV_FRAME_GLOBAL_RELATIVE_ALT
                "params": [0, 0, 0, None, float(row["lat"]), float(row["lon"]), float(row["alt_rel"])],
                "type": "SimpleItem"
            })
            seq += 1

    plan = {
        "fileType": "Plan",
        "version": 1,
        "mission": {
            "cruiseSpeed": 8.0,
            "hoverSpeed": 3.0,
            "items": items,
            "plannedHomePosition": [0, 0, 0]
        }
    }
    with open(output_plan_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
    print(f"Exported QGC plan to {output_plan_path}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        convert_to_qgc_plan(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python csv_to_qgc.py <input.csv> <output.plan>")
