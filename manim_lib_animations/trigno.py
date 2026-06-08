from manim import *
import numpy as np

class Sine(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(
            phi = 0 * DEGREES,
            theta = -90 * DEGREES
        )
        axes = Axes(
            x_range = [0 , 2 * PI],
            y_range = [-1.5 , 1.5 , 0.5]
        )
        sine_wave = axes.plot(
            lambda x: np.sin(x),
            color = YELLOW
        )
        self.play(
            Create(axes),
            Create(sine_wave)
        )
        self.wait(1)