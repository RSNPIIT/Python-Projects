from manim import *

class Shrek(Scene):
    def construct(self):
        p = Text(
            "RSNPIIT did it 🔌",
            font = "Sentient"
        ).scale(2)
        self.play(Write(p))
        self.wait() 