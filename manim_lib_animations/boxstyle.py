from manim import *

# A class is needed in Manim (both in GL and CE) as it was written in OOPS by 3Blue1Brown
class Box(Scene):
    def construct(self):
        tex = Text("This is my Box Animation in manim").scale(0.8)
        self.play(
            Write(tex)
        )
        self.play(
            Flash(tex[-1].get_top(), color = GREEN, line_length = 0.8, num_lines = 15),
            Flash(tex[0].get_bottom(), color = GREEN, line_length = 0.8, num_lines = 15)
        )
        group = VGroup(*[
            Rectangle(height = 0.5 , width = 0.5 , fill_opacity = 1)
            for _ in range(5)    
        ])
        group.arrange()
        group.set_color_by_gradient(RED , ORANGE , YELLOW_C , PURE_GREEN)

        self.play(ReplacementTransform(tex , group))
        s1 = SurroundingRectangle(group , color = WHITE)
        s2 = SurroundingRectangle(s1 , color = ORANGE)
        s3 = SurroundingRectangle(s2 , color = YELLOW_C)

        self.play(
            Write(s1),
            Write(s2),
            Write(s3)
        )

        t1 = Text("1    2    3    4    5").next_to(s3 , UP, buff = 0.55).scale(0.8)
        
        self.play(Write(t1), run_time = 0.45)
        for i in range(5):
            self.play(
                Indicate(t1[i] , color = RED , scale_factor = 0.8),
                Indicate(group[i], color = YELLOW_C ,scale_factor = 0.9)
            )

        d = Dot(color = RED)
        grp = VGroup(group, t1, s1, s2, s3)
        self.play(
            ReplacementTransform(grp , d)
        )
        self.play(d.animate.scale(150))
        self.play(FadeOut(d))
        self.wait(3)