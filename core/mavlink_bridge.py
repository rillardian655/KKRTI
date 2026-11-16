"""MAVLink Bridge using pymavlink for bidirectional telemetry & control."""

import time
import math
import threading
import logging
from typing import Optional, Callable
from pymavlink import mavutil

from core.telemetry import (
    DroneTelemetry, Position, Attitude, Velocity, BatteryState, DroneState
)

logger = logging.getLogger("MAVLinkBridge")


class MAVLinkBridge:
    """Manages the raw MAVLink socket connection and telemetry parsing loop."""

    def __init__(self, endpoint: str = "udp:127.0.0.1:14550", baud: int = 57600):
        self.endpoint = endpoint
        self.baud = baud
        self.master: Optional[mavutil.mavfile] = None
        self.telemetry = DroneTelemetry()
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Callbacks
        self.on_message_callback: Optional[Callable[[any], None]] = None

    def connect(self, timeout: int = 15) -> bool:
        """Establishes connection and waits for the first heartbeat from the autopilot."""
        logger.info(f"Connecting to MAVLink endpoint: {self.endpoint} ...")
        try:
            self.master = mavutil.mavlink_connection(self.endpoint, baud=self.baud)
        except Exception as e:
            logger.error(f"Failed to create connection to {self.endpoint}: {e}")
            return False

        logger.info(f"Waiting for vehicle heartbeat (timeout={timeout}s)...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            msg = self.master.wait_heartbeat(timeout=1.0)
            if msg:
                target_sys = self.master.target_system
                target_comp = self.master.target_component
                logger.info(f"Heartbeat received from System {target_sys}, Component {target_comp}")
                with self._lock:
                    self.telemetry.state.mavlink_connected = True
                    self.telemetry.state.last_heartbeat = time.time()
                
                # Request standard data streams
                self._request_data_streams()

                # Start background listener thread
                self._running = True
                self._thread = threading.Thread(target=self._telemetry_worker, daemon=True)
                self._thread.start()
                return True

        logger.error(f"Heartbeat timeout on {self.endpoint}!")
        return False

    def disconnect(self):
        """Stops listener and closes socket."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self.master:
            self.master.close()
            self.master = None
        with self._lock:
            self.telemetry.state.mavlink_connected = False
        logger.info("MAVLink connection closed.")

    def _request_data_streams(self):
        """Requests periodic telemetry messages at desired frequencies (Hz)."""
        if not self.master:
            return
        
        # MAV_DATA_STREAM_ALL at 4Hz
        self.master.mav.request_data_stream_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL,
            4,  # Hz
            1   # Start
        )

    def _telemetry_worker(self):
        """Background thread parsing incoming MAVLink packets."""
        while self._running and self.master:
            try:
                msg = self.master.recv_match(blocking=True, timeout=0.5)
                if not msg:
                    continue

                msg_type = msg.get_type()

                with self._lock:
                    now = time.time()
                    self.telemetry.timestamp = now

                    if msg_type == "HEARTBEAT":
                        self.telemetry.state.last_heartbeat = now
                        self.telemetry.state.mavlink_connected = True
                        self.telemetry.state.armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
                        
                        # Interpret custom flight mode string for ArduPilot
                        try:
                            self.telemetry.state.mode = mavutil.mode_string_v10(msg)
                        except Exception:
                            self.telemetry.state.mode = f"MODE_{msg.custom_mode}"

                    elif msg_type == "GLOBAL_POSITION_INT":
                        self.telemetry.position.lat = msg.lat / 1e7
                        self.telemetry.position.lon = msg.lon / 1e7
                        self.telemetry.position.alt_rel = msg.relative_alt / 1000.0  # mm to m
                        self.telemetry.position.alt_msl = msg.alt / 1000.0

                        if self.telemetry.home_position is None:
                            self.telemetry.home_position = Position(
                                lat=self.telemetry.position.lat,
                                lon=self.telemetry.position.lon,
                                alt_rel=0.0,
                                alt_msl=self.telemetry.position.alt_msl
                            )

                        self.telemetry.velocity.vx = msg.vx / 100.0  # cm/s to m/s
                        self.telemetry.velocity.vy = msg.vy / 100.0
                        self.telemetry.velocity.vz = msg.vz / 100.0
                        self.telemetry.velocity.groundspeed = math.hypot(
                            self.telemetry.velocity.vx, self.telemetry.velocity.vy
                        )
                        self.telemetry.velocity.climb_rate = -self.telemetry.velocity.vz

                    elif msg_type == "ATTITUDE":
                        self.telemetry.attitude.roll = math.degrees(msg.roll)
                        self.telemetry.attitude.pitch = math.degrees(msg.pitch)
                        yaw_deg = math.degrees(msg.yaw)
                        self.telemetry.attitude.yaw = (yaw_deg + 360.0) % 360.0

                    elif msg_type == "SYS_STATUS":
                        self.telemetry.battery.voltage = msg.voltage_battery / 1000.0  # mV to V
                        self.telemetry.battery.current = msg.current_battery / 100.0   # cA to A
                        self.telemetry.battery.percentage = float(msg.battery_remaining)

                    elif msg_type == "GPS_RAW_INT":
                        self.telemetry.state.gps_fix_type = msg.fix_type
                        self.telemetry.state.satellites_visible = msg.satellites_visible

                    elif msg_type == "HOME_POSITION":
                        self.telemetry.home_position = Position(
                            lat=msg.latitude / 1e7,
                            lon=msg.longitude / 1e7,
                            alt_rel=0.0,
                            alt_msl=msg.altitude / 1000.0
                        )

                if self.on_message_callback:
                    self.on_message_callback(msg)

            except Exception as e:
                if self._running:
                    logger.debug(f"Telemetry parse error: {e}")

    def get_snapshot(self) -> DroneTelemetry:
        """Returns a thread-safe copy of current telemetry."""
        with self._lock:
            # Shallow clone of current fields
            snapshot = DroneTelemetry(
                position=Position(
                    lat=self.telemetry.position.lat,
                    lon=self.telemetry.position.lon,
                    alt_rel=self.telemetry.position.alt_rel,
                    alt_msl=self.telemetry.position.alt_msl
                ),
                attitude=Attitude(
                    roll=self.telemetry.attitude.roll,
                    pitch=self.telemetry.attitude.pitch,
                    yaw=self.telemetry.attitude.yaw
                ),
                velocity=Velocity(
                    vx=self.telemetry.velocity.vx,
                    vy=self.telemetry.velocity.vy,
                    vz=self.telemetry.velocity.vz,
                    groundspeed=self.telemetry.velocity.groundspeed,
                    climb_rate=self.telemetry.velocity.climb_rate
                ),
                battery=BatteryState(
                    voltage=self.telemetry.battery.voltage,
                    current=self.telemetry.battery.current,
                    percentage=self.telemetry.battery.percentage
                ),
                state=DroneState(
                    armed=self.telemetry.state.armed,
                    mode=self.telemetry.state.mode,
                    mavlink_connected=self.telemetry.state.mavlink_connected,
                    last_heartbeat=self.telemetry.state.last_heartbeat,
                    gps_fix_type=self.telemetry.state.gps_fix_type,
                    satellites_visible=self.telemetry.state.satellites_visible
                ),
                home_position=self.telemetry.home_position,
                target_waypoint=self.telemetry.target_waypoint,
                current_wp_index=self.telemetry.current_wp_index,
                total_waypoints=self.telemetry.total_waypoints,
                timestamp=self.telemetry.timestamp
            )
            return snapshot
