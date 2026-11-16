"""Signal processing filters for sensor measurement smoothing."""

class LowPassFilter:
    def __init__(self, alpha: float = 0.2):
        if not (0.0 < alpha <= 1.0):
            raise ValueError("Filter alpha must be in range (0.0, 1.0]")
        self.alpha = alpha
        self.filtered_value = None

    def update(self, raw_value: float) -> float:
        if self.filtered_value is None:
            self.filtered_value = raw_value
        else:
            self.filtered_value = (self.alpha * raw_value) + ((1.0 - self.alpha) * self.filtered_value)
        return self.filtered_value

    def reset(self):
        self.filtered_value = None
