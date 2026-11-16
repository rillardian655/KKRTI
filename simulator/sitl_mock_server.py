"""High-fidelity Standalone MAVLink SITL Physics Simulator for Drone Testing."""

import time
import math
import socket
import select
import threading
import logging
from typing import Optional, Tuple
from pymavlink import mavutil
from pymavlink.dialects.v20 import common as mavlink2

logger = logging.getLogger("MockSITL")


class MockSITLServer:
    """Emulates an ArduPilot/PX4 quadcopter with physics, kinematics, and full MAVLink protocol."""

    def __init__(self,
                 target_host: str = "127.0.0.1",
                 target_port: int = 14550,
                 home_lat: float = -7.925500,
                 home_lon: float = 110.548500,
                 home_alt: float = 190.0):
        self.target_host = target_host
        self.target_port = target_port
        self.home_lat = home_lat
        self.home_lon = home_lon
        self.home_alt = home_alt

        # Vehicle Physical States
        self.lat = home_lat
        self.lon = home_lon
        self.alt_rel = 0.0          # Relative altitude (m)
        self.alt_msl = home_alt     # MSL altitude (m)
        
        self.roll = 0.0             # Radians
        self.pitch = 0.0            # Radians
        self.yaw = 0.0              # Radians
        
        self.vx = 0.0               # North (m/s)
        self.vy = 0.0               # East (m/s)
        self.vz = 0.0               # Down (m/s)
        
        self.target_speed = 6.0     # m/s
        self.climb_speed = 2.5      # m/s
        self.descent_speed = 1.5    # m/s

        # Autonomous Control Target
        self.target_lat = home_lat
        self.target_lon = home_lon
        self.target_alt = 0.0

        # Status & Modes
        self.armed = False
        self.mode = "GUIDED"
        self.battery_voltage = 16.6 # 4S LiPo (V)
        self.battery_remaining = 98 # %
        self.current_draw = 1.5     # Amps

        # Networking
        self.sock: Optional[socket.socket] = None
        self.client_addr: Tuple[str, int] = (target_host, target_port)
        self.mav: Optional[mavlink2.MAVLink] = None
        
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Initializes UDP socket and starts the physics + telemetry loop."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind to port 0 (dynamic port) so port 14550 is left open for the GCS/DroneController to listen!
        self.sock.bind(("0.0.0.0", 0))
        self.sock.setblocking(False)

        # MAVLink protocol encoder (System ID 1, Component ID 1)
        class UDPSender:
            def __init__(self, parent):
                self.parent = parent
            def write(self, buf):
                if self.parent.sock:
                    try:
                        self.parent.sock.sendto(buf, self.parent.client_addr)
                    except Exception:
                        pass

        self.mav = mavlink2.MAVLink(UDPSender(self), srcSystem=1, srcComponent=1)

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info(f"Mock SITL Server online, streaming to udp:{self.target_host}:{self.target_port} (Home: {self.home_lat:.6f}, {self.home_lon:.6f})")

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        if self.sock:
            self.sock.close()
            self.sock = None
        logger.info("Mock SITL Server stopped.")

    def _run_loop(self):
        """Main simulation tick (50 Hz)."""
        dt = 0.02  # 20ms per cycle
        last_heartbeat = 0.0
        last_fast_telemetry = 0.0
        last_slow_telemetry = 0.0

        while self._running:
            now = time.time()

            # 1. Process Incoming Packets
            self._handle_network_rx()

            # 2. Physics & Kinematics Step
            self._update_physics(dt)

            # 3. MAVLink Telemetry Broadcasts
            # 1 Hz Heartbeat
            if now - last_heartbeat >= 1.0:
                self._send_heartbeat()
                last_heartbeat = now

            # 10 Hz Fast Telemetry (GPS, Attitude)
            if now - last_fast_telemetry >= 0.1:
                self._send_fast_telemetry()
                last_fast_telemetry = now

            # 2 Hz Slow Telemetry (Battery, System Status)
            if now - last_slow_telemetry >= 0.5:
                self._send_slow_telemetry()
                last_slow_telemetry = now

            time.sleep(dt)

    def _handle_network_rx(self):
        """Reads incoming MAVLink packets and parses commands."""
        if not self.sock:
            return

        ready, _, _ = select.select([self.sock], [], [], 0.0)
        if not ready:
            return

        try:
            data, addr = self.sock.recvfrom(2048)
            self.client_addr = addr

            # Parse incoming bytes with mavlink parser
            msgs = self.mav.parse_buffer(data)
            if msgs:
                for msg in msgs:
                    self._process_mavlink_msg(msg)
        except Exception:
            pass

    def _process_mavlink_msg(self, msg):
        msg_type = msg.get_type()

        if msg_type == "COMMAND_LONG":
            cmd = msg.command
            # ARM / DISARM
            if cmd == mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM:
                arm_cmd = (msg.param1 == 1.0)
                self.armed = arm_cmd
                logger.info(f"[SITL] Motors {'ARMED' if self.armed else 'DISARMED'}")
                self._send_ack(cmd, mavutil.mavlink.MAV_RESULT_ACCEPTED)

            # SET MODE VIA COMMAND_LONG
            elif cmd == mavutil.mavlink.MAV_CMD_DO_SET_MODE:
                custom_mode = int(msg.param2)
                self._apply_custom_mode(custom_mode)
                self._send_ack(cmd, mavutil.mavlink.MAV_RESULT_ACCEPTED)

            # TAKEOFF
            elif cmd == mavutil.mavlink.MAV_CMD_NAV_TAKEOFF:
                target_alt = msg.param7
                if self.armed:
                    self.target_alt = target_alt
                    self.target_lat = self.lat
                    self.target_lon = self.lon
                    logger.info(f"[SITL] Takeoff initiated to {target_alt:.1f}m")
                    self._send_ack(cmd, mavutil.mavlink.MAV_RESULT_ACCEPTED)
                else:
                    self._send_ack(cmd, mavutil.mavlink.MAV_RESULT_FAILED)

            # SPEED CHANGE
            elif cmd == mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED:
                speed = msg.param2
                if speed > 0:
                    self.target_speed = speed
                    logger.info(f"[SITL] Speed updated to {speed:.1f} m/s")
                self._send_ack(cmd, mavutil.mavlink.MAV_RESULT_ACCEPTED)

            # SERVO ACTUATION (Payload Drop)
            elif cmd == mavutil.mavlink.MAV_CMD_DO_SET_SERVO:
                servo_ch = int(msg.param1)
                pwm = int(msg.param2)
                logger.info(f"[SITL Payload Drop] Servo {servo_ch} fired -> PWM {pwm}!")
                self._send_ack(cmd, mavutil.mavlink.MAV_RESULT_ACCEPTED)

        elif msg_type == "SET_POSITION_TARGET_GLOBAL_INT":
            self.target_lat = msg.lat_int / 1e7
            self.target_lon = msg.lon_int / 1e7
            self.target_alt = msg.alt
            logger.info(f"[SITL] New Target WP -> Lat={self.target_lat:.6f}, Lon={self.target_lon:.6f}, Alt={self.target_alt:.1f}m")

        elif msg_type == "SET_MODE":
            self._apply_custom_mode(msg.custom_mode)

    def _apply_custom_mode(self, custom_mode: int):
        # 4=GUIDED, 6=RTL, 9=LAND in ArduCopter
        if custom_mode == 4:
            self.mode = "GUIDED"
            logger.info("[SITL] Flight Mode: GUIDED")
        elif custom_mode == 6:
            self.mode = "RTL"
            self.target_lat = self.home_lat
            self.target_lon = self.home_lon
            self.target_alt = 15.0  # Return at 15m
            logger.info("[SITL] Flight Mode: RTL (Returning Home)")
        elif custom_mode == 9:
            self.mode = "LAND"
            self.target_alt = 0.0
            logger.info("[SITL] Flight Mode: LAND (Descending)")

    def _update_physics(self, dt: float):
        """Simulates 3D kinematics, yaw alignment, bank angle, and battery discharge."""
        if not self.armed and self.alt_rel <= 0.05:
            # Idle on ground
            self.vx = self.vy = self.vz = 0.0
            self.roll = self.pitch = 0.0
            return

        # 1. Horizontal Kinematics (Meters per degree approx)
        m_per_deg_lat = 111320.0
        m_per_deg_lon = 111320.0 * math.cos(math.radians(self.lat))

        d_lat_m = (self.target_lat - self.lat) * m_per_deg_lat
        d_lon_m = (self.target_lon - self.lon) * m_per_deg_lon
        dist_horizontal = math.hypot(d_lat_m, d_lon_m)

        if dist_horizontal > 0.2 and self.alt_rel > 0.5:
            target_yaw = math.atan2(d_lon_m, d_lat_m)
            # Smooth yaw rotation
            yaw_diff = (target_yaw - self.yaw + math.pi) % (2 * math.pi) - math.pi
            self.yaw += max(min(yaw_diff, 1.5 * dt), -1.5 * dt)

            # Move towards target
            step = min(dist_horizontal, self.target_speed * dt)
            move_lat_m = step * math.cos(target_yaw)
            move_lon_m = step * math.sin(target_yaw)

            self.lat += move_lat_m / m_per_deg_lat
            self.lon += move_lon_m / m_per_deg_lon

            self.vx = move_lat_m / dt
            self.vy = move_lon_m / dt
            self.pitch = math.radians(-5.0)  # Slight nose down during forward flight
            self.roll = math.radians(math.sin(self.yaw) * 4.0)
        else:
            self.vx = self.vy = 0.0
            self.pitch = 0.0
            self.roll = 0.0

        # 2. Altitude Kinematics
        if self.mode == "RTL" and dist_horizontal <= 1.5:
            # Over home base in RTL: initiate descent
            self.target_alt = 0.0

        alt_err = self.target_alt - self.alt_rel
        if abs(alt_err) > 0.05:
            climb_dir = 1.0 if alt_err > 0 else -1.0
            rate = self.climb_speed if climb_dir > 0 else self.descent_speed
            delta_h = climb_dir * min(abs(alt_err), rate * dt)
            self.alt_rel += delta_h
            self.vz = -delta_h / dt  # Downwards in NED
        else:
            self.vz = 0.0

        if (self.mode in ("LAND", "RTL")) and self.alt_rel <= 0.1 and self.target_alt == 0.0:
            self.alt_rel = 0.0
            self.armed = False
            self.mode = "LANDED"
            logger.info("[SITL] Drone Touchdown & Disarmed.")

        self.alt_msl = self.home_alt + self.alt_rel

        # 3. Battery Drain Simulation
        drain_rate = 0.02 if not self.armed else 0.08  # % per second
        self.battery_remaining = max(0.0, self.battery_remaining - (drain_rate * dt))
        self.battery_voltage = 14.0 + (self.battery_remaining / 100.0) * 2.8

    def _send_ack(self, command: int, result: int):
        if not self.mav:
            return
        self.mav.command_ack_send(command, result)

    def _send_heartbeat(self):
        if not self.mav or not self.client_addr:
            return

        base_mode = mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED
        if self.armed:
            base_mode |= mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED

        # ArduCopter mode custom mapping: 4=GUIDED, 6=RTL, 9=LAND
        mode_map = {"GUIDED": 4, "RTL": 6, "LAND": 9, "LANDED": 9}
        custom_mode = mode_map.get(self.mode, 4)

        self.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_QUADROTOR,
            mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
            base_mode,
            custom_mode,
            mavutil.mavlink.MAV_STATE_ACTIVE,
            3
        )

    def _send_fast_telemetry(self):
        if not self.mav or not self.client_addr:
            return

        boot_ms = int(time.time() * 1000) & 0xFFFFFFFF

        yaw_cdeg = int((((math.degrees(self.yaw) % 360.0) + 360.0) % 360.0) * 100)

        # ATTITUDE
        self.mav.attitude_send(
            boot_ms,
            self.roll,
            self.pitch,
            self.yaw,
            0.0, 0.0, 0.0
        )

        # GLOBAL_POSITION_INT
        self.mav.global_position_int_send(
            boot_ms,
            int(self.lat * 1e7),
            int(self.lon * 1e7),
            int(self.alt_msl * 1000),
            int(self.alt_rel * 1000),
            int(self.vx * 100),
            int(self.vy * 100),
            int(self.vz * 100),
            yaw_cdeg
        )

        # GPS_RAW_INT
        self.mav.gps_raw_int_send(
            int(time.time() * 1e6),
            3,  # 3D Fix
            int(self.lat * 1e7),
            int(self.lon * 1e7),
            int(self.alt_msl * 1000),
            100, 100,  # eph, epv
            int(math.hypot(self.vx, self.vy) * 100),
            yaw_cdeg,
            14  # Satellites
        )

    def _send_slow_telemetry(self):
        if not self.mav or not self.client_addr:
            return

        # SYS_STATUS
        self.mav.sys_status_send(
            0, 0, 0,
            500,  # load
            int(self.battery_voltage * 1000),
            int(self.current_draw * 100),
            int(self.battery_remaining),
            0, 0, 0, 0, 0, 0
        )

        # HOME_POSITION
        self.mav.home_position_send(
            int(self.home_lat * 1e7),
            int(self.home_lon * 1e7),
            int(self.home_alt * 1000),
            0.0, 0.0, 0.0,
            [1.0, 0.0, 0.0, 0.0],
            0.0, 0.0, 0.0,
            int(time.time() * 1e6)
        )
