"""Mission 12: Loitering orbit while expanding loiter radius dynamically."""

import time
import math
import logging
from core.drone_controller import DroneController

logger = logging.getLogger("Mission12")

def run_mission(endpoint: str = "udp:127.0.0.1:14550"):
    logger.info("=== Starting Mission 12: Dynamic Loiter Orbit ===")
    drone = DroneController(endpoint=endpoint)
    if not drone.connect():
        return False

    try:
        while drone.telemetry.position.lat == 0.0:
            time.sleep(0.1)

        home = drone.telemetry.position
        if not drone.takeoff(altitude=15.0):
            return False

        # Expanding circular orbit from 10m to 25m
        radii = [15.0, 25.0]
        for radius in radii:
            logger.info(f"[LOITER] Orbiting with radius: {radius:.1f}m...")
            steps = 8
            for i in range(steps):
                angle = 2.0 * math.pi * (i / steps)
                dlat = (radius * math.cos(angle)) / 111320.0
                dlon = (radius * math.sin(angle)) / (111320.0 * math.cos(math.radians(home.lat)))
                drone.goto_location(home.lat + dlat, home.lon + dlon, 15.0, speed=5.5)
                drone.wait_for_waypoint(home.lat + dlat, home.lon + dlon, 15.0, acceptance_radius=2.0, timeout=12.0)

        drone.return_to_launch()
        return True
    finally:
        drone.disconnect()

if __name__ == "__main__":
    run_mission()
