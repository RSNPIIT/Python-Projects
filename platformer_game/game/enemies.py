"""Thorn-beetles, void-moths and spitting brambles.

Enemies are evaded, never killed: contact costs a heart.  Each enemy exposes
a forgiving hitbox and draws itself with plain pygame primitives so the whole
bestiary remains asset-free.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from .utils import clamp, draw_glow, polygon_alpha


class Enemy:
    kind = "enemy"

    def __init__(self, x: float, y: float, w: float, h: float):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.alive = True
        self.phase = (x * 0.013 + y * 0.017) % math.tau
        self.time = 0.0

    @property
    def rect(self) -> pygame.FRect:
        return pygame.FRect(self.x, self.y, self.w, self.h)

    @property
    def hit_rect(self) -> pygame.FRect:
        return pygame.FRect(self.x + 3, self.y + 3, self.w - 6, self.h - 6)

    def update(self, dt: float, player, world) -> None:
        self.time += dt

    def draw(self, surface, cam_x, cam_y, time_s, palette) -> None:
        pass


class Crawler(Enemy):
    kind = "crawler"

    def __init__(self, x: float, y: float, min_x: float, max_x: float,
                 speed: float = 70.0, direction: int = -1):
        super().__init__(x, y, 42, 26)
        self.min_x = min_x
        self.max_x = max_x
        self.vx = speed * direction
        self.speed = speed

    def update(self, dt, player, world):
        self.time += dt
        self.x += self.vx * dt
        if self.x < self.min_x:
            self.x = self.min_x
            self.vx = abs(self.vx)
        elif self.x + self.w > self.max_x:
            self.x = self.max_x - self.w
            self.vx = -abs(self.vx)
        # a little jitter in movement for character
        self.y = self.y  # anchored to the platform

    def draw(self, surface, cam_x, cam_y, time_s, palette):
        cx = self.x + self.w / 2 - cam_x
        cy = self.y + self.h / 2 - cam_y
        if cx < -80 or cx > 1360 or cy < -80 or cy > 800:
            return
        bob = math.sin(self.time * 9 + self.phase) * 1.4
        d = 1 if self.vx >= 0 else -1
        dark = (24, 30, 32)
        shell = (46, 58, 56)
        accent = palette["danger"]
        thorn = palette["thorn"]
        # shadow
        pygame.draw.ellipse(surface, (0, 0, 0, 70), (cx - 24, cy + 10, 48, 10))
        # legs
        for i in range(3):
            lx = cx - 13 + i * 12
            swing = math.sin(self.time * 11 + i * 2.0 + self.phase) * 4
            pygame.draw.line(surface, dark, (lx, cy + 3), (lx + swing, cy + 14), 3)
            pygame.draw.line(surface, dark, (lx, cy + 3), (lx - swing * 0.6, cy + 14), 2)
        # shell
        pygame.draw.ellipse(surface, dark, (cx - 23, cy - 12 + bob, 46, 28))
        pygame.draw.ellipse(surface, shell, (cx - 19, cy - 10 + bob, 38, 22))
        pygame.draw.arc(surface, (70, 84, 80), (cx - 19, cy - 10 + bob, 38, 22),
                        0.3, 2.9, 2)
        # back thorns
        for i in range(3):
            bx = cx - 13 + i * 12
            by = cy - 8 + bob
            pygame.draw.polygon(surface, thorn,
                                [(bx - 4, by), (bx + 1, by - 12 - i * 2), (bx + 5, by)])
            pygame.draw.line(surface, (18, 24, 24), (bx - 4, by), (bx + 1, by - 12 - i * 2), 1)
        # eyes
        eye_y = cy - 2 + bob
        for side in (-1, 1):
            pygame.draw.circle(surface, (12, 12, 16), (int(cx + d * 10 + side * 3), int(eye_y)), 3)
            pygame.draw.circle(surface, accent, (int(cx + d * 10 + side * 3), int(eye_y)), 2)
        draw_glow(surface, (cx + d * 10, eye_y), 14, accent, 40, 2.2)


class Flyer(Enemy):
    kind = "flyer"

    def __init__(self, x: float, y: float, anchor_w: float = 140.0,
                 anchor_h: float = 60.0, speed: float = 0.9):
        super().__init__(x, y, 30, 24)
        self.anchor_x = x
        self.anchor_y = y
        self.anchor_w = anchor_w
        self.anchor_h = anchor_h
        self.speed = speed
        self.drift_x = x
        self.drift_y = y
        self.chase = 0.0

    def update(self, dt, player, world):
        self.time += dt
        t = self.time * self.speed + self.phase
        tx = self.anchor_x + math.sin(t * 0.8) * self.anchor_w
        ty = self.anchor_y + math.sin(t * 1.7) * self.anchor_h
        # gently lean toward a nearby player
        dx = player.x + player.w / 2 - (self.x + self.w / 2)
        dy = player.y + player.h / 2 - (self.y + self.h / 2)
        dist = math.hypot(dx, dy)
        self.chase = clamp((460 - dist) / 460, 0.0, 1.0)
        if dist < 460 and dist > 1:
            tx += dx / dist * 48 * self.chase
            ty += dy / dist * 40 * self.chase
        self.drift_x += (tx - self.drift_x) * min(1.0, dt * 2.2)
        self.drift_y += (ty - self.drift_y) * min(1.0, dt * 2.2)
        self.x = self.drift_x
        self.y = self.drift_y

    def draw(self, surface, cam_x, cam_y, time_s, palette):
        cx = self.x + self.w / 2 - cam_x
        cy = self.y + self.h / 2 - cam_y
        if cx < -80 or cx > 1360 or cy < -80 or cy > 800:
            return
        t = self.time
        flap = abs(math.sin(t * 9 + self.phase))
        glow = palette["orb"]
        danger = palette["danger"]
        # spectral trail
        for i in range(1, 4):
            pygame.draw.circle(surface, (*glow, max(10, 34 - i * 8)),
                               (int(cx - math.cos(t * 4) * i * 7), int(cy + i * 3)), 7 - i)
        draw_glow(surface, (cx, cy), 36, glow, 62, 2.2)
        # wings
        wing_up = 10 + flap * 12
        left = [(cx - 4, cy), (cx - 24, cy - wing_up), (cx - 30, cy + 4), (cx - 10, cy + 7)]
        right = [(cx + 4, cy), (cx + 24, cy - wing_up), (cx + 30, cy + 4), (cx + 10, cy + 7)]
        polygon_alpha(surface, glow, left, 110)
        polygon_alpha(surface, glow, right, 110)
        pygame.draw.lines(surface, (*glow, 190), False, left, 2)
        pygame.draw.lines(surface, (*glow, 190), False, right, 2)
        # body
        pygame.draw.ellipse(surface, (30, 36, 44), (cx - 9, cy - 9, 18, 20))
        pygame.draw.ellipse(surface, (68, 84, 96), (cx - 6, cy - 8, 12, 14))
        # eyes
        for side in (-1, 1):
            pygame.draw.circle(surface, danger, (int(cx + side * 3), int(cy - 2)), 2)
        draw_glow(surface, (cx, cy - 1), 10, danger, 50, 2.0)
        # antennae
        pygame.draw.line(surface, (150, 190, 190), (cx - 2, cy - 9), (cx - 8, cy - 18), 1)
        pygame.draw.line(surface, (150, 190, 190), (cx + 2, cy - 9), (cx + 8, cy - 18), 1)


class Spitter(Enemy):
    kind = "spitter"

    def __init__(self, x: float, y: float, facing: int = -1):
        super().__init__(x, y, 42, 46)
        self.facing = facing
        self.cooldown = 1.0 + (x % 7) * 0.13
        self.charge = 0.0
        self.recoil = 0.0

    def update(self, dt, player, world):
        self.time += dt
        self.recoil = max(0.0, self.recoil - dt)
        if self.charge > 0:
            self.charge -= dt
            if self.charge <= 0:
                self._fire(player, world)
                self.cooldown = 2.3
        else:
            self.cooldown -= dt
            dx = player.x + player.w / 2 - (self.x + self.w / 2)
            dy = player.y + player.h / 2 - (self.y + 14)
            if self.cooldown <= 0 and abs(dx) < 560 and abs(dy) < 260:
                self.charge = 0.55
                self.facing = 1 if dx > 0 else -1

    def _fire(self, player, world):
        px = self.x + self.w / 2 + self.facing * 16
        py = self.y + 10
        tx = player.x + player.w / 2
        ty = player.y + player.h / 2
        dx, dy = tx - px, ty - py
        dist = max(1.0, math.hypot(dx, dy))
        speed = 280.0
        world.spawn_projectile(px, py, dx / dist * speed, dy / dist * speed, self.facing)
        self.recoil = 0.25

    @property
    def hit_rect(self) -> pygame.FRect:
        return pygame.FRect(self.x + 5, self.y + 8, self.w - 10, self.h - 12)

    def draw(self, surface, cam_x, cam_y, time_s, palette):
        cx = self.x + self.w / 2 - cam_x
        cy = self.y + self.h - cam_y
        if cx < -100 or cx > 1380 or cy < -100 or cy > 820:
            return
        t = self.time
        sway = math.sin(t * 1.6 + self.phase) * 2
        thorn = palette["thorn"]
        danger = palette["danger"]
        body = palette["rock_light"]
        draw_glow(surface, (cx, cy - 18), 34, danger if self.charge > 0 else palette["accent"],
                  40 + int((1 - max(0.0, self.charge) / 0.55) * 70 if self.charge > 0 else 20), 2.0)
        # roots
        for side in (-1, 1):
            pygame.draw.line(surface, palette["rock_dark"], (cx, cy - 2),
                             (cx + side * 24 + sway, cy + 2), 5)
        pygame.draw.ellipse(surface, palette["rock_dark"], (cx - 26, cy - 8, 52, 12))
        # stem / bulb
        pts = [(cx - 15, cy - 2), (cx - 17, cy - 30), (cx - 8, cy - 44),
               (cx + 8, cy - 44), (cx + 17, cy - 30), (cx + 15, cy - 2)]
        pygame.draw.polygon(surface, palette["rock"], pts)
        pygame.draw.polygon(surface, body,
                            [(cx - 10, cy - 3), (cx - 12, cy - 28), (cx - 4, cy - 39),
                             (cx + 9, cy - 36), (cx + 11, cy - 5)])
        # petals
        for i in range(5):
            a = -1.4 + i * 0.7 + sway * 0.04
            px = cx + math.cos(a) * 17
            py = cy - 38 + math.sin(a) * 10
            pygame.draw.polygon(surface, thorn,
                                [(cx - 4, cy - 36), (px, py - 10), (cx + 5, cy - 33)])
        # maw
        maw_y = cy - 34 + (self.recoil * 8)
        maw = 7 + (1 if self.charge > 0 else 0)
        pygame.draw.circle(surface, (18, 12, 16), (int(cx + self.facing * 4), int(maw_y)), maw)
        if self.charge > 0:
            k = 1.0 - self.charge / 0.55
            draw_glow(surface, (cx + self.facing * 4, maw_y), 22,
                      danger, int(80 + k * 140), 2.0)
            pygame.draw.circle(surface, (255, 180, 150),
                               (int(cx + self.facing * 4), int(maw_y)), max(2, int(2 + k * 5)))
        # eyes
        for side in (-1, 1):
            pygame.draw.circle(surface, danger, (int(cx + side * 6), int(cy - 22)), 2)
        # grass base
        for i in range(3):
            gx = cx - 18 + i * 18
            pygame.draw.lines(surface, palette["moss"],
                              False, [(gx, cy), (gx - 5, cy - 14), (gx - 10, cy - 18)], 2)


@dataclass
class Projectile:
    x: float
    y: float
    vx: float
    vy: float
    life: float = 4.5
    radius: float = 8.0
    phase: float = 0.0
    alive: bool = True

    @property
    def rect(self) -> pygame.FRect:
        r = self.radius
        return pygame.FRect(self.x - r, self.y - r, r * 2, r * 2)

    def update(self, dt: float, world) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 46.0 * dt
        self.life -= dt
        self.phase += dt * 10.0
        if self.life <= 0:
            self.alive = False
            return
        if world.point_solid(self.x, self.y):
            self.alive = False

    def draw(self, surface, cam_x, cam_y, palette) -> None:
        sx = self.x - cam_x
        sy = self.y - cam_y
        if sx < -40 or sx > 1320 or sy < -40 or sy > 760:
            return
        draw_glow(surface, (sx, sy), 22, palette["danger"], 80, 2.0)
        pts = []
        for i in range(6):
            a = self.phase + i * math.pi / 3
            r = 9 if i % 2 == 0 else 4
            pts.append((sx + math.cos(a) * r, sy + math.sin(a) * r))
        pygame.draw.polygon(surface, palette["thorn"], pts)
        pygame.draw.circle(surface, (40, 20, 24), (int(sx), int(sy)), 3)
        pygame.draw.circle(surface, palette["danger"], (int(sx), int(sy)), 2)
