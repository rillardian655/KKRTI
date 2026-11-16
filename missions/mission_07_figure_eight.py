"""Mission 07: Continuous figure-eight loiter pattern for radar and payload testing."""

import math
import time
import logging
from core.drone_controller import DroneController

logger = logging.getLogger("Mission07")

def run_mission(endpoint: str = "udp:127.0.0.1:14550", loops: int = 1):
    logger.info("=== Starting Mission 07: Figure-Eight Trajectory ===")
    drone = DroneController(endpoint=endpoint)
    if not drone.connect():
        return False

    try:
        while drone.telemetry.position.lat == 0.0:
            time.sleep(0.1)

        home = drone.telemetry.position
        if not drone.takeoff(altitude=16.0):
            return False

        radius_m = 25.0
        points = 12
        for _ in range(loops):
            # Left loop
            for i in range(points):
                angle = 2.0 * math.pi * (i / points)
                dx = radius_m * math.cos(angle) - radius_m
                dy = radius_m * math.sin(angle)
                lat = home.lat + (dx / 111320.0)
                lon = home.lon + (dy / (111320.0 * math.cos(math.radians(home.lat))))
                drone.goto_location(lat, lon, 16.0, speed=7.0)
                drone.wait_for_waypoint(lat, lon, 16.0, acceptance_radius=3.0, timeout=15.0)

            # Right loop
            for i in range(points):
                angle = 2.0 * math.pi * (i / points)
                dx = radius_m * math.cos(angle) + radius_m
                dy = radius_m * math.sin(angle)
                lat = home.lat + (dx / 111320.0)
                lon = home.lon + (dy / (111320.0 * math.cos(math.radians(home.lat))))
                drone.goto_location(lat, lon, 16.0, speed=7.0)
                drone.wait_for_waypoint(lat, lon, 16.0, acceptance_radius=3.0, timeout=15.0)

        drone.return_to_launch()
        return True
    finally:
        drone.disconnect()

if __name__ == "__main__":
    run_mission()
