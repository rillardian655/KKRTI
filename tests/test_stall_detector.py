import unittest
from core.stall_detector import StallDetector

class TestStallDetector(unittest.TestCase):
    def setUp(self):
        self.detector = StallDetector(stall_speed_m_s=10.0, critical_pitch_deg=16.0)

    def test_nominal_speed(self):
        warn, _ = self.detector.evaluate(airspeed_m_s=15.0, pitch_deg=5.0)
        self.assertFalse(warn)

    def test_low_speed_high_pitch(self):
        warn, msg = self.detector.evaluate(airspeed_m_s=8.0, pitch_deg=12.0)
        self.assertTrue(warn)
        self.assertIn("STALL WARNING", msg)

if __name__ == '__main__':
    unittest.main()
