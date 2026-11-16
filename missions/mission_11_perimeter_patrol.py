"""Mission 11: Continuous boundary patrol sequence around flight perimeter."""

import time
import logging
from core.drone_controller import DroneController

logger = logging.getLogger("Mission11")

def run_mission(endpoint: str = "udp:127.0.0.1:14550", boundary_radius_m: float = 40.0):
    logger.info("=== Starting Mission 11: Perimeter Patrol Surveillance ===")
    drone = DroneController(endpoint=endpoint)
    if not drone.connect():
        return False

    try:
        while drone.telemetry.position.lat == 0.0:
            time.sleep(0.1)

        home = drone.telemetry.position
        if not drone.takeoff(altitude=16.0):
            return False

        # 4 corners offset
        d_lat = boundary_radius_m / 111320.0
        d_lon = boundary_radius_m / (111320.0 * 0.99)

        corners = [
            (home.lat + d_lat, home.lon + d_lon),
            (home.lat - d_lat, home.lon + d_lon),
            (home.lat - d_lat, home.lon - d_lon),
            (home.lat + d_lat, home.lon - d_lon)
        ]

        for idx, (clat, clon) in enumerate(corners):
            logger.info(f"[PATROL] Moving to perimeter corner #{idx + 1}...")
            drone.goto_location(clat, clon, 16.0, speed=6.5)
            drone.wait_for_waypoint(clat, clon, 16.0, acceptance_radius=2.5, timeout=25.0)
            time.sleep(1.0)

        logger.info("[PATROL] Perimeter circuit complete. Returning to launch...")
        drone.return_to_launch()
        return True
    finally:
        drone.disconnect()

if __name__ == "__main__":
    run_mission()
