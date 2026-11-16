import unittest
import math
from core.path_following import compute_course_correction

class TestPathFollowing(unittest.TestCase):
    def test_on_path_no_correction(self):
        heading = compute_course_correction(cross_track_error_m=0.0, path_heading_rad=0.0)
        self.assertAlmostEqual(heading, 0.0)

    def test_left_deviation_steers_right(self):
        # Drone is to the left (-10m), should correct positive
        heading = compute_course_correction(cross_track_error_m=-10.0, path_heading_rad=0.0)
        self.assertTrue(heading > 0.0)

if __name__ == '__main__':
    unittest.main()
