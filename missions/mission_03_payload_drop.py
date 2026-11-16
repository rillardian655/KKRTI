"""Mission 03: Precision Payload Drop (KRTI VTOL / TD Scenario)."""

import time
import logging
from core.drone_controller import DroneController

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Mission03")


def run_mission(endpoint: str = "udp:127.0.0.1:14550"):
    logger.info("=== Starting Mission 03: Autonomous Payload Drop (KRTI Mission) ===")
    drone = DroneController(endpoint=endpoint)

    if not drone.connect():
        logger.error("Failed to connect to drone.")
        return False

    try:
        # Wait for valid GPS position
        while drone.telemetry.position.lat == 0.0:
            time.sleep(0.1)

        home = drone.telemetry.position
        # Simulated target drop coordinate ~120m North-East
        drop_target_lat = home.lat + 0.0006
        drop_target_lon = home.lon + 0.0005

        cruise_alt = 16.0
        drop_alt = 8.0

        # Step 1: Takeoff
        logger.info(f"Step 1: Takeoff to cruise altitude {cruise_alt}m...")
        if not drone.takeoff(altitude=cruise_alt):
            logger.error("Takeoff failed!")
            return False

        # Step 2: Transit to Drop Zone
        logger.info(f"Step 2: Flying to Drop Zone -> Lat={drop_target_lat:.6f}, Lon={drop_target_lon:.6f}...")
        drone.goto_location(drop_target_lat, drop_target_lon, cruise_alt, speed=8.0)
        drone.wait_for_waypoint(drop_target_lat, drop_target_lon, cruise_alt, acceptance_radius=2.0, timeout=45.0)

        # Step 3: Descend to Release Altitude
        logger.info(f"Step 3: Descending to drop altitude {drop_alt}m...")
        drone.goto_location(drop_target_lat, drop_target_lon, drop_alt, speed=2.0)
        drone.wait_for_waypoint(drop_target_lat, drop_target_lon, drop_alt, acceptance_radius=1.5, timeout=20.0)

        # Step 4: Stabilize & Actuate Servo
        logger.info("Step 4: Target acquired! Hovering 3 seconds for stabilization...")
        time.sleep(3.0)

        logger.info("[PAYLOAD MECHANISM] Triggering servo release on Channel 9...")
        drone.trigger_payload_servo(servo_channel=9, pwm_value=2000)
        time.sleep(1.5)
        logger.info("[PAYLOAD RELEASED] Target payload successfully deployed on mark!")

        # Step 5: Climb back to cruise altitude
        logger.info(f"Step 5: Climbing back to {cruise_alt}m for clearance...")
        drone.goto_location(drop_target_lat, drop_target_lon, cruise_alt, speed=4.0)
        drone.wait_for_waypoint(drop_target_lat, drop_target_lon, cruise_alt, acceptance_radius=2.0, timeout=15.0)

        # Step 6: Return to Launch (RTL)
        logger.info("Step 6: Returning home (RTL)...")
        drone.return_to_launch()

        while True:
            snap = drone.telemetry
            if snap.position.alt_rel <= 0.2 and not snap.state.armed:
                logger.info("Touchdown verified! Vehicle safe and disarmed.")
                break
            time.sleep(1.0)

        logger.info("=== Mission 03 Completed Successfully! ===")
        return True

    finally:
        drone.disconnect()


if __name__ == "__main__":
    run_mission()
