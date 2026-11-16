import unittest
from core.kalman_filter import KalmanFilter1D

class TestKalman(unittest.TestCase):
    def test_convergence(self):
        kf = KalmanFilter1D(process_noise_q=0.01, measurement_noise_r=0.1, initial_estimate=0.0)
        # Repeated measurements of 10.0
        val = 0.0
        for _ in range(20):
            val = kf.update(10.0)
        self.assertAlmostEqual(val, 10.0, places=1)

if __name__ == '__main__':
    unittest.main()
