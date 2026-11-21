"""Bubble Blast - Visual Particles & Shockwave Effects"""
import math
import random
import pygame

class DropletParticle:
    def __init__(self, x: float, y: float, vx: float, vy: float, color: tuple[int, int, int]):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = random.uniform(3.0, 6.0)
        self.orig_size = self.size
        self.lifetime = random.uniform(0.3, 0.55)
        self.max_lifetime = self.lifetime

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 220.0 * dt  # Gravity
        self.size = self.orig_size * (self.lifetime / self.max_lifetime)
        return True

    def draw(self, surface: pygame.Surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if self.size >= 1.0 and alpha > 0:
            surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            surface.blit(surf, (self.x - self.size, self.y - self.size))


class ShockwaveRing:
    def __init__(self, x: float, y: float, color: tuple[int, int, int], max_radius: float = 40.0):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 8.0
        self.max_radius = max_radius
        self.lifetime = 0.25
        self.max_lifetime = 0.25

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False
        progress = 1.0 - (self.lifetime / self.max_lifetime)
        self.radius = 8.0 + (self.max_radius - 8.0) * progress
        return True

    def draw(self, surface: pygame.Surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if alpha > 0:
            r = int(self.radius)
            surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (r + 2, r + 2), r, width=2)
            surface.blit(surf, (self.x - r - 2, self.y - r - 2))


class FloatingText:
    def __init__(self, x: float, y: float, text: str, color: tuple[int, int, int], font: pygame.font.Font):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = font
        self.lifetime = 0.8
        self.max_lifetime = 0.8
        self.vy = -50.0

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        self.y += self.vy * dt
        return self.lifetime > 0

    def draw(self, surface: pygame.Surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if alpha > 0:
            rendered = self.font.render(self.text, True, self.color)
            rendered.set_alpha(alpha)
            surface.blit(rendered, (self.x, self.y))


class ParticleSystem:
    def __init__(self):
        self.droplets: list[DropletParticle] = []
        self.rings: list[ShockwaveRing] = []
        self.texts: list[FloatingText] = []

    def emit_bubble_pop(self, x: float, y: float, color: tuple[int, int, int], count: int = 24):
        self.rings.append(ShockwaveRing(x, y, color))
        for _ in range(count):
            angle = random.random() * math.pi * 2
            speed = random.uniform(80, 260)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 40.0
            self.droplets.append(DropletParticle(x, y, vx, vy, color))

    def add_floating_text(self, x: float, y: float, text: str, color: tuple[int, int, int], font: pygame.font.Font):
        self.texts.append(FloatingText(x, y, text, color, font))

    def update(self, dt: float):
        self.droplets = [d for d in self.droplets if d.update(dt)]
        self.rings = [r for r in self.rings if r.update(dt)]
        self.texts = [t for t in self.texts if t.update(dt)]

    def draw(self, surface: pygame.Surface):
        for r in self.rings:
            r.draw(surface)
        for d in self.droplets:
            d.draw(surface)
        for t in self.texts:
            t.draw(surface)
