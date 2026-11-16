import unittest
from core.telemetry import (
    calculate_haversine_distance, calculate_distance_3d, calculate_bearing, Position
)

class TestTelemetryMath(unittest.TestCase):
    def test_haversine_distance_zero(self):
        dist = calculate_haversine_distance(-7.9255, 110.5485, -7.9255, 110.5485)
        self.assertAlmostEqual(dist, 0.0, places=2)

    def test_haversine_known_offset(self):
        dist = calculate_haversine_distance(0.0, 0.0, 1.0, 0.0)
        self.assertTrue(110000.0 < dist < 112000.0)

    def test_distance_3d(self):
        d3 = calculate_distance_3d(0.0, 0.0, 0.0, 0.0, 0.0, 10.0)
        self.assertAlmostEqual(d3, 10.0, places=2)

    def test_bearing_north(self):
        bearing = calculate_bearing(0.0, 0.0, 1.0, 0.0)
        self.assertAlmostEqual(bearing, 0.0, delta=1.0)

    def test_bearing_east(self):
        bearing = calculate_bearing(0.0, 0.0, 0.0, 1.0)
        self.assertAlmostEqual(bearing, 90.0, delta=1.0)

if __name__ == '__main__':
    unittest.main()
