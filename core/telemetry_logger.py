"""Flight telemetry recorder to CSV format for post-flight analysis."""

import csv
import os
import time
from core.telemetry import DroneTelemetry

class TelemetryLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        filename = f"flight_{int(time.time())}.csv"
        self.file_path = os.path.join(log_dir, filename)
        self._file = open(self.file_path, "w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow([
            "timestamp", "mode", "armed", "lat", "lon", "alt_rel", "groundspeed",
            "roll", "pitch", "yaw", "battery_pct", "voltage"
        ])

    def log(self, t: DroneTelemetry):
        self._writer.writerow([
            f"{t.timestamp:.3f}", t.state.mode, t.state.armed,
            f"{t.position.lat:.6f}", f"{t.position.lon:.6f}", f"{t.position.alt_rel:.2f}",
            f"{t.velocity.groundspeed:.2f}", f"{t.attitude.roll:.1f}",
            f"{t.attitude.pitch:.1f}", f"{t.attitude.yaw:.1f}",
            f"{t.battery.percentage:.1f}", f"{t.battery.voltage:.2f}"
        ])
        self._file.flush()

    def close(self):
        if self._file and not self._file.closed:
            self._file.close()
