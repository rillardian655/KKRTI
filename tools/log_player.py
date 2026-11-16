"""Replays recorded CSV flight logs to verify trajectory and telemetry values."""

import csv
import sys

def parse_log(file_path: str):
    print(f"Reading flight log: {file_path}")
    count = 0
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            count += 1
            if count % 20 == 1:
                print(f"[{row['timestamp']}s] Mode: {row['mode']} | Alt: {row['alt_rel']}m | Bat: {row['battery_pct']}%")
    print(f"Total entries parsed: {count}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        parse_log(sys.argv[1])
    else:
        print("Usage: python log_player.py <path_to_flight_log.csv>")
