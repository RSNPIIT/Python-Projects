"""Block Blast - PowerUp Orbs"""
import math
import pygame
from core.constants import PowerUpType, SCREEN_HEIGHT

class PowerUp:
    def __init__(self, x: float, y: float, powerup_type: str):
        self.x = x
        self.y = y
        self.type = powerup_type
        self.radius = 16
        self.vy = 85.0  # Drift downward speed
        self.time_alive = 0.0

    @property
    def color(self) -> tuple[int, int, int]:
        return {
            PowerUpType.SPREAD_SHOT: (255, 180, 50),
            PowerUpType.PIERCE: (50, 220, 255),
            PowerUpType.RAPID_FIRE: (255, 70, 160),
            PowerUpType.BOMB: (255, 60, 60),
            PowerUpType.FREEZE: (100, 240, 220),
        }.get(self.type, (255, 255, 255))

    @property
    def label(self) -> str:
        return {
            PowerUpType.SPREAD_SHOT: "3X",
            PowerUpType.PIERCE: "⚡",
            PowerUpType.RAPID_FIRE: ">>",
            PowerUpType.BOMB: "💣",
            PowerUpType.FREEZE: "❄",
        }.get(self.type, "?")

    def update(self, dt: float) -> bool:
        self.time_alive += dt
        self.y += self.vy * dt
        return self.y < SCREEN_HEIGHT + 30

    def draw(self, surface: pygame.Surface, offset: tuple[float, float], font: pygame.font.Font):
        pulse = 1.0 + 0.15 * math.sin(self.time_alive * 9.0)
        r = int(self.radius * pulse)
        pos = (int(self.x + offset[0]), int(self.y + offset[1]))

        # Outer glowing halo
        halo_surf = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        halo_col = (*self.color, 70)
        pygame.draw.circle(halo_surf, halo_col, (r * 2, r * 2), r + 6)
        surface.blit(halo_surf, (pos[0] - r * 2, pos[1] - r * 2))

        # Inner solid circle
        pygame.draw.circle(surface, self.color, pos, r)
        pygame.draw.circle(surface, (255, 255, 255), pos, r, width=2)

        # Icon/Label
        text = font.render(self.label, True, (20, 20, 30))
        tr = text.get_rect(center=pos)
        surface.blit(text, tr)
