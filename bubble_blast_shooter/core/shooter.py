"""Bubble Blast Shooter - Launcher, Aim Raycaster & Ammo Display"""
import math
import random
import pygame
from core.constants import (
    SHOOTER_X, SHOOTER_Y, SHOOTER_RING_RADIUS,
    BUBBLE_RADIUS, MARGIN_LEFT, SCREEN_WIDTH,
    GRID_TOP_MARGIN, COLOR_TEXT_WHITE, COLOR_ACCENT,
    BUBBLE_COLORS
)
from core.bubble import get_bubble_surface
from core.grid import BubbleGrid

class Shooter:
    def __init__(self, start_ammo: int = 45):
        self.x = float(SHOOTER_X)
        self.y = float(SHOOTER_Y)
        self.ammo = start_ammo
        self.current_color = 0
        self.next_color = 1
        self.aim_angle = -math.pi / 2  # Straight up

        # Next bubble preview position (resting on right flank of pedestal)
        self.preview_x = self.x + 46.0
        self.preview_y = self.y + 12.0
        self.preview_radius = 16

        # Swapping animation / pulse
        self.pulse_timer = 0.0

    def reload(self, available_colors: list[int]):
        """Refills current and next bubble colors from colors currently present on the grid."""
        if not available_colors:
            available_colors = [0, 1, 2, 3, 4, 5]

        self.current_color = self.next_color
        self.next_color = random.choice(available_colors)
        if self.current_color not in available_colors:
            self.current_color = random.choice(available_colors)

    def init_colors(self, available_colors: list[int]):
        if not available_colors:
            available_colors = [0, 1, 2, 3, 4, 5]
        self.current_color = random.choice(available_colors)
        self.next_color = random.choice(available_colors)

    def swap_bubbles(self):
        """Swaps current active bubble with the previewed next bubble."""
        self.current_color, self.next_color = self.next_color, self.current_color

    def update_aim(self, mouse_pos: tuple[int, int]):
        mx, my = mouse_pos
        dx = mx - self.x
        dy = my - (self.y - 12)  # Aim from top of pedestal

        angle = math.atan2(dy, dx)
        # Constrain angle: cannot shoot downwards or strictly horizontally
        min_angle = -math.pi + 0.18  # ~ -170 deg
        max_angle = -0.18            # ~ -10 deg

        if angle > 0:
            angle = min_angle if dx < 0 else max_angle
        else:
            angle = max(min_angle, min(max_angle, angle))

        self.aim_angle = angle

    def calculate_trajectory(self, grid: BubbleGrid) -> list[tuple[float, float]]:
        """
        Raycasts the laser trajectory with wall reflections until ceiling or bubble collision.
        Returns a list of sampled points along the laser line.
        """
        points = []
        curr_x = self.x
        curr_y = self.y - 14.0
        vx = math.cos(self.aim_angle)
        vy = math.sin(self.aim_angle)

        left_wall = MARGIN_LEFT + BUBBLE_RADIUS
        right_wall = SCREEN_WIDTH - MARGIN_LEFT - BUBBLE_RADIUS

        step_dist = 6.0
        max_steps = 260

        for _ in range(max_steps):
            points.append((curr_x, curr_y))
            curr_x += vx * step_dist
            curr_y += vy * step_dist

            # Wall Reflection
            if curr_x <= left_wall:
                curr_x = left_wall
                vx = -vx
            elif curr_x >= right_wall:
                curr_x = right_wall
                vx = -vx

            # Collision with Ceiling
            if curr_y <= GRID_TOP_MARGIN + BUBBLE_RADIUS:
                points.append((curr_x, curr_y))
                break

            # Collision with any Bubble in the grid
            if grid.check_collision_with_bubble(curr_x, curr_y, BUBBLE_RADIUS * 0.9):
                points.append((curr_x, curr_y))
                break

        return points

    def draw(self, surface: pygame.Surface, font_ammo: pygame.font.Font, grid: BubbleGrid):
        # 1. Draw Glowing Laser Trajectory Beam
        traj = self.calculate_trajectory(grid)
        if len(traj) > 1:
            # Subtle neon laser glow
            aim_color = BUBBLE_COLORS.get(self.current_color, (100, 200, 255))
            glow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

            # Draw dotted energetic laser dots
            for idx in range(0, len(traj), 3):
                pt = traj[idx]
                pygame.draw.circle(glow_surf, (*aim_color, 110), (int(pt[0]), int(pt[1])), 4)
                pygame.draw.circle(glow_surf, (255, 255, 255, 210), (int(pt[0]), int(pt[1])), 2)

            # Impact Starburst Halo at trajectory endpoint (just like screenshot)
            end_x, end_y = traj[-1]
            pygame.draw.circle(glow_surf, (*aim_color, 160), (int(end_x), int(end_y)), BUBBLE_RADIUS + 6)
            pygame.draw.circle(glow_surf, (255, 255, 255, 230), (int(end_x), int(end_y)), BUBBLE_RADIUS - 4)

            surface.blit(glow_surf, (0, 0))

        # 2. Sleek Dark Glass Launcher Pedestal
        ring_cx = int(self.x)
        ring_cy = int(self.y + 14)
        r = SHOOTER_RING_RADIUS

        # Pedestal outer ring
        pygame.draw.circle(surface, (16, 22, 38), (ring_cx, ring_cy), r)
        pygame.draw.circle(surface, (255, 255, 255), (ring_cx, ring_cy), r, width=3)
        pygame.draw.circle(surface, (45, 60, 95), (ring_cx, ring_cy), r - 4, width=1)

        # Ammo Count Display Inside Pedestal (Matching screenshot e.g. "42")
        ammo_str = str(max(0, self.ammo))
        txt = font_ammo.render(ammo_str, True, COLOR_TEXT_WHITE)
        surface.blit(txt, txt.get_rect(center=(ring_cx, ring_cy)))

        # 3. Current Loaded Bubble (resting at the top of the ring)
        b_curr = get_bubble_surface(self.current_color, BUBBLE_RADIUS)
        surface.blit(b_curr, b_curr.get_rect(center=(ring_cx, ring_cy - 24)))

        # 4. Next Upcoming Bubble Preview (resting on bottom right)
        px = int(self.preview_x)
        py = int(self.preview_y)
        pr = self.preview_radius

        # Soft shadow & halo for preview
        pygame.draw.circle(surface, (14, 18, 30), (px, py), pr + 2)
        pygame.draw.circle(surface, (255, 255, 255, 120), (px, py), pr + 2, width=1)
        b_next = get_bubble_surface(self.next_color, pr)
        surface.blit(b_next, b_next.get_rect(center=(px, py)))
