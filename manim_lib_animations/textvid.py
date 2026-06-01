from manim import *

class Testing(Scene):
    def construct(self):

        # Make a Textual argument and send it to the edge of the Upper Left Row
        name = Tex("RSNPIIT").to_edge(UL , buff = 0.5)
        sq = Square(side_length = 0.5).shift(LEFT * 3)
        tri = Triangle().scale(0.6).to_edge(DR)

        self.play(Write(name))
        self.play(
            DrawBorderThenFill(sq),
            run_time = 2)
        self.play(Create(tri))
        self.wait()