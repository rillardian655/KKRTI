"""Mission 10: Classical aviation teardrop procedure turn for runway reversal."""

import time
import math
import logging
from core.drone_controller import DroneController

logger = logging.getLogger("Mission10")

def run_mission(endpoint: str = "udp:127.0.0.1:14550"):
    logger.info("=== Starting Mission 10: Teardrop Turnaround Pattern ===")
    drone = DroneController(endpoint=endpoint)
    if not drone.connect():
        return False

    try:
        while drone.telemetry.position.lat == 0.0:
            time.sleep(0.1)

        home = drone.telemetry.position
        if not drone.takeoff(altitude=18.0):
            return False

        # Leg 1: Outbound straight 60m
        out_lat = home.lat + (60.0 / 111320.0)
        drone.goto_location(out_lat, home.lon, 18.0, speed=7.0)
        drone.wait_for_waypoint(out_lat, home.lon, 18.0, acceptance_radius=2.5, timeout=25.0)

        # Leg 2: 30 deg divergence
        div_lat = out_lat + (30.0 / 111320.0)
        div_lon = home.lon + (20.0 / (111320.0 * math.cos(math.radians(home.lat))))
        drone.goto_location(div_lat, div_lon, 18.0, speed=6.0)
        drone.wait_for_waypoint(div_lat, div_lon, 18.0, acceptance_radius=2.5, timeout=15.0)

        logger.info("[TEARDROP] Turnaround complete. Heading back home on reciprocal track...")
        drone.return_to_launch()
        return True
    finally:
        drone.disconnect()

if __name__ == "__main__":
    run_mission()
