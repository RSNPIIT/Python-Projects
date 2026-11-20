from manim import *
import numpy as np

class SupermassiveBlackHoleInfall(Scene):
    def construct(self):
        # 1. Setup Spacetime Axes (Horizontal = Radial Distance r, Vertical = Ingoing Time t*)
        axes = Axes(
            x_range=list((0, 5, 1)),
            y_range=list((0, 6, 1)),
            x_length=7.2,
            y_length=5.6,
            axis_config={"color": GREY_B, "include_tip": True},
        ).to_edge(DOWN, buff=0.7).to_edge(LEFT, buff=0.9)

        x_label = axes.get_x_axis_label(Text("r (Radial Space)", font_size=20), edge=RIGHT, direction=DOWN)
        y_label = axes.get_y_axis_label(Text("t* (Time)", font_size=20), edge=UP, direction=LEFT)

        title = Text("Falling Into a Supermassive Black Hole", font_size=28).to_edge(UP, buff=0.25)
        self.add(title)
        self.play(Create(axes), Write(x_label), Write(y_label))

        # 2. Singularity (r = 0) and Event Horizon (r = Rs = 2.2)
        Rs = 2.2
        singularity_line = Line(axes.c2p(0, 0), axes.c2p(0, 6), color=RED_E, stroke_width=7)
        singularity_label = Text("Singularity (r=0)", font_size=16, color=RED_E).next_to(singularity_line, UP, buff=0.1)

        horizon_line = DashedLine(axes.c2p(Rs, 0), axes.c2p(Rs, 6), color=YELLOW, stroke_width=4)
        horizon_label = Text("Event Horizon (r=Rs)", font_size=16, color=YELLOW).next_to(horizon_line, UP, buff=0.1)

        interior_zone = Polygon(
            axes.c2p(0, 0), axes.c2p(Rs, 0), axes.c2p(Rs, 6), axes.c2p(0, 6),
            color=RED, fill_opacity=0.12, stroke_width=0
        )

        self.play(
            FadeIn(interior_zone),
            Create(singularity_line), Write(singularity_label),
            Create(horizon_line), Write(horizon_label)
        )

        # 3. ValueTracker for Astronaut's Radial Position r (from r = 4.6 down to r = 0.05)
        r_tracker = ValueTracker(4.6)

        # Smooth infall trajectory curve t*(r) in ingoing coordinates
        def get_time_from_r(r):
            progress = (4.6 - r) / 4.6
            return 0.4 + 5.2 * (progress ** 0.85)

        # Draw faint planned worldline preview
        worldline_preview = ParametricFunction(
            lambda r: axes.c2p(r, get_time_from_r(r)),
            t_range=list((0.05, 4.6)),
            color=GREY_D,
            stroke_width=2
        )
        self.add(worldline_preview)

        # 4. Dynamic Astronaut Dot, Traced Worldline, and Attached Light Cone
        astronaut = always_redraw(
            lambda: Dot(
                axes.c2p(r_tracker.get_value(), get_time_from_r(r_tracker.get_value())),
                color=WHITE,
                radius=0.08
            )
        )

        astronaut_tag = always_redraw(
            lambda: Text("Observer", font_size=16, color=WHITE).next_to(astronaut, RIGHT, buff=0.15)
        )

        traced_path = TracedPath(astronaut.get_center, stroke_color=ORANGE, stroke_width=4)

        def get_dynamic_light_cone():
            r_val = r_tracker.get_value()
            t_val = get_time_from_r(r_val)
            center = axes.c2p(r_val, t_val)
            scale = 0.55

            # Ingoing light ray always moves inward at -45 deg
            ingoing_vec = np.array([-1.0, 1.0, 0.0])
            ingoing_vec = ingoing_vec / np.linalg.norm(ingoing_vec) * scale

            # Outgoing light ray slope = 1 - Rs/r (tilts past vertical inside r < Rs)
            outgoing_slope = 1.0 - (Rs / max(r_val, 0.25))
            outgoing_vec = np.array([outgoing_slope, 1.0, 0.0])
            outgoing_vec = outgoing_vec / np.linalg.norm(outgoing_vec) * scale

            cone_color = BLUE if r_val > Rs else RED_B

            left_ray = Arrow(center, center + ingoing_vec, buff=0, color=cone_color, stroke_width=3, tip_length=0.14)
            right_ray = Arrow(center, center + outgoing_vec, buff=0, color=cone_color, stroke_width=3, tip_length=0.14)
            cone_fill = Polygon(
                center, center + ingoing_vec, center + outgoing_vec,
                color=cone_color, fill_opacity=0.35, stroke_width=0
            )
            return VGroup(cone_fill, left_ray, right_ray)

        dynamic_cone = always_redraw(get_dynamic_light_cone)

        # 5. Side Panel: Live Local Spacetime Frame & Status Readout
        panel = RoundedRectangle(corner_radius=0.15, width=4.6, height=4.4, color=TEAL).to_edge(RIGHT, buff=0.35).shift(DOWN * 0.2)
        panel_header = Text("Observer's Local Axes", font_size=20, color=TEAL).next_to(panel.get_top(), DOWN, buff=0.2)

        def get_status_text():
            r_val = r_tracker.get_value()
            if r_val > Rs + 0.05:
                return Text("OUTSIDE HORIZON (r > Rs)\n• Tidal forces gentle\n• Escape still possible\n• Time flows upward (t*)", font_size=15, color=GREEN_B, line_spacing=1.2)
            elif abs(r_val - Rs) <= 0.05:
                return Text("AT EVENT HORIZON (r = Rs)\n• Outgoing light freezes\n• Point of no return!", font_size=15, color=YELLOW, line_spacing=1.2)
            else:
                return Text("INSIDE HORIZON (r < Rs)\n• SPACE & TIME FLIPPED!\n• -r is now Future Time\n• Singularity is inevitable", font_size=15, color=RED_B, line_spacing=1.2)

        status_display = always_redraw(
            lambda: get_status_text().next_to(panel_header, DOWN, buff=0.25)
        )

        # Live Rotating Coordinate Gizmo inside the Side Panel
        gizmo_center = panel.get_center() + DOWN * 0.95 + LEFT * 0.3

        def get_local_axes_gizmo():
            r_val = r_tracker.get_value()
            transition = np.clip((Rs + 0.4 - r_val) / 0.8, 0.0, 1.0)
            angle = transition * (PI / 2)

            t_dir = np.array([-np.sin(angle), np.cos(angle), 0.0])
            r_dir = np.array([np.cos(angle), np.sin(angle), 0.0])

            t_vec = Arrow(gizmo_center, gizmo_center + t_dir * 0.95, buff=0, color=GREEN, stroke_width=4)
            r_vec = Arrow(gizmo_center, gizmo_center + r_dir * 0.95, buff=0, color=ORANGE, stroke_width=4)

            if transition < 0.5:
                t_lbl = Text("Time (t*)", font_size=15, color=GREEN).next_to(t_vec.get_end(), UP, buff=0.1)
                r_lbl = Text("Space (r)", font_size=15, color=ORANGE).next_to(r_vec.get_end(), RIGHT, buff=0.1)
            else:
                t_lbl = Text("Space (t*)", font_size=15, color=GREEN).next_to(t_vec.get_end(), LEFT, buff=0.1)
                r_lbl = Text("Future (-r)", font_size=15, color=ORANGE).next_to(r_vec.get_end(), UP, buff=0.1)

            return VGroup(t_vec, r_vec, t_lbl, r_lbl)

        local_gizmo = always_redraw(get_local_axes_gizmo)

        self.play(Create(panel), Write(panel_header))
        self.add(traced_path, dynamic_cone, astronaut, astronaut_tag, status_display, local_gizmo)
        self.wait(0.8)

        # 6. Animate the Fall
        self.play(r_tracker.animate.set_value(2.25), run_time=3.5, rate_func=linear)
        self.wait(0.5)

        # Cross the Event Horizon (triggers the 90-degree axis flip)
        self.play(r_tracker.animate.set_value(1.75), run_time=2.0, rate_func=smooth)
        self.wait(0.8)

        # Inexorable fall into the singularity r = 0
        self.play(r_tracker.animate.set_value(0.05), run_time=3.5, rate_func=rush_into)

        flash = Flash(axes.c2p(0, get_time_from_r(0.05)), color=RED, flash_radius=0.6)
        self.play(flash)
        self.wait(1.5)

