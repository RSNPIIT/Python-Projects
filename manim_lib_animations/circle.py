from manim import *

class Circ(Scene):
    def construct(self):
        c = Circle(
            radius = 2,
            color = RED,
            fill_color = YELLOW,
            fill_opacity = 0.75
        )
        rect = Rectangle(
            color = WHITE,
            height = 3,
            width = 2.5
        ).to_edge(UL)

        self.play(
            Write(c),
            Write(rect)
        )
        self.wait(1)