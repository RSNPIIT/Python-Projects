"""Bubble Blast - 4-Direction Plasma Darts"""
import pygame
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, PROJECTILE_SPEED

class Projectile:
    def __init__(self, x: float, y: float, dir_x: int, dir_y: int, color: tuple[int, int, int] = (255, 75, 95)):
        self.x = x
        self.y = y
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.color = color
        self.speed = PROJECTILE_SPEED
        self.radius = 5.0
        self.alive = True
        self.trail_positions: list[tuple[float, float]] = []

    def update(self, dt: float) -> bool:
        # Record trail
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > 5:
            self.trail_positions.pop(0)

        self.x += self.dir_x * self.speed * dt
        self.y += self.dir_y * self.speed * dt

        # Out of bounds check
        if self.x < -30 or self.x > SCREEN_WIDTH + 30 or self.y < -30 or self.y > SCREEN_HEIGHT + 30:
            self.alive = False

        return self.alive

    def draw(self, surface: pygame.Surface):
        # 1. Glowing Trail Behind Dart
        for i, (tx, ty) in enumerate(self.trail_positions):
            alpha = int(180 * (i + 1) / (len(self.trail_positions) + 1))
            tr = max(2, int(self.radius * (i + 1) / len(self.trail_positions)))
            tsurf = pygame.Surface((tr * 2, tr * 2), pygame.SRCALPHA)
            pygame.draw.circle(tsurf, (*self.color, alpha), (tr, tr), tr)
            surface.blit(tsurf, (tx - tr, ty - tr))

        # 2. Plasma Dart Core
        cx, cy = int(self.x), int(self.y)
        pygame.draw.circle(surface, self.color, (cx, cy), int(self.radius + 2))
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), int(self.radius))
