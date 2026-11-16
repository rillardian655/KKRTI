import unittest
from core.filters import LowPassFilter

class TestFilters(unittest.TestCase):
    def test_low_pass_initial(self):
        lpf = LowPassFilter(alpha=0.5)
        val = lpf.update(10.0)
        self.assertEqual(val, 10.0)

    def test_smoothing(self):
        lpf = LowPassFilter(alpha=0.2)
        lpf.update(0.0)
        val = lpf.update(10.0)
        self.assertAlmostEqual(val, 2.0)

if __name__ == '__main__':
    unittest.main()
