import unittest
from simulator.thrust_model import calculate_thrust_force_n

class TestThrustModel(unittest.TestCase):
    def test_zero_rpm(self):
        self.assertEqual(calculate_thrust_force_n(0.0), 0.0)

    def test_positive_thrust(self):
        t = calculate_thrust_force_n(rpm=5000)
        self.assertTrue(t > 0.0)

if __name__ == '__main__':
    unittest.main()
