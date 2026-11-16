"""Mission 02: Waypoint Navigation & Autonomous Aerial Survey."""

import time
import logging
from core.drone_controller import DroneController
from core.mission_planner import MissionPlanner, Waypoint

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Mission02")


def run_mission(endpoint: str = "udp:127.0.0.1:14550"):
    logger.info("=== Starting Mission 02: Aerial Waypoint Survey ===")
    drone = DroneController(endpoint=endpoint)

    if not drone.connect():
        logger.error("Failed to connect to drone.")
        return False

    try:
        while drone.telemetry.position.lat == 0.0:
            time.sleep(0.1)

        home = drone.telemetry.position
        logger.info(f"Home Coordinate: Lat={home.lat:.6f}, Lon={home.lon:.6f}")

        # Setup Survey Grid using MissionPlanner
        planner = MissionPlanner()
        # Create a 4-point rectangular survey area
        # 100m North/East offsets
        wp_list = [
            Waypoint(lat=home.lat + 0.0008, lon=home.lon + 0.0005, alt_rel=18.0, speed=7.0, action="TRIGGER_CAM"),
            Waypoint(lat=home.lat + 0.0008, lon=home.lon - 0.0005, alt_rel=18.0, speed=7.0, action="TRIGGER_CAM"),
            Waypoint(lat=home.lat + 0.0003, lon=home.lon - 0.0005, alt_rel=20.0, speed=7.0, action="TRIGGER_CAM"),
            Waypoint(lat=home.lat + 0.0003, lon=home.lon + 0.0005, alt_rel=20.0, speed=7.0, action="TRIGGER_CAM"),
        ]
        for wp in wp_list:
            planner.add_waypoint(wp)

        # 1. Takeoff
        if not drone.takeoff(altitude=15.0):
            logger.error("Takeoff failed!")
            return False

        # 2. Execute Waypoints
        photo_count = 0
        while not planner.is_finished():
            wp = planner.get_current_waypoint()
            logger.info(f"Navigating to WP #{planner.current_index + 1}/{len(planner.waypoints)}: "
                        f"Lat={wp.lat:.6f}, Lon={wp.lon:.6f}, Alt={wp.alt_rel:.1f}m")

            drone.goto_location(lat=wp.lat, lon=wp.lon, alt_rel=wp.alt_rel, speed=wp.speed)
            reached = drone.wait_for_waypoint(wp.lat, wp.lon, wp.alt_rel, acceptance_radius=2.5, timeout=40.0)

            if reached:
                if wp.action == "TRIGGER_CAM":
                    photo_count += 1
                    logger.info(f"[CAMERA TRIGGER] Captured survey frame #{photo_count} at ({wp.lat:.6f}, {wp.lon:.6f})")
                    time.sleep(0.5)

            planner.advance()

        # 3. Return to Launch
        logger.info("Survey completed! Returning to Launch (RTL)...")
        drone.return_to_launch()

        # Wait until landing is complete
        while True:
            snap = drone.telemetry
            if snap.position.alt_rel <= 0.2 and not snap.state.armed:
                logger.info("Landed safely at Home position.")
                break
            time.sleep(1.0)

        logger.info(f"=== Mission 02 Completed! Total survey frames: {photo_count} ===")
        return True

    finally:
        drone.disconnect()


if __name__ == "__main__":
    run_mission()
