"""Particles, floating score text and screen-space ambient motes."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import numpy as np
import pygame

from .constants import BIOMES, SCREEN_H, SCREEN_W
from .utils import clamp, draw_glow, glow_surface

_rng = random.Random(4242)


@dataclass(slots=True)
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    size: float
    color: tuple[int, int, int]
    gravity: float = 0.0
    drag: float = 1.5
    kind: str = "glow"      # glow | spark | leaf | dust | ring
    angle: float = 0.0
    spin: float = 0.0


@dataclass(slots=True)
class FloatText:
    x: float
    y: float
    value: str
    color: tuple[int, int, int]
    life: float = 1.1
    max_life: float = 1.1
    vy: float = -40.0
    big: bool = False


class ParticleSystem:
    MAX = 700

    def __init__(self) -> None:
        self.particles: list[Particle] = []
        self.texts: list[FloatText] = []

    # ------------------------------------------------------------------
    def clear(self) -> None:
        self.particles.clear()
        self.texts.clear()

    def add(self, p: Particle) -> None:
        if len(self.particles) < self.MAX:
            self.particles.append(p)

    def burst(self, x: float, y: float, color, count: int = 10,
              speed: float = 140.0, life: float = 0.55, gravity: float = 700.0,
              size: float = 4.0, kind: str = "glow", spread: float = math.tau) -> None:
        for _ in range(count):
            a = _rng.uniform(0, spread) - (0.0 if spread >= math.tau else spread / 2)
            sp = speed * _rng.uniform(0.25, 1.0)
            self.add(Particle(
                x=x, y=y,
                vx=math.cos(a) * sp,
                vy=math.sin(a) * sp,
                life=life * _rng.uniform(0.6, 1.25),
                max_life=life,
                size=size * _rng.uniform(0.6, 1.5),
                color=color,
                gravity=gravity,
                drag=_rng.uniform(1.5, 3.5),
                kind=kind,
                angle=_rng.uniform(0, math.tau),
                spin=_rng.uniform(-8, 8),
            ))

    def trail(self, x: float, y: float, color, count: int = 1, size: float = 5.0,
              speed: float = 30.0, life: float = 0.45) -> None:
        for _ in range(count):
            self.add(Particle(
                x=x + _rng.uniform(-3, 3), y=y + _rng.uniform(-3, 3),
                vx=_rng.uniform(-speed, speed) * 0.4,
                vy=_rng.uniform(-speed, speed) * 0.5 - 25,
                life=life * _rng.uniform(0.5, 1.1), max_life=life,
                size=size * _rng.uniform(0.5, 1.2), color=color,
                gravity=180, drag=2.2, kind="glow",
            ))

    def dust(self, x: float, y: float, color, count: int = 6, strength: float = 1.0) -> None:
        for _ in range(count):
            self.add(Particle(
                x=x + _rng.uniform(-10, 10), y=y + _rng.uniform(-3, 3),
                vx=_rng.uniform(-60, 60) * strength,
                vy=_rng.uniform(-70, -10) * strength,
                life=_rng.uniform(0.25, 0.6), max_life=0.6,
                size=_rng.uniform(3, 8), color=color,
                gravity=240, drag=3.0, kind="dust",
            ))

    def ring(self, x: float, y: float, color, radius: float = 20,
             life: float = 0.4) -> None:
        self.add(Particle(x=x, y=y, vx=0, vy=0, life=life, max_life=life,
                          size=radius, color=color, gravity=0, drag=0,
                          kind="ring"))

    def text(self, x: float, y: float, value: str, color, big: bool = False) -> None:
        self.texts.append(FloatText(x=x, y=y, value=value, color=color, big=big))

    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        alive: list[Particle] = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.vy += p.gravity * dt
            damp = max(0.0, 1.0 - p.drag * dt)
            p.vx *= damp
            p.vy *= damp
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.angle += p.spin * dt
            if p.kind == "leaf":
                p.vx += math.sin((p.life + p.angle) * 4.0) * 30.0 * dt
            alive.append(p)
        self.particles = alive

        texts = []
        for t in self.texts:
            t.life -= dt
            t.y += t.vy * dt
            t.vy *= max(0.0, 1.0 - 1.9 * dt)
            if t.life > 0:
                texts.append(t)
        self.texts = texts

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float,
             font=None) -> None:
        for p in self.particles:
            a = clamp(p.life / max(0.001, p.max_life), 0.0, 1.0)
            sx = p.x - cam_x
            sy = p.y - cam_y
            if sx < -80 or sx > SCREEN_W + 80 or sy < -80 or sy > SCREEN_H + 80:
                continue
            if p.kind == "ring":
                r = int(p.size * (1.0 + (1.0 - a) * 1.8))
                pygame.draw.circle(surface, (*p.color, int(120 * a)), (int(sx), int(sy)),
                                   max(1, r), 2)
            elif p.kind == "spark":
                ex = sx - p.vx * 0.02
                ey = sy - p.vy * 0.02
                pygame.draw.line(surface, (*p.color, int(220 * a)), (sx, sy), (ex, ey),
                                 max(1, int(p.size * 0.35)))
            elif p.kind == "leaf":
                pts = []
                for k in range(3):
                    ang = p.angle + k * 2.094
                    pts.append((sx + math.cos(ang) * p.size * 1.4,
                                sy + math.sin(ang) * p.size * 0.7))
                pygame.draw.polygon(surface, (*p.color, int(200 * a)), pts)
            elif p.kind == "dust":
                pygame.draw.circle(surface, (*p.color, int(150 * a)),
                                   (int(sx), int(sy)), max(1, int(p.size * a)))
            else:
                rad = max(2, int(p.size * (0.4 + a * 0.9)))
                draw_glow(surface, (sx, sy), rad * 2, p.color, int(180 * a), 2.0)

        if font is not None:
            for t in self.texts:
                a = clamp(t.life / max(0.001, t.max_life), 0.0, 1.0)
                img = font.render(t.value, True, t.color)
                img.set_alpha(int(255 * a))
                pos = (int(t.x - cam_x - img.get_width() / 2), int(t.y - cam_y))
                surface.blit(img, pos)


class AmbientField:
    """Numpy-driven screen-space motes.  Different colours per biome."""

    def __init__(self, count: int = 72) -> None:
        self.count = count
        rng = np.random.default_rng(7)
        self.x = rng.uniform(0, SCREEN_W, count)
        self.y = rng.uniform(0, SCREEN_H, count)
        self.size = rng.uniform(0.7, 2.4, count)
        self.speed = rng.uniform(5, 22, count)
        self.phase = rng.uniform(0, math.tau, count)
        self.drift = rng.uniform(-12, 18, count)
        self.depth = rng.uniform(0.3, 1.0, count)

    def update(self, dt: float, wind: float = 8.0) -> None:
        self.y -= self.speed * dt
        self.x += (wind * self.depth + np.sin(self.phase + self.y * 0.01) * 6) * dt
        self.y = np.where(self.y < -10, SCREEN_H + 10, self.y)
        self.x = np.where(self.x < -10, SCREEN_W + 10, self.x)
        self.x = np.where(self.x > SCREEN_W + 10, -10, self.x)

    def draw(self, surface: pygame.Surface, biome_index: int, time: float) -> None:
        palette = BIOMES[biome_index % len(BIOMES)]
        base = palette["accent"]
        for i in range(self.count):
            alpha = int((60 + 110 * (0.5 + 0.5 * math.sin(time * 2.0 + self.phase[i])))
                        * self.depth[i])
            col = base if i % 5 else palette["accent2"]
            x, y = int(self.x[i]), int(self.y[i])
            pygame.draw.circle(surface, (*col, alpha), (x, y), max(1, int(self.size[i])))
