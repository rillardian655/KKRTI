import unittest
from core.speed_governor import SpeedGovernor

class TestSpeedGovernor(unittest.TestCase):
    def test_speed_limiting(self):
        gov = SpeedGovernor(max_speed_m_s=10.0, max_accel_m_s2=2.0)
        # Starting at 0, target 10 m/s with dt = 1.0s -> max step is 2 m/s
        speed = gov.compute_step(target_speed=10.0, dt=1.0)
        self.assertAlmostEqual(speed, 2.0, places=2)

    def test_max_speed_clamp(self):
        gov = SpeedGovernor(max_speed_m_s=5.0, max_accel_m_s2=10.0)
        speed = gov.compute_step(target_speed=20.0, dt=1.0)
        self.assertAlmostEqual(speed, 5.0, places=2)

if __name__ == '__main__':
    unittest.main()
