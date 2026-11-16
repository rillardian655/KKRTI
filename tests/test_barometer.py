import unittest
from core.barometer import pressure_to_altitude

class TestBarometer(unittest.TestCase):
    def test_sea_level(self):
        alt = pressure_to_altitude(1013.25, 1013.25)
        self.assertAlmostEqual(alt, 0.0, places=1)

    def test_higher_altitude(self):
        # Pressure decreases with altitude
        alt = pressure_to_altitude(900.0, 1013.25)
        self.assertTrue(alt > 900.0)

if __name__ == '__main__':
    unittest.main()
