"""Measures communication loop trip time and packet jitter."""

import time
from typing import List

class LatencyProfiler:
    def __init__(self):
        self.samples_ms: List[float] = []

    def record_sample(self, duration_sec: float):
        self.samples_ms.append(duration_sec * 1000.0)

    @property
    def average_ms(self) -> float:
        return sum(self.samples_ms) / len(self.samples_ms) if self.samples_ms else 0.0

    @property
    def max_ms(self) -> float:
        return max(self.samples_ms) if self.samples_ms else 0.0
