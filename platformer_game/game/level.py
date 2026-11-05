"""Procedural bramble: chunks, climbing routes, thorns and collectibles.

The level is an endless horizontal ribbon of 1440px chunks.  Each chunk picks
a feature (gap, climb, tier, shrine, spitter, thorn run, rest) and the ground
height drifts gently between chunks.  Biomes cycle every nine chunks and the
whole wheel repeats forever.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

import pygame

from .constants import (
    BIOMES,
    BIOME_COUNT,
    CHUNKS_PER_BIOME,
    CHUNK_W,
    PLAYER_H,
    SCREEN_H,
    SCREEN_W,
    TILE,
)
from .enemies import Crawler, Flyer, Projectile, Spitter
from .pickups import Checkpoint, Pickup
from .utils import clamp, color_lerp, draw_glow


@dataclass
class Solid:
    x: float
    y: float
    w: float
    h: float
    kind: str = "ground"     # ground | ledge | stone | moving
    one_way: bool = False
    jag: list[float] = field(default_factory=list)
    seed: int = 0
    base_y: float = 0.0
    move_amp: float = 0.0
    move_speed: float = 1.0
    move_phase: float = 0.0

    @property
    def rect(self) -> pygame.FRect:
        return pygame.FRect(self.x, self.y, self.w, self.h)


@dataclass
class Vine:
    x: float
    top: float
    bottom: float
    phase: float = 0.0
    seed: int = 0


@dataclass
class Hazard:
    x: float
    y: float
    w: float
    h: float = 26.0
    seed: int = 0

    @property
    def rect(self) -> pygame.FRect:
        return pygame.FRect(self.x, self.y - self.h, self.w, self.h)


@dataclass
class Decor:
    kind: str
    x: float
    y: float
    scale: float = 1.0
    seed: int = 0


@dataclass
class Chunk:
    index: int
    start_x: float
    ground_y: float
    biome: int
    solids: list[Solid] = field(default_factory=list)
    hazards: list[Hazard] = field(default_factory=list)
    vines: list[Vine] = field(default_factory=list)
    decor: list[Decor] = field(default_factory=list)
    pickups: list[Pickup] = field(default_factory=list)
    enemies: list = field(default_factory=list)
    checkpoints: list[Checkpoint] = field(default_factory=list)

    @property
    def end_x(self) -> float:
        return self.start_x + CHUNK_W


PARTICLES = None  # set by Game so enemies could spawn fx later if needed


class World:
    def __init__(self, seed: int, mode: str = "loop") -> None:
        self.seed = seed
        self.mode = mode
        self.rng = random.Random(seed)
        self.chunks: dict[int, Chunk] = {}
        self.projectiles: list[Projectile] = []
        self.time = 0.0
        self.ground_y = 640.0
        self.last_chunk_index = -1
        self.ensure_until(SCREEN_W * 2.2)
        start = self.chunks[0]
        self.spawn_x = 170.0
        self.spawn_y = start.ground_y - PLAYER_H - 1
        self.loop_at_start = 1

    # ==================================================================
    # generation
    # ==================================================================
    def ensure_until(self, x: float) -> None:
        while self.last_chunk_index * CHUNK_W + CHUNK_W < x:
            self.last_chunk_index += 1
            self.chunks[self.last_chunk_index] = self._make_chunk(self.last_chunk_index)

    def _chunk_index(self, x: float) -> int:
        return max(0, int(x // CHUNK_W))

    def get_chunk(self, index: int) -> Chunk | None:
        return self.chunks.get(index)

    def _rng(self) -> random.Random:
        return self.rng

    # ------------------------------------------------------------------
    def _make_chunk(self, index: int) -> Chunk:
        start = index * CHUNK_W
        biome = (index // CHUNKS_PER_BIOME) % BIOME_COUNT
        if index == 0:
            self.ground_y = 640.0
        else:
            self.ground_y = clamp(self.ground_y + self.rng.choice([-40, -20, 0, 0, 20, 40]),
                                  550.0, 700.0)
        chunk = Chunk(index=index, start_x=start, ground_y=self.ground_y, biome=biome)
        segments: list[list[float]] = [[start, start + CHUNK_W]]
        difficulty = clamp(index / 55.0, 0.0, 1.0)

        if index == 0:
            self._f_intro(chunk, difficulty, segments)
        elif index % 8 == 3:
            self._f_rest(chunk, difficulty, segments)
        elif index % 5 == 2:
            self._f_climb(chunk, difficulty, segments)
        else:
            roll = self.rng.random()
            if roll < 0.18:
                self._f_flat(chunk, difficulty, segments)
            elif roll < 0.40:
                self._f_gap(chunk, difficulty, segments)
            elif roll < 0.55:
                self._f_climb(chunk, difficulty, segments)
            elif roll < 0.69:
                self._f_tiers(chunk, difficulty, segments)
            elif roll < 0.82:
                self._f_thorn_run(chunk, difficulty, segments)
            elif roll < 0.93:
                self._f_shrine(chunk, difficulty, segments)
            else:
                self._f_spitter(chunk, difficulty, segments)

        # ground colliders from the surviving segments
        for x0, x1 in segments:
            if x1 - x0 < 60:
                continue
            n = max(8, int((x1 - x0) / 52))
            jag = [self.rng.uniform(-3.0, 4.0) for _ in range(n)]
            jag[0] = jag[-1] = 0.0
            chunk.solids.append(Solid(x0, chunk.ground_y, x1 - x0, 640,
                                      "ground", False, jag,
                                      self.rng.randint(1, 99999)))

        # resting points
        if index % 6 == 0 and not chunk.checkpoints:
            self._auto_checkpoint(chunk, segments)
        # extra collectibles and set dressing
        self._dress_ground(chunk, segments, difficulty)
        self._ensure_gem(chunk, difficulty)
        if index % 4 == 1:
            self._ensure_heart(chunk, segments)
        if index > 0 and index % 5 == 1:
            self._ensure_armor(chunk, segments)
        if self.mode == "trial" and index % 3 == 1:
            self._place_chrono(chunk, segments)

        # keep holes from becoming unjumpable traps at the very start
        return chunk

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _carve(self, segments, x0, x1):
        out = []
        for a, b in segments:
            if x1 <= a or x0 >= b:
                out.append([a, b])
                continue
            if x0 - a >= 110:
                out.append([a, x0])
            if b - x1 >= 110:
                out.append([x1, b])
        if out:
            segments[:] = out

    def _add_ledge(self, chunk, x, y, w, one_way=True):
        n = max(5, int(w / 32))
        jag = [self.rng.uniform(-2.5, 3.0) for _ in range(n)]
        jag[0] = jag[-1] = 0.0
        chunk.solids.append(Solid(x, y, w, 24, "ledge", one_way, jag,
                                  self.rng.randint(1, 99999)))

    def _add_stone(self, chunk, x, y, w, h):
        chunk.solids.append(Solid(x, y, w, h, "stone", False, [], self.rng.randint(1, 99999)))

    def _add_moving_ledge(self, chunk, x, base_y, w, amp=40.0, speed=1.0):
        """A one-way platform that drifts vertically around ``base_y``."""
        n = max(5, int(w / 32))
        jag = [self.rng.uniform(-2.5, 3.0) for _ in range(n)]
        jag[0] = jag[-1] = 0.0
        phase = self.rng.uniform(0.0, math.tau)
        y = base_y + math.sin(phase) * amp
        solid = Solid(x, y, w, 24, "moving", True, jag,
                      self.rng.randint(1, 99999))
        solid.base_y = base_y
        solid.move_amp = amp
        solid.move_speed = speed
        solid.move_phase = phase
        chunk.solids.append(solid)

    def _add_hazard(self, chunk, x, y, w, h=26):
        if w < 30:
            return
        chunk.hazards.append(Hazard(x, y, w, h, self.rng.randint(1, 99999)))

    def _add_vine(self, chunk, x, top, bottom):
        chunk.vines.append(Vine(x, top, bottom, self.rng.uniform(0, 6.28),
                                self.rng.randint(1, 99999)))

    def _add_coin(self, chunk, x, y, phase=None):
        chunk.pickups.append(Pickup("coin", x, y,
                                    phase if phase is not None else self.rng.uniform(0, 6.28)))

    def _add_gem(self, chunk, x, y):
        chunk.pickups.append(Pickup("gem", x, y, self.rng.uniform(0, 6.28)))

    def _add_heart(self, chunk, x, y):
        chunk.pickups.append(Pickup("heart", x, y, self.rng.uniform(0, 6.28)))

    def _add_armor(self, chunk, x, y):
        chunk.pickups.append(Pickup("armor", x, y, self.rng.uniform(0, 6.28)))

    def _add_chrono(self, chunk, x, y):
        chunk.pickups.append(Pickup("chrono", x, y, self.rng.uniform(0, 6.28)))

    def _coin_arc(self, chunk, cx, cy, count=5, spread=160, height=46):
        for i in range(count):
            t = i / max(1, count - 1)
            x = cx + (t - 0.5) * spread
            y = cy - math.sin(t * math.pi) * height
            self._add_coin(chunk, x, y)

    def _coin_line(self, chunk, x0, x1, y, count=4):
        for i in range(count):
            t = i / max(1, count - 1)
            self._add_coin(chunk, x0 + (x1 - x0) * t, y)

    def _add_crawler(self, chunk, x, gy, min_x, max_x, speed=70):
        chunk.enemies.append(Crawler(max(min_x, x), gy - 26, min_x, max_x, speed,
                                     direction=self.rng.choice((-1, 1))))

    def _add_flyer(self, chunk, x, y, aw=120, ah=48, speed=0.9):
        chunk.enemies.append(Flyer(x, y, aw, ah, speed))

    def _add_spitter(self, chunk, x, gy, facing=1):
        chunk.enemies.append(Spitter(x, gy - 46, facing))

    def _checkpoint(self, chunk, x, y=None):
        if y is None:
            y = chunk.ground_y
        chunk.checkpoints.append(Checkpoint(x, y))

    def _add_decor(self, chunk, kind, x, y, scale=1.0):
        chunk.decor.append(Decor(kind, x, y, scale, self.rng.randint(1, 99999)))

    # ------------------------------------------------------------------
    # features
    # ------------------------------------------------------------------
    def _f_intro(self, chunk, d, segments):
        gy = chunk.ground_y
        self._coin_arc(chunk, chunk.start_x + 450, gy - 100, 6, 190, 42)
        self._add_ledge(chunk, chunk.start_x + 700, gy - 118, 200)
        self._add_coin(chunk, chunk.start_x + 760, gy - 150)
        self._add_coin(chunk, chunk.start_x + 820, gy - 150)
        self._add_gem(chunk, chunk.start_x + 930, gy - 165)
        self._add_armor(chunk, chunk.start_x + 820, gy - 152)
        self._add_moving_ledge(chunk, chunk.start_x + 1180, gy - 165, 165, 36, 1.0)
        self._checkpoint(chunk, chunk.start_x + 1080)
        self._add_decor(chunk, "lantern", chunk.start_x + 320, gy)
        self._add_decor(chunk, "sign", chunk.start_x + 470, gy)
        self._add_decor(chunk, "mushroom", chunk.start_x + 610, gy)
        self._add_decor(chunk, "crystal", chunk.start_x + 1240, gy, 0.9)

    def _f_flat(self, chunk, d, segments):
        gy = chunk.ground_y
        start = chunk.start_x
        n = 1 + (1 if self.rng.random() < 0.35 + d * 0.3 else 0)
        for i in range(n):
            hx = start + 280 + i * 380 + self.rng.randint(-40, 60)
            hw = self.rng.randint(62, 104)
            self._add_hazard(chunk, hx, gy, hw)
            self._coin_arc(chunk, hx + hw / 2, gy - 46, 3, 110, 24)
        self._add_ledge(chunk, start + 780, gy - 132, self.rng.randint(150, 220))
        self._add_crawler(chunk, start + 520, gy, start + 300, start + 720,
                          self.rng.uniform(58, 82))
        if self.rng.random() < 0.55:
            self._add_flyer(chunk, start + 1040, gy - 190, 80, 38, 0.8)
        self._coin_line(chunk, start + 880, start + 1180, gy - 165, 4)
        if self.rng.random() < 0.6:
            self._add_moving_ledge(chunk, start + 990, gy - 210, 150, 42, 1.05)

    def _f_gap(self, chunk, d, segments):
        gy = chunk.ground_y
        start = chunk.start_x
        gw = int(120 + 50 * d + self.rng.randint(-10, 15))
        gx = start + 530 + self.rng.randint(-70, 90)
        self._carve(segments, gx, gx + gw)
        self._coin_arc(chunk, gx + gw / 2, gy - 70, 5, gw + 60, 46)
        if gw > 145:
            self._add_moving_ledge(chunk, gx + gw / 2 - 55, gy - 128, 110, 46, 1.15)
        else:
            self._add_ledge(chunk, gx + gw / 2 - 50, gy - 88, 100)
        self._add_flyer(chunk, gx + gw / 2, gy - 235, gw * 0.5, 36, 1.05)
        if self.rng.random() < 0.7:
            self._add_ledge(chunk, gx - 40, gy - 150, 140)
        self._add_hazard(chunk, gx + gw + 150, gy, 74)
        self._add_decor(chunk, "crystal", gx - 30, gy)
        if self.rng.random() < 0.4:
            self._add_crawler(chunk, start + 980, gy, start + 940, start + 1250, 74)

    def _f_climb(self, chunk, d, segments):
        gy = chunk.ground_y
        start = chunk.start_x
        vx = start + 700
        self._add_vine(chunk, vx, gy - 352, gy + 6)
        self._add_ledge(chunk, vx - 235, gy - 118, 190)
        self._add_ledge(chunk, vx + 68, gy - 228, 195)
        self._add_ledge(chunk, vx - 218, gy - 332, 230)
        self._add_gem(chunk, vx - 120, gy - 365)
        self._add_coin(chunk, vx + 16, gy - 90)
        self._add_coin(chunk, vx + 18, gy - 160)
        self._add_coin(chunk, vx + 14, gy - 230)
        self._add_coin(chunk, vx + 12, gy - 300)
        self._add_coin(chunk, vx - 135, gy - 148)
        self._add_coin(chunk, vx + 155, gy - 258)
        self._add_stone(chunk, start + 1040, gy - 76, 56, 76)
        self._add_hazard(chunk, start + 300, gy, 76)
        self._add_crawler(chunk, start + 470, gy, start + 410, start + 660, 68)
        self._add_flyer(chunk, vx + 10, gy - 280, 90, 42, 0.85)
        if self.rng.random() < 0.45:
            self._add_ledge(chunk, start + 40, gy - 160, 150)
        self._add_decor(chunk, "crystal", start + 920, gy, 1.1)

    def _f_tiers(self, chunk, d, segments):
        gy = chunk.ground_y
        start = chunk.start_x
        self._add_ledge(chunk, start + 285, gy - 96, 210)
        self._add_ledge(chunk, start + 585, gy - 186, 190)
        self._add_ledge(chunk, start + 850, gy - 278, 225)
        self._add_gem(chunk, start + 960, gy - 312)
        for i, (x, y) in enumerate(((370, 126), (660, 216), (935, 308))):
            self._add_coin(chunk, start + x, gy - y)
        self._add_hazard(chunk, start + 520, gy, 70)
        self._add_hazard(chunk, start + 750, gy, 64)
        self._add_crawler(chunk, start + 1110, gy, start + 1060, start + 1340, 80)
        self._add_flyer(chunk, start + 760, gy - 220, 100, 52, 0.9)
        self._coin_arc(chunk, start + 520, gy - 34, 3, 130, 26)
        self._add_decor(chunk, "lantern", start + 430, gy)

    def _f_thorn_run(self, chunk, d, segments):
        gy = chunk.ground_y
        start = chunk.start_x
        spots = [start + 300, start + 520, start + 740]
        for i, x in enumerate(spots):
            w = 62 + int(24 * d)
            self._add_hazard(chunk, x, gy, w)
            self._coin_arc(chunk, x + w / 2, gy - 58, 3, w + 70, 34)
        self._add_ledge(chunk, start + 620, gy - 150, 170)
        self._add_moving_ledge(chunk, start + 900, gy - 185, 140, 34, 1.0)
        self._add_crawler(chunk, start + 990, gy, start + 940, start + 1240, 78)
        if self.rng.random() < 0.5:
            self._add_flyer(chunk, start + 900, gy - 200, 90, 40, 0.75)
        self._add_gem(chunk, start + 950, gy - 200)
        self._add_decor(chunk, "crystal", start + 1180, gy)

    def _f_shrine(self, chunk, d, segments):
        gy = chunk.ground_y
        start = chunk.start_x
        self._add_ledge(chunk, start + 500, gy - 112, 150)
        self._add_moving_ledge(chunk, start + 430, gy - 175, 125, 38, 0.9)
        self._add_ledge(chunk, start + 735, gy - 205, 150)
        self._add_ledge(chunk, start + 615, gy - 300, 250)
        self._add_gem(chunk, start + 690, gy - 336)
        self._add_gem(chunk, start + 815, gy - 336)
        self._add_heart(chunk, start + 750, gy - 336)
        self._add_hazard(chunk, start + 570, gy, 170)
        self._add_flyer(chunk, start + 700, gy - 250, 110, 55, 0.95)
        self._add_crawler(chunk, start + 1180, gy, start + 1100, start + 1330, 72)
        for i in range(4):
            self._add_coin(chunk, start + 560 + i * 55, gy - 330)

    def _f_spitter(self, chunk, d, segments):
        gy = chunk.ground_y
        start = chunk.start_x
        self._add_ledge(chunk, start + 640, gy - 194, 270)
        self._add_spitter(chunk, start + 745, gy - 194, -1)
        self._add_vine(chunk, start + 545, gy - 194, gy + 4)
        self._add_hazard(chunk, start + 610, gy, 150)
        self._add_coin(chunk, start + 700, gy - 226)
        self._add_coin(chunk, start + 790, gy - 226)
        self._add_coin(chunk, start + 880, gy - 226)
        self._add_crawler(chunk, start + 1110, gy, start + 1050, start + 1330, 82)
        self._add_flyer(chunk, start + 380, gy - 190, 100, 48, 0.8)
        self._add_decor(chunk, "crystal", start + 1020, gy)

    def _f_rest(self, chunk, d, segments):
        gy = chunk.ground_y
        start = chunk.start_x
        self._checkpoint(chunk, start + 330)
        self._add_heart(chunk, start + 760, gy - 40)
        self._add_decor(chunk, "lantern", start + 210, gy)
        self._add_decor(chunk, "lantern", start + 560, gy)
        self._add_decor(chunk, "sign", start + 860, gy)
        self._coin_line(chunk, start + 480, start + 760, gy - 88, 4)
        self._add_ledge(chunk, start + 960, gy - 122, 180)
        self._add_gem(chunk, start + 1050, gy - 156)
        self._add_armor(chunk, start + 600, gy - 70)
        self._add_moving_ledge(chunk, start + 1160, gy - 155, 145, 34, 0.85)
        self._add_decor(chunk, "mushroom", start + 640, gy)
        self._add_decor(chunk, "mushroom", start + 1180, gy, 1.2)

    # ------------------------------------------------------------------
    def _auto_checkpoint(self, chunk, segments):
        gy = chunk.ground_y
        candidates = [chunk.start_x + CHUNK_W - 170, chunk.start_x + 200,
                      chunk.start_x + 860]
        for x in candidates:
            if not any(a <= x <= b for a, b in segments):
                continue
            if any(h.rect.inflate(120, 40).collidepoint(x, gy - 20) for h in chunk.hazards):
                continue
            if any(abs(e.x - x) < 100 for e in chunk.enemies):
                continue
            self._checkpoint(chunk, x, gy)
            return

    def _dress_ground(self, chunk, segments, difficulty):
        gy = chunk.ground_y
        for a, b in segments:
            length = b - a
            if length < 80:
                continue
            n = int(clamp(length / 260, 1, 4))
            for _ in range(n):
                x = self.rng.uniform(a + 30, b - 30)
                kind = self.rng.choices(
                    ["grass", "mushroom", "crystal", "flower", "grass"],
                    weights=[5, 2, 1, 2, 4],
                )[0]
                if kind == "mushroom":
                    scale = self.rng.uniform(0.7, 1.3)
                elif kind == "crystal":
                    scale = self.rng.uniform(0.6, 1.1)
                else:
                    scale = self.rng.uniform(0.7, 1.25)
                self._add_decor(chunk, kind, x, gy, scale)
        # hanging vines under floating ledges are drawn automatically

    def _free_spot(self, chunk, x, y, pad: float = 14.0) -> bool:
        for s in chunk.solids:
            r = s.rect.inflate(pad * 2, pad * 2)
            if r.collidepoint(x, y):
                return False
        for h in chunk.hazards:
            if h.rect.inflate(pad * 2, pad * 2).collidepoint(x, y):
                return False
        return True

    def _ensure_gem(self, chunk, difficulty):
        if any(p.kind == "gem" for p in chunk.pickups):
            return
        if self.rng.random() >= 0.75:
            return
        gy = chunk.ground_y
        for _ in range(10):
            x = chunk.start_x + self.rng.uniform(260, CHUNK_W - 200)
            y = gy - self.rng.uniform(64, 112)
            if self._free_spot(chunk, x, y, 20):
                self._add_gem(chunk, x, y)
                return

    def _ensure_armor(self, chunk, segments):
        if any(p.kind == "armor" for p in chunk.pickups):
            return
        gy = chunk.ground_y
        for _ in range(8):
            x = chunk.start_x + self.rng.uniform(260, CHUNK_W - 220)
            y = gy - 76
            if self._free_spot(chunk, x, y, 18):
                self._add_armor(chunk, x, y)
                return

    def _ensure_heart(self, chunk, segments):
        if any(p.kind == "heart" for p in chunk.pickups):
            return
        gy = chunk.ground_y
        for _ in range(8):
            x = chunk.start_x + self.rng.uniform(200, CHUNK_W - 200)
            y = gy - 70
            if self._free_spot(chunk, x, y, 18):
                self._add_heart(chunk, x, y)
                return

    def _place_chrono(self, chunk, segments):
        gy = chunk.ground_y
        for _ in range(8):
            x = chunk.start_x + self.rng.uniform(300, CHUNK_W - 250)
            y = gy - 110
            if self._free_spot(chunk, x, y, 18):
                self._add_chrono(chunk, x, y)
                return

    # ==================================================================
    # queries
    # ==================================================================
    def _chunk_range(self, x0, x1):
        return range(max(0, int(x0 // CHUNK_W) - 1),
                     int(x1 // CHUNK_W) + 2)

    def solids_near(self, rect) -> list[Solid]:
        out = []
        for i in self._chunk_range(rect.left - 40, rect.right + 40):
            c = self.chunks.get(i)
            if c:
                out.extend(c.solids)
        return out

    def point_solid(self, x, y) -> bool:
        for i in self._chunk_range(x - 1, x + 1):
            c = self.chunks.get(i)
            if not c:
                continue
            for s in c.solids:
                if s.rect.collidepoint(x, y):
                    return True
        return False

    def vine_at(self, rect):
        best = None
        best_d = 1e9
        for i in self._chunk_range(rect.left - 60, rect.right + 60):
            c = self.chunks.get(i)
            if not c:
                continue
            for v in c.vines:
                if rect.bottom >= v.top - 20 and rect.top <= v.bottom + 6:
                    d = abs((rect.left + rect.right) / 2 - v.x)
                    if d <= 32 and d < best_d:
                        best = v
                        best_d = d
        return best

    def hazards_near(self, rect) -> list[Hazard]:
        out = []
        for i in self._chunk_range(rect.left - 40, rect.right + 40):
            c = self.chunks.get(i)
            if c:
                for h in c.hazards:
                    if h.rect.colliderect(rect):
                        out.append(h)
        return out

    def pickups_near(self, rect) -> list[Pickup]:
        out = []
        for i in self._chunk_range(rect.left - 80, rect.right + 80):
            c = self.chunks.get(i)
            if c:
                for p in c.pickups:
                    if not p.collected and p.rect.colliderect(rect):
                        out.append(p)
        return out

    def checkpoints_near(self, rect) -> list[Checkpoint]:
        out = []
        for i in self._chunk_range(rect.left - 80, rect.right + 80):
            c = self.chunks.get(i)
            if c:
                for cp in c.checkpoints:
                    if cp.rect.colliderect(rect):
                        out.append(cp)
        return out

    def enemies_near(self, rect) -> list:
        out = []
        for i in self._chunk_range(rect.left - 240, rect.right + 240):
            c = self.chunks.get(i)
            if c:
                for e in c.enemies:
                    if e.alive and e.hit_rect.colliderect(rect):
                        out.append(e)
        return out

    def visible_chunks(self, cam_x: float) -> list[Chunk]:
        i0 = max(0, int(cam_x // CHUNK_W) - 1)
        i1 = int((cam_x + SCREEN_W) // CHUNK_W) + 1
        return [c for i in range(i0, i1 + 1) if (c := self.chunks.get(i))]

    def ground_y_at(self, x: float) -> float | None:
        for i in self._chunk_range(x - 4, x + 4):
            c = self.chunks.get(i)
            if not c:
                continue
            for s in c.solids:
                if s.kind == "ground" and s.x <= x <= s.x + s.w:
                    return s.y
        return None

    def has_ground_below(self, x: float, y: float, depth: float = 140.0) -> bool:
        for i in self._chunk_range(x - 4, x + 4):
            c = self.chunks.get(i)
            if not c:
                continue
            for s in c.solids:
                if s.one_way:
                    continue
                if s.x <= x <= s.x + s.w and s.y >= y - 10 and s.y <= y + depth:
                    return True
        return False

    def chunk_index_at(self, x: float) -> int:
        return max(0, int(x // CHUNK_W))

    def progress_meters(self, x: float) -> int:
        return max(0, int((x - self.spawn_x) / TILE))

    def loop_number(self, x: float) -> int:
        span = CHUNK_W * CHUNKS_PER_BIOME * BIOME_COUNT
        return max(1, int(max(0.0, x - self.spawn_x) // span) + 1)

    def biome_at(self, x: float) -> int:
        return (self.chunk_index_at(x) // CHUNKS_PER_BIOME) % BIOME_COUNT

    # ==================================================================
    # simulation
    # ==================================================================
    def update_moving_platforms(self, dt: float, player, time_s: float) -> None:
        """Animate elevator platforms and carry the player standing on them."""
        for chunk in self.chunks.values():
            for s in chunk.solids:
                if s.move_amp <= 0.0:
                    continue
                old_y = s.y
                s.y = s.base_y + math.sin(time_s * s.move_speed + s.move_phase) * s.move_amp
                if (player is not None and player.on_ground
                        and player.ground_solid is s):
                    player.y += s.y - old_y

    def update(self, dt: float, player, cam_x: float) -> None:
        self.time += dt
        # projectiles
        alive = []
        for p in self.projectiles:
            p.update(dt, self)
            if p.alive:
                alive.append(p)
        self.projectiles = alive
        # enemies near the camera
        for c in self.visible_chunks(cam_x):
            for e in c.enemies:
                if e.alive and abs(e.x - (cam_x + SCREEN_W / 2)) < SCREEN_W:
                    e.update(dt, player, self)
        # pickups animate
        for c in self.visible_chunks(cam_x):
            for p in c.pickups:
                if not p.collected:
                    p.update(dt, player.x + player.w / 2, player.y + player.h / 2,
                             self.time)
        # prune far-behind chunks
        keep_from = self.chunk_index_at(cam_x) - 22
        if keep_from > 0:
            for i in [k for k in self.chunks if k < keep_from]:
                del self.chunks[i]

    def spawn_projectile(self, x, y, vx, vy, facing=1):
        self.projectiles.append(Projectile(x, y, vx, vy, phase=self.rng.uniform(0, 6.28)))

    # ==================================================================
    # drawing
    # ==================================================================
    def draw_terrain(self, surface: pygame.Surface, cam_x: float, cam_y: float,
                     time_s: float) -> None:
        for c in self.visible_chunks(cam_x):
            pal = BIOMES[c.biome]
            # vines first (behind ledges / ground)
            for v in c.vines:
                self._draw_vine(surface, v, pal, cam_x, cam_y, time_s)
            for s in c.solids:
                if s.x + s.w < cam_x - 120 or s.x > cam_x + SCREEN_W + 120:
                    continue
                if s.kind == "ground":
                    self._draw_ground(surface, s, pal, cam_x, cam_y, time_s)
                elif s.kind == "ledge":
                    self._draw_ledge(surface, s, pal, cam_x, cam_y, time_s)
                elif s.kind == "moving":
                    self._draw_moving(surface, s, pal, cam_x, cam_y, time_s)
                else:
                    self._draw_stone(surface, s, pal, cam_x, cam_y, time_s)
            for h in c.hazards:
                if h.x + h.w < cam_x - 80 or h.x > cam_x + SCREEN_W + 80:
                    continue
                self._draw_hazard(surface, h, pal, cam_x, cam_y, time_s)
            for d in c.decor:
                if d.x < cam_x - 100 or d.x > cam_x + SCREEN_W + 100:
                    continue
                self._draw_decor(surface, d, pal, cam_x, cam_y, time_s)

    def draw_pickups(self, surface, cam_x, cam_y, time_s):
        for c in self.visible_chunks(cam_x):
            for p in c.pickups:
                if not p.collected:
                    p.draw(surface, cam_x, cam_y, time_s)

    def draw_checkpoints(self, surface, cam_x, cam_y, time_s):
        for c in self.visible_chunks(cam_x):
            for cp in c.checkpoints:
                cp.draw(surface, cam_x, cam_y, time_s)

    def draw_enemies(self, surface, cam_x, cam_y, time_s):
        for c in self.visible_chunks(cam_x):
            for e in c.enemies:
                if e.alive:
                    e.draw(surface, cam_x, cam_y, time_s, BIOMES[c.biome])

    def draw_projectiles(self, surface, cam_x, cam_y, time_s):
        for p in self.projectiles:
            p.draw(surface, cam_x, cam_y, BIOMES[self.biome_at(p.x)])

    # ------------------------------------------------------------------
    def _draw_ground(self, surface, s: Solid, pal, cx, cy, t):
        x = s.x - cx
        y = s.y - cy
        if x + s.w < -120 or x > SCREEN_W + 120:
            return
        n = len(s.jag)
        top = [(x + s.w * i / (n - 1), y + s.jag[i]) for i in range(n)]
        bottom = y + 740
        pygame.draw.polygon(surface, pal["rock_dark"], top + [(x + s.w, bottom), (x, bottom)])

        # deep soil gradient: lighter near the surface, black in the deep
        for i in range(9):
            by = y + 24 + i * 62
            if by > SCREEN_H + 80:
                break
            col = color_lerp(pal["rock"], pal["rock_dark"], i / 8.0)
            pygame.draw.rect(surface, col, (int(x), int(by), int(s.w), 64))

        # wavy strata
        for k in range(4):
            by = y + 96 + k * 92
            if by > SCREEN_H + 70:
                break
            pts = []
            for i in range(9):
                px = x + i * s.w / 8
                py = by + math.sin(i * 0.9 + k * 1.7 + s.seed * 0.01) * 8 + k * 3
                pts.append((px, py))
            pygame.draw.lines(surface, color_lerp(pal["rock_dark"], (0, 0, 0), 0.3),
                              False, pts, 2)

        # buried stones
        for k in range(5):
            bx = x + 40 + ((s.seed * 37 + k * 211) % max(60, int(s.w - 80)))
            by = y + 74 + ((s.seed * 53 + k * 137) % 400)
            bw = 18 + (s.seed + k * 17) % 38
            bh = 10 + (s.seed + k * 23) % 20
            pygame.draw.ellipse(surface, pal["rock"],
                                (bx - bw / 2, by - bh / 2, bw, bh))
            pygame.draw.ellipse(surface, pal["rock_light"],
                                (bx - bw / 2, by - bh / 2, bw, bh), 1)
            pygame.draw.arc(surface, pal["rock_dark"],
                            (bx - bw / 2, by - bh / 2, bw, bh), 3.3, 5.9, 1)

        # roots snaking down through the soil
        nroots = max(2, int(s.w / 260))
        for k in range(nroots):
            rx = x + 50 + (s.seed * 61 + k * 173) % max(80, int(s.w - 100))
            length = 120 + (s.seed + k * 47) % 260
            pts = [(rx, y + 6)]
            for j in range(1, 7):
                pts.append((rx + math.sin(j * 1.35 + k * 1.9 + s.seed * 0.02) * 13,
                            y + 6 + length * j / 6))
            pygame.draw.lines(surface, pal["rock_dark"], False, pts, 5)
            pygame.draw.lines(surface, color_lerp(pal["vine"], pal["rock_dark"], 0.35),
                              False, pts, 2)
            bx, by = pts[3]
            pygame.draw.line(surface, pal["rock_dark"], (bx, by), (bx + 22, by + 28), 2)
            pygame.draw.line(surface, pal["rock_dark"], (bx, by), (bx - 17, by + 36), 2)
            pygame.draw.circle(surface, pal["accent"],
                               (int(rx + math.sin(6 * 1.35 + k * 1.9) * 13),
                                int(y + 6 + length)), 1)

        # mycelium glows in the dark soil
        for k in range(3):
            gx = x + 30 + ((s.seed * 83 + k * 271) % max(60, int(s.w - 60)))
            gy = y + 66 + ((s.seed * 29 + k * 97) % 320)
            draw_glow(surface, (gx, gy), 13, pal["accent"], 28, 2.2)
            pygame.draw.circle(surface, pal["accent"], (int(gx), int(gy)), 1)

        # topsoil / moss cap
        pygame.draw.polygon(surface, pal["rock"],
                            top + [(px, py + 34) for px, py in reversed(top)])
        pygame.draw.polygon(surface, pal["moss_dark"],
                            top + [(px, py + 15) for px, py in reversed(top)])
        pygame.draw.lines(surface, pal["moss"], False, top, 3)

        # moss clumps and swaying blades along the lip
        for i in range(1, n - 1):
            px, py = top[i]
            if i % 2 == 0:
                pygame.draw.circle(surface, pal["moss_dark"],
                                   (int(px), int(py + 2)), 4 + (i % 3))
            if i % 3 == 0:
                sway = math.sin(t * 1.7 + i * 0.7 + s.seed) * 2.2
                pygame.draw.lines(surface, pal["moss"], False,
                                  [(px, py), (px + sway, py - 6 - i % 4),
                                   (px + sway * 1.5, py - 10 - i % 5)], 1)
            if i % 9 == 4:
                pygame.draw.circle(surface, pal["accent"], (int(px), int(py - 1)), 1)

        # exposed earth faces at the segment edges
        for ex in (x, x + s.w):
            pygame.draw.line(surface, color_lerp(pal["rock_dark"], (0, 0, 0), 0.4),
                             (ex, y + 4), (ex, y + 620), 5)
            pygame.draw.line(surface, pal["rock"], (ex, y + 6), (ex, y + 90), 2)
        for k in range(3):
            ex = x + (s.seed * (k + 1) * 31) % max(10, int(s.w - 10))
            pygame.draw.lines(surface, pal["rock_dark"], False,
                              [(ex, y + 20), (ex + 5, y + 50), (ex - 2, y + 80)], 2)

        # cracks reaching down from the surface
        for k in range(3):
            frac = ((s.seed * (k + 3) * 37) % 977) / 977.0
            px = x + 30 + frac * max(20, s.w - 60)
            length = 40 + (s.seed + k * 71) % 70
            pygame.draw.line(surface, color_lerp(pal["rock_dark"], (0, 0, 0), 0.35),
                             (px, y + 26), (px - 9, y + 26 + length), 2)
            pygame.draw.line(surface, color_lerp(pal["rock_dark"], (0, 0, 0), 0.35),
                             (px - 9, y + 26 + length * 0.55), (px + 10, y + 40 + length), 1)

    def _draw_ledge(self, surface, s: Solid, pal, cx, cy, t):
        x = s.x - cx
        y = s.y - cy
        if x + s.w < -80 or x > SCREEN_W + 80:
            return
        n = max(4, len(s.jag))
        top = [(x + s.w * i / (n - 1), y + s.jag[i]) for i in range(n)]
        depth = 26
        under = []
        for i in range(n - 1, -1, -1):
            px, py = top[i]
            taper = 0.55 + 0.45 * math.sin(i * 1.7 + s.seed * 0.01)
            under.append((px, py + depth * taper + 10))
        body = top + under
        pygame.draw.polygon(surface, pal["rock_dark"], body)
        # front face
        face = top + [(px, py + 15) for px, py in reversed(top)]
        pygame.draw.polygon(surface, pal["rock"], face)
        # moss
        moss = top + [(px, py + 10) for px, py in reversed(top)]
        pygame.draw.polygon(surface, pal["moss_dark"], moss)
        pygame.draw.lines(surface, pal["moss"], False, top, 2)
        # hanging roots
        for k in range(2 + s.seed % 3):
            rx = x + 18 + ((s.seed * (k + 1) * 29) % max(20, int(s.w - 36)))
            length = 16 + (s.seed + k * 13) % 34
            sway = math.sin(t * 1.2 + k + s.seed) * 3
            pygame.draw.lines(surface, pal["vine"], False,
                              [(rx, y + 24), (rx + sway, y + 24 + length * 0.6),
                               (rx + sway * 1.7, y + 24 + length)], 2)
            if k == 0:
                pygame.draw.circle(surface, pal["accent"], (int(rx + sway * 1.7),
                                                            int(y + 24 + length)), 1)
        # moss tufts
        for i in range(1, n - 1, 2):
            px, py = top[i]
            pygame.draw.line(surface, pal["moss"], (px, py), (px - 2, py - 4), 1)

    def _draw_moving(self, surface, s: Solid, pal, cx, cy, t):
        x = s.x - cx
        top = s.y - cy
        if x + s.w < -80 or x > SCREEN_W + 80:
            return
        # motion guide
        guide_x = x + s.w / 2
        a = s.base_y - cy - s.move_amp
        b = s.base_y - cy + s.move_amp
        guide_col = color_lerp(pal["accent"], pal["rock_dark"], 0.35)
        for k in range(6):
            y0 = a + (b - a) * (k / 6)
            pygame.draw.line(surface, guide_col, (guide_x, y0),
                             (guide_x, y0 + (b - a) / 12), 1)
        pygame.draw.circle(surface, pal["accent"], (int(guide_x), int(a)), 2)
        pygame.draw.circle(surface, pal["accent"], (int(guide_x), int(b)), 2)
        # slab
        self._draw_ledge(surface, s, pal, cx, cy, t)
        # rune + energy glow
        pulse = 0.5 + 0.5 * math.sin(t * 3.4 + s.move_phase)
        rune_x = x + s.w / 2
        rune_y = top - 12
        draw_glow(surface, (rune_x, rune_y), 26, pal["accent2"], 45 + int(pulse * 40), 2.0)
        pygame.draw.polygon(surface, pal["accent2"],
                            [(rune_x, rune_y - 7), (rune_x + 6, rune_y),
                             (rune_x, rune_y + 7), (rune_x - 6, rune_y)])
        pygame.draw.polygon(surface, (255, 255, 255),
                            [(rune_x, rune_y - 4), (rune_x + 3, rune_y),
                             (rune_x, rune_y + 4), (rune_x - 3, rune_y)], 1)
        # little chevrons showing travel
        for side, dy in ((-1, -1), (1, 1)):
            for k in range(2):
                yy = rune_y + side * (16 + k * 8)
                pygame.draw.lines(surface, guide_col, False,
                                  [(rune_x - 5, yy), (rune_x, yy + side * 4),
                                   (rune_x + 5, yy)], 1)
        # underside glow
        draw_glow(surface, (rune_x, top + 18), 30, pal["accent"], 26, 2.4)

    def _draw_stone(self, surface, s: Solid, pal, cx, cy, t):
        x = s.x - cx
        y = s.y - cy
        if x + s.w < -60 or x > SCREEN_W + 60:
            return
        rect = pygame.Rect(int(x), int(y), int(s.w), int(s.h))
        pygame.draw.rect(surface, pal["rock_dark"], rect, border_radius=4)
        inner = rect.inflate(-6, -6)
        if inner.w > 0 and inner.h > 0:
            pygame.draw.rect(surface, pal["rock"], inner, border_radius=3)
        # block seams
        for i in range(1, int(s.h // 42)):
            yy = y + i * 42
            pygame.draw.line(surface, pal["rock_dark"], (x + 4, yy), (x + s.w - 4, yy), 1)
        # moss on top and side
        pygame.draw.rect(surface, pal["moss_dark"], (x, y, s.w, 8), border_radius=3)
        pygame.draw.line(surface, pal["moss"], (x + 2, y + 1), (x + s.w - 2, y + 1), 2)
        pygame.draw.line(surface, pal["moss_dark"], (x + 2, y + 10), (x + 2, y + s.h - 4), 2)
        # cracks
        pygame.draw.lines(surface, pal["rock_dark"], False,
                          [(x + s.w * 0.5, y + 16), (x + s.w * 0.3, y + s.h * 0.45),
                           (x + s.w * 0.6, y + s.h * 0.7)], 1)
        # glowing lichen
        pygame.draw.circle(surface, pal["accent"], (int(x + 6), int(y + 22)), 1)
        pygame.draw.circle(surface, pal["accent"], (int(x + s.w - 7), int(y + s.h - 30)), 1)

    def _draw_hazard(self, surface, h: Hazard, pal, cx, cy, t):
        x = h.x - cx
        y = h.y - cy
        if x + h.w < -40 or x > SCREEN_W + 40:
            return
        pulse = 0.5 + 0.5 * math.sin(t * 3.0 + h.seed)
        # danger telegraph
        draw_glow(surface, (x + h.w / 2, y - 6), int(h.w * 0.55) + 10,
                  pal["danger"], 22 + int(pulse * 16), 2.6)
        # base
        pygame.draw.rect(surface, pal["rock_dark"], (x - 2, y - 4, h.w + 4, 8))
        n = max(2, int(h.w / 17))
        step = h.w / n
        for i in range(n):
            sx = x + i * step
            peak = h.h * (0.75 + 0.35 * math.sin(i * 2.3 + h.seed))
            pygame.draw.polygon(surface, pal["thorn_dark"],
                                [(sx - 2, y), (sx + step / 2, y - peak), (sx + step + 2, y)])
            pygame.draw.polygon(surface, pal["thorn"],
                                [(sx + 2, y), (sx + step / 2, y - peak * 0.94),
                                 (sx + step - 2, y)])
            tip = (sx + step / 2, y - peak * 0.9)
            pygame.draw.circle(surface, pal["danger"], (int(tip[0]), int(tip[1])), 1)
        pygame.draw.line(surface, pal["thorn_dark"], (x, y), (x + h.w, y), 2)

    def _draw_vine(self, surface, v: Vine, pal, cx, cy, t):
        x = v.x - cx
        top = v.top - cy
        bottom = v.bottom - cy
        if x < -60 or x > SCREEN_W + 60:
            return
        steps = max(6, int((bottom - top) / 26))
        pts = []
        for i in range(steps + 1):
            f = i / steps
            sway = math.sin(t * 1.1 + v.phase + f * 3.2) * (2 + f * 7)
            pts.append((x + sway, top + (bottom - top) * f))
        if len(pts) > 1:
            pygame.draw.lines(surface, pal["rock_dark"], False, pts, 6)
            pygame.draw.lines(surface, pal["vine"], False, pts, 3)
            pygame.draw.lines(surface, pal["moss_dark"], False,
                              [(px - 1, py) for px, py in pts], 1)
        # leaves + glow beads
        for i in range(3, steps, 3):
            px, py = pts[i]
            side = 1 if (i // 3) % 2 else -1
            leaf = [(px, py), (px + side * 10, py - 4), (px + side * 5, py + 5)]
            pygame.draw.polygon(surface, pal["moss"], leaf)
        for i in (2, steps // 2, steps - 1):
            if 0 <= i < len(pts):
                px, py = pts[i]
                draw_glow(surface, (px, py), 10, pal["accent"], 40, 2.0)
                pygame.draw.circle(surface, pal["accent"], (int(px), int(py)), 1)
        # grip knot at the top
        pygame.draw.circle(surface, pal["rock_dark"], (int(x), int(top)), 5)

    def _draw_decor(self, surface, d: Decor, pal, cx, cy, t):
        x = d.x - cx
        y = d.y - cy
        s = d.scale
        sway = math.sin(t * 1.6 + d.seed) * 2 * s
        if d.kind == "grass":
            for i in range(3):
                gx = x + (i - 1) * 5 * s
                pygame.draw.lines(surface, pal["moss"], False,
                                  [(gx, y), (gx + sway + (i - 1) * 2, y - 10 * s - i * 2),
                                   (gx + sway * 1.4, y - 16 * s - i * 2)], 1)
        elif d.kind == "mushroom":
            stem_h = 13 * s
            pygame.draw.line(surface, (216, 210, 190), (x, y), (x + sway * 0.4, y - stem_h), 2)
            draw_glow(surface, (x + sway * 0.4, y - stem_h), int(24 * s),
                      pal["accent"], 36, 2.2)
            pygame.draw.ellipse(surface, pal["accent"],
                                (x - 9 * s, y - stem_h - 8 * s, 18 * s, 10 * s))
            pygame.draw.ellipse(surface, (255, 255, 255),
                                (x - 3 * s, y - stem_h - 6 * s, 3 * s, 2 * s))
        elif d.kind == "crystal":
            col = pal["gem"]
            for i, (dx, hgt) in enumerate(((0, 26), (-8, 17), (9, 14))):
                pts = [(x + dx * s, y), (x + (dx - 5) * s, y - hgt * 0.45 * s),
                       (x + dx * s, y - hgt * s), (x + (dx + 6) * s, y - hgt * 0.4 * s)]
                pygame.draw.polygon(surface, color_lerp(col, (28, 24, 42), 0.35), pts)
                pygame.draw.polygon(surface, color_lerp(col, (255, 255, 255), 0.25),
                                    [pts[0], pts[1], pts[2]], 1)
            draw_glow(surface, (x, y - 14), 28, col, 34, 2.3)
        elif d.kind == "flower":
            pygame.draw.line(surface, pal["moss_dark"], (x, y), (x + sway, y - 18 * s), 1)
            draw_glow(surface, (x + sway, y - 20 * s), 18, pal["accent2"], 34, 2.2)
            pygame.draw.circle(surface, pal["accent2"],
                               (int(x + sway), int(y - 20 * s)), max(1, int(3 * s)))
        elif d.kind == "lantern":
            pygame.draw.line(surface, pal["rock_dark"], (x, y), (x, y - 58), 3)
            pygame.draw.line(surface, pal["rock_dark"], (x, y - 58), (x + 16, y - 58), 2)
            draw_glow(surface, (x + 16, y - 44), 42, (255, 196, 112), 54, 2.0)
            pygame.draw.line(surface, (110, 96, 72), (x + 16, y - 58), (x + 16, y - 50), 1)
            pygame.draw.circle(surface, (255, 196, 112), (int(x + 16), int(y - 44)), 5)
            pygame.draw.circle(surface, (255, 246, 214), (int(x + 16), int(y - 44)), 2)
        elif d.kind == "sign":
            pygame.draw.line(surface, pal["rock_dark"], (x, y), (x, y - 36), 3)
            rect = pygame.Rect(int(x - 22), int(y - 50), 44, 18)
            pygame.draw.rect(surface, pal["rock_light"], rect, border_radius=2)
            pygame.draw.rect(surface, pal["rock_dark"], rect, 1, border_radius=2)
            pygame.draw.line(surface, pal["moss"], (x - 15, y - 41), (x + 15, y - 41), 2)
            pygame.draw.line(surface, pal["moss"], (x + 8, y - 46), (x + 14, y - 41), 1)
            pygame.draw.line(surface, pal["moss"], (x + 8, y - 36), (x + 14, y - 41), 1)

