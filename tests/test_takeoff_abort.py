import unittest
from core.takeoff_abort import TakeoffAbortDetector

class TestTakeoffAbort(unittest.TestCase):
    def setUp(self):
        self.detector = TakeoffAbortDetector(min_climb_rate_m_s=0.5, max_tilt_deg=30.0, timeout_sec=4.0)

    def test_nominal(self):
        abort, reason = self.detector.evaluate(climb_rate=1.2, roll_deg=2.0, pitch_deg=5.0, elapsed_sec=2.0)
        self.assertFalse(abort)

    def test_tilt_abort(self):
        abort, reason = self.detector.evaluate(climb_rate=1.2, roll_deg=35.0, pitch_deg=5.0, elapsed_sec=2.0)
        self.assertTrue(abort)
        self.assertIn("Excessive tilt", reason)

if __name__ == '__main__':
    unittest.main()
