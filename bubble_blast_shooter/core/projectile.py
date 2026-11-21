"""Bubble Blast Shooter - Flying Bubble Projectile"""
import math
import pygame
from core.constants import (
    BUBBLE_RADIUS, SCREEN_WIDTH, MARGIN_LEFT,
    GRID_TOP_MARGIN, PROJECTILE_SPEED
)
from core.bubble import Bubble, get_bubble_surface

class Projectile:
    def __init__(self, x: float, y: float, angle_rad: float, color_id: int):
        self.x = x
        self.y = y
        self.vx = math.cos(angle_rad) * PROJECTILE_SPEED
        self.vy = math.sin(angle_rad) * PROJECTILE_SPEED
        self.color_id = color_id
        self.radius = BUBBLE_RADIUS
        self.alive = True
        self.wall_bounce_count = 0
        self.trail: list[tuple[float, float, float]] = []  # (x, y, alpha)

    def update(self, dt: float, sound_mgr=None) -> bool:
        if not self.alive:
            return False

        # Sub-stepping for ultra-accurate collision detection at high projectile speed
        steps = 4
        sub_dt = dt / steps

        left_wall = MARGIN_LEFT + self.radius
        right_wall = SCREEN_WIDTH - MARGIN_LEFT - self.radius

        for _ in range(steps):
            self.x += self.vx * sub_dt
            self.y += self.vy * sub_dt

            # Wall Ricochet Reflections
            if self.x <= left_wall:
                self.x = left_wall
                self.vx = abs(self.vx)
                self.wall_bounce_count += 1
                if sound_mgr:
                    sound_mgr.play("bounce")
            elif self.x >= right_wall:
                self.x = right_wall
                self.vx = -abs(self.vx)
                self.wall_bounce_count += 1
                if sound_mgr:
                    sound_mgr.play("bounce")

            # Ceiling hit check
            if self.y <= GRID_TOP_MARGIN + self.radius:
                self.y = GRID_TOP_MARGIN + self.radius
                self.alive = False
                break

        # Record trail
        self.trail.append((self.x, self.y, 1.0))
        self.trail = [(tx, ty, alpha - dt * 3.5) for (tx, ty, alpha) in self.trail if alpha > 0.05]

        return self.alive

    def draw(self, surface: pygame.Surface):
        # 1. Motion Trail
        for tx, ty, alpha in self.trail:
            r = int(self.radius * 0.7 * alpha)
            if r > 1:
                t_surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(t_surf, (255, 255, 255, int(60 * alpha)), (r + 1, r + 1), r)
                surface.blit(t_surf, (int(tx - r - 1), int(ty - r - 1)))

        # 2. Main 3D Bubble
        surf = get_bubble_surface(self.color_id, self.radius)
        surface.blit(surf, surf.get_rect(center=(int(self.x), int(self.y))))
