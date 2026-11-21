"""Block Blast - Polished PowerUp Orbs"""
import math
import pygame
from core.constants import PowerUpType, SCREEN_HEIGHT

class PowerUp:
    def __init__(self, x: float, y: float, powerup_type: str):
        self.x = x
        self.y = y
        self.type = powerup_type
        self.radius = 18
        self.vy = 80.0
        self.time_alive = 0.0

    @property
    def color(self) -> tuple[int, int, int]:
        return {
            PowerUpType.SPREAD_SHOT: (255, 175, 40),
            PowerUpType.PIERCE: (40, 225, 255),
            PowerUpType.RAPID_FIRE: (255, 60, 160),
            PowerUpType.BOMB: (255, 50, 50),
            PowerUpType.FREEZE: (80, 240, 220),
        }.get(self.type, (255, 255, 255))

    @property
    def tag_text(self) -> str:
        return {
            PowerUpType.SPREAD_SHOT: "3X",
            PowerUpType.PIERCE: "BOLT",
            PowerUpType.RAPID_FIRE: "SPD",
            PowerUpType.BOMB: "TNT",
            PowerUpType.FREEZE: "ICE",
        }.get(self.type, "PWR")

    @property
    def label(self) -> str:
        return {
            PowerUpType.SPREAD_SHOT: "3X SPREAD",
            PowerUpType.PIERCE: "LASER DRILL",
            PowerUpType.RAPID_FIRE: "RAPID FIRE",
            PowerUpType.BOMB: "MEGA BOMB",
            PowerUpType.FREEZE: "PUSHBACK",
        }.get(self.type, "POWERUP")

    def update(self, dt: float) -> bool:
        self.time_alive += dt
        self.y += self.vy * dt
        return self.y < SCREEN_HEIGHT + 35

    def draw(self, surface: pygame.Surface, offset: tuple[float, float], font: pygame.font.Font):
        pulse = 1.0 + 0.12 * math.sin(self.time_alive * 8.0)
        r = int(self.radius * pulse)
        pos = (int(self.x + offset[0]), int(self.y + offset[1]))

        # Outer soft glow halo
        halo_r = r + 10
        halo_surf = pygame.Surface((halo_r * 2, halo_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(halo_surf, (*self.color, 45), (halo_r, halo_r), halo_r)
        pygame.draw.circle(halo_surf, (*self.color, 90), (halo_r, halo_r), r + 4)
        surface.blit(halo_surf, (pos[0] - halo_r, pos[1] - halo_r))

        # Main glowing capsule body
        pygame.draw.circle(surface, (18, 22, 34), pos, r)
        pygame.draw.circle(surface, self.color, pos, r, width=3)
        pygame.draw.circle(surface, (255, 255, 255), pos, r - 3, width=1)

        # Centered bold tag text (e.g. 3X, TNT, ICE, SPD, BOLT)
        txt = font.render(self.tag_text, True, (255, 255, 255))
        tr = txt.get_rect(center=pos)
        surface.blit(txt, tr)
