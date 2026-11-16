"""High-level Drone Controller for Autonomous Missions & KRTI Flight Execution."""

import time
import math
import logging
from typing import Optional, Tuple
from pymavlink import mavutil

from core.mavlink_bridge import MAVLinkBridge
from core.telemetry import (
    DroneTelemetry, Position, calculate_haversine_distance, calculate_distance_3d
)
from core.geofence_manager import GeofenceManager
from core.failsafe_manager import FailsafeManager

logger = logging.getLogger("DroneController")


class DroneController:
    """High-level API for autonomous drone operations via MAVLink."""

    def __init__(self,
                 endpoint: str = "udp:127.0.0.1:14550",
                 geofence: Optional[GeofenceManager] = None,
                 failsafe: Optional[FailsafeManager] = None):
        self.endpoint = endpoint
        self.bridge = MAVLinkBridge(endpoint=endpoint)
        self.geofence = geofence
        self.failsafe = failsafe or FailsafeManager()
        self.active_target: Optional[Position] = None

    def connect(self, timeout: int = 15) -> bool:
        """Connects to the drone autopilot / SITL and waits for initial GPS fix."""
        connected = self.bridge.connect(timeout=timeout)
        if connected:
            # Wait up to 3 seconds for position stream
            start = time.time()
            while time.time() - start < 3.0:
                if self.telemetry.position.lat != 0.0:
                    break
                time.sleep(0.1)
        return connected

    def disconnect(self):
        """Disconnects the telemetry bridge."""
        self.bridge.disconnect()

    @property
    def telemetry(self) -> DroneTelemetry:
        """Retrieves the latest telemetry snapshot."""
        snap = self.bridge.get_snapshot()
        if self.active_target:
            snap.target_waypoint = self.active_target
        return snap

    def set_mode(self, mode: str, timeout: float = 5.0) -> bool:
        """Changes flight mode (e.g. GUIDED, AUTO, RTL, LAND, LOITER)."""
        if not self.bridge.master:
            return False

        mode_upper = mode.upper()
        logger.info(f"Setting flight mode to {mode_upper}...")

        # Obtain mode ID from pymavlink
        mode_mapping = self.bridge.master.mode_mapping()
        if mode_mapping is None or mode_upper not in mode_mapping:
            logger.warning(f"Unknown flight mode '{mode_upper}', falling back to raw mode request.")
            # Default GUIDED for ArduCopter is typically 4
            mode_id = 4 if mode_upper == "GUIDED" else 6  # 6=RTL, 9=LAND
        else:
            mode_id = mode_mapping[mode_upper]

        self.bridge.master.set_mode(mode_id)

        # Wait until mode change is reflected
        start = time.time()
        while time.time() - start < timeout:
            snap = self.telemetry
            if snap.state.mode.upper() == mode_upper:
                logger.info(f"Mode confirmed: {mode_upper}")
                return True
            time.sleep(0.2)

        logger.warning(f"Mode change to {mode_upper} timed out, current mode: {self.telemetry.state.mode}")
        return False

    def arm(self, timeout: float = 10.0) -> bool:
        """Arms drone motors."""
        if not self.bridge.master:
            return False

        logger.info("Sending ARM command...")
        self.bridge.master.mav.command_long_send(
            self.bridge.master.target_system,
            self.bridge.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,  # Confirmation
            1,  # 1 = Arm, 0 = Disarm
            0, 0, 0, 0, 0, 0
        )

        start = time.time()
        while time.time() - start < timeout:
            if self.telemetry.state.armed:
                logger.info("Motors Armed successfully!")
                return True
            time.sleep(0.3)

        logger.error("Arming failed or timed out.")
        return False

    def disarm(self, force: bool = False) -> bool:
        """Disarms drone motors."""
        if not self.bridge.master:
            return False

        logger.info("Sending DISARM command...")
        param2 = 21196.0 if force else 0.0  # Magic number to force disarm if airborne
        self.bridge.master.mav.command_long_send(
            self.bridge.master.target_system,
            self.bridge.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            0,  # Disarm
            param2,
            0, 0, 0, 0, 0
        )
        return True

    def takeoff(self, altitude: float, timeout: float = 30.0) -> bool:
        """Commands autonomous vertical takeoff to specified relative altitude (meters)."""
        if not self.bridge.master:
            return False

        logger.info(f"Initiating TAKEOFF to {altitude:.1f}m AGL...")

        # Switch to GUIDED mode first
        if not self.set_mode("GUIDED"):
            logger.warning("Could not set GUIDED mode, proceeding anyway.")

        if not self.telemetry.state.armed:
            if not self.arm():
                logger.error("Cannot takeoff: Arming rejected.")
                return False

        self.bridge.master.mav.command_long_send(
            self.bridge.master.target_system,
            self.bridge.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,
            0, 0, 0, 0, 0, 0,
            altitude
        )

        # Wait until target altitude is reached (-1m tolerance)
        start = time.time()
        while time.time() - start < timeout:
            snap = self.telemetry
            self._check_safety()

            if snap.position.alt_rel >= (altitude * 0.92):
                logger.info(f"Reached takeoff altitude: {snap.position.alt_rel:.2f}m")
                return True
            time.sleep(0.4)

        logger.warning(f"Takeoff wait reached timeout! Current alt: {self.telemetry.position.alt_rel:.1f}m")
        return False

    def goto_location(self, lat: float, lon: float, alt_rel: float, speed: Optional[float] = None):
        """Sends guided waypoint target (SET_POSITION_TARGET_GLOBAL_INT)."""
        if not self.bridge.master:
            return

        if speed is not None:
            self.set_speed(speed)

        self.active_target = Position(lat=lat, lon=lon, alt_rel=alt_rel)
        logger.info(f"Going to waypoint: Lat={lat:.6f}, Lon={lon:.6f}, Alt={alt_rel:.1f}m")

        # Type mask: ignore velocities and accelerations, focus on position
        type_mask = 0b0000111111111000

        self.bridge.master.mav.set_position_target_global_int_send(
            0,  # time_boot_ms
            self.bridge.master.target_system,
            self.bridge.master.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            type_mask,
            int(lat * 1e7),
            int(lon * 1e7),
            alt_rel,
            0, 0, 0,  # vx, vy, vz
            0, 0, 0,  # afx, afy, afz
            0, 0      # yaw, yaw_rate
        )

    def set_speed(self, speed_m_s: float):
        """Sets target ground speed in m/s."""
        if not self.bridge.master:
            return
        self.bridge.master.mav.command_long_send(
            self.bridge.master.target_system,
            self.bridge.master.target_component,
            mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,
            0,
            0,            # 0=Airspeed, 1=Groundspeed
            speed_m_s,
            -1,           # throttle -1 = no change
            0, 0, 0, 0
        )

    def trigger_payload_servo(self, servo_channel: int = 9, pwm_value: int = 2000):
        """Actuates a servo channel (useful for KRTI payload release mechanism)."""
        if not self.bridge.master:
            return
        logger.info(f"[PAYLOAD] Actuating Servo Ch {servo_channel} to PWM {pwm_value}...")
        self.bridge.master.mav.command_long_send(
            self.bridge.master.target_system,
            self.bridge.master.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            0,
            servo_channel,
            pwm_value,
            0, 0, 0, 0, 0
        )

    def return_to_launch(self) -> bool:
        """Triggers Return-to-Launch (RTL) mode."""
        logger.warning("Initiating RETURN-TO-LAUNCH (RTL)!")
        return self.set_mode("RTL")

    def land(self) -> bool:
        """Triggers autonomous LAND mode."""
        logger.info("Initiating autonomous LAND...")
        return self.set_mode("LAND")

    def wait_for_waypoint(self,
                          target_lat: float,
                          target_lon: float,
                          target_alt: float,
                          acceptance_radius: float = 2.5,
                          timeout: float = 60.0) -> bool:
        """Blocks until the drone reaches the waypoint within the acceptance radius or timeout occurs."""
        start = time.time()
        while time.time() - start < timeout:
            snap = self.telemetry
            self._check_safety()

            dist = calculate_distance_3d(
                snap.position.lat, snap.position.lon, snap.position.alt_rel,
                target_lat, target_lon, target_alt
            )

            if dist <= acceptance_radius:
                logger.info(f"Waypoint Reached! (Distance: {dist:.2f}m <= {acceptance_radius}m)")
                return True

            time.sleep(0.4)

        logger.warning(f"Waypoint wait timed out after {timeout}s.")
        return False

    def _check_safety(self):
        """Invokes the failsafe manager to detect geofence/battery/link faults."""
        if not self.failsafe:
            return

        def _trigger_rtl(reason: str):
            logger.critical(f"Executing Emergency RTL due to: {reason}")
            self.return_to_launch()

        def _trigger_land(reason: str):
            logger.critical(f"Executing Emergency LAND due to: {reason}")
            self.land()

        self.failsafe.evaluate(
            telemetry=self.telemetry,
            geofence=self.geofence,
            on_trigger_rtl=_trigger_rtl,
            on_trigger_land=_trigger_land
        )
