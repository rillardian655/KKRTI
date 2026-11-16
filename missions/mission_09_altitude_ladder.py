"""Mission 09: Stepwise vertical ladder profile to evaluate climb performance and power draw."""

import time
import logging
from core.drone_controller import DroneController

logger = logging.getLogger("Mission09")

def run_mission(endpoint: str = "udp:127.0.0.1:14550", altitudes: list = None):
    if altitudes is None:
        altitudes = [10.0, 20.0, 30.0]

    logger.info("=== Starting Mission 09: Stepped Altitude Ladder Climb ===")
    drone = DroneController(endpoint=endpoint)
    if not drone.connect():
        return False

    try:
        if not drone.takeoff(altitude=altitudes[0]):
            return False

        home = drone.telemetry.position
        for target_h in altitudes:
            logger.info(f"[LADDER] Climbing to target altitude: {target_h:.1f}m...")
            drone.goto_location(home.lat, home.lon, target_h, speed=2.5)
            drone.wait_for_waypoint(home.lat, home.lon, target_h, acceptance_radius=1.5, timeout=20.0)
            time.sleep(3.0)

        logger.info("[LADDER] Reached highest altitude tier. Returning home...")
        drone.return_to_launch()
        return True
    finally:
        drone.disconnect()

if __name__ == "__main__":
    run_mission()
