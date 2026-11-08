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

    def __init__(self, x: float, y: float, facing: int = -1, speed_mult: float = 1.0):
        super().__init__(x, y, 42, 46)
        self.facing = facing
        self.speed_mult = speed_mult
        self.cooldown = (0.85 + (x % 7) * 0.10) / max(0.5, speed_mult)
        self.charge = 0.0
        self.recoil = 0.0

    def update(self, dt, player, world):
        self.time += dt
        self.recoil = max(0.0, self.recoil - dt)
        if self.charge > 0:
            self.charge -= dt
            if self.charge <= 0:
                self._fire(player, world)
                self.cooldown = 1.75 / max(0.5, self.speed_mult)
        else:
            self.cooldown -= dt
            dx = player.x + player.w / 2 - (self.x + self.w / 2)
            dy = player.y + player.h / 2 - (self.y + 14)
            if self.cooldown <= 0 and abs(dx) < 620 and abs(dy) < 310:
                self.charge = 0.45 / max(0.6, self.speed_mult)
                self.facing = 1 if dx > 0 else -1

    def _fire(self, player, world):
        px = self.x + self.w / 2 + self.facing * 16
        py = self.y + 10
        tx = player.x + player.w / 2 + player.vx * 0.14
        ty = player.y + player.h / 2
        dx, dy = tx - px, ty - py
        dist = max(1.0, math.hypot(dx, dy))
        speed = 335.0 * self.speed_mult
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
    gravity: float = 46.0
    bomb: bool = False

    @property
    def rect(self) -> pygame.FRect:
        r = self.radius
        return pygame.FRect(self.x - r, self.y - r, r * 2, r * 2)

    def update(self, dt: float, world) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
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
        if self.bomb:
            draw_glow(surface, (sx, sy), 28, palette["danger"], 115, 2.0)
            pygame.draw.circle(surface, (36, 18, 22), (int(sx), int(sy)), 9)
            pygame.draw.circle(surface, palette["danger"], (int(sx), int(sy)), 6)
            pygame.draw.circle(surface, (255, 235, 180), (int(sx - 2), int(sy - 2)), 3)
            # trailing spark tail
            tx = sx - self.vx * 0.03
            ty = sy - self.vy * 0.03
            pygame.draw.line(surface, palette["accent2"], (sx, sy), (tx, ty), 2)
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


class Jumper(Enemy):
    kind = "jumper"

    def __init__(self, x: float, y: float, min_x: float, max_x: float,
                 speed: float = 95.0, speed_mult: float = 1.0):
        super().__init__(x, y, 36, 28)
        self.min_x = min_x
        self.max_x = max_x
        self.speed = speed * speed_mult
        self.speed_mult = speed_mult
        self.vx = self.speed
        self.vy = 0.0
        self.on_ground = True
        self.ground_y = y
        self.jump_timer = 0.9 / max(0.4, speed_mult)
        self.jump_prep = 0.0
        self.facing = 1

    def update(self, dt: float, player, world) -> None:
        self.time += dt
        if self.on_ground:
            if self.jump_prep > 0:
                self.jump_prep -= dt
                if self.jump_prep <= 0:
                    self.on_ground = False
                    self.vy = -560.0 * (0.88 + 0.22 * self.speed_mult)
                    dx = (player.x + player.w / 2) - (self.x + self.w / 2)
                    self.facing = 1 if dx > 0 else -1
                    self.vx = self.facing * self.speed * 1.85
            else:
                self.x += self.vx * dt
                if self.x < self.min_x:
                    self.x = self.min_x
                    self.vx = abs(self.vx)
                    self.facing = 1
                elif self.x + self.w > self.max_x:
                    self.x = self.max_x - self.w
                    self.vx = -abs(self.vx)
                    self.facing = -1
                self.jump_timer -= dt
                dx = abs((player.x + player.w / 2) - (self.x + self.w / 2))
                if self.jump_timer <= 0 and dx < 520:
                    self.jump_prep = 0.24
                    self.jump_timer = 1.25 / max(0.5, self.speed_mult)
        else:
            self.vy += 1280.0 * dt
            self.x += self.vx * dt
            self.y += self.vy * dt
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.vy = 0.0
                self.on_ground = True
                self.x = clamp(self.x, self.min_x, self.max_x - self.w)
                self.vx = self.facing * self.speed

    def draw(self, surface, cam_x, cam_y, time_s, palette):
        cx = self.x + self.w / 2 - cam_x
        cy = self.y + self.h / 2 - cam_y
        if cx < -80 or cx > 1360 or cy < -80 or cy > 800:
            return
        prep = self.jump_prep > 0
        squash = 0.7 if prep else (1.2 if not self.on_ground and self.vy < 0 else 1.0)
        dark = (22, 28, 30)
        body = palette["rock_light"]
        danger = palette["danger"]
        accent = palette["accent"]
        # shadow
        if self.on_ground:
            pygame.draw.ellipse(surface, (0, 0, 0, 80), (cx - 18, cy + 10, 36, 8))
        # coiled hind legs
        leg_offset = 6 if prep else 0
        for side in (-1, 1):
            lx = cx + side * 12
            knee = (lx + side * 8, cy + 2 + leg_offset)
            foot = (lx + side * 4, cy + 12)
            pygame.draw.lines(surface, dark, False, [(cx, cy), knee, foot], 3)
            pygame.draw.circle(surface, palette["thorn_dark"], (int(foot[0]), int(foot[1])), 2)
        # body shell
        bw, bh = int(32 * (1.2 if prep else 1.0)), int(22 * squash)
        pygame.draw.ellipse(surface, dark, (cx - bw // 2, cy - bh // 2, bw, bh))
        pygame.draw.ellipse(surface, body, (cx - (bw - 6) // 2, cy - (bh - 4) // 2, bw - 6, bh - 4))
        # dorsal spine
        pygame.draw.polygon(surface, palette["thorn"],
                            [(cx - 4, cy - bh // 2), (cx, cy - bh // 2 - 8), (cx + 4, cy - bh // 2)])
        # glowing eyes
        eye_col = danger if prep else accent
        eye_x = cx + self.facing * 9
        pygame.draw.circle(surface, eye_col, (int(eye_x), int(cy - 2)), 3)
        draw_glow(surface, (eye_x, cy - 2), 16, eye_col, 70 if prep else 35, 2.0)


class Shocker(Enemy):
    kind = "shocker"

    def __init__(self, x: float, y: float, patrol_dist: float = 75.0,
                 patrol_speed: float = 1.45, speed_mult: float = 1.0):
        super().__init__(x, y, 36, 36)
        self.anchor_x = x
        self.anchor_y = y
        self.patrol_dist = patrol_dist
        self.speed = patrol_speed * speed_mult
        self.speed_mult = speed_mult
        self.pulse_timer = 1.65 / max(0.4, speed_mult)
        self.is_pulsing = False
        self.pulse_life = 0.0

    def update(self, dt: float, player, world) -> None:
        self.time += dt
        self.x = self.anchor_x + math.cos(self.time * self.speed * 0.65 + self.phase) * (self.patrol_dist * 0.45)
        self.y = self.anchor_y + math.sin(self.time * self.speed + self.phase) * self.patrol_dist
        self.pulse_timer -= dt
        if self.pulse_timer <= 0:
            self.is_pulsing = True
            self.pulse_life = 0.55
            self.pulse_timer = 1.85 / max(0.4, self.speed_mult)
        if self.pulse_life > 0:
            self.pulse_life -= dt
            if self.pulse_life <= 0:
                self.is_pulsing = False

    @property
    def hit_rect(self) -> pygame.FRect:
        if self.is_pulsing:
            return pygame.FRect(self.x - 20, self.y - 20, self.w + 40, self.h + 40)
        return pygame.FRect(self.x + 3, self.y + 3, self.w - 6, self.h - 6)

    def draw(self, surface, cam_x, cam_y, time_s, palette):
        cx = self.x + self.w / 2 - cam_x
        cy = self.y + self.h / 2 - cam_y
        if cx < -100 or cx > 1380 or cy < -100 or cy > 820:
            return
        t = self.time
        pulse_col = (140, 240, 255)
        core_col = palette["orb"]
        # charge telegraph right before pulsing
        if not self.is_pulsing and self.pulse_timer < 0.35:
            pygame.draw.circle(surface, (*pulse_col, 110), (int(cx), int(cy)), 26, 1)
        # shock field when pulsing
        if self.is_pulsing:
            r = int(34 + math.sin(t * 26.0) * 5)
            draw_glow(surface, (cx, cy), r * 2, pulse_col, 130, 2.2)
            pygame.draw.circle(surface, (200, 250, 255), (int(cx), int(cy)), r, 2)
            for i in range(6):
                a = t * 14.0 + i * (math.tau / 6)
                px = cx + math.cos(a) * (r + 5)
                py = cy + math.sin(a) * (r + 5)
                pygame.draw.line(surface, (255, 255, 255), (cx, cy), (px, py), 1)
        # electric prongs
        draw_glow(surface, (cx, cy), 28, core_col, 65, 2.0)
        pygame.draw.circle(surface, (26, 32, 40), (int(cx), int(cy)), 14)
        pygame.draw.circle(surface, core_col, (int(cx), int(cy)), 10)
        pygame.draw.circle(surface, (255, 255, 255), (int(cx), int(cy)), 4)
        for i in range(4):
            a = t * 3.8 + i * (math.pi / 2)
            tip_x = cx + math.cos(a) * 19
            tip_y = cy + math.sin(a) * 19
            base_x = cx + math.cos(a) * 11
            base_y = cy + math.sin(a) * 11
            pygame.draw.line(surface, palette["thorn"], (base_x, base_y), (tip_x, tip_y), 2)
            pygame.draw.circle(surface, core_col, (int(tip_x), int(tip_y)), 2)


class Ghost(Enemy):
    kind = "ghost"

    def __init__(self, x: float, y: float, speed: float = 78.0, speed_mult: float = 1.0):
        super().__init__(x, y, 34, 40)
        self.speed = speed * speed_mult
        self.speed_mult = speed_mult
        self.alpha = 1.0
        self.phased = False

    def update(self, dt: float, player, world) -> None:
        self.time += dt
        cycle = (self.time * 1.65 + self.phase) % math.tau
        val = math.sin(cycle)
        self.phased = val < -0.32
        self.alpha = clamp(0.28 + 0.72 * ((val + 1.0) / 2.0), 0.20, 1.0)
        # stalk towards player
        dx = (player.x + player.w / 2) - (self.x + self.w / 2)
        dy = (player.y + player.h / 2) - (self.y + self.h / 2)
        dist = max(1.0, math.hypot(dx, dy))
        if dist < 720:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * (self.speed * 0.78) * dt

    @property
    def hit_rect(self) -> pygame.FRect:
        if self.phased or self.alpha < 0.50:
            return pygame.FRect(-9999, -9999, 0, 0)
        return pygame.FRect(self.x + 4, self.y + 4, self.w - 8, self.h - 8)

    def draw(self, surface, cam_x, cam_y, time_s, palette):
        cx = self.x + self.w / 2 - cam_x
        cy = self.y + self.h / 2 - cam_y
        if cx < -80 or cx > 1360 or cy < -80 or cy > 800:
            return
        t = self.time
        a_int = int(220 * self.alpha)
        col = palette["gem"]
        danger = palette["danger"]
        shroud = pygame.Surface((60, 68), pygame.SRCALPHA)
        pts = [
            (30, 4), (46, 16), (48, 44),
            (40 + math.sin(t * 4.0) * 4, 60),
            (30, 52),
            (20 - math.sin(t * 4.0) * 4, 60),
            (12, 44), (14, 16),
        ]
        pygame.draw.polygon(shroud, (*col, a_int), pts)
        pygame.draw.polygon(shroud, (240, 220, 255, min(255, a_int + 20)), pts, 1)
        eye_col = danger if not self.phased else col
        pygame.draw.circle(shroud, (*eye_col, a_int), (24, 26), 3)
        pygame.draw.circle(shroud, (*eye_col, a_int), (36, 26), 3)
        surface.blit(shroud, (cx - 30, cy - 34))
        if not self.phased:
            draw_glow(surface, (cx, cy), 32, eye_col, int(55 * self.alpha), 2.0)


class Roller(Enemy):
    kind = "roller"

    def __init__(self, x: float, y: float, min_x: float, max_x: float,
                 speed: float = 215.0, speed_mult: float = 1.0):
        super().__init__(x, y, 36, 36)
        self.min_x = min_x
        self.max_x = max_x
        self.speed = speed * speed_mult
        self.speed_mult = speed_mult
        self.vx = self.speed
        self.angle = 0.0

    def update(self, dt: float, player, world) -> None:
        self.time += dt
        self.x += self.vx * dt
        self.angle += (self.vx / 16.0) * dt * 10.0
        if self.x < self.min_x:
            self.x = self.min_x
            self.vx = abs(self.vx)
        elif self.x + self.w > self.max_x:
            self.x = self.max_x - self.w
            self.vx = -abs(self.vx)

    def draw(self, surface, cam_x, cam_y, time_s, palette):
        cx = self.x + self.w / 2 - cam_x
        cy = self.y + self.h / 2 - cam_y
        if cx < -80 or cx > 1360 or cy < -80 or cy > 800:
            return
        r = 16
        danger = palette["danger"]
        thorn = palette["thorn"]
        pygame.draw.ellipse(surface, (0, 0, 0, 75), (cx - 16, cy + 12, 32, 6))
        pygame.draw.circle(surface, (30, 26, 32), (int(cx), int(cy)), r)
        pygame.draw.circle(surface, palette["rock_dark"], (int(cx), int(cy)), r - 3)
        for i in range(8):
            a = self.angle + i * (math.pi / 4)
            tx = cx + math.cos(a) * (r + 7)
            ty = cy + math.sin(a) * (r + 7)
            bx1 = cx + math.cos(a - 0.25) * (r - 2)
            by1 = cy + math.sin(a - 0.25) * (r - 2)
            bx2 = cx + math.cos(a + 0.25) * (r - 2)
            by2 = cy + math.sin(a + 0.25) * (r - 2)
            pygame.draw.polygon(surface, thorn, [(bx1, by1), (tx, ty), (bx2, by2)])
        pygame.draw.circle(surface, danger, (int(cx), int(cy)), 4)
        draw_glow(surface, (cx, cy), 18, danger, 65, 2.0)


class Crusher(Enemy):
    """Suspended runic monolith that locks on, trembles, and slams down violently."""
    kind = "crusher"

    def __init__(self, x: float, ground_y: float, hover_height: float = 195.0,
                 speed_mult: float = 1.0):
        w, h = 50, 56
        hover_y = ground_y - hover_height - h
        super().__init__(x, hover_y, w, h)
        self.hover_y = hover_y
        self.slam_y = ground_y - h
        self.speed_mult = speed_mult
        self.state = "idle"   # idle | telegraph | slam | rest | rise
        self.timer = 0.5 + (x % 9) * 0.14

    def update(self, dt: float, player, world) -> None:
        self.time += dt
        if self.state == "idle":
            self.y = self.hover_y + math.sin(self.time * 2.6 + self.phase) * 5.0
            self.timer -= dt
            dx = abs((player.x + player.w / 2) - (self.x + self.w / 2))
            if (dx < 165 and self.timer <= 0.4) or self.timer <= -1.1:
                self.state = "telegraph"
                self.timer = 0.27 / max(0.6, self.speed_mult)
        elif self.state == "telegraph":
            self.timer -= dt
            if self.timer <= 0:
                self.state = "slam"
        elif self.state == "slam":
            self.y += 940.0 * self.speed_mult * dt
            if self.y >= self.slam_y:
                self.y = self.slam_y
                self.state = "rest"
                self.timer = 0.42 / max(0.6, self.speed_mult)
        elif self.state == "rest":
            self.timer -= dt
            if self.timer <= 0:
                self.state = "rise"
        elif self.state == "rise":
            self.y -= 240.0 * self.speed_mult * dt
            if self.y <= self.hover_y:
                self.y = self.hover_y
                self.state = "idle"
                self.timer = 0.85 / max(0.5, self.speed_mult)

    @property
    def hit_rect(self) -> pygame.FRect:
        return pygame.FRect(self.x + 3, self.y + 3, self.w - 6, self.h - 4)

    def draw(self, surface, cam_x, cam_y, time_s, palette):
        jx = math.sin(self.time * 55.0) * 3.0 if self.state == "telegraph" else 0.0
        sx = self.x - cam_x + jx
        sy = self.y - cam_y
        if sx < -100 or sx > 1380 or sy < -200 or sy > 840:
            return
        cx = sx + self.w / 2
        danger = palette["danger"]
        accent = palette["accent"]
        hot = self.state in ("telegraph", "slam", "rest")
        rune_col = danger if hot else accent

        # chain / energy tether reaching upward
        top_y = self.hover_y - cam_y - 60
        pygame.draw.line(surface, palette["rock_dark"], (cx, top_y), (cx, sy), 4)
        pygame.draw.line(surface, rune_col, (cx, top_y), (cx, sy), 1)

        # ground shadow telegraph directly below
        gy_screen = self.slam_y + self.h - cam_y
        pygame.draw.ellipse(surface, (*danger, 95 if hot else 38),
                            (cx - 24, gy_screen - 4, 48, 8))

        # monolith slab
        body = pygame.Rect(int(sx), int(sy), int(self.w), int(self.h))
        pygame.draw.rect(surface, (18, 22, 28), body, border_radius=5)
        pygame.draw.rect(surface, palette["rock_light"], body.inflate(-6, -6), border_radius=4)
        pygame.draw.rect(surface, palette["rock"], body.inflate(-12, -12), border_radius=3)

        # bottom crusher spikes
        for i in range(4):
            tx = sx + 5 + i * 11
            pygame.draw.polygon(surface, palette["thorn"],
                                [(tx, sy + self.h - 2), (tx + 5, sy + self.h + 9), (tx + 10, sy + self.h - 2)])

        # glowing carved rune-eyes
        draw_glow(surface, (cx, sy + self.h * 0.48), 34, rune_col, 95 if hot else 45, 2.0)
        pygame.draw.polygon(surface, rune_col,
                            [(cx, sy + 14), (cx + 10, sy + 27), (cx, sy + 40), (cx - 10, sy + 27)], 2)
        for side in (-1, 1):
            pygame.draw.circle(surface, rune_col, (int(cx + side * 12), int(sy + 20)), 3)


class Bomber(Enemy):
    """Aerial cinder-wyrm patrolling overhead and dropping arcing firebombs."""
    kind = "bomber"

    def __init__(self, x: float, y: float, patrol_w: float = 210.0,
                 speed_mult: float = 1.0):
        super().__init__(x, y, 44, 28)
        self.anchor_x = x
        self.anchor_y = y
        self.patrol_w = patrol_w
        self.speed_mult = speed_mult
        self.cooldown = (1.1 + (x % 5) * 0.18) / max(0.5, speed_mult)
        self.facing = -1

    def update(self, dt: float, player, world) -> None:
        self.time += dt
        t = self.time * 1.15 * self.speed_mult + self.phase
        new_x = self.anchor_x + math.sin(t) * self.patrol_w
        self.facing = 1 if math.cos(t) >= 0 else -1
        self.x = new_x
        self.y = self.anchor_y + math.sin(t * 2.1) * 22.0

        self.cooldown -= dt
        dx = (player.x + player.w / 2) - (self.x + self.w / 2)
        dy = (player.y + player.h / 2) - (self.y + self.h)
        if self.cooldown <= 0 and abs(dx) < 520 and -80 < dy < 440:
            vx = clamp(dx * 0.85, -240.0, 240.0) * self.speed_mult
            vy = -70.0
            world.spawn_bomb(self.x + self.w / 2, self.y + self.h, vx, vy)
            self.cooldown = 1.75 / max(0.5, self.speed_mult)

    def draw(self, surface, cam_x, cam_y, time_s, palette):
        cx = self.x + self.w / 2 - cam_x
        cy = self.y + self.h / 2 - cam_y
        if cx < -100 or cx > 1380 or cy < -100 or cy > 820:
            return
        t = self.time
        d = self.facing
        flap = math.sin(t * 11.0 + self.phase) * 13.0
        danger = palette["danger"]
        accent2 = palette["accent2"]

        draw_glow(surface, (cx, cy + 6), 36, danger, 65, 2.2)
        # armored wyrm wings
        for side in (-1, 1):
            wing = [
                (cx + side * 4, cy - 2),
                (cx + side * 28, cy - 12 - flap),
                (cx + side * 20, cy + 5 - flap * 0.3),
            ]
            polygon_alpha(surface, danger, wing, 145)
            pygame.draw.lines(surface, palette["thorn"], True, wing, 1)
        # body & glowing bomb-sac underneath
        pygame.draw.ellipse(surface, (28, 22, 26), (cx - 16, cy - 9, 32, 16))
        pygame.draw.circle(surface, accent2 if self.cooldown < 0.35 else danger,
                           (int(cx), int(cy + 8)), 6)
        pygame.draw.circle(surface, (255, 240, 200), (int(cx + d * 10), int(cy - 3)), 3)
