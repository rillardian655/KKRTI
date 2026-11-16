import unittest
from simulator.gyroscopic_torque import calculate_gyroscopic_torque_nm

class TestGyroscopic(unittest.TestCase):
    def test_zero_yaw_rate(self):
        tau = calculate_gyroscopic_torque_nm(prop_inertia_kg_m2=0.0001, prop_rpm=6000, yaw_rate_rad_s=0.0)
        self.assertEqual(tau, 0.0)

    def test_positive_torque(self):
        tau = calculate_gyroscopic_torque_nm(prop_inertia_kg_m2=0.0001, prop_rpm=6000, yaw_rate_rad_s=1.0)
        self.assertTrue(tau > 0.0)

if __name__ == '__main__':
    unittest.main()
