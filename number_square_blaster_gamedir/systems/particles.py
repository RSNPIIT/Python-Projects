"""Block Blast - High-Speed Particle & Floating Text System"""
import math
import random
import pygame

class Particle:
    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: tuple[int, int, int],
        size: float = 4.0,
        lifetime: float = 0.5,
        decay: float = 0.95
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.orig_size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.decay = decay

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= self.decay
        self.vy *= self.decay
        self.size = self.orig_size * (self.lifetime / self.max_lifetime)
        return True

    def draw(self, surface: pygame.Surface, offset: tuple[float, float]):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if self.size >= 1.0 and alpha > 0:
            surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            col = (*self.color[:3], alpha)
            pygame.draw.circle(surf, col, (int(self.size), int(self.size)), int(self.size))
            surface.blit(surf, (self.x + offset[0] - self.size, self.y + offset[1] - self.size))


class FloatingText:
    def __init__(self, x: float, y: float, text: str, color: tuple[int, int, int], font: pygame.font.Font):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = font
        self.lifetime = 0.65
        self.max_lifetime = 0.65
        self.vy = -55.0

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        self.y += self.vy * dt
        return self.lifetime > 0

    def draw(self, surface: pygame.Surface, offset: tuple[float, float]):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if alpha > 0:
            rendered = self.font.render(self.text, True, self.color)
            rendered.set_alpha(alpha)
            surface.blit(rendered, (self.x + offset[0], self.y + offset[1]))


class ParticleSystem:
    def __init__(self):
        self.particles: list[Particle] = []
        self.texts: list[FloatingText] = []

    def emit_sparks(self, x: float, y: float, color: tuple[int, int, int], count: int = 8):
        for _ in range(count):
            angle = random.random() * math.pi * 2
            speed = random.uniform(60, 220)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(2.5, 5.0)
            life = random.uniform(0.2, 0.45)
            self.particles.append(Particle(x, y, vx, vy, color, size, life))

    def emit_explosion(self, x: float, y: float, color: tuple[int, int, int], count: int = 35):
        for _ in range(count):
            angle = random.random() * math.pi * 2
            speed = random.uniform(100, 380)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(4.0, 9.0)
            life = random.uniform(0.35, 0.7)
            # Mix with fiery colors
            c = random.choice([color, (255, 230, 100), (255, 120, 50), (255, 255, 255)])
            self.particles.append(Particle(x, y, vx, vy, c, size, life, decay=0.92))

    def emit_rocket_trail(self, x: float, y: float):
        vx = (random.random() * 2 - 1) * 20
        vy = random.uniform(20, 60)
        c = random.choice([(255, 120, 40), (255, 210, 60), (200, 200, 220)])
        self.particles.append(Particle(x, y, vx, vy, c, size=3.0, lifetime=0.22, decay=0.88))

    def add_floating_text(self, x: float, y: float, text: str, color: tuple[int, int, int], font: pygame.font.Font):
        self.texts.append(FloatingText(x, y, text, color, font))

    def update(self, dt: float):
        self.particles = [p for p in self.particles if p.update(dt)]
        self.texts = [t for t in self.texts if t.update(dt)]

    def draw(self, surface: pygame.Surface, offset: tuple[float, float] = (0.0, 0.0)):
        for p in self.particles:
            p.draw(surface, offset)
        for t in self.texts:
            t.draw(surface, offset)
