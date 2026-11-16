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
from core.orientation import euler_to_quaternion, quaternion_to_euler
from core.speed_governor import SpeedGovernor
from core.emergency_stop import trigger_emergency_kill
from core.pid_controller import PIDController
from core.filters import LowPassFilter
from core.barometer import pressure_to_altitude
from core.gps_filter import GPSFilter
from core.dubins import generate_arc
from core.complementary_filter import ComplementaryFilter
from core.takeoff_abort import TakeoffAbortDetector
from core.airspeed import differential_pressure_to_airspeed
from core.path_following import compute_course_correction
from core.servo_limiter import ServoLimiter
from core.thermal_model import BatteryThermalModel
from core.kalman_filter import KalmanFilter1D
from core.declination import magnetic_to_true_heading
from core.energy_metrics import calculate_flight_energy
from core.geometry import point_to_line_distance
from core.stall_detector import StallDetector

__all__ = [
    "Position", "Attitude", "Velocity", "BatteryState", "DroneState", "DroneTelemetry",
    "calculate_haversine_distance", "calculate_distance_3d", "calculate_bearing",
    "MAVLinkBridge", "DroneController", "GeofenceManager", "MissionPlanner",
    "Waypoint", "FailsafeManager", "euler_to_quaternion", "quaternion_to_euler",
    "SpeedGovernor", "trigger_emergency_kill", "PIDController", "LowPassFilter",
    "pressure_to_altitude", "GPSFilter", "generate_arc", "ComplementaryFilter",
    "TakeoffAbortDetector", "differential_pressure_to_airspeed", "compute_course_correction",
    "ServoLimiter", "BatteryThermalModel", "KalmanFilter1D", "magnetic_to_true_heading",
    "calculate_flight_energy", "point_to_line_distance", "StallDetector"
]
