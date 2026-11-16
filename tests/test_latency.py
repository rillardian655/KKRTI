import unittest
from tools.latency_profiler import LatencyProfiler

class TestLatency(unittest.TestCase):
    def test_profiler_statistics(self):
        p = LatencyProfiler()
        p.record_sample(0.010)
        p.record_sample(0.020)
        self.assertAlmostEqual(p.average_ms, 15.0, places=1)
        self.assertAlmostEqual(p.max_ms, 20.0, places=1)

if __name__ == '__main__':
    unittest.main()
