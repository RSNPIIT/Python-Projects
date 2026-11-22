"""Kapman Game - Particles & Visual FX"""
import math
import random
import pygame

class SparkParticle:
    def __init__(self, x: float, y: float, color: tuple[int, int, int]):
        self.x = x
        self.y = y
        angle = random.random() * math.pi * 2
        speed = random.uniform(30, 90)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.lifetime = random.uniform(0.2, 0.4)
        self.max_lifetime = self.lifetime
        self.radius = random.uniform(1.5, 3.0)

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        return self.lifetime > 0

    def draw(self, surface: pygame.Surface, offset_y: int = 0):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        r = int(self.radius * (self.lifetime / self.max_lifetime))
        if r > 0 and alpha > 0:
            surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (r + 1, r + 1), r)
            surface.blit(surf, (int(self.x - r), int(self.y - r + offset_y)))


class ParticleSystem:
    def __init__(self):
        self.particles: list[SparkParticle] = []

    def emit_sparks(self, x: float, y: float, color: tuple[int, int, int], count: int = 8):
        for _ in range(count):
            self.particles.append(SparkParticle(x, y, color))

    def update(self, dt: float):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface: pygame.Surface, offset_y: int = 0):
        for p in self.particles:
            p.draw(surface, offset_y=offset_y)
