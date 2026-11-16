import unittest
from core.geometry import point_to_line_distance

class TestGeometry(unittest.TestCase):
    def test_perpendicular_distance(self):
        # Point (0, 5) to horizontal line from (-10, 0) to (10, 0)
        d = point_to_line_distance(0.0, 5.0, -10.0, 0.0, 10.0, 0.0)
        self.assertAlmostEqual(d, 5.0, places=2)

    def test_endpoint_distance(self):
        # Point (15, 0) to horizontal line from (-10, 0) to (10, 0)
        d = point_to_line_distance(15.0, 0.0, -10.0, 0.0, 10.0, 0.0)
        self.assertAlmostEqual(d, 5.0, places=2)

if __name__ == '__main__':
    unittest.main()
