"""Archer Bubble Blast - Power-Up Drops"""
import math
import pygame
from core.constants import PowerUpType, ARENA_FLOOR

class PowerUp:
    def __init__(self, x: float, y: float, ptype: str):
        self.x = x
        self.y = y
        self.type = ptype
        self.radius = 16.0
        self.vy = 120.0
        self.time_alive = 0.0
        self.alive = True

    @property
    def color(self) -> tuple[int, int, int]:
        return {
            PowerUpType.DOUBLE_ARROW: (255, 205, 50),
            PowerUpType.SHIELD: (80, 225, 255),
            PowerUpType.SLOW_MO: (180, 100, 255),
            PowerUpType.DYNAMITE: (255, 60, 70),
            PowerUpType.EXTRA_LIFE: (255, 80, 140),
        }.get(self.type, (255, 255, 255))

    @property
    def label(self) -> str:
        return {
            PowerUpType.DOUBLE_ARROW: "2X",
            PowerUpType.SHIELD: "SHIELD",
            PowerUpType.SLOW_MO: "SLOW",
            PowerUpType.DYNAMITE: "TNT",
            PowerUpType.EXTRA_LIFE: "+1 LIFE",
        }.get(self.type, "PWR")

    def update(self, dt: float) -> bool:
        self.time_alive += dt
        self.y += self.vy * dt
        # Stop at floor
        if self.y >= ARENA_FLOOR - self.radius:
            self.y = ARENA_FLOOR - self.radius
            self.vy = 0.0

        # Disappear after 10 seconds if not collected
        if self.time_alive > 10.0:
            self.alive = False

        return self.alive

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        cx = int(self.x)
        cy = int(self.y)
        r = int(self.radius)

        pulse = 1.0 + 0.12 * math.sin(self.time_alive * 8.0)
        pr = int(r * pulse)

        # Glowing outer halo
        halo_surf = pygame.Surface((pr * 2 + 6, pr * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(halo_surf, (*self.color, 70), (pr + 3, pr + 3), pr + 2)
        surface.blit(halo_surf, (cx - pr - 3, cy - pr - 3))

        # Main capsule body
        pygame.draw.circle(surface, (20, 26, 40), (cx, cy), pr)
        pygame.draw.circle(surface, self.color, (cx, cy), pr, width=2)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), pr - 3, width=1)

        # Label Text
        txt = font.render(self.label, True, (255, 255, 255))
        surface.blit(txt, txt.get_rect(center=(cx, cy)))
