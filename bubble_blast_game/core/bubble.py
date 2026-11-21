"""Bubble Blast - Glossy Liquid Bubble Entity"""
import math
import pygame
from core.constants import (
    STAGE_EMPTY, STAGE_BLUE, STAGE_YELLOW, STAGE_GREEN, STAGE_RED,
    BUBBLE_COLORS
)

class Bubble:
    def __init__(self, col: int, row: int, center_x: float, center_y: float, stage: int = STAGE_EMPTY):
        self.col = col
        self.row = row
        self.x = center_x
        self.y = center_y
        self.stage = stage
        self.base_radius = 26.0
        
        # Animations
        self.anim_time = col * 0.4 + row * 0.3
        self.wobble_scale_x = 1.0
        self.wobble_scale_y = 1.0
        self.hit_timer = 0.0

    @property
    def is_alive(self) -> bool:
        return self.stage != STAGE_EMPTY

    @property
    def color(self) -> tuple[int, int, int]:
        return BUBBLE_COLORS.get(self.stage, (200, 200, 200))

    def hit(self) -> bool:
        """
        Takes a hit from tap or projectile.
        Returns True if the bubble POPS (was STAGE_RED), False if it advanced a stage.
        """
        self.hit_timer = 0.15
        if self.stage == STAGE_RED:
            self.stage = STAGE_EMPTY
            return True
        elif self.stage == STAGE_GREEN:
            self.stage = STAGE_RED
            return False
        elif self.stage == STAGE_YELLOW:
            self.stage = STAGE_GREEN
            return False
        elif self.stage == STAGE_BLUE:
            self.stage = STAGE_YELLOW
            return False
        return False

    def update(self, dt: float):
        if not self.is_alive:
            return

        self.anim_time += dt

        # Squish bounce on hit
        if self.hit_timer > 0:
            self.hit_timer -= dt
            factor = math.sin(self.hit_timer * 35.0) * 0.25
            self.wobble_scale_x = 1.0 + factor
            self.wobble_scale_y = 1.0 - factor
        else:
            # Idle gentle breathing
            wobble = math.sin(self.anim_time * 3.5) * 0.04
            self.wobble_scale_x = 1.0 + wobble
            self.wobble_scale_y = 1.0 - wobble

    def draw(self, surface: pygame.Surface):
        if not self.is_alive:
            return

        col = self.color
        rx = int(self.base_radius * self.wobble_scale_x)
        ry = int(self.base_radius * self.wobble_scale_y)
        cx, cy = int(self.x), int(self.y)

        # 1. Red Bubble Energetic Pulsing Glow
        if self.stage == STAGE_RED:
            pulse = 1.0 + 0.15 * math.sin(self.anim_time * 8.0)
            halo_r = int((rx + 6) * pulse)
            halo_surf = pygame.Surface((halo_r * 2 + 4, halo_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(halo_surf, (*col, 65), (halo_r + 2, halo_r + 2), halo_r)
            surface.blit(halo_surf, (cx - halo_r - 2, cy - halo_r - 2))

        # 2. Main Bubble Body
        bubble_rect = pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2)
        pygame.draw.ellipse(surface, col, bubble_rect)

        # 3. Inner Dark Shading (Lower-Right Gradient)
        shade_surf = pygame.Surface((rx * 2, ry * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shade_surf, (0, 0, 0, 45), (4, 4, rx * 2 - 6, ry * 2 - 6))
        surface.blit(shade_surf, (cx - rx, cy - ry))

        # 4. Glossy Specular Highlight (Upper-Left Glass Sheen)
        sheen_w = int(rx * 0.9)
        sheen_h = int(ry * 0.55)
        sheen_x = cx - int(rx * 0.6)
        sheen_y = cy - int(ry * 0.7)
        sheen_surf = pygame.Surface((sheen_w, sheen_h), pygame.SRCALPHA)
        pygame.draw.ellipse(sheen_surf, (255, 255, 255, 140), (0, 0, sheen_w, sheen_h))
        surface.blit(sheen_surf, (sheen_x, sheen_y))

        # 5. Crisp Micro Glint (Bright White Specular Dot)
        dot_x = cx - int(rx * 0.35)
        dot_y = cy - int(ry * 0.45)
        pygame.draw.circle(surface, (255, 255, 255), (dot_x, dot_y), max(2, int(rx * 0.12)))

        # 6. Subtle Perimeter Rim
        pygame.draw.ellipse(surface, (255, 255, 255, 110), bubble_rect, width=1)
