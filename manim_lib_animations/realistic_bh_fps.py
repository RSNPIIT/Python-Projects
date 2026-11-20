from manim import *
import numpy as np

class RealisticBlackHoleFPS(ThreeDScene):
    def construct(self):
        self.camera.background_color = BLACK

        # Pure First-Person FOV looking straight along -Z toward the singularity
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES, zoom=1.0)

        Rs = 2.3  # Event Horizon radius

        # 1. Deep 3D Starfield with Subtle Blueshift Potential
        rng = np.random.default_rng(108)
        stars = VGroup()
        for _ in range(180):
            vec = rng.normal(size=3)
            vec = vec / np.linalg.norm(vec) * rng.uniform(7.0, 18.0)
            star_color = interpolate_color(WHITE, BLUE_A, float(rng.uniform(0.0, 0.5)))
            star = Dot3D(point=vec, radius=float(rng.uniform(0.02, 0.048)), color=star_color)
            stars.add(star)

        # 2. Relativistic Beamed Accretion Disk (Segmented for Doppler Shift)
        # Left side (cos(angle) < 0) moves TOWARD viewer -> Bright Blue-White
        # Right side (cos(angle) > 0) moves AWAY from viewer -> Dim Red-Orange
        c_ice_blue = ManimColor("#A8F0FF")
        c_deep_red = ManimColor("#5C0A00")

        def create_beamed_disk(r_inner, r_outer, num_rings=10, num_sectors=36, tilt_x=76 * DEGREES, tilt_y=14 * DEGREES):
            disk_group = VGroup()
            radii = np.linspace(r_inner, r_outer, num_rings)
            d_theta = TAU / num_sectors

            for r_idx, rad in enumerate(radii):
                radial_falloff = 1.0 - (r_idx / num_rings) * 0.65
                for s in range(num_sectors):
                    theta_start = float(s * d_theta)
                    theta_mid = theta_start + d_theta / 2.0

                    # Doppler factor: +1 on approaching left side, -1 on receding right side
                    doppler = float(-np.cos(theta_mid))

                    if doppler >= 0:
                        # Approaching plasma: intense blue-white beaming
                        seg_color = interpolate_color(YELLOW_A, c_ice_blue, float(doppler ** 0.7))
                        seg_color = interpolate_color(seg_color, WHITE, float(doppler ** 1.6))
                        stroke_w = float((2.2 + 3.8 * doppler) * radial_falloff)
                        opacity = float(min(0.95, (0.45 + 0.55 * doppler) * radial_falloff))
                    else:
                        # Receding plasma: redshifted and dimmed
                        rec = float(abs(doppler))
                        seg_color = interpolate_color(ORANGE, c_deep_red, float(rec ** 0.8))
                        stroke_w = float(max(0.8, (2.2 - 1.3 * rec) * radial_falloff))
                        opacity = float(max(0.12, (0.45 - 0.32 * rec) * radial_falloff))

                    arc = Arc(
                        radius=float(rad),
                        start_angle=theta_start,
                        angle=float(d_theta * 1.05),
                        color=seg_color,
                        stroke_width=stroke_w,
                        stroke_opacity=opacity
                    )
                    disk_group.add(arc)

            disk_group.rotate(tilt_x, axis=RIGHT)
            disk_group.rotate(tilt_y, axis=UP)
            return disk_group

        main_disk = create_beamed_disk(Rs * 1.18, Rs * 2.9, num_rings=10, num_sectors=36)

        # 3. Gravitationally Lensed Secondary Halo (Light bent over & under the shadow)
        lensed_halo = create_beamed_disk(
            Rs * 1.06, Rs * 1.45,
            num_rings=5, num_sectors=32,
            tilt_x=12 * DEGREES, tilt_y=14 * DEGREES
        )

        # 4. Relativistic Polar Jets (Erupting perpendicular to the accretion disk)
        jets = VGroup()
        for direction in [1, -1]:
            for j in range(5):
                jet_len = Rs * (4.5 - j * 0.6)
                jet_line = Line(
                    start=ORIGIN,
                    end=np.array([0.0, direction * jet_len, 0.0]),
                    color=interpolate_color(BLUE_C, WHITE, j / 5.0),
                    stroke_width=float(4.5 - j * 0.7),
                    stroke_opacity=float(0.18 + j * 0.08)
                )
                jets.add(jet_line)
        jets.rotate(76 * DEGREES, axis=RIGHT)
        jets.rotate(14 * DEGREES, axis=UP)

        # 5. Photon Sphere Ring & Event Horizon Shadow
        photon_ring = Circle(radius=Rs * 1.04, color=ManimColor("#BCEEFF"), stroke_width=2.5, stroke_opacity=0.85)
        photon_ring.rotate(14 * DEGREES, axis=UP)

        horizon_sphere = Sphere(radius=Rs, resolution=(16, 16))
        horizon_sphere.set_color(BLACK)
        horizon_sphere.set_opacity(0.92)

        # 6. 3D Spacetime Coordinate Cage with Kerr Frame-Dragging Twist
        spacetime_cage = VGroup()
        for z_pos in np.linspace(-Rs * 1.4, Rs * 3.2, 8):
            ring = Circle(radius=Rs * 1.65, color=BLUE_E, stroke_width=1.1, stroke_opacity=0.28)
            ring.shift(OUT * float(z_pos))
            spacetime_cage.add(ring)

        for angle in np.linspace(0, TAU, 8, endpoint=False):
            # Helical twist shows frame-dragging of spacetime near the spinning black hole
            pts = []
            for z_val in np.linspace(-Rs * 1.4, Rs * 3.2, 12):
                twist = 0.25 * (1.0 - (z_val + Rs * 1.4) / (Rs * 4.6))
                a = angle + twist
                pts.append(np.array([Rs * 1.65 * np.cos(a), Rs * 1.65 * np.sin(a), z_val]))
            spiral_line = VMobject(color=TEAL_E, stroke_width=1.2, stroke_opacity=0.32)
            spiral_line.set_points_smoothly(pts)
            spacetime_cage.add(spiral_line)

        singularity_core = Dot3D(point=ORIGIN, radius=0.18, color=RED_E)

        world = VGroup(
            stars,
            spacetime_cage,
            jets,
            horizon_sphere,
            photon_ring,
            lensed_halo,
            main_disk,
            singularity_core
        )
        self.add(world)

        # Position black hole ahead of camera
        world.shift(IN * 12.5)

        # 7. Phase 1: Initial Cruise & Gravitational Acceleration (r > 1.5 Rs)
        self.play(
            world.animate.shift(OUT * 8.2),
            Rotate(main_disk, angle=PI * 0.85, axis=np.array([0.2, 0.95, 0.25]), about_point=singularity_core.get_center()),
            Rotate(lensed_halo, angle=PI * 0.5, axis=OUT, about_point=singularity_core.get_center()),
            run_time=4.2,
            rate_func=lambda t: t ** 1.35
        )

        # 8. Phase 2: Photon Sphere & Event Horizon Crossing (r = Rs) -> THE TIME-SPACE AXIS FLIP
        c_horizon_blue = ManimColor("#B8F2FF")
        c_photon_cyan = ManimColor("#80E5FF")
        c_star_blue = ManimColor("#CCEFFF")

        self.move_camera(
            zoom=1.55,
            added_anims=[
                world.animate.shift(OUT * 2.1),
                horizon_sphere.animate.set_opacity(0.15),
                Rotate(spacetime_cage, angle=90 * DEGREES, axis=RIGHT, about_point=singularity_core.get_center()),
                spacetime_cage.animate.set_color(RED_D).set_stroke(opacity=0.5),
                main_disk.animate.scale(0.52).set_color(c_horizon_blue),
                lensed_halo.animate.scale(0.58).set_color(WHITE),
                photon_ring.animate.scale(0.62).set_color(c_photon_cyan),
                stars.animate.scale(0.55).set_color(c_star_blue),
                jets.animate.scale(0.5),
            ],
            run_time=2.4,
            rate_func=smooth
        )

        # 9. Phase 3: Interior Plunge (r < Rs -> r = 0)
        self.move_camera(
            zoom=3.2,
            added_anims=[
                world.animate.shift(OUT * 2.2),
                spacetime_cage.animate.scale(0.08),
                main_disk.animate.scale(0.15),
                lensed_halo.animate.scale(0.15),
                photon_ring.animate.scale(0.15),
                stars.animate.scale(0.2),
                jets.animate.scale(0.1),
            ],
            run_time=2.0,
            rate_func=rush_into
        )

        # Singularity impact blackout
        blackout = FullScreenRectangle(fill_color=BLACK, fill_opacity=1.0, stroke_width=0)
        self.add_fixed_in_frame_mobjects(blackout)
        self.play(FadeIn(blackout), run_time=0.35)
        self.wait(0.7)

