import unittest
from core.geofence_manager import GeofenceManager
from core.telemetry import Position

class TestGeofence(unittest.TestCase):
    def setUp(self):
        self.fence = GeofenceManager()
        self.fence.enabled = True
        self.fence.max_altitude_rel = 30.0
        self.fence.max_distance_from_home = 100.0
        self.fence.set_polygon([
            (0.0, 0.0),
            (0.0, 1.0),
            (1.0, 1.0),
            (1.0, 0.0)
        ])

    def test_inside_polygon(self):
        self.assertTrue(self.fence.is_point_inside_polygon(0.5, 0.5))

    def test_outside_polygon(self):
        self.assertFalse(self.fence.is_point_inside_polygon(2.0, 2.0))

    def test_altitude_breach(self):
        pos = Position(lat=0.5, lon=0.5, alt_rel=35.0)
        safe, reason = self.fence.check_position(pos)
        self.assertFalse(safe)
        self.assertIn("Upper Altitude Breach", reason)

if __name__ == '__main__':
    unittest.main()
