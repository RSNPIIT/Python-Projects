from manim import *
import numpy as np

class BlackHoleFPS(ThreeDScene):
    def construct(self):
        self.camera.background_color = BLACK

        # 1. Pure First-Person Camera looking straight down the Z-axis toward (0, 0, 0)
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES, zoom=1.0)

        Rs = 2.4  # Event Horizon radius

        # 2. 3D Starfield Surrounding the Black Hole
        rng = np.random.default_rng(42)
        stars = VGroup()
        for _ in range(140):
            vec = rng.normal(size=3)
            vec = vec / np.linalg.norm(vec) * rng.uniform(6.5, 16.0)
            star = Dot3D(point=vec, radius=rng.uniform(0.025, 0.05), color=WHITE)
            stars.add(star)

        # 3. Glowing Accretion Disk & Photon Ring
        accretion_rings = VGroup()
        ring_radii = np.linspace(Rs * 1.15, Rs * 2.6, 12)
        for i, rad in enumerate(ring_radii):
            opacity = 0.7 * (1.0 - i / len(ring_radii))
            color = interpolate_color(YELLOW, ORANGE, i / len(ring_radii))
            ring = Circle(radius=rad, color=color, stroke_width=3.5, stroke_opacity=opacity)
            ring.rotate(72 * DEGREES, axis=RIGHT)
            ring.rotate(18 * DEGREES, axis=UP)
            accretion_rings.add(ring)

        # 4. Singularity Core & Translucent Event Horizon Boundary
        singularity_core = Sphere(radius=0.25, resolution=(12, 12))
        singularity_core.set_color(RED_E)

        horizon_shell = Surface(
            lambda u, v: np.array([
                Rs * np.cos(u) * np.sin(v),
                Rs * np.sin(u) * np.sin(v),
                Rs * np.cos(v)
            ]),
            u_range=list((0, TAU)),
            v_range=list((0, PI)),
            resolution=(16, 16),
            fill_opacity=0.22,
            checkerboard_colors=[BLACK, GREY_E],
            stroke_color=YELLOW_E,
            stroke_width=0.6
        )

        # 5. 3D Spacetime Coordinate Cage (Visualizes the Time-Space Axis Flip in 3D FOV)
        # Blue rings = Radial Spatial slices (r); Green lines = Time flow (t)
        spacetime_cage = VGroup()
        for z_pos in np.linspace(-Rs * 1.5, Rs * 3.5, 10):
            slice_ring = Circle(radius=Rs * 1.8, color=BLUE_D, stroke_width=1.4, stroke_opacity=0.4)
            slice_ring.shift(OUT * z_pos)
            spacetime_cage.add(slice_ring)

        for angle in np.linspace(0, TAU, 10, endpoint=False):
            x_off = Rs * 1.8 * np.cos(angle)
            y_off = Rs * 1.8 * np.sin(angle)
            time_line = Line(
                start=np.array([x_off, y_off, Rs * 3.5]),
                end=np.array([x_off, y_off, -Rs * 1.5]),
                color=GREEN_D,
                stroke_width=1.4,
                stroke_opacity=0.4
            )
            spacetime_cage.add(time_line)

        world = VGroup(stars, accretion_rings, spacetime_cage, horizon_shell, singularity_core)
        self.add(world)

        # Start with the black hole ahead of the observer
        world.shift(IN * 11.0)

        # 6. Phase 1: Approaching the Supermassive Black Hole (r > Rs)
        self.play(
            world.animate.shift(OUT * 7.8),
            Rotate(accretion_rings, angle=PI * 0.6, axis=OUT, about_point=world.get_center()),
            run_time=4.0,
            rate_func=linear
        )

        # 7. Phase 2: Crossing the Event Horizon (r = Rs) -> THE TIME-SPACE AXIS FLIP
        self.move_camera(
            zoom=1.45,
            added_anims=[
                world.animate.shift(OUT * 1.5),
                Rotate(spacetime_cage, angle=90 * DEGREES, axis=RIGHT, about_point=singularity_core.get_center()),
                spacetime_cage.animate.set_color(RED_C),
                accretion_rings.animate.scale(0.55).set_color(BLUE_B),
                stars.animate.scale(0.65),
            ],
            run_time=2.5,
            rate_func=smooth
        )

        # 8. Phase 3: Inside the Event Horizon (r < Rs) -> Inevitable Fall to Singularity (r = 0)
        self.move_camera(
            zoom=2.6,
            added_anims=[
                world.animate.shift(OUT * 1.65),
                spacetime_cage.animate.scale(0.12),
                accretion_rings.animate.scale(0.25),
            ],
            run_time=2.5,
            rate_func=rush_into
        )

        # Total darkness upon reaching the singularity
        blackout = FullScreenRectangle(fill_color=BLACK, fill_opacity=1.0, stroke_width=0)
        self.add_fixed_in_frame_mobjects(blackout)
        self.play(FadeIn(blackout), run_time=0.4)
        self.wait(0.8)

