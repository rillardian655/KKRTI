import unittest
from core.dubins import generate_arc

class TestDubins(unittest.TestCase):
    def test_arc_points_count(self):
        pts = generate_arc(start_x=0.0, start_y=0.0, start_heading_rad=0.0,
                           turn_angle_rad=1.57, turn_radius_m=20.0, steps=8)
        self.assertEqual(len(pts), 9)

    def test_arc_start_point(self):
        pts = generate_arc(start_x=0.0, start_y=0.0, start_heading_rad=0.0,
                           turn_angle_rad=1.57, turn_radius_m=20.0, steps=8)
        self.assertAlmostEqual(pts[0][0], 0.0, places=2)
        self.assertAlmostEqual(pts[0][1], 0.0, places=2)

if __name__ == '__main__':
    unittest.main()
