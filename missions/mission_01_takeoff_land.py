"""Mission 01: Basic Takeoff, Altitude Hold, and Autonomous Land."""

import time
import logging
from core.drone_controller import DroneController

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Mission01")


def run_mission(endpoint: str = "udp:127.0.0.1:14550", target_alt: float = 12.0):
    logger.info("=== Starting Mission 01: Basic Takeoff & Land ===")
    drone = DroneController(endpoint=endpoint)

    if not drone.connect():
        logger.error("Failed to connect to drone. Is SITL running?")
        return False

    try:
        # 1. Arm and Takeoff
        logger.info(f"Commanding takeoff to {target_alt:.1f} meters...")
        if not drone.takeoff(altitude=target_alt, timeout=25.0):
            logger.error("Takeoff sequence failed.")
            return False

        # 2. Altitude Hold
        logger.info("Holding altitude for 5 seconds...")
        for i in range(5, 0, -1):
            snap = drone.telemetry
            logger.info(f"Hovering... Alt: {snap.position.alt_rel:.2f}m | Battery: {snap.battery.percentage:.1f}%")
            time.sleep(1.0)

        # 3. Autonomous Land
        logger.info("Initiating autonomous landing...")
        drone.land()

        # Wait until on ground
        while True:
            snap = drone.telemetry
            if snap.position.alt_rel <= 0.2 and not snap.state.armed:
                logger.info("Drone safely landed and disarmed!")
                break
            time.sleep(0.5)

        logger.info("=== Mission 01 Completed Successfully! ===")
        return True

    finally:
        drone.disconnect()


if __name__ == "__main__":
    run_mission()
