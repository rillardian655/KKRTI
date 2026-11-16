import unittest
import time
from core.failsafe_manager import FailsafeManager
from core.telemetry import DroneTelemetry, DroneState, BatteryState

class TestFailsafeManager(unittest.TestCase):
    def setUp(self):
        self.failsafe = FailsafeManager(battery_low_pct=20.0, battery_critical_pct=10.0)

    def test_healthy_telemetry(self):
        t = DroneTelemetry()
        t.state.mavlink_connected = True
        t.state.last_heartbeat = time.time()
        t.battery.percentage = 80.0
        rtl_called = []
        land_called = []
        res = self.failsafe.evaluate(t, None, rtl_called.append, land_called.append)
        self.assertTrue(res)
        self.assertEqual(len(rtl_called), 0)

    def test_battery_critical_triggers_land(self):
        t = DroneTelemetry()
        t.state.mavlink_connected = True
        t.state.last_heartbeat = time.time()
        t.battery.percentage = 8.0
        rtl_called = []
        land_called = []
        res = self.failsafe.evaluate(t, None, rtl_called.append, land_called.append)
        self.assertFalse(res)
        self.assertEqual(len(land_called), 1)

if __name__ == '__main__':
    unittest.main()
