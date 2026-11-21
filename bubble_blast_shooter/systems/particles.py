"""Bubble Blast Shooter - Particles, Droplets & Falling Avalanche Bubbles"""
import math
import random
import pygame
from core.constants import SCREEN_HEIGHT, BUBBLE_RADIUS
from core.bubble import get_bubble_surface

class BubbleDroplet:
    def __init__(self, x: float, y: float, vx: float, vy: float, color: tuple[int, int, int]):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = random.uniform(3.0, 5.5)
        self.lifetime = random.uniform(0.35, 0.55)
        self.max_lifetime = self.lifetime

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 380.0 * dt  # Gravity
        return True

    def draw(self, surface: pygame.Surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        r = int(self.radius * (self.lifetime / self.max_lifetime))
        if r > 0 and alpha > 0:
            surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (r + 1, r + 1), r)
            surface.blit(surf, (int(self.x - r - 1), int(self.y - r - 1)))


class FallingBubble:
    """Detached orphan bubble that drops down in an avalanche with physics."""
    def __init__(self, x: float, y: float, color_id: int):
        self.x = x
        self.y = y
        self.vx = random.uniform(-60.0, 60.0)
        self.vy = random.uniform(-90.0, -20.0)
        self.color_id = color_id
        self.radius = BUBBLE_RADIUS
        self.alive = True
        self.gravity = 980.0

    def update(self, dt: float) -> bool:
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.y > SCREEN_HEIGHT + 40:
            self.alive = False
        return self.alive

    def draw(self, surface: pygame.Surface):
        surf = get_bubble_surface(self.color_id, self.radius)
        surface.blit(surf, surf.get_rect(center=(int(self.x), int(self.y))))


class FloatingScoreText:
    def __init__(self, x: float, y: float, text: str, color: tuple[int, int, int], font: pygame.font.Font):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = font
        self.lifetime = 0.75
        self.max_lifetime = 0.75
        self.vy = -55.0

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        self.y += self.vy * dt
        return self.lifetime > 0

    def draw(self, surface: pygame.Surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if alpha > 0:
            rendered = self.font.render(self.text, True, self.color)
            rendered.set_alpha(alpha)
            surface.blit(rendered, (int(self.x), int(self.y)))


class ParticleSystem:
    def __init__(self):
        self.droplets: list[BubbleDroplet] = []
        self.falling_bubbles: list[FallingBubble] = []
        self.scores: list[FloatingScoreText] = []

    def emit_burst(self, x: float, y: float, color: tuple[int, int, int], count: int = 18):
        for _ in range(count):
            angle = random.random() * math.pi * 2
            speed = random.uniform(80, 240)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 40.0
            self.droplets.append(BubbleDroplet(x, y, vx, vy, color))

    def add_falling_bubble(self, x: float, y: float, color_id: int):
        self.falling_bubbles.append(FallingBubble(x, y, color_id))

    def add_score(self, x: float, y: float, text: str, color: tuple[int, int, int], font: pygame.font.Font):
        self.scores.append(FloatingScoreText(x, y, text, color, font))

    def update(self, dt: float):
        self.droplets = [d for d in self.droplets if d.update(dt)]
        self.falling_bubbles = [fb for fb in self.falling_bubbles if fb.update(dt)]
        self.scores = [s for s in self.scores if s.update(dt)]

    def draw(self, surface: pygame.Surface):
        for fb in self.falling_bubbles:
            fb.draw(surface)
        for d in self.droplets:
            d.draw(surface)
        for s in self.scores:
            s.draw(surface)
