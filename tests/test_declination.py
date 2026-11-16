import unittest
from core.declination import magnetic_to_true_heading

class TestDeclination(unittest.TestCase):
    def test_yogyakarta_correction(self):
        true_h = magnetic_to_true_heading(magnetic_heading_deg=100.0, region_key="yogyakarta")
        self.assertAlmostEqual(true_h, 100.75, places=2)

    def test_wraparound(self):
        true_h = magnetic_to_true_heading(magnetic_heading_deg=359.5, region_key="yogyakarta")
        self.assertAlmostEqual(true_h, 0.25, places=2)

if __name__ == '__main__':
    unittest.main()
