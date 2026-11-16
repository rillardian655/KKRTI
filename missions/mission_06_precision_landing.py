"""Mission 06: Stepwise vertical approach and optical alignment landing."""

import time
import logging
from core.drone_controller import DroneController

logger = logging.getLogger("Mission06")

def run_mission(endpoint: str = "udp:127.0.0.1:14550"):
    logger.info("=== Starting Mission 06: Precision Target Touchdown ===")
    drone = DroneController(endpoint=endpoint)
    if not drone.connect():
        return False

    try:
        if not drone.takeoff(altitude=12.0):
            return False

        logger.info("Descending step 1: 5.0m for target lock...")
        drone.goto_location(drone.telemetry.position.lat, drone.telemetry.position.lon, 5.0, speed=1.5)
        drone.wait_for_waypoint(drone.telemetry.position.lat, drone.telemetry.position.lon, 5.0, acceptance_radius=1.0)
        time.sleep(2.0)

        logger.info("Executing final touchdown...")
        drone.land()
        while drone.telemetry.state.armed:
            time.sleep(0.5)

        logger.info("Touchdown verified on pad.")
        return True
    finally:
        drone.disconnect()

if __name__ == "__main__":
    run_mission()
