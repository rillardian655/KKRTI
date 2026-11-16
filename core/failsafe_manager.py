"""Autonomous Safety & Failsafe Manager."""

import time
import logging
from typing import Optional, Callable
from core.telemetry import DroneTelemetry
from core.geofence_manager import GeofenceManager


logger = logging.getLogger("FailsafeManager")


class FailsafeManager:
    """Monitors telemetry conditions and executes automatic safety procedures (RTL, LAND)."""

    def __init__(self,
                 battery_low_pct: float = 20.0,
                 battery_critical_pct: float = 10.0,
                 telemetry_timeout_sec: float = 4.0):
        self.battery_low_pct = battery_low_pct
        self.battery_critical_pct = battery_critical_pct
        self.telemetry_timeout_sec = telemetry_timeout_sec
        self.failsafe_triggered: bool = False
        self.active_reason: Optional[str] = None

    def evaluate(self,
                 telemetry: DroneTelemetry,
                 geofence: Optional[GeofenceManager],
                 on_trigger_rtl: Callable[[str], None],
                 on_trigger_land: Callable[[str], None]) -> bool:
        """Evaluates health criteria. If a violation is detected, calls the appropriate action.
        
        Returns:
            True if all systems normal, False if a failsafe action was triggered.
        """
        if self.failsafe_triggered:
            return False

        # 1. Telemetry Link Timeout Check
        if not telemetry.is_link_alive(timeout_sec=self.telemetry_timeout_sec):
            self.failsafe_triggered = True
            self.active_reason = f"MAVLink telemetry link lost (> {self.telemetry_timeout_sec}s timeout)"
            logger.critical(f"[FAILSAFE] {self.active_reason}! Triggering Return-to-Launch...")
            on_trigger_rtl(self.active_reason)
            return False

        # 2. Critical Battery Check (< 10%)
        if telemetry.battery.percentage <= self.battery_critical_pct:
            self.failsafe_triggered = True
            self.active_reason = f"Battery critical ({telemetry.battery.percentage:.1f}%)"
            logger.critical(f"[FAILSAFE] {self.active_reason}! Triggering Emergency Landing...")
            on_trigger_land(self.active_reason)
            return False

        # 3. Low Battery Check (< 20%)
        if telemetry.battery.percentage <= self.battery_low_pct:
            self.failsafe_triggered = True
            self.active_reason = f"Battery low threshold reached ({telemetry.battery.percentage:.1f}%)"
            logger.warning(f"[FAILSAFE] {self.active_reason}! Triggering Return-to-Launch...")
            on_trigger_rtl(self.active_reason)
            return False

        # 4. Geofence Check
        if geofence and geofence.enabled:
            safe, reason = geofence.check_position(telemetry.position, telemetry.home_position)
            if not safe:
                self.failsafe_triggered = True
                self.active_reason = f"Geofence Violation: {reason}"
                logger.critical(f"[FAILSAFE] {self.active_reason}! Triggering Return-to-Launch...")
                on_trigger_rtl(self.active_reason)
                return False

        return True

    def reset(self):
        self.failsafe_triggered = False
        self.active_reason = None
