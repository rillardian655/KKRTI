"""Core autonomous flight controller package."""

from core.telemetry import (
    Position, Attitude, Velocity, BatteryState, DroneState, DroneTelemetry,
    calculate_haversine_distance, calculate_distance_3d, calculate_bearing
)
from core.mavlink_bridge import MAVLinkBridge
from core.drone_controller import DroneController
from core.geofence_manager import GeofenceManager
from core.mission_planner import MissionPlanner, Waypoint
from core.failsafe_manager import FailsafeManager

__all__ = [
    "Position", "Attitude", "Velocity", "BatteryState", "DroneState", "DroneTelemetry",
    "calculate_haversine_distance", "calculate_distance_3d", "calculate_bearing",
    "MAVLinkBridge", "DroneController", "GeofenceManager", "MissionPlanner",
    "Waypoint", "FailsafeManager"
]
