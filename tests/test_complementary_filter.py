import unittest
from core.complementary_filter import ComplementaryFilter

class TestComplementaryFilter(unittest.TestCase):
    def test_level_acceleration(self):
        cf = ComplementaryFilter(alpha=0.9)
        # Level condition: accel_z = 9.81
        p, r = cf.update(0.0, 0.0, 0.0, 0.0, 9.81, dt=0.02)
        self.assertAlmostEqual(p, 0.0, places=1)
        self.assertAlmostEqual(r, 0.0, places=1)

if __name__ == '__main__':
    unittest.main()
