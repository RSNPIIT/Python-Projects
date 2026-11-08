"""The Wayfarer: movement, climbing, wall-jumps, dash and procedural art."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from .constants import (
    AIR_ACCEL,
    AIR_FRICTION,
    CLIMB_HORIZONTAL,
    CLIMB_SPEED,
    COYOTE_TIME,
    DASH_COOLDOWN,
    DASH_SPEED,
    DASH_TIME,
    GRAVITY,
    GROUND_ACCEL,
    GROUND_FRICTION,
    INVULN_TIME,
    JUMP_BUFFER,
    JUMP_CUT,
    JUMP_CUT_SPEED,
    JUMP_HOLD_GRAVITY,
    JUMP_HOLD_TIME,
    JUMP_VELOCITY,
    MAX_ARMOR,
    MAX_FALL,
    MAX_HEARTS,
    MOVE_SPEED,
    PLAYER,
    PLAYER_H,
    PLAYER_W,
    WALL_JUMP_X,
    WALL_JUMP_Y,
    WALL_SLIDE_SPEED,
    HERO_CLOAKS,
    HERO_SCARFS,
    HERO_HEADGEARS,
    HERO_TRAILS,
)
from .utils import clamp, color_lerp, draw_glow, glow_surface, lerp

ART = 1.16


@dataclass
class Inputs:
    left: bool = False
    right: bool = False
    up: bool = False
    down: bool = False
    jump_pressed: bool = False
    jump_held: bool = False
    dash_pressed: bool = False


class Player:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.w = PLAYER_W
        self.h = PLAYER_H
        self.vx = 0.0
        self.vy = 0.0
        self.facing = 1
        self.hearts = 3
        self.armor = 0
        self.jump_boost = 0.0
        self.jump_boosting = False
        self.on_ground = False
        self.ground_solid = None
        self.wall_dir = 0
        self.coyote = 0.0
        self.jump_buffer = 0.0
        self.drop_timer = 0.0
        self.wall_lock = 0.0
        self.climbing = False
        self.vine = None
        self.dashing = False
        self.dash_timer = 0.0
        self.dash_cooldown = 0.0
        self.dash_dir = 1
        self.air_dash_used = False
        self.invuln = 0.0
        self.hurt_timer = 0.0
        self.time = 0.0
        self.run_t = 0.0
        self.land_squash = 0.0
        self.squash_x = 1.0
        self.squash_y = 1.0
        self.events: list[str] = []
        self.was_on_ground = False
        self.scarf: list[list[float]] = []
        self._init_scarf()
        self.anim_state = "idle"
        # customization options
        self.custom_cloak = 0
        self.custom_scarf = 0
        self.custom_headgear = 0
        self.custom_trail = 0
        self.trail_particles: list[dict] = []
        self.ghost_afterimages: list[dict] = []

    # ------------------------------------------------------------------
    @property
    def rect(self) -> pygame.FRect:
        return pygame.FRect(self.x, self.y, self.w, self.h)

    @property
    def center(self) -> tuple[float, float]:
        return (self.x + self.w / 2, self.y + self.h / 2)

    def _init_scarf(self) -> None:
        nx = self.x + self.w / 2
        ny = self.y + 12
        self.scarf = [[nx, ny] for _ in range(10)]

    def reset(self, x: float, y: float, hearts: int | None = None) -> None:
        self.x, self.y = x, y
        self.vx = self.vy = 0.0
        self.facing = 1
        self.on_ground = False
        self.ground_solid = None
        self.climbing = False
        self.vine = None
        self.dashing = False
        self.dash_timer = 0.0
        self.dash_cooldown = 0.0
        self.air_dash_used = False
        self.coyote = 0.0
        self.jump_buffer = 0.0
        self.jump_boost = 0.0
        self.jump_boosting = False
        self.invuln = 0.0
        self.hurt_timer = 0.0
        self.hearts = hearts if hearts is not None else self.hearts
        self.land_squash = 0.0
        self._init_scarf()

    def heal(self, amount: int = 1) -> bool:
        before = self.hearts
        self.hearts = min(MAX_HEARTS, self.hearts + amount)
        return self.hearts > before

    def add_armor(self, amount: int = 1) -> bool:
        before = self.armor
        self.armor = min(MAX_ARMOR, self.armor + amount)
        return self.armor > before

    # ------------------------------------------------------------------
    def update(self, dt: float, inp: Inputs, world) -> None:
        self.time += dt
        self.events.clear()
        self.jump_boosting = False
        self.invuln = max(0.0, self.invuln - dt)
        self.hurt_timer = max(0.0, self.hurt_timer - dt)
        self.dash_cooldown = max(0.0, self.dash_cooldown - dt)
        self.drop_timer = max(0.0, self.drop_timer - dt)
        self.wall_lock = max(0.0, self.wall_lock - dt)
        self.land_squash = max(0.0, self.land_squash - dt)
        self.coyote = max(0.0, self.coyote - dt)
        self.jump_buffer = max(0.0, self.jump_buffer - dt)

        if inp.jump_pressed:
            self.jump_buffer = JUMP_BUFFER

        dir_x = (1 if inp.right else 0) - (1 if inp.left else 0)
        if dir_x:
            self.facing = dir_x

        self.was_on_ground = self.on_ground
        if self.on_ground:
            self.coyote = COYOTE_TIME

        vine = world.vine_at(self.rect)

        # anchor onto a vine with up/down
        if (not self.climbing and vine is not None and (inp.up or inp.down)
                and not self.dashing and self.dash_timer <= 0):
            self.climbing = True
            self.vine = vine
            self.vx = 0.0
            self.vy = 0.0
            self.events.append("grab")

        if self.climbing:
            self._update_climb(dt, inp, dir_x, vine)
        else:
            self._update_normal(dt, inp, dir_x, vine)

        solids = world.solids_near(self.rect)
        self._move(dt, solids)
        self._update_wall_state(solids)
        self._support_check(solids)

        if self.on_ground:
            self.air_dash_used = False
            if not self.was_on_ground:
                self.events.append("land")
                self.land_squash = 0.11
        if self.on_ground and abs(self.vx) > 12 and not self.climbing:
            self.run_t += dt * (0.7 + abs(self.vx) / MOVE_SPEED)
        else:
            self.run_t += dt * 0.4

        self._update_scarf(dt)
        self._update_custom_trails(dt)
        self._update_anim_state()

    # ------------------------------------------------------------------
    def _update_climb(self, dt, inp, dir_x, vine) -> None:
        self.on_ground = False
        self.vx = 0.0
        self.vy = 0.0
        if vine is None:
            self.climbing = False
            return
        self.vine = vine
        if inp.jump_pressed:
            self.climbing = False
            self.vy = -JUMP_VELOCITY * 0.92
            self.vx = dir_x * 240.0 if dir_x else self.facing * 180.0
            self.facing = dir_x or self.facing
            self.jump_buffer = 0.0
            self.jump_boost = JUMP_HOLD_TIME
            self.events.append("jump")
            return
        self.x += dir_x * CLIMB_HORIZONTAL * dt
        climb_dir = (1 if inp.down else 0) - (1 if inp.up else 0)
        self.y += climb_dir * CLIMB_SPEED * dt
        # clamp to the vine: at the top the feet rest level with the ledge
        min_y = vine.top - self.h + 20
        max_y = vine.bottom - self.h + 10
        self.y = clamp(self.y, min_y, max_y)
        if climb_dir > 0 and self.y >= max_y - 0.5:
            self.climbing = False
            self.vine = None
            return
        # stay attached while the body still overlaps the vine
        if not world_vine_contains(vine, self.rect):
            self.climbing = False
            self.vine = None

    def _update_normal(self, dt, inp, dir_x, vine) -> None:
        # start a dash
        if (inp.dash_pressed and self.dash_cooldown <= 0.0 and not self.dashing
                and (self.on_ground or not self.air_dash_used)):
            self.dashing = True
            self.dash_timer = DASH_TIME
            self.dash_cooldown = DASH_COOLDOWN
            self.dash_dir = dir_x or self.facing
            self.facing = self.dash_dir
            self.vy = 0.0
            self.vx = self.dash_dir * DASH_SPEED
            self.air_dash_used = not self.on_ground
            self.events.append("dash")

        if self.dashing:
            self.dash_timer -= dt
            self.vx = self.dash_dir * DASH_SPEED
            self.vy = 0.0
            if self.dash_timer <= 0:
                self.dashing = False
                self.vx *= 0.62
            return

        # drop through a one-way ledge
        if (self.on_ground and self.ground_solid is not None
                and self.ground_solid.one_way and inp.down and inp.jump_pressed):
            self.drop_timer = 0.22
            self.y += 6
            self.on_ground = False
            self.ground_solid = None
            self.jump_buffer = 0.0
            self.events.append("drop")
            return

        # horizontal control
        if self.wall_lock <= 0:
            target = dir_x * MOVE_SPEED
            accel = GROUND_ACCEL if self.on_ground else AIR_ACCEL
            if dir_x == 0:
                friction = GROUND_FRICTION if self.on_ground else AIR_FRICTION
                if self.vx > 0:
                    self.vx = max(0.0, self.vx - friction * dt)
                elif self.vx < 0:
                    self.vx = min(0.0, self.vx + friction * dt)
            else:
                if self.vx < target:
                    self.vx = min(target, self.vx + accel * dt)
                elif self.vx > target:
                    self.vx = max(target, self.vx - accel * dt)

        # gravity + hold-to-rise: a held Space bends gravity while ascending
        self.jump_boosting = self.jump_boost > 0.0 and inp.jump_held and self.vy < 0.0
        if self.jump_boosting:
            self.vy += GRAVITY * JUMP_HOLD_GRAVITY * dt
            self.jump_boost = max(0.0, self.jump_boost - dt)
        else:
            self.vy += GRAVITY * dt
        if self.vy > MAX_FALL:
            self.vy = MAX_FALL
        sliding = (not self.on_ground and self.wall_dir != 0 and dir_x == self.wall_dir
                   and self.vy > 0)
        if sliding:
            self.vy = min(self.vy, WALL_SLIDE_SPEED)
            if not hasattr(self, "_slide_timer"):
                self._slide_timer = 0.0
            self._slide_timer += dt
            if self._slide_timer > 0.08:
                self._slide_timer = 0.0
                self.events.append("slide")
        # release-to-cut: tapping Space gives a short hop, holding goes higher
        if not inp.jump_held and self.vy < -JUMP_CUT_SPEED:
            self.vy = -JUMP_CUT_SPEED

        # jumps
        if self.jump_buffer > 0:
            if self.on_ground or self.coyote > 0:
                self.vy = -JUMP_VELOCITY
                self.on_ground = False
                self.coyote = 0.0
                self.jump_buffer = 0.0
                self.jump_boost = JUMP_HOLD_TIME
                self.events.append("jump")
            elif self.wall_dir != 0:
                self.vy = -WALL_JUMP_Y
                self.vx = -self.wall_dir * WALL_JUMP_X
                self.facing = -self.wall_dir
                self.wall_lock = 0.16
                self.jump_buffer = 0.0
                self.jump_boost = JUMP_HOLD_TIME * 0.8
                self.events.append("wall_jump")
            elif vine is not None and self.jump_buffer > 0:
                pass

    # ------------------------------------------------------------------
    def _move(self, dt: float, solids) -> None:
        if self.climbing:
            return
        # horizontal
        self.x += self.vx * dt
        rect = self.rect
        for s in solids:
            if s.one_way:
                continue
            if rect.colliderect(s.rect):
                if self.vx > 0:
                    self.x = s.rect.left - self.w
                elif self.vx < 0:
                    self.x = s.rect.right
                self.vx = 0.0
                rect = self.rect
        # vertical
        prev_bottom = self.y + self.h
        self.y += self.vy * dt
        rect = self.rect
        landed = False
        for s in solids:
            sr = s.rect
            if s.one_way:
                if self.vy <= 0 or self.drop_timer > 0:
                    continue
                if rect.colliderect(sr) and prev_bottom <= sr.top + 8:
                    self.y = sr.top - self.h
                    self.vy = 0.0
                    self.on_ground = True
                    self.ground_solid = s
                    landed = True
                    rect = self.rect
                continue
            if rect.colliderect(sr):
                if self.vy > 0:
                    self.y = sr.top - self.h
                    self.vy = 0.0
                    self.on_ground = True
                    self.ground_solid = s
                    landed = True
                elif self.vy < 0:
                    self.y = sr.bottom
                    self.vy = 0.0
                rect = self.rect
        if not landed and self.vy != 0:
            self.on_ground = False
            self.ground_solid = None

    def _support_check(self, solids) -> None:
        if self.climbing or self.vy < -30:
            return
        feet = pygame.FRect(self.x + 3, self.y + self.h - 1, self.w - 6, 4)
        for s in solids:
            if s.one_way and self.drop_timer > 0:
                continue
            if s.rect.colliderect(feet) and self.y + self.h <= s.rect.top + 5:
                self.on_ground = True
                self.ground_solid = s
                return
        if self.vy >= 0:
            self.on_ground = False
            self.ground_solid = None

    def _update_wall_state(self, solids) -> None:
        self.wall_dir = 0
        if self.on_ground or self.climbing:
            return
        probe = pygame.FRect(self.x - 3, self.y + 6, self.w + 6, self.h - 12)
        for s in solids:
            if s.one_way:
                continue
            if probe.colliderect(s.rect):
                if s.rect.centerx < self.x + self.w / 2:
                    self.wall_dir = -1
                else:
                    self.wall_dir = 1
                return

    # ------------------------------------------------------------------
    def _update_scarf(self, dt: float) -> None:
        neck_x = self.x + self.w / 2 - self.facing * 3
        neck_y = self.y + 14
        pts = self.scarf
        pts[0][0] = neck_x
        pts[0][1] = neck_y
        k = min(1.0, dt * 16.0)
        for i in range(1, len(pts)):
            px, py = pts[i - 1]
            x, y = pts[i]
            x += (px - x) * k - self.vx * 0.009 * dt
            y += (py - y) * k + 22.0 * dt
            x += math.sin(self.time * 5.0 + i * 0.8) * 9.0 * dt
            pts[i][0], pts[i][1] = x, y

    def _update_anim_state(self) -> None:
        if self.dashing:
            self.anim_state = "dash"
        elif self.climbing:
            self.anim_state = "climb"
        elif not self.on_ground:
            self.anim_state = "jump" if self.vy < 0 else "fall"
        elif abs(self.vx) > 20:
            self.anim_state = "run"
        else:
            self.anim_state = "idle"

    def _update_custom_trails(self, dt: float) -> None:
        trail_id = HERO_TRAILS[self.custom_trail % len(HERO_TRAILS)]["id"]

        # Update active trail particles
        alive_p = []
        for p in self.trail_particles:
            p["life"] -= dt
            if p["life"] > 0:
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                alive_p.append(p)
        self.trail_particles = alive_p

        # Update ghost images
        alive_g = []
        for g in self.ghost_afterimages:
            g["life"] -= dt
            if g["life"] > 0:
                alive_g.append(g)
        self.ghost_afterimages = alive_g

        # Spawn custom particles based on movement
        speed = math.hypot(self.vx, self.vy)
        cx, cy = self.x + self.w / 2, self.y + self.h - 8
        if trail_id == "flame" and (speed > 35 or self.dashing):
            if random.random() < 0.65:
                self.trail_particles.append({
                    "x": cx + random.uniform(-6, 6),
                    "y": cy + random.uniform(-6, 2),
                    "vx": random.uniform(-18, 18) - self.vx * 0.1,
                    "vy": random.uniform(-50, -15),
                    "life": 0.45,
                    "max_life": 0.45,
                    "r": random.randint(2, 4),
                    "type": "flame",
                })
        elif trail_id == "stars" and (speed > 35 or self.dashing):
            if random.random() < 0.5:
                self.trail_particles.append({
                    "x": cx + random.uniform(-10, 10),
                    "y": cy - random.uniform(2, 24),
                    "vx": random.uniform(-12, 12),
                    "vy": random.uniform(-18, 10),
                    "life": 0.5,
                    "max_life": 0.5,
                    "r": random.randint(1, 3),
                    "type": "star",
                })
        elif trail_id == "ghost" and (self.dashing or speed > 220):
            if not self.ghost_afterimages or (self.time - self.ghost_afterimages[-1].get("t", 0)) > 0.05:
                self.ghost_afterimages.append({
                    "x": self.x,
                    "y": self.y,
                    "facing": self.facing,
                    "life": 0.35,
                    "max_life": 0.35,
                    "t": self.time,
                })
        elif trail_id == "prismatic" and speed > 30:
            if random.random() < 0.6:
                self.trail_particles.append({
                    "x": cx + random.uniform(-8, 8),
                    "y": cy + random.uniform(-12, 2),
                    "vx": random.uniform(-14, 14),
                    "vy": random.uniform(-25, 5),
                    "life": 0.55,
                    "max_life": 0.55,
                    "r": random.randint(2, 3),
                    "type": "prism",
                    "phase": self.time * 5.0,
                })

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        if self.invuln > 0.22 and int(self.time * 22) % 2 == 0:
            return
        sx = self.x + self.w / 2 - cam_x
        sy = self.y + self.h - cam_y
        d = self.facing
        hurt = clamp(self.hurt_timer / 0.28, 0.0, 1.0)

        # squash & stretch
        target_x, target_y = 1.0, 1.0
        if self.anim_state in ("jump", "fall"):
            stretch = clamp(abs(self.vy) / 1700.0, 0.0, 0.16)
            target_y = 1.0 + stretch
            target_x = 1.0 - stretch * 0.55
        if self.land_squash > 0:
            target_x = 1.16
            target_y = 0.84
        if self.dashing:
            target_x = 1.2
            target_y = 0.86
        if self.climbing:
            target_x = 0.94
            target_y = 1.03
        self.squash_x = lerp(self.squash_x, target_x, 0.25)
        self.squash_y = lerp(self.squash_y, target_y, 0.25)
        ax, ay = self.squash_x, self.squash_y

        def P(x: float, y: float) -> tuple[float, float]:
            return (sx + x * d * ax * ART, sy + y * ay * ART)

        # shadow
        if self.on_ground and not self.climbing:
            pygame.draw.ellipse(surface, (0, 0, 0, 70),
                                (sx - 19, sy - 5, 38, 9))

        # Hero customization settings
        cloak_cfg = HERO_CLOAKS[self.custom_cloak % len(HERO_CLOAKS)]
        scarf_cfg = HERO_SCARFS[self.custom_scarf % len(HERO_SCARFS)]
        headgear_cfg = HERO_HEADGEARS[self.custom_headgear % len(HERO_HEADGEARS)]
        trail_cfg = HERO_TRAILS[self.custom_trail % len(HERO_TRAILS)]
        headgear_id = headgear_cfg["id"]
        trail_id = trail_cfg["id"]

        custom_trim = cloak_cfg["trim"]
        custom_eye = cloak_cfg["eye"]
        custom_scarf = scarf_cfg["scarf"]
        custom_scarf_dark = scarf_cfg["scarf_dark"]

        if trail_id == "prismatic":
            pr_phase = self.time * 4.0
            custom_scarf = (
                int(140 + 110 * math.sin(pr_phase)),
                int(140 + 110 * math.sin(pr_phase + 2.094)),
                int(140 + 110 * math.sin(pr_phase + 4.188)),
            )
            custom_scarf_dark = (
                int(custom_scarf[0] * 0.65),
                int(custom_scarf[1] * 0.65),
                int(custom_scarf[2] * 0.65),
            )

        # Draw custom ghost afterimages
        for g in self.ghost_afterimages:
            ga = int(110 * (g["life"] / g["max_life"]))
            if ga > 5:
                gx = g["x"] + self.w / 2 - cam_x
                gy = g["y"] + self.h - cam_y
                gs = pygame.Surface((PLAYER_W * 2, PLAYER_H * 2), pygame.SRCALPHA)
                pygame.draw.ellipse(gs, (*custom_trim, ga), (8, 12, PLAYER_W + 8, PLAYER_H + 4))
                surface.blit(gs, (gx - PLAYER_W, gy - PLAYER_H * 1.5))

        # Draw custom trail particles
        for p in self.trail_particles:
            px = p["x"] - cam_x
            py = p["y"] - cam_y
            frac = p["life"] / p["max_life"]
            if p["type"] == "flame":
                col = (255, int(120 + 120 * frac), int(40 * frac))
                pygame.draw.circle(surface, col, (int(px), int(py)), max(1, int(p["r"] * frac)))
            elif p["type"] == "star":
                col = (230, 245, 255)
                draw_glow(surface, (px, py), 12, col, int(60 * frac), 2.0)
                pygame.draw.circle(surface, col, (int(px), int(py)), max(1, int(p["r"] * frac)))
            elif p["type"] == "prism":
                pph = p.get("phase", 0)
                col = (
                    int(140 + 110 * math.sin(pph)),
                    int(140 + 110 * math.sin(pph + 2.094)),
                    int(140 + 110 * math.sin(pph + 4.188)),
                )
                pygame.draw.circle(surface, col, (int(px), int(py)), max(1, int(p["r"] * frac)))

        # scarf trail (drawn behind the body)
        pts = [(p[0] - cam_x, p[1] - cam_y) for p in self.scarf]
        if len(pts) > 2:
            for i in range(len(pts) - 1, 0, -1):
                a = i / len(pts)
                width = max(1, int(6 * (1 - a) + 2))
                col = color_lerp(custom_scarf, custom_scarf_dark, a)
                pygame.draw.line(surface, col, pts[i], pts[i - 1], width)
            pygame.draw.circle(surface, custom_scarf, (int(pts[1][0]), int(pts[1][1])), 3)

        cloak = cloak_cfg["cloak"]
        cloak_light = cloak_cfg["cloak_light"]
        if hurt:
            cloak = color_lerp(cloak, (255, 235, 220), hurt * 0.75)
            cloak_light = color_lerp(cloak_light, (255, 255, 255), hurt * 0.6)

        bob = 0.0
        if self.anim_state == "idle":
            bob = math.sin(self.time * 2.6) * 1.4
        elif self.anim_state == "run":
            bob = abs(math.sin(self.run_t * 12.0)) * 2.2
        sy_body = sy + bob

        def B(x: float, y: float) -> tuple[float, float]:
            return (sx + x * d * ax * ART, sy_body + y * ay * ART)

        # legs
        leg_col = (22, 26, 32)
        boot = PLAYER["boot"]
        if self.climbing:
            phase = math.sin(self.run_t * 9.0) * 4
            for side in (-1, 1):
                hip = B(side * 5, -15)
                foot = B(side * 8 + phase * 0.4 * side, -1)
                pygame.draw.line(surface, leg_col, hip, foot, 5)
                pygame.draw.circle(surface, boot, (int(foot[0]), int(foot[1])), 3)
        elif self.anim_state in ("jump", "fall"):
            knee = B(-4, -10)
            foot = B(-11, 1)
            pygame.draw.line(surface, leg_col, B(-3, -16), knee, 5)
            pygame.draw.line(surface, leg_col, knee, foot, 5)
            pygame.draw.circle(surface, boot, (int(foot[0]), int(foot[1])), 3)
            foot2 = B(10, -5)
            pygame.draw.line(surface, leg_col, B(4, -15), foot2, 5)
            pygame.draw.circle(surface, boot, (int(foot2[0]), int(foot2[1])), 3)
        else:
            swing = math.sin(self.run_t * 12.0) * 7.0 if self.anim_state == "run" else 0.0
            for side, ph in ((-1, swing), (1, -swing)):
                hip = B(side * 4, -14)
                foot = B(side * 3 + ph, 0)
                pygame.draw.line(surface, leg_col, hip, foot, 5)
                pygame.draw.ellipse(surface, boot, (foot[0] - 4, foot[1] - 3, 8, 5))

        # cloak body
        if self.climbing:
            cloak_pts = [B(-9, -42), B(9, -42), B(14, -20), B(12, -4), B(0, 1),
                         B(-12, -4), B(-14, -20)]
        else:
            flare = 2.0 + (0.0 if self.anim_state == "idle" else 1.5)
            cloak_pts = [B(-8, -41), B(8, -41), B(13, -26), B(16 + flare, -2),
                         B(0, 0), B(-16 - flare, -2), B(-13, -26)]
        pygame.draw.polygon(surface, cloak, cloak_pts)
        pygame.draw.polygon(surface, color_lerp(cloak, custom_trim, 0.22), cloak_pts, 1)
        # lit panel on the facing side
        lit = [B(4, -38), B(11, -25), B(14, -4), B(2, -1), B(4, -22)]
        pygame.draw.polygon(surface, cloak_light, lit)
        # rim light
        pygame.draw.lines(surface, custom_trim, False,
                          [B(7, -39), B(12, -26), B(15, -3)], 1)
        # belt
        pygame.draw.line(surface, custom_scarf_dark, B(-9, -17), B(9, -17), 2)
        pygame.draw.rect(surface, custom_trim,
                         (int(B(0, -18)[0]) - 2, int(B(0, -18)[1]) - 2, 4, 4))

        # arms
        arm_col = leg_col
        if self.climbing:
            for side in (-1, 1):
                start = B(side * 7, -33)
                hand = B(side * 8, -44 + math.sin(self.run_t * 9 + side) * 2)
                pygame.draw.line(surface, cloak, start, hand, 5)
                pygame.draw.circle(surface, (218, 200, 184), (int(hand[0]), int(hand[1])), 2)
        elif self.dashing:
            pygame.draw.line(surface, cloak, B(6, -30), B(-9, -22), 5)
            pygame.draw.line(surface, cloak, B(-2, -28), B(-12, -16), 4)
        else:
            swing = math.sin(self.run_t * 12.0) * 3.0 if self.anim_state == "run" else 0
            pygame.draw.line(surface, cloak, B(2, -30), B(-6, -19 + swing), 4)
            # lantern arm
            hand = B(11, -22 - swing * 0.4)
            pygame.draw.line(surface, cloak, B(5, -31), hand, 4)

        # head & custom headgear
        if headgear_id == "hood":
            hood_pts = [B(-9, -32), B(-9, -45), B(0, -52), B(9, -45), B(10, -32), B(0, -29)]
            pygame.draw.polygon(surface, cloak, hood_pts)
            pygame.draw.polygon(surface, color_lerp(cloak, custom_trim, 0.3), hood_pts, 1)
            pygame.draw.line(surface, color_lerp(cloak, custom_trim, 0.18),
                             B(0, -51), B(-1, -42), 1)
        elif headgear_id == "crown":
            hood_pts = [B(-9, -32), B(-9, -43), B(0, -46), B(9, -43), B(10, -32), B(0, -29)]
            pygame.draw.polygon(surface, cloak, hood_pts)
            crown_pts = [B(-8, -44), B(-9, -54), B(-4, -48), B(0, -57), B(4, -48), B(9, -54), B(8, -44)]
            pygame.draw.polygon(surface, (255, 215, 60), crown_pts)
            pygame.draw.polygon(surface, (255, 245, 140), crown_pts, 1)
            pygame.draw.circle(surface, (255, 60, 80), (int(B(0, -49)[0]), int(B(0, -49)[1])), 2)
        elif headgear_id == "horns":
            hood_pts = [B(-9, -32), B(-9, -43), B(0, -46), B(9, -43), B(10, -32), B(0, -29)]
            pygame.draw.polygon(surface, cloak, hood_pts)
            # curved bramble horns
            pygame.draw.lines(surface, (240, 210, 175), False,
                              [B(-5, -42), B(-12, -54), B(-18, -50)], 3)
            pygame.draw.line(surface, (240, 210, 175), B(-10, -49), B(-14, -45), 2)
            pygame.draw.lines(surface, (255, 230, 200), False,
                              [B(5, -42), B(12, -54), B(18, -50)], 3)
            pygame.draw.line(surface, (255, 230, 200), B(10, -49), B(14, -45), 2)
        elif headgear_id == "bandana":
            hood_pts = [B(-9, -32), B(-9, -43), B(0, -46), B(9, -43), B(10, -32), B(0, -29)]
            pygame.draw.polygon(surface, cloak, hood_pts)
            band_pts = [B(-9, -41), B(-9, -46), B(9, -46), B(9, -41)]
            pygame.draw.polygon(surface, custom_scarf, band_pts)
            plate_x = int(B(-4, -46)[0])
            plate_y = int(B(-4, -46)[1])
            pygame.draw.rect(surface, (220, 235, 245), (plate_x, plate_y, 8, 4), border_radius=1)
            # ribbons blowing backward
            sw = math.sin(self.time * 12.0) * 3
            rb_start = B(-8 * d, -43)
            pygame.draw.line(surface, custom_scarf, rb_start,
                             (rb_start[0] - d * (14 + sw), rb_start[1] + 4), 2)
            pygame.draw.line(surface, custom_scarf_dark, rb_start,
                             (rb_start[0] - d * (18 - sw), rb_start[1] + 8), 2)
        elif headgear_id == "halo":
            hood_pts = [B(-9, -32), B(-9, -44), B(0, -48), B(9, -44), B(10, -32), B(0, -29)]
            pygame.draw.polygon(surface, cloak, hood_pts)
            halo_c = B(0, -57)
            draw_glow(surface, halo_c, 20, (255, 235, 120), 85, 2.0)
            pygame.draw.ellipse(surface, (255, 245, 150),
                                (halo_c[0] - 11, halo_c[1] - 4, 22, 8), 2)
        elif headgear_id == "wizard":
            brim_pts = [B(-14, -43), B(14, -43), B(12, -41), B(-12, -41)]
            pygame.draw.polygon(surface, (18, 22, 28), brim_pts)
            cone_pts = [B(-8, -43), B(-16 * d, -64), B(8, -43)]
            pygame.draw.polygon(surface, cloak, cone_pts)
            pygame.draw.polygon(surface, custom_trim, cone_pts, 1)
            pygame.draw.rect(surface, (255, 215, 60), (int(B(-3, -46)[0]), int(B(-3, -46)[1]), 6, 3))
        else:
            hood_pts = [B(-9, -32), B(-9, -45), B(0, -52), B(9, -45), B(10, -32), B(0, -29)]
            pygame.draw.polygon(surface, cloak, hood_pts)
            pygame.draw.polygon(surface, color_lerp(cloak, custom_trim, 0.3), hood_pts, 1)

        face = B(d * 2.5, -39)
        pygame.draw.circle(surface, (12, 16, 22), (int(face[0]), int(face[1])),
                           int(6.2 * ART))
        pygame.draw.arc(surface, custom_trim,
                        (int(face[0] - 7 * ART), int(face[1] - 7 * ART),
                         int(14 * ART), int(14 * ART)), 3.4, 6.1, 1)
        # eyes
        eye_glow = custom_eye
        e1 = B(d * 2, -41)
        e2 = B(d * 7.5, -40)
        for ep in (e1, e2):
            pygame.draw.circle(surface, eye_glow, (int(ep[0]), int(ep[1])), 2)
            draw_glow(surface, ep, 12, eye_glow, 95, 2.4)

        # lantern (only when not climbing)
        if not self.climbing:
            lx, ly = B(13, -19 + math.sin(self.time * 2.2) * 1.2)
            pygame.draw.line(surface, (120, 110, 90), (lx, ly - 5), (lx, ly + 1), 1)
            draw_glow(surface, (lx, ly), 36, PLAYER["lantern"], 72, 2.2)
            pygame.draw.circle(surface, PLAYER["lantern"], (int(lx), int(ly)), 4)
            pygame.draw.circle(surface, (255, 244, 210), (int(lx), int(ly)), 2)
            pygame.draw.arc(surface, (90, 80, 60),
                            (int(lx - 6), int(ly - 9), 12, 12), 3.4, 6.1, 1)

        # held-jump speed lines around the feet
        if self.jump_boosting:
            for side in (-1, 1):
                pygame.draw.line(surface, (135, 235, 215),
                                 (sx + side * (11 + side), sy + 7),
                                 (sx + side * (17 + side), sy + 17), 1)
                pygame.draw.line(surface, (85, 175, 165),
                                 (sx + side * 7, sy + 4),
                                 (sx + side * 10, sy + 11), 1)

        # armor bubble
        if self.armor > 0 and not self.climbing:
            pulse = 0.5 + 0.5 * math.sin(self.time * 3.4)
            r = int(27 + pulse * 3)
            box = (sx - r, sy - 70, r * 2, 78)
            pygame.draw.ellipse(surface, (48, 112, 126), box, 1)
            pygame.draw.arc(surface, (128, 232, 255), box,
                            0.3 + self.time * 1.2, 1.9 + self.time * 1.2, 2)
            pygame.draw.arc(surface, (86, 190, 215), box,
                            3.5 + self.time * 0.9, 5.2 + self.time * 0.9, 1)

    # ------------------------------------------------------------------
    def draw_hint(self, surface, cam_x, cam_y, world) -> None:
        """A tiny context hint when standing next to a climbable vine."""
        if self.climbing:
            return
        vine = world.vine_at(self.rect.inflate(60, 40))
        if vine is None:
            return
        sx = self.x + self.w / 2 - cam_x
        sy = self.y - cam_y - 24
        global _HINT_FONT
        if _HINT_FONT is None:
            _HINT_FONT = pygame.font.SysFont("avenirnext", 13, bold=True)
        img = _HINT_FONT.render("W / S  CLIMB", True, (220, 240, 230))
        img.set_alpha(190)
        surface.blit(img, (int(sx - img.get_width() / 2), int(sy)))


_HINT_FONT = None


def world_vine_contains(vine, rect) -> bool:
    cx = rect.centerx
    return (vine.x - 26 <= cx <= vine.x + 26
            and rect.bottom >= vine.top
            and rect.top <= vine.bottom)
