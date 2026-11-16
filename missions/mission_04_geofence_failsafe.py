"""Mission 04: Geofence Enforcement & Autonomous Emergency Failsafe Verification."""

import time
import logging
from core.drone_controller import DroneController
from core.geofence_manager import GeofenceManager
from core.failsafe_manager import FailsafeManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Mission04")


def run_mission(endpoint: str = "udp:127.0.0.1:14550"):
    logger.info("=== Starting Mission 04: Geofence Breach & Autonomous Failsafe Test ===")

    # Setup strict Geofence (max 80 meters from home)
    geofence = GeofenceManager()
    geofence.enabled = True
    geofence.max_distance_from_home = 70.0  # Max 70 meters
    geofence.max_altitude_rel = 25.0

    failsafe = FailsafeManager(battery_low_pct=20.0, telemetry_timeout_sec=4.0)

    drone = DroneController(endpoint=endpoint, geofence=geofence, failsafe=failsafe)

    if not drone.connect():
        logger.error("Failed to connect to drone.")
        return False

    try:
        while drone.telemetry.position.lat == 0.0:
            time.sleep(0.1)

        home = drone.telemetry.position
        logger.info(f"Home Position: Lat={home.lat:.6f}, Lon={home.lon:.6f}")
        logger.info(f"Geofence Active: Max Radius = {geofence.max_distance_from_home}m")

        # 1. Takeoff
        if not drone.takeoff(altitude=12.0):
            logger.error("Takeoff failed!")
            return False

        # 2. Command an intentional breach waypoint (150 meters away, exceeding 70m limit)
        breach_lat = home.lat + 0.0014  # ~155 meters North
        breach_lon = home.lon
        logger.warning(f"Commanding waypoint OUTSIDE geofence: Lat={breach_lat:.6f}, Lon={breach_lon:.6f} (~155m)")
        drone.goto_location(breach_lat, breach_lon, 12.0, speed=8.0)

        # 3. Monitor drone until failsafe engages
        logger.info("Monitoring perimeter status...")
        breach_detected = False
        start_time = time.time()

        while time.time() - start_time < 30.0:
            snap = drone.telemetry
            drone._check_safety()

            dist = snap.distance_to_home() or 0.0
            logger.info(f"Distance from Home: {dist:.1f}m | Flight Mode: {snap.state.mode}")

            if failsafe.failsafe_triggered:
                logger.critical(f"SUCCESS: Failsafe triggered! Reason: {failsafe.active_reason}")
                logger.info(f"Drone Autopilot Mode Switched to: {snap.state.mode}")
                breach_detected = True
                break

            time.sleep(0.5)

        if not breach_detected:
            logger.error("Test failed: Geofence breach was not detected in time!")
            drone.return_to_launch()
            return False

        # Wait for drone to return and land
        logger.info("Waiting for drone to complete Return-To-Launch...")
        while True:
            snap = drone.telemetry
            if snap.position.alt_rel <= 0.2 and not snap.state.armed:
                logger.info("Drone safely recovered at home base!")
                break
            time.sleep(1.0)

        logger.info("=== Mission 04 Completed: Failsafe Interception Verified 100%! ===")
        return True

    finally:
        drone.disconnect()


if __name__ == "__main__":
    run_mission()
