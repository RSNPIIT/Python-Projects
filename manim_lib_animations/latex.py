from manim import *

class Ipsum(Scene):
    def construct(self):
        titl = Tex(r"This is some \LaTeX").scale(2)
        self.play(
            Write(titl)
        )
        self.wait(3)