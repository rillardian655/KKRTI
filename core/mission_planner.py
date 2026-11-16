"""Waypoint Mission Planner and Autonomous Flight Path Generator."""

from dataclasses import dataclass
import json
import math
from typing import List, Optional, Dict, Any
from core.telemetry import Position, calculate_haversine_distance


@dataclass
class Waypoint:
    lat: float
    lon: float
    alt_rel: float
    speed: float = 6.0          # m/s
    hold_sec: float = 0.0       # Hold time at waypoint in seconds
    action: str = "NAV"         # "NAV", "LAND", "RTL", "DROP_PAYLOAD", "TRIGGER_CAM"
    param1: float = 0.0         # Auxiliary parameter (e.g. servo angle or trigger count)

    def to_position(self) -> Position:
        return Position(lat=self.lat, lon=self.lon, alt_rel=self.alt_rel)


class MissionPlanner:
    """Manages waypoints, mission progression, and path generation."""

    def __init__(self):
        self.waypoints: List[Waypoint] = []
        self.current_index: int = 0
        self.is_running: bool = False

    def clear(self):
        self.waypoints.clear()
        self.current_index = 0
        self.is_running = False

    def add_waypoint(self, wp: Waypoint):
        self.waypoints.append(wp)

    def load_from_json(self, file_path: str):
        """Loads waypoint list from a structured JSON file."""
        self.clear()
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data.get("waypoints", []):
            wp = Waypoint(
                lat=item["lat"],
                lon=item["lon"],
                alt_rel=item.get("alt", 15.0),
                speed=item.get("speed", 6.0),
                hold_sec=item.get("hold_sec", 0.0),
                action=item.get("action", "NAV"),
                param1=item.get("param1", 0.0)
            )
            self.waypoints.append(wp)

    def save_to_json(self, file_path: str, mission_name: str = "Autonomous_Mission"):
        """Saves current waypoints to a JSON file."""
        out = {
            "mission_name": mission_name,
            "count": len(self.waypoints),
            "waypoints": [
                {
                    "lat": wp.lat,
                    "lon": wp.lon,
                    "alt": wp.alt_rel,
                    "speed": wp.speed,
                    "hold_sec": wp.hold_sec,
                    "action": wp.action,
                    "param1": wp.param1
                }
                for wp in self.waypoints
            ]
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)

    def generate_lawnmower_grid(self,
                                center_lat: float,
                                center_lon: float,
                                width_m: float,
                                height_m: float,
                                line_spacing_m: float,
                                altitude_m: float,
                                speed_m_s: float = 6.0) -> List[Waypoint]:
        """Generates a survey/mapping lawnmower search grid centered at a coordinate."""
        self.clear()

        # Rough conversion: 1 deg lat ~ 111,320m; 1 deg lon ~ 111,320 * cos(lat)
        m_per_deg_lat = 111320.0
        m_per_deg_lon = 111320.0 * math.cos(math.radians(center_lat))

        half_w = width_m / 2.0
        half_h = height_m / 2.0

        min_lat = center_lat - (half_h / m_per_deg_lat)
        max_lat = center_lat + (half_h / m_per_deg_lat)
        min_lon = center_lon - (half_w / m_per_deg_lon)
        max_lon = center_lon + (half_w / m_per_deg_lon)

        num_lines = max(2, int(height_m / line_spacing_m))
        lat_step = (max_lat - min_lat) / (num_lines - 1)

        flip = False
        for i in range(num_lines):
            curr_lat = min_lat + i * lat_step
            if not flip:
                # Left to Right
                self.add_waypoint(Waypoint(curr_lat, min_lon, altitude_m, speed=speed_m_s, action="TRIGGER_CAM"))
                self.add_waypoint(Waypoint(curr_lat, max_lon, altitude_m, speed=speed_m_s, action="TRIGGER_CAM"))
            else:
                # Right to Left
                self.add_waypoint(Waypoint(curr_lat, max_lon, altitude_m, speed=speed_m_s, action="TRIGGER_CAM"))
                self.add_waypoint(Waypoint(curr_lat, min_lon, altitude_m, speed=speed_m_s, action="TRIGGER_CAM"))
            flip = not flip

        return self.waypoints

    def get_current_waypoint(self) -> Optional[Waypoint]:
        if 0 <= self.current_index < len(self.waypoints):
            return self.waypoints[self.current_index]
        return None

    def advance(self) -> bool:
        """Advances to the next waypoint. Returns True if there are more waypoints, False if completed."""
        self.current_index += 1
        if self.current_index >= len(self.waypoints):
            self.is_running = False
            return False
        return True

    def is_finished(self) -> bool:
        return self.current_index >= len(self.waypoints)

