"""
particles.py - Particle VFX system for KFlapper.
Manages drifting feathers, coin score sparkles, ground impact puffs, ambient biome dust/stars, and screen flash effects.
"""

import math
import random
import pygame


class Feather:
    """Soft floating feather particle that sways side to side as it falls."""

    def __init__(self, x: float, y: float, color: tuple):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-2.2, 0.5)
        self.vy = random.uniform(-1.5, 0.5)
        self.sway_phase = random.uniform(0, math.pi * 2)
        self.sway_speed = random.uniform(4.0, 7.0)
        self.size = random.uniform(4.0, 7.0)
        self.alpha = 255.0
        self.decay = random.uniform(3.5, 5.5)
        self.alive = True

    def update(self, dt: float):
        self.sway_phase += self.sway_speed * dt
        self.vx = math.sin(self.sway_phase) * 1.8 - 1.2
        self.vy += 2.0 * dt
        if self.vy > 2.2:
            self.vy = 2.2

        self.x += self.vx
        self.y += self.vy
        self.alpha -= self.decay
        if self.alpha <= 0:
            self.alive = False

    def draw(self, surface: pygame.Surface):
        if not self.alive or self.alpha <= 0:
            return
        a = max(0, min(255, int(self.alpha)))
        s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        c = (*self.color[:3], a)
        pygame.draw.ellipse(s, c, (0, 0, int(self.size * 2), int(self.size)))
        surface.blit(s, (self.x - self.size, self.y - self.size / 2))


class Sparkle:
    """Glowing diamond sparkle particle for score achievements and medals."""

    def __init__(self, x: float, y: float, color: tuple = (255, 235, 120)):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-2.5, 2.5)
        self.vy = random.uniform(-3.5, 1.0)
        self.size = random.uniform(5.0, 10.0)
        self.alpha = 255.0
        self.decay = random.uniform(5.0, 8.0)
        self.alive = True

    def update(self, dt: float):
        self.x += self.vx
        self.y += self.vy
        self.vy += 1.5 * dt
        self.alpha -= self.decay
        self.size = max(0.5, self.size - 0.1)
        if self.alpha <= 0:
            self.alive = False

    def draw(self, surface: pygame.Surface):
        if not self.alive or self.alpha <= 0:
            return
        a = max(0, min(255, int(self.alpha)))
        sz = int(self.size)
        if sz <= 0:
            return
        surf = pygame.Surface((sz * 2 + 2, sz * 2 + 2), pygame.SRCALPHA)
        c = (*self.color[:3], a)
        cx, cy = sz + 1, sz + 1
        pts = [(cx, cy - sz), (cx + sz, cy), (cx, cy + sz), (cx - sz, cy)]
        pygame.draw.polygon(surf, c, pts)
        surface.blit(surf, (self.x - cx, self.y - cy))


class DustPuff:
    """Impact dust puff when hitting ground or pipe."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3.0, 3.0)
        self.vy = random.uniform(-3.5, -0.5)
        self.radius = random.uniform(4.0, 9.0)
        self.alpha = 230.0
        self.decay = random.uniform(6.0, 10.0)
        self.alive = True

    def update(self, dt: float):
        self.x += self.vx
        self.y += self.vy
        self.vy += 3.0 * dt
        self.radius += 0.2
        self.alpha -= self.decay
        if self.alpha <= 0:
            self.alive = False

    def draw(self, surface: pygame.Surface):
        if not self.alive or self.alpha <= 0:
            return
        r = int(self.radius)
        if r <= 0:
            return
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        c = (230, 220, 200, max(0, min(255, int(self.alpha))))
        pygame.draw.circle(surf, c, (r, r), r)
        surface.blit(surf, (self.x - r, self.y - r))


class AmbientMote:
    """Atmospheric drifting particle matching active biome (Mars dust, Cyber sparks, Cosmic stars)."""

    def __init__(self, x: float, y: float, fx_type: str):
        self.x = x
        self.y = y
        self.fx_type = fx_type
        self.alive = True

        if fx_type == "red_dust":
            self.color = random.choice([(255, 100, 70), (220, 60, 45), (255, 150, 90)])
            self.vx = random.uniform(-3.8, -1.8)
            self.vy = random.uniform(-0.6, 0.6)
            self.size = random.uniform(2.0, 4.5)
            self.alpha = random.uniform(140, 240)
            self.decay = random.uniform(0.6, 1.4)
        elif fx_type == "cyber_sparks":
            self.color = random.choice([(0, 240, 255), (255, 0, 180), (160, 255, 255)])
            self.vx = random.uniform(-4.5, -2.0)
            self.vy = random.uniform(-1.0, 1.0)
            self.size = random.uniform(2.5, 4.0)
            self.alpha = random.uniform(180, 255)
            self.decay = random.uniform(1.0, 2.0)
        elif fx_type == "stars":
            self.color = random.choice([(255, 255, 255), (200, 220, 255), (255, 235, 160)])
            self.vx = random.uniform(-1.2, -0.4)
            self.vy = 0.0
            self.size = random.uniform(1.5, 3.5)
            self.alpha = random.uniform(120, 255)
            self.decay = random.uniform(0.3, 0.8)
        else:
            self.color = (255, 255, 255)
            self.vx = -1.0
            self.vy = 0.0
            self.size = 2.0
            self.alpha = 200.0
            self.decay = 1.0

    def update(self, dt: float):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= self.decay
        if self.alpha <= 0 or self.x < -20:
            self.alive = False

    def draw(self, surface: pygame.Surface):
        if not self.alive:
            return
        sz = int(self.size)
        if sz <= 0:
            return
        surf = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
        c = (*self.color[:3], max(0, min(255, int(self.alpha))))
        if self.fx_type == "cyber_sparks":
            # Square digital pixel
            pygame.draw.rect(surf, c, (0, 0, sz * 2, sz * 2))
        else:
            pygame.draw.circle(surf, c, (sz, sz), sz)
        surface.blit(surf, (int(self.x), int(self.y)))


class ParticleManager:
    """Manages all active particles in the scene."""

    def __init__(self):
        self.particles = []
        self.screen_shake = 0.0
        self.screen_flash = 0.0
        self.ambient_timer = 0.0

    def emit_flap_feathers(self, x: float, y: float, color: tuple, count: int = 3):
        for _ in range(count):
            self.particles.append(Feather(x - 14, y + random.uniform(-6, 6), color))

    def emit_score_sparkles(self, x: float, y: float, count: int = 14):
        for _ in range(count):
            self.particles.append(Sparkle(x + random.uniform(-20, 20), y + random.uniform(-20, 20)))

    def emit_biome_transition(self, accent_color: tuple):
        """Massive milestone celebration burst when entering a new sector."""
        self.screen_shake = 12.0
        self.screen_flash = 0.8
        import config
        from ..config import SCREEN_WIDTH, SCREEN_HEIGHT
        for _ in range(45):
            self.particles.append(Sparkle(random.uniform(100, SCREEN_WIDTH - 100), random.uniform(80, 450), color=accent_color))

    def emit_crash_burst(self, x: float, y: float, body_color: tuple):
        self.screen_shake = 18.0
        self.screen_flash = 1.0
        for _ in range(16):
            self.particles.append(Feather(x, y, body_color))
        for _ in range(20):
            self.particles.append(DustPuff(x, y))

    def update_ambient(self, dt: float, fx_type: str, screen_w: int, screen_h: int):
        if fx_type == "feathers":
            return
        self.ambient_timer += dt
        if self.ambient_timer > 0.08:
            self.ambient_timer = 0.0
            spawn_x = screen_w + random.uniform(10, 50)
            spawn_y = random.uniform(30, screen_h - 130)
            self.particles.append(AmbientMote(spawn_x, spawn_y, fx_type))

    def update(self, dt: float):
        if self.screen_shake > 0:
            self.screen_shake = max(0.0, self.screen_shake - 35.0 * dt)
        if self.screen_flash > 0:
            self.screen_flash = max(0.0, self.screen_flash - 4.5 * dt)

        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface: pygame.Surface):
        for p in self.particles:
            p.draw(surface)

        if self.screen_flash > 0:
            alpha = int(self.screen_flash * 180)
            flash_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, alpha))
            surface.blit(flash_surf, (0, 0))

    def get_shake_offset(self) -> tuple:
        if self.screen_shake <= 0:
            return 0, 0
        return (random.uniform(-self.screen_shake, self.screen_shake),
                random.uniform(-self.screen_shake, self.screen_shake))

    def clear(self):
        self.particles.clear()
        self.screen_shake = 0.0
        self.screen_flash = 0.0
