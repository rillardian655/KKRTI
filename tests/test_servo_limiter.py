import unittest
from core.servo_limiter import ServoLimiter

class TestServoLimiter(unittest.TestCase):
    def setUp(self):
        self.limiter = ServoLimiter(pwm_min=1000, pwm_max=2000, deadband=25)

    def test_clamping(self):
        self.assertEqual(self.limiter.clamp(800), 1000)
        self.assertEqual(self.limiter.clamp(2500), 2000)
        self.assertEqual(self.limiter.clamp(1400), 1400)

    def test_deadband(self):
        self.assertTrue(self.limiter.in_deadband(1510))
        self.assertFalse(self.limiter.in_deadband(1550))

if __name__ == '__main__':
    unittest.main()
