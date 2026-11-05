"""Procedural, biome-specific parallax silhouettes.

Three tileable layers are generated once per biome:
  * far  - spires, ridges and a hazy moon
  * mid  - giant thorned trees, arches and hanging vines
  * near - dark brambles and overhanging thorns framing the playfield

Everything is generated from a seeded RNG with pygame primitives; there are
no external art assets.
"""

from __future__ import annotations

import math
import random

import pygame

from .constants import BIOMES, SCREEN_H, SCREEN_W
from .utils import color_lerp, draw_glow, glow_surface

LAYER_W = 1600
LAYER_H = 840


def _alpha(color, a: int):
    return (color[0], color[1], color[2], max(0, min(255, int(a))))


def _ridge(surface, rng, color, base_y, amp, alpha, step=90):
    pts = [(0, LAYER_H)]
    x = 0
    y = base_y
    while x <= LAYER_W + step:
        pts.append((x, y))
        x += rng.randint(step // 2, step)
        y += rng.uniform(-amp, amp)
        y = max(base_y - amp * 2.2, min(base_y + amp * 0.5, y))
    pts.append((LAYER_W, y))
    pts.append((LAYER_W, LAYER_H))
    pygame.draw.polygon(surface, _alpha(color, alpha), pts)


def _spire(surface, rng, x, base_y, width, height, color, alpha, thorn_color):
    lean = rng.uniform(-0.25, 0.25)
    top_x = x + lean * height
    top_y = base_y - height
    pts = [
        (x - width, base_y),
        (x - width * 0.55, base_y - height * 0.35),
        (x - width * 0.18, base_y - height * 0.68),
        (top_x - width * 0.07, top_y),
        (top_x + width * 0.05, top_y + height * 0.03),
        (x + width * 0.30, base_y - height * 0.55),
        (x + width * 0.62, base_y - height * 0.22),
        (x + width, base_y),
    ]
    pygame.draw.polygon(surface, _alpha(color, alpha), pts)
    # thorny protrusions
    for i in range(4):
        t = 0.2 + i * 0.18
        px = x + (top_x - x) * t + width * 0.4
        py = base_y - height * t
        size = rng.uniform(10, 26)
        pygame.draw.polygon(
            surface,
            _alpha(thorn_color, alpha),
            [(px, py), (px + size, py - size * 0.5), (px + size * 0.2, py + size * 0.3)],
        )


def _vine(surface, rng, x, y0, length, color, alpha, leaf_color, leaf_alpha):
    pts = []
    steps = max(4, int(length / 26))
    sway = rng.uniform(-18, 18)
    for i in range(steps + 1):
        t = i / steps
        px = x + math.sin(t * 4.0 + rng.random()) * sway * t
        py = y0 + length * t
        pts.append((px, py))
    if len(pts) > 1:
        pygame.draw.lines(surface, _alpha(color, alpha), False, pts, 2)
    for i in range(2, steps, 2):
        px, py = pts[i]
        side = -1 if i % 4 == 0 else 1
        leaf = [(px, py), (px + side * 9, py + 4), (px + side * 3, py + 10)]
        pygame.draw.polygon(surface, _alpha(leaf_color, leaf_alpha), leaf)


def _tree(surface, rng, x, base_y, height, width, color, alpha, thorn_color):
    # curved trunk
    top_x = x + rng.uniform(-70, 70)
    steps = 12
    left = []
    right = []
    for i in range(steps + 1):
        t = i / steps
        cx = x + (top_x - x) * t + math.sin(t * 3.0) * 22
        cy = base_y - height * t
        w = width * (1.0 - t * 0.72)
        left.append((cx - w, cy))
        right.append((cx + w, cy))
    pygame.draw.polygon(surface, _alpha(color, alpha), left + right[::-1])

    # roots
    for _ in range(rng.randint(2, 4)):
        side = rng.choice((-1, 1))
        rl = rng.uniform(40, 110)
        pygame.draw.polygon(
            surface,
            _alpha(color, alpha),
            [
                (x + side * width * 0.4, base_y - 20),
                (x + side * (width + rl), base_y + 8),
                (x + side * width * 0.2, base_y + 50),
            ],
        )

    # branches
    branch_ends = []
    for i in range(rng.randint(3, 6)):
        t = rng.uniform(0.28, 0.88)
        by = base_y - height * t
        bx = x + (top_x - x) * t
        side = rng.choice((-1, 1))
        length = rng.uniform(70, 190) * (1.0 - t * 0.3)
        ex = bx + side * length
        ey = by - rng.uniform(10, 80)
        pygame.draw.line(surface, _alpha(color, alpha), (bx, by), (ex, ey),
                         max(3, int(width * 0.22 * (1 - t))))
        branch_ends.append((ex, ey, side))
        # thorns along the branch
        for k in range(3):
            tt = 0.3 + k * 0.2
            tx = bx + (ex - bx) * tt
            ty = by + (ey - by) * tt
            size = rng.uniform(8, 16)
            pygame.draw.polygon(
                surface,
                _alpha(thorn_color, int(alpha * 0.55)),
                [(tx, ty - 8), (tx + side * size, ty), (tx, ty + 2)],
            )
        _vine(surface, rng, ex, ey, rng.uniform(50, 160), color,
              min(255, alpha + 20), thorn_color, int(alpha * 0.55))

    # canopy / bramble crown
    for i in range(rng.randint(5, 9)):
        bx = top_x + rng.uniform(-width * 2.0, width * 2.0)
        by = base_y - height + rng.uniform(-40, 80)
        r = rng.uniform(22, 70)
        pygame.draw.circle(surface, _alpha(color, alpha), (int(bx), int(by)), int(r))
        for k in range(3):
            a = rng.uniform(0, math.tau)
            tx = bx + math.cos(a) * r * 1.4
            ty = by + math.sin(a) * r * 1.1
            pygame.draw.polygon(
                surface,
                _alpha(thorn_color, int(alpha * 0.6)),
                [(bx + math.cos(a) * r * 0.8, by + math.sin(a) * r * 0.8),
                 (tx + math.cos(a + 0.4) * 10, ty),
                 (tx, ty + 6)],
            )
    return branch_ends


def build_layers(biome_index: int) -> list[pygame.Surface]:
    palette = BIOMES[biome_index]
    rng = random.Random(9001 + biome_index * 733)

    far = pygame.Surface((LAYER_W, LAYER_H), pygame.SRCALPHA)
    mid = pygame.Surface((LAYER_W, LAYER_H), pygame.SRCALPHA)
    near = pygame.Surface((LAYER_W, LAYER_H), pygame.SRCALPHA)

    fog = palette["fog"]
    sky_bottom = palette["sky_bottom"]
    rock_dark = palette["rock_dark"]
    rock = palette["rock"]
    accent = palette["accent"]
    accent2 = palette["accent2"]

    far_color = color_lerp(fog, sky_bottom, 0.45)
    mid_color = color_lerp(fog, rock_dark, 0.60)
    near_color = color_lerp(fog, (0, 0, 0), 0.55)
    thorn_muted = color_lerp(mid_color, fog, 0.35)

    # ---- far -------------------------------------------------------------
    _ridge(far, rng, far_color, LAYER_H * 0.62, 34, 110)
    _ridge(far, rng, color_lerp(fog, sky_bottom, 0.30), LAYER_H * 0.73, 46, 90)
    for i in range(5):
        x = 120 + i * (LAYER_W - 240) / 4 + rng.uniform(-70, 70)
        h = rng.uniform(220, 430)
        _spire(far, rng, x, LAYER_H * 0.78, rng.uniform(45, 95), h,
               far_color, 130, palette["thorn_dark"])
    _ridge(far, rng, far_color, LAYER_H * 0.86, 26, 120)

    # ---- mid -------------------------------------------------------------
    for i in range(4):
        x = 160 + i * (LAYER_W - 320) / 3 + rng.uniform(-70, 70)
        h = rng.uniform(330, 560)
        _tree(mid, rng, x, LAYER_H * 0.86, h, rng.uniform(26, 48),
              mid_color, 175, thorn_muted)
    # arches
    for _ in range(2):
        ax = rng.uniform(240, LAYER_W - 240)
        ay = LAYER_H * 0.58
        w = rng.uniform(100, 190)
        pts = []
        for i in range(13):
            t = i / 12
            pts.append((ax - w + 2 * w * t, ay - math.sin(t * math.pi) * rng.uniform(90, 150)))
        pygame.draw.lines(mid, _alpha(mid_color, 120), False, pts, 10)
        for i in range(1, 12, 2):
            px, py = pts[i]
            pygame.draw.line(mid, _alpha(mid_color, 120), (px, py), (px, py + rng.uniform(30, 90)), 3)
        for i in range(1, 12, 3):
            px, py = pts[i]
            pygame.draw.polygon(mid, _alpha(palette["thorn_dark"], 150),
                                [(px, py - 6), (px + 12, py - 16), (px + 5, py + 4)])

    # floating motes of light
    for _ in range(34):
        x = rng.uniform(80, LAYER_W - 80)
        y = rng.uniform(LAYER_H * 0.25, LAYER_H * 0.85)
        a = rng.randint(40, 110)
        r = rng.randint(1, 3)
        pygame.draw.circle(mid, _alpha(accent, a), (int(x), int(y)), r)
        pygame.draw.circle(mid, _alpha(accent, max(10, a // 4)), (int(x), int(y)), r + 3, 1)

    # ---- near ------------------------------------------------------------
    # overhanging thorns from the top
    for _ in range(5):
        x = rng.uniform(120, LAYER_W - 120)
        length = rng.uniform(60, 210)
        pts = [(x - 26, 0), (x + 24, 0)]
        for i in range(8):
            t = i / 7
            pts.append((x + math.sin(t * 3.4) * 18, length * t))
        pygame.draw.polygon(near, _alpha(near_color, 220), pts)
        for i in range(4):
            t = 0.25 + i * 0.18
            px = x + math.sin(t * 3.4) * 18
            py = length * t
            pygame.draw.polygon(near, _alpha(near_color, 235),
                                [(px - 8, py), (px + 14, py + 10), (px + 2, py + 22)])

    # bramble mass along the bottom
    x = -40
    while x < LAYER_W + 40:
        r = rng.uniform(30, 80)
        pygame.draw.circle(near, _alpha(near_color, 200),
                           (int(x), int(LAYER_H - r * 0.3)), int(r))
        for k in range(3):
            a = rng.uniform(-math.pi, 0)
            tx = x + math.cos(a) * r
            ty = LAYER_H - r * 0.3 + math.sin(a) * r
            pygame.draw.polygon(near, _alpha(near_color, 230),
                                [(tx, ty), (tx + rng.uniform(-14, 14), ty - rng.uniform(20, 50)),
                                 (tx + 8, ty)])
        x += rng.uniform(45, 110)

    return [far, mid, near]


class BackgroundDirector:
    """Caches generated backdrops and draws them with parallax."""

    LAYER_SPEC = (
        (0.10, 0.10, -10),   # factor x, factor y, offset
        (0.22, 0.18, -30),
        (0.40, 0.28, -55),
    )

    def __init__(self) -> None:
        self._cache: dict[int, list[pygame.Surface]] = {}
        self._order: list[int] = []

    def get(self, biome_index: int) -> list[pygame.Surface]:
        biome_index %= len(BIOMES)
        if biome_index in self._cache:
            return self._cache[biome_index]
        layers = build_layers(biome_index)
        if len(self._order) >= 2:
            old = self._order.pop(0)
            self._cache.pop(old, None)
        self._cache[biome_index] = layers
        self._order.append(biome_index)
        return layers

    def prepare(self, biome_index: int) -> None:
        self.get(biome_index)

    def draw(self, surface: pygame.Surface, cam_x: float, cam_y: float,
             biome_index: int, time_s: float = 0.0) -> None:
        layers = self.get(biome_index)
        # The near layer sits almost entirely behind the opaque terrain.  The
        # two distant layers carry the parallax read and keep the frame cheap.
        for layer, (fx, fy, off) in zip(layers[:2], self.LAYER_SPEC[:2]):
            shift = -cam_x * fx
            ox = int(shift % LAYER_W)
            oy = int(off - cam_y * fy)
            surface.blit(layer, (ox - LAYER_W, oy))
            surface.blit(layer, (ox, oy))

    def draw_foreground(self, surface: pygame.Surface, cam_x: float,
                        cam_y: float, biome_index: int) -> None:
        """A thin, very dark layer in front of the world for depth."""
        layers = self.get(biome_index)
        near = layers[2]
        fx, fy = 0.62, 0.40
        ox = int((-cam_x * fx) % LAYER_W)
        oy = int(-70 - cam_y * fy)
        # We only want the top overhang and bottom brambles; the whole near
        # layer would cover the playfield.  Clip to the frame edges.
        clip_h = 120
        surface.blit(near, (ox - LAYER_W, oy), area=pygame.Rect(0, 0, LAYER_W, clip_h))
        surface.blit(near, (ox, oy), area=pygame.Rect(0, 0, LAYER_W, clip_h))
        surface.blit(near, (ox - LAYER_W, oy + LAYER_H - 90),
                     area=pygame.Rect(0, LAYER_H - 90, LAYER_W, 90))
        surface.blit(near, (ox, oy + LAYER_H - 90),
                     area=pygame.Rect(0, LAYER_H - 90, LAYER_W, 90))
