"""Mission 08: Autonomous return and holding orbit upon simulated data link loss."""

import time
import logging
from core.drone_controller import DroneController

logger = logging.getLogger("Mission08")

def run_mission(endpoint: str = "udp:127.0.0.1:14550"):
    logger.info("=== Starting Mission 08: Autonomous Comms Loss Recovery ===")
    drone = DroneController(endpoint=endpoint)
    if not drone.connect():
        return False

    try:
        if not drone.takeoff(altitude=15.0):
            return False

        logger.info("Simulating flight towards remote boundary...")
        home = drone.telemetry.position
        target_lat = home.lat + 0.0005
        target_lon = home.lon + 0.0005
        drone.goto_location(target_lat, target_lon, 15.0, speed=6.0)
        time.sleep(4.0)

        logger.warning("[SIMULATION] Telemetry communication lost! Executing autonomous safety RTL...")
        drone.return_to_launch()

        while True:
            snap = drone.telemetry
            if snap.position.alt_rel <= 0.2 and not snap.state.armed:
                logger.info("Autonomous failsafe recovery touchdown verified.")
                break
            time.sleep(1.0)
        return True
    finally:
        drone.disconnect()

if __name__ == "__main__":
    run_mission()
