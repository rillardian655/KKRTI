import unittest
from simulator.atmosphere import get_air_density_at_altitude

class TestAtmosphere(unittest.TestCase):
    def test_sea_level_density(self):
        rho = get_air_density_at_altitude(0.0)
        self.assertAlmostEqual(rho, 1.225, places=2)

    def test_high_altitude_density_drop(self):
        rho = get_air_density_at_altitude(2000.0)
        self.assertTrue(rho < 1.225)
        self.assertTrue(rho > 0.9)

if __name__ == '__main__':
    unittest.main()
