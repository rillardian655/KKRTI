import unittest
from core.gps_filter import GPSFilter

class TestGPSFilter(unittest.TestCase):
    def setUp(self):
        self.filter = GPSFilter(max_hdop=2.0, min_satellites=8)

    def test_acceptable_fix(self):
        self.assertTrue(self.filter.is_fix_acceptable(fix_type=3, satellites=12, eph_cm=120))

    def test_insufficient_satellites(self):
        self.assertFalse(self.filter.is_fix_acceptable(fix_type=3, satellites=5, eph_cm=120))

    def test_poor_hdop(self):
        self.assertFalse(self.filter.is_fix_acceptable(fix_type=3, satellites=10, eph_cm=350))

if __name__ == '__main__':
    unittest.main()
