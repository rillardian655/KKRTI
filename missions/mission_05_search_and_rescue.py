"""Mission 05: Expanding Square / Spiral Search Pattern for SAR Operations."""

import time
import math
import logging
from core.drone_controller import DroneController

logger = logging.getLogger("Mission05")

def run_mission(endpoint: str = "udp:127.0.0.1:14550", legs: int = 5):
    logger.info("=== Starting Mission 05: Search & Rescue Spiral Pattern ===")
    drone = DroneController(endpoint=endpoint)
    if not drone.connect():
        return False

    try:
        while drone.telemetry.position.lat == 0.0:
            time.sleep(0.1)

        home = drone.telemetry.position
        if not drone.takeoff(altitude=15.0):
            return False

        step_dist_m = 15.0
        curr_lat = home.lat
        curr_lon = home.lon

        # Expanding box pattern
        for leg in range(1, legs + 1):
            dist = leg * step_dist_m
            dlat = (dist / 111320.0) if (leg % 2 == 1) else 0.0
            dlon = (dist / (111320.0 * math.cos(math.radians(curr_lat)))) if (leg % 2 == 0) else 0.0

            curr_lat += dlat
            curr_lon += dlon

            logger.info(f"[SAR] Leg #{leg}: Navigating outward ({dist:.1f}m)...")
            drone.goto_location(curr_lat, curr_lon, 15.0, speed=6.0)
            drone.wait_for_waypoint(curr_lat, curr_lon, 15.0, acceptance_radius=2.5, timeout=30.0)
            time.sleep(1.0)

        logger.info("[SAR] Pattern complete! Returning home...")
        drone.return_to_launch()
        return True
    finally:
        drone.disconnect()

if __name__ == "__main__":
    run_mission()
