import unittest
from core.airspeed import differential_pressure_to_airspeed

class TestAirspeed(unittest.TestCase):
    def test_zero_pressure(self):
        self.assertEqual(differential_pressure_to_airspeed(0.0), 0.0)

    def test_known_airspeed(self):
        # 10 m/s with rho 1.225 -> delta_P = 0.5 * 1.225 * 100 = 61.25 Pa
        speed = differential_pressure_to_airspeed(61.25, 1.225)
        self.assertAlmostEqual(speed, 10.0, places=2)

if __name__ == '__main__':
    unittest.main()
