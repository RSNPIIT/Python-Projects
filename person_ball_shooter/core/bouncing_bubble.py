"""Archer Bubble Blast - Physics-Based Bouncing Bubble Entity"""
import math
import pygame
from core.constants import (
    ARENA_LEFT, ARENA_RIGHT, ARENA_TOP, ARENA_FLOOR,
    GRAVITY, BUBBLE_PROPERTIES
)

class BouncingBubble:
    def __init__(self, x: float, y: float, size: int, vx: float = 160.0, vy: float = 0.0):
        self.x = x
        self.y = y
        self.size = size
        self.vx = vx
        self.vy = vy

        props = BUBBLE_PROPERTIES[size]
        self.radius = props["radius"]
        self.bounce_vy = props["bounce_vy"]
        self.color = props["color"]
        self.points = props["points"]
        
        self.anim_time = 0.0
        self.alive = True

    def split(self) -> list["BouncingBubble"]:
        """
        Splits this bubble into two smaller bubbles.
        Returns empty list if this was the smallest bubble (popped completely).
        """
        self.alive = False
        if self.size <= 1:
            return []

        new_size = self.size - 1
        speed_boost = 1.08
        new_vx = abs(self.vx) * speed_boost
        upward_pop = -260.0

        b1 = BouncingBubble(self.x - 12, self.y, new_size, vx=-new_vx, vy=upward_pop)
        b2 = BouncingBubble(self.x + 12, self.y, new_size, vx=new_vx, vy=upward_pop)
        return [b1, b2]

    def update(self, dt: float, sound_mgr=None):
        self.anim_time += dt

        # Apply gravity
        self.vy += GRAVITY * dt

        # Apply velocity
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Left / Right Wall Bounces
        if self.x - self.radius < ARENA_LEFT:
            self.x = ARENA_LEFT + self.radius
            self.vx = abs(self.vx)
        elif self.x + self.radius > ARENA_RIGHT:
            self.x = ARENA_RIGHT - self.radius
            self.vx = -abs(self.vx)

        # Ceiling Bounce
        if self.y - self.radius < ARENA_TOP:
            self.y = ARENA_TOP + self.radius
            self.vy = abs(self.vy)

        # Floor Bounce
        if self.y + self.radius >= ARENA_FLOOR:
            self.y = ARENA_FLOOR - self.radius
            self.vy = self.bounce_vy
            if sound_mgr and self.size >= 3:
                sound_mgr.play("bounce")

    def draw(self, surface: pygame.Surface):
        cx = int(self.x)
        cy = int(self.y)
        r = int(self.radius)

        # 1. Subtle Outer Glow Halo
        halo_r = r + 8
        halo_surf = pygame.Surface((halo_r * 2 + 4, halo_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(halo_surf, (*self.color, 45), (halo_r + 2, halo_r + 2), halo_r)
        surface.blit(halo_surf, (cx - halo_r - 2, cy - halo_r - 2))

        # 2. Main Bubble Sphere
        pygame.draw.circle(surface, self.color, (cx, cy), r)

        # 3. Inner Dark Shading (Lower-Right)
        shade_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(shade_surf, (0, 0, 0, 50), (r + 3, r + 3), r - 3)
        surface.blit(shade_surf, (cx - r, cy - r))

        # 4. Glossy Specular Crescent (Upper-Left Sheen)
        sheen_w = int(r * 0.9)
        sheen_h = int(r * 0.55)
        sheen_x = cx - int(r * 0.6)
        sheen_y = cy - int(r * 0.7)
        sheen_surf = pygame.Surface((sheen_w, sheen_h), pygame.SRCALPHA)
        pygame.draw.ellipse(sheen_surf, (255, 255, 255, 140), (0, 0, sheen_w, sheen_h))
        surface.blit(sheen_surf, (sheen_x, sheen_y))

        # 5. Crisp Specular Glint Dot
        dot_x = cx - int(r * 0.35)
        dot_y = cy - int(r * 0.45)
        pygame.draw.circle(surface, (255, 255, 255), (dot_x, dot_y), max(2, int(r * 0.15)))

        # 6. Smooth Outer Glass Rim
        pygame.draw.circle(surface, (255, 255, 255, 120), (cx, cy), r, width=1)
