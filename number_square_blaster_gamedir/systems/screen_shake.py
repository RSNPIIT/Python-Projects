"""Block Blast - Screen Shake Juice System"""
import random

class ScreenShake:
    def __init__(self):
        self.duration = 0.0
        self.intensity = 0.0

    def add_shake(self, intensity: float = 6.0, duration: float = 0.2):
        self.intensity = max(self.intensity, intensity)
        self.duration = max(self.duration, duration)

    def update(self, dt: float) -> tuple[float, float]:
        if self.duration > 0:
            self.duration -= dt
            decay = max(0.0, self.duration)
            offset_x = (random.random() * 2 - 1) * self.intensity * decay * 4.0
            offset_y = (random.random() * 2 - 1) * self.intensity * decay * 4.0
            return (offset_x, offset_y)
        else:
            self.intensity = 0.0
            return (0.0, 0.0)
