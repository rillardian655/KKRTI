"""One-dimensional discrete Kalman filter for altitude and velocity state estimation."""

class KalmanFilter1D:
    def __init__(self, process_noise_q: float = 0.01, measurement_noise_r: float = 0.1, initial_estimate: float = 0.0):
        self.q = process_noise_q
        self.r = measurement_noise_r
        self.state_estimate = initial_estimate
        self.error_covariance = 1.0

    def update(self, measurement: float) -> float:
        # Prediction step
        self.error_covariance += self.q

        # Measurement update step
        kalman_gain = self.error_covariance / (self.error_covariance + self.r)
        self.state_estimate += kalman_gain * (measurement - self.state_estimate)
        self.error_covariance = (1.0 - kalman_gain) * self.error_covariance

        return self.state_estimate
