"""Telemetry and Spatial Utilities for UAV Missions."""

from dataclasses import dataclass, field
import math
import time
from typing import Optional, Tuple


@dataclass
class Position:
    lat: float = 0.0          # Latitude in degrees
    lon: float = 0.0          # Longitude in degrees
    alt_rel: float = 0.0      # Altitude above home in meters
    alt_msl: float = 0.0      # Altitude above Mean Sea Level in meters


@dataclass
class Attitude:
    roll: float = 0.0         # Degrees (-180 to 180)
    pitch: float = 0.0        # Degrees (-90 to 90)
    yaw: float = 0.0          # Heading in degrees (0 to 360)


@dataclass
class Velocity:
    vx: float = 0.0           # North velocity in m/s
    vy: float = 0.0           # East velocity in m/s
    vz: float = 0.0           # Down velocity in m/s
    groundspeed: float = 0.0  # Total horizontal speed in m/s
    climb_rate: float = 0.0   # Vertical speed in m/s (+ up, - down)


@dataclass
class BatteryState:
    voltage: float = 16.8     # Volts (e.g. 4S LiPo)
    current: float = 0.0      # Amperes
    percentage: float = 100.0 # 0 - 100%


@dataclass
class DroneState:
    armed: bool = False
    mode: str = "INITIALIZING"
    mavlink_connected: bool = False
    last_heartbeat: float = 0.0
    sys_status: int = 0
    gps_fix_type: int = 3     # 3 = 3D Fix
    satellites_visible: int = 12


@dataclass
class DroneTelemetry:
    position: Position = field(default_factory=Position)
    attitude: Attitude = field(default_factory=Attitude)
    velocity: Velocity = field(default_factory=Velocity)
    battery: BatteryState = field(default_factory=BatteryState)
    state: DroneState = field(default_factory=DroneState)
    home_position: Optional[Position] = None
    target_waypoint: Optional[Position] = None
    current_wp_index: int = 0
    total_waypoints: int = 0
    timestamp: float = field(default_factory=time.time)

    def is_link_alive(self, timeout_sec: float = 4.0) -> bool:
        """Check if MAVLink telemetry heartbeat is active."""
        if not self.state.mavlink_connected:
            return False
        return (time.time() - self.state.last_heartbeat) < timeout_sec

    def distance_to_target(self) -> Optional[float]:
        """Calculates distance in meters to the active target waypoint."""
        if not self.target_waypoint:
            return None
        return calculate_distance_3d(
            self.position.lat, self.position.lon, self.position.alt_rel,
            self.target_waypoint.lat, self.target_waypoint.lon, self.target_waypoint.alt_rel
        )

    def distance_to_home(self) -> Optional[float]:
        """Calculates horizontal distance to home in meters."""
        if not self.home_position:
            return None
        return calculate_haversine_distance(
            self.position.lat, self.position.lon,
            self.home_position.lat, self.home_position.lon
        )


# ============================================================================
# Geospatial Helper Functions
# ============================================================================

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates horizontal great-circle distance between two GPS coordinates in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def calculate_distance_3d(lat1: float, lon1: float, alt1: float,
                          lat2: float, lon2: float, alt2: float) -> float:
    """Calculates 3D Euclidean distance in meters."""
    horizontal = calculate_haversine_distance(lat1, lon1, lat2, lon2)
    vertical = alt2 - alt1
    return math.sqrt(horizontal ** 2 + vertical ** 2)


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates initial bearing (azimuth) from point 1 to point 2 in degrees (0..360)."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    initial_bearing = math.degrees(math.atan2(y, x))
    return (initial_bearing + 360.0) % 360.0
