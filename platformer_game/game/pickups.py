"""Collectibles and checkpoints, drawn entirely with pygame primitives."""

from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from .constants import PLAYER_H
from .utils import (
    clamp,
    draw_glow,
    heart_points,
    polygon_alpha,
    glow_surface,
)

KIND_RADIUS = {
    "coin": 12,
    "gem": 15,
    "heart": 14,
    "chrono": 14,
}


@dataclass
class Pickup:
    kind: str
    x: float
    y: float
    phase: float = 0.0
    collected: bool = False
    home_x: float = 0.0
    home_y: float = 0.0

    def __post_init__(self) -> None:
        if self.home_x == 0.0 and self.home_y == 0.0:
            self.home_x, self.home_y = self.x, self.y

    @property
    def radius(self) -> int:
        return KIND_RADIUS.get(self.kind, 12)

    @property
    def rect(self) -> pygame.FRect:
        r = self.radius + 2
        return pygame.FRect(self.x - r, self.y - r, r * 2, r * 2)

    def update(self, dt: float, px: float, py: float, time_s: float,
               magnet_allowed: bool = True) -> bool:
        if self.collected:
            return True
        bob = math.sin(time_s * 2.6 + self.phase) * 4.0
        self.y = self.home_y + bob
        # coins drift toward the player
        if magnet_allowed and self.kind in ("coin", "gem"):
            dx = px - self.x
            dy = py - self.y
            dist = math.hypot(dx, dy)
            reach = 118 if self.kind == "coin" else 72
            if 0.1 < dist < reach:
                pull = (1.0 - dist / reach) * (520 if self.kind == "coin" else 380)
                self.x += dx / dist * pull * dt
                self.home_x += dx / dist * pull * dt
                self.y += dy / dist * pull * dt
                self.home_y += dy / dist * pull * dt
        return False

    def overlaps_player(self, player) -> bool:
        pr = player.rect.inflate(-8, -8)
        return pr.colliderect(self.rect())

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float,
             time_s: float, ui_font=None) -> None:
        sx = self.x - cam_x
        sy = self.y - cam_y
        if sx < -60 or sx > 1340 or sy < -60 or sy > 780:
            return
        t = time_s
        if self.kind == "coin":
            self._draw_coin(surface, sx, sy, t)
        elif self.kind == "gem":
            self._draw_gem(surface, sx, sy, t)
        elif self.kind == "heart":
            self._draw_heart(surface, sx, sy, t)
        elif self.kind == "chrono":
            self._draw_chrono(surface, sx, sy, t)

    def _draw_coin(self, surface, sx, sy, t):
        spin = abs(math.cos(t * 3.4 + self.phase))
        w = max(2, int(9 * spin))
        draw_glow(surface, (sx, sy), 19, (255, 198, 96), 40, 2.2)
        pygame.draw.ellipse(surface, (255, 205, 104), (sx - w, sy - 9, w * 2, 18))
        pygame.draw.ellipse(surface, (176, 120, 42), (sx - w, sy - 9, w * 2, 18), 2)
        if w > 4:
            pygame.draw.ellipse(surface, (255, 242, 190), (sx - w * 0.35, sy - 5, w * 0.5, 6))
        sparkle = 0.5 + 0.5 * math.sin(t * 5.2 + self.phase)
        pygame.draw.circle(surface, (255, 250, 220),
                           (int(sx + 10), int(sy - 12)), max(1, int(1 + sparkle * 2)))

    def _draw_gem(self, surface, sx, sy, t):
        pulse = 0.5 + 0.5 * math.sin(t * 2.4 + self.phase)
        draw_glow(surface, (sx, sy), 34, (172, 132, 255), 76 + int(pulse * 34), 2.0)
        scale = 1.0 + pulse * 0.08
        w = 13 * scale
        h = 19 * scale
        pts = [(sx, sy - h), (sx + w, sy - h * 0.25), (sx, sy + h), (sx - w, sy - h * 0.25)]
        pygame.draw.polygon(surface, (154, 116, 255), pts)
        pygame.draw.polygon(surface, (198, 168, 255),
                            [(sx, sy - h), (sx + w * 0.45, sy - h * 0.2), (sx, sy + h * 0.55)])
        pygame.draw.polygon(surface, (108, 76, 200),
                            [(sx, sy - h), (sx - w * 0.6, sy - h * 0.15), (sx, sy + h * 0.55)])
        pygame.draw.polygon(surface, (236, 220, 255), pts, 1)
        pygame.draw.circle(surface, (255, 255, 255), (int(sx - w * 0.25), int(sy - h * 0.25)), 2)
        for k in range(3):
            a = t * 1.4 + k * 2.1 + self.phase
            px = sx + math.cos(a) * 22
            py = sy + math.sin(a) * 18
            pygame.draw.circle(surface, (220, 200, 255), (int(px), int(py)), 1)

    def _draw_heart(self, surface, sx, sy, t):
        pulse = 0.86 + 0.14 * math.sin(t * 3.2 + self.phase)
        draw_glow(surface, (sx, sy), 28, (255, 110, 140), 70, 2.0)
        pts = heart_points(sx, sy, 26 * pulse)
        pygame.draw.polygon(surface, (255, 120, 148), pts)
        pygame.draw.polygon(surface, (255, 196, 210),
                            heart_points(sx - 1.5, sy - 1.5, 13 * pulse))
        pygame.draw.polygon(surface, (176, 54, 80), pts, 2)

    def _draw_chrono(self, surface, sx, sy, t):
        pulse = 0.5 + 0.5 * math.sin(t * 3.0 + self.phase)
        draw_glow(surface, (sx, sy), 30, (120, 240, 255), 66 + int(pulse * 30), 2.0)
        pygame.draw.circle(surface, (92, 190, 214), (int(sx), int(sy)), 14)
        pygame.draw.circle(surface, (188, 252, 255), (int(sx), int(sy)), 14, 2)
        angle = t * 2.2 + self.phase
        pygame.draw.line(surface, (240, 255, 255), (sx, sy),
                         (sx + math.cos(angle) * 7, sy + math.sin(angle) * 7), 2)
        pygame.draw.line(surface, (240, 255, 255), (sx, sy), (sx, sy - 8), 2)
        pygame.draw.circle(surface, (255, 255, 255), (int(sx), int(sy)), 2)
        pygame.draw.circle(surface, (230, 255, 255), (int(sx), int(sy - 17)), 2)


@dataclass
class Checkpoint:
    x: float
    y: float
    phase: float = 0.0
    active: bool = False

    @property
    def rect(self) -> pygame.FRect:
        return pygame.FRect(self.x - 30, self.y - 84, 60, 84)

    def respawn_pos(self) -> tuple[float, float]:
        return (self.x - 14, self.y - PLAYER_H - 2)

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float,
             time_s: float) -> None:
        sx = self.x - cam_x
        sy = self.y - cam_y
        if sx < -80 or sx > 1360:
            return
        t = time_s + self.phase
        pulse = 0.5 + 0.5 * math.sin(t * 2.0)
        col = (128, 255, 200) if self.active else (92, 120, 112)
        glowcol = (140, 255, 208) if self.active else (80, 120, 110)
        if self.active:
            beam = pygame.Surface((70, 300), pygame.SRCALPHA)
            for i in range(8):
                a = int(26 * (1 - i / 8) * (0.5 + pulse * 0.5))
                pygame.draw.rect(beam, (*glowcol, a), (16 + i * 2, 0, 38 - i * 4, 300))
            surface.blit(beam, (int(sx - 35), int(sy - 300)))
            draw_glow(surface, (sx, sy - 46), 60, glowcol, 90 + int(pulse * 40), 2.0)

        # stones
        pygame.draw.ellipse(surface, (24, 34, 32), (sx - 30, sy - 10, 60, 18))
        # monolith
        pygame.draw.polygon(surface, (42, 56, 54),
                            [(sx - 12, sy), (sx - 9, sy - 58), (sx, sy - 72),
                             (sx + 9, sy - 58), (sx + 12, sy)])
        pygame.draw.polygon(surface, (66, 84, 78),
                            [(sx - 12, sy), (sx - 9, sy - 58), (sx - 2, sy - 68),
                             (sx - 1, sy)])
        # rune
        pygame.draw.circle(surface, col, (int(sx), int(sy - 40)), 6, 2)
        pygame.draw.line(surface, col, (sx, sy - 46), (sx, sy - 34), 1)
        pygame.draw.line(surface, col, (sx - 4, sy - 44), (sx + 4, sy - 36), 1)
        if self.active:
            for i in range(3):
                a = t * 1.7 + i * 2.094
                px = sx + math.cos(a) * 24
                py = sy - 42 + math.sin(a * 1.3) * 26
                pygame.draw.circle(surface, (200, 255, 230), (int(px), int(py)), 2)
