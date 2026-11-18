from manim import *
import numpy as np

class BlackHoleSpacetimeFlip(Scene):
    def construct(self):
        # 1. Setup Spacetime Axes (Horizontal = Radial Space r, Vertical = Time ct)
        axes = Axes(
            x_range=[0, 5, 1],
            y_range=[0, 5, 1],
            x_length=7,
            y_length=5.5,
            axis_config={"color": GREY_B, "include_tip": True},
        ).to_edge(DOWN, buff=0.8).to_edge(LEFT, buff=1.0)

        x_label = axes.get_x_axis_label(MathTex("r \\text{ (Space)}"), edge=RIGHT, direction=DOWN)
        y_label = axes.get_y_axis_label(MathTex("ct \\text{ (Time)}"), edge=UP, direction=LEFT)

        title = Title("Black Hole Event Horizon: Time–Space Axis Flip", font_size=36)
        self.add(title)
        self.play(Create(axes), Write(x_label), Write(y_label))

        # 2. Plot Singularity (r = 0) and Event Horizon (r = Rs = 2.0)
        Rs = 2.0
        singularity_line = DashedLine(
            start=axes.c2p(0, 0),
            end=axes.c2p(0, 5),
            color=RED_E,
            stroke_width=6
        )
        singularity_label = Text("Singularity (r = 0)", font_size=20, color=RED_E).next_to(singularity_line, UP)

        horizon_line = DashedLine(
            start=axes.c2p(Rs, 0),
            end=axes.c2p(Rs, 5),
            color=YELLOW,
            stroke_width=4
        )
        horizon_label = Text("Event Horizon (r = Rs)", font_size=20, color=YELLOW).next_to(horizon_line, UP)

        # Shade the interior region (r < Rs)
        interior_region = Polygon(
            axes.c2p(0, 0), axes.c2p(Rs, 0), axes.c2p(Rs, 5), axes.c2p(0, 5),
            color=RED, fill_opacity=0.12, stroke_width=0
        )

        self.play(
            FadeIn(interior_region),
            Create(singularity_line), Write(singularity_label),
            Create(horizon_line), Write(horizon_label)
        )

        # 3. Helper Function to Create Tilted Light Cones in Schwarzschild Coordinates
        def create_light_cone(r_val, t_val, scale=0.45):
            center = axes.c2p(r_val, t_val)
            
            # Coordinate speed of light: dr/dt = +/- (1 - Rs/r)
            # In standard Schwarzschild coords, cones narrow at Rs; 
            # using Eddington-Finkelstein tilt angle for visual clarity across the horizon:
            # Angle of ingoing ray = -45 deg; outgoing ray tilts inward as r decreases
            outgoing_slope = 1.0 - (Rs / max(r_val, 0.25))  # >0 outside, 0 at Rs, <0 inside
            
            # Left (ingoing) ray always points inward toward r=0
            ingoing_vec = np.array([-1.0, 1.0, 0.0])
            ingoing_vec = ingoing_vec / np.linalg.norm(ingoing_vec) * scale

            # Right (outgoing) ray tilts across the vertical time axis
            outgoing_vec = np.array([outgoing_slope, 1.0, 0.0])
            outgoing_vec = outgoing_vec / np.linalg.norm(outgoing_vec) * scale

            left_ray = Arrow(center, center + ingoing_vec, buff=0, color=BLUE_C, stroke_width=3, tip_length=0.15)
            right_ray = Arrow(center, center + outgoing_vec, buff=0, color=BLUE_C, stroke_width=3, tip_length=0.15)
            
            cone_fill = Polygon(
                center,
                center + ingoing_vec,
                center + outgoing_vec,
                color=BLUE,
                fill_opacity=0.35,
                stroke_width=0
            )
            dot = Dot(center, color=WHITE, radius=0.05)
            return VGroup(cone_fill, left_ray, right_ray, dot)

        # 4. Animate Light Cones Crossing the Horizon
        radii = [4.2, 3.0, 2.0, 1.3, 0.7]
        cones = VGroup(*[create_light_cone(r, 1.8) for r in radii])

        cone_caption = Text("Light cones tip inward as gravity increases", font_size=22, color=BLUE_B).to_edge(RIGHT).shift(UP * 1.5)
        self.play(Write(cone_caption))
        for cone in cones:
            self.play(FadeIn(cone), run_time=0.5)

        self.wait(1)

        # 5. Animate the Time-Space Axis Flip Inside r < Rs
        flip_box = RoundedRectangle(corner_radius=0.15, width=4.5, height=3.2, color=TEAL).to_edge(RIGHT, buff=0.5).shift(DOWN * 0.8)
        flip_title = Text("Inside Event Horizon (r < Rs)", font_size=22, color=TEAL).next_to(flip_box.get_top(), DOWN, buff=0.2)

        # Mini axes inside the callout box that physically rotate/swap
        mini_origin = flip_box.get_center() + DOWN * 0.3
        t_arrow = Arrow(mini_origin, mini_origin + UP * 1.1, buff=0, color=GREEN)
        r_arrow = Arrow(mini_origin, mini_origin + RIGHT * 1.1, buff=0, color=ORANGE)
        t_text = MathTex("t \\text{ (Timelike)}", color=GREEN, font_size=24).next_to(t_arrow, UP, buff=0.1)
        r_text = MathTex("r \\text{ (Spacelike)}", color=ORANGE, font_size=24).next_to(r_arrow, RIGHT, buff=0.1)

        self.play(Create(flip_box), Write(flip_title))
        self.play(GrowArrow(t_arrow), Write(t_text), GrowArrow(r_arrow), Write(r_text))
        self.wait(0.8)

        # Swap the roles: r becomes future-directed timelike (-r), t becomes spacelike
        new_r_arrow = Arrow(mini_origin, mini_origin + UP * 1.1, buff=0, color=ORANGE)
        new_t_arrow = Arrow(mini_origin, mini_origin + RIGHT * 1.1, buff=0, color=GREEN)
        new_r_text = MathTex("-r \\text{ (Future Time)}", color=ORANGE, font_size=24).next_to(new_r_arrow, UP, buff=0.1)
        new_t_text = MathTex("t \\text{ (Space)}", color=GREEN, font_size=24).next_to(new_t_arrow, RIGHT, buff=0.1)

        explanation = Text(
            "Moving forward in time\nnow means decreasing r\n(falling to singularity).",
            font_size=18,
            color=WHITE,
            line_spacing=1.2
        ).next_to(flip_box, DOWN, buff=0.25)

        self.play(
            Transform(r_arrow, new_r_arrow),
            Transform(t_arrow, new_t_arrow),
            Transform(r_text, new_r_text),
            Transform(t_text, new_t_text),
            Write(explanation),
            run_time=1.8
        )
        self.wait(2)

