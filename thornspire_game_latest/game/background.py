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


def _pine(surface, rng, x, base_y, height, width, color, snow_color, alpha):
    pygame.draw.rect(surface, _alpha(color, alpha), (int(x - width * 0.14), int(base_y - height * 0.25), int(width * 0.28), int(height * 0.25)))
    tiers = 5
    for i in range(tiers):
        t = i / tiers
        ty = base_y - height * (0.20 + t * 0.72)
        tw = width * (1.0 - t * 0.62)
        th = height * 0.28
        pts = [(x, ty - th), (x + tw, ty), (x - tw, ty)]
        pygame.draw.polygon(surface, _alpha(color, alpha), pts)
        cap = [(x, ty - th), (x + tw * 0.45, ty - th * 0.55), (x - tw * 0.45, ty - th * 0.55)]
        pygame.draw.polygon(surface, _alpha(snow_color, int(alpha * 0.65)), cap)


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
    mid_color = color_lerp(fog, rock_dark, 0.62)
    near_color = color_lerp(fog, (0, 0, 0), 0.55)
    thorn_muted = color_lerp(mid_color, fog, 0.35)

    if biome_index == 1:  # EMBER REACH — Volcanoes, lava rivers & basalt columns
        _ridge(far, rng, far_color, LAYER_H * 0.66, 42, 120)
        for i in range(3):
            vx = 230 + i * 540 + rng.uniform(-50, 50)
            vh = rng.uniform(290, 410)
            vw = rng.uniform(180, 260)
            by = LAYER_H * 0.84
            cone = [(vx - vw, by), (vx - 44, by - vh), (vx + 44, by - vh), (vx + vw, by)]
            pygame.draw.polygon(far, _alpha(far_color, 185), cone)
            # glowing caldera & lava veins
            pygame.draw.ellipse(far, _alpha(accent, 190), (int(vx - 46), int(by - vh - 10), 92, 22))
            for k in range(3):
                lx = vx + (k - 1) * 18
                pts = [(lx, by - vh + 6)]
                for s in range(1, 6):
                    pts.append((lx + math.sin(s * 1.4 + k) * 26 + (k - 1) * s * 14, by - vh + s * (vh / 5.5)))
                pygame.draw.lines(far, _alpha(accent, 155), False, pts, 3)
        # basalt columns in mid
        bx = 40
        while bx < LAYER_W - 40:
            cw = rng.randint(34, 62)
            ch = rng.randint(150, 420)
            if rng.random() < 0.68:
                rect = pygame.Rect(int(bx), int(LAYER_H * 0.88 - ch), cw - 4, ch)
                pygame.draw.rect(mid, _alpha(mid_color, 195), rect)
                pygame.draw.line(mid, _alpha(accent, 90), (rect.x, rect.y), (rect.right, rect.y), 2)
            bx += cw + rng.randint(8, 36)

    elif biome_index == 2:  # FROST WEALD — Jagged glaciers & snow-laden pine forests
        for i in range(6):
            gx = 110 + i * 265 + rng.uniform(-40, 40)
            gh = rng.uniform(280, 470)
            gw = rng.uniform(90, 150)
            by = LAYER_H * 0.82
            pygame.draw.polygon(far, _alpha(far_color, 165), [(gx - gw, by), (gx, by - gh), (gx + gw, by)])
            pygame.draw.polygon(far, _alpha(accent2, 75), [(gx, by - gh), (gx + gw * 0.55, by), (gx, by)])
        _ridge(far, rng, far_color, LAYER_H * 0.82, 24, 130)
        for i in range(9):
            px = 70 + i * 175 + rng.uniform(-35, 35)
            _pine(mid, rng, px, LAYER_H * 0.88, rng.uniform(240, 460), rng.uniform(55, 95),
                  mid_color, accent2, 195)

    elif biome_index == 3:  # VOID BLOOM — Floating fractured monoliths & cosmic lotus
        _ridge(far, rng, far_color, LAYER_H * 0.75, 38, 110)
        for i in range(6):
            mx = 130 + i * 250 + rng.uniform(-40, 40)
            my = rng.uniform(170, 420)
            mh = rng.uniform(130, 240)
            mw = rng.uniform(26, 48)
            tilt = rng.uniform(-22, 22)
            pts = [(mx - mw + tilt, my), (mx, my - mh * 0.4), (mx + mw + tilt, my), (mx, my + mh * 0.6)]
            pygame.draw.polygon(mid, _alpha(mid_color, 195), pts)
            pygame.draw.polygon(mid, _alpha(accent, 135), pts, 2)
            pygame.draw.circle(mid, _alpha(accent2, 165), (int(mx + tilt * 0.5), int(my)), 5)

    elif biome_index == 4:  # SUNKEN ABYSS — Submerged temple columns, coral fans & giant kelp
        _ridge(far, rng, far_color, LAYER_H * 0.72, 30, 110)
        for i in range(5):
            cx = 160 + i * 310 + rng.uniform(-40, 40)
            ch = rng.uniform(220, 410)
            by = LAYER_H * 0.86
            # broken fluted column
            pygame.draw.rect(far, _alpha(far_color, 175), (int(cx - 24), int(by - ch), 48, int(ch)))
            pygame.draw.rect(far, _alpha(far_color, 200), (int(cx - 34), int(by - ch - 14), 68, 16))
        # giant swaying kelp & coral fans in mid
        for i in range(11):
            kx = 60 + i * 145 + rng.uniform(-25, 25)
            kh = rng.uniform(260, 520)
            pts = []
            for s in range(12):
                t = s / 11
                pts.append((kx + math.sin(t * 5.0 + i) * 28, LAYER_H * 0.90 - kh * t))
            pygame.draw.lines(mid, _alpha(mid_color, 185), False, pts, 7)
            for s in range(2, 11, 2):
                lx, ly = pts[s]
                side = 1 if s % 4 == 0 else -1
                pygame.draw.ellipse(mid, _alpha(accent, 85), (int(lx + side * 6), int(ly - 8), 22, 12))

    elif biome_index == 5:  # SOLAR DUNES — Stepped pyramids, obelisks & sweeping sand dunes
        # huge sun disc in far haze
        pygame.draw.circle(far, _alpha(accent2, 75), (int(LAYER_W * 0.72), int(LAYER_H * 0.34)), 105)
        for i in range(3):
            px = 240 + i * 560 + rng.uniform(-40, 40)
            ph = rng.uniform(230, 340)
            pw = ph * 1.25
            by = LAYER_H * 0.80
            pygame.draw.polygon(far, _alpha(far_color, 185), [(px - pw, by), (px, by - ph), (px + pw, by)])
            pygame.draw.polygon(far, _alpha(accent, 55), [(px, by - ph), (px + pw, by), (px + pw * 0.18, by)])
        _ridge(far, rng, far_color, LAYER_H * 0.82, 22, 150, step=160)
        # carved obelisks in mid
        for i in range(5):
            ox = 150 + i * 310 + rng.uniform(-45, 45)
            oh = rng.uniform(240, 430)
            by = LAYER_H * 0.88
            pts = [(ox - 24, by), (ox - 15, by - oh + 34), (ox, by - oh), (ox + 15, by - oh + 34), (ox + 24, by)]
            pygame.draw.polygon(mid, _alpha(mid_color, 205), pts)
            pygame.draw.circle(mid, _alpha(accent, 175), (int(ox), int(by - oh + 48)), 6)

    elif biome_index == 6:  # CELESTIAL SPIRE — Armillary star-rings & cathedral spires
        for i in range(2):
            rx = 380 + i * 760
            ry = LAYER_H * 0.38
            pygame.draw.circle(far, _alpha(accent2, 80), (int(rx), int(ry)), 135, 3)
            pygame.draw.circle(far, _alpha(accent, 95), (int(rx), int(ry)), 95, 2)
            pygame.draw.ellipse(far, _alpha(accent2, 75), (int(rx - 155), int(ry - 42), 310, 84), 2)
        for i in range(6):
            sx = 120 + i * 260 + rng.uniform(-30, 30)
            sh = rng.uniform(310, 540)
            by = LAYER_H * 0.88
            pts = [(sx - 34, by), (sx - 10, by - sh * 0.75), (sx, by - sh), (sx + 10, by - sh * 0.75), (sx + 34, by)]
            pygame.draw.polygon(mid, _alpha(mid_color, 195), pts)
            pygame.draw.line(mid, _alpha(accent2, 120), (sx, by - sh), (sx, by - sh + 90), 2)

    elif biome_index == 7:  # TOXIC MIRE — Giant glowing toadstools & twisted swamp bog
        _ridge(far, rng, far_color, LAYER_H * 0.70, 30, 115)
        for i in range(6):
            mx = 130 + i * 255 + rng.uniform(-45, 45)
            mh = rng.uniform(220, 440)
            cap_w = rng.uniform(110, 210)
            by = LAYER_H * 0.88
            top_x = mx + rng.uniform(-30, 30)
            top_y = by - mh
            pygame.draw.lines(mid, _alpha(mid_color, 200), False,
                              [(mx, by), (mx + (top_x - mx) * 0.5 + 18, by - mh * 0.5), (top_x, top_y)], 18)
            pygame.draw.ellipse(mid, _alpha(mid_color, 215),
                                (int(top_x - cap_w / 2), int(top_y - 34), int(cap_w), 58))
            pygame.draw.arc(mid, _alpha(accent, 165),
                            (int(top_x - cap_w / 2), int(top_y - 34), int(cap_w), 58), 0, math.pi, 3)
            for k in range(4):
                sx = top_x - cap_w * 0.32 + k * (cap_w * 0.21)
                pygame.draw.circle(mid, _alpha(accent, 140), (int(sx), int(top_y - 10)), 5)

    elif biome_index == 8:  # CRIMSON CITADEL — Blood moon, gothic castle towers & iron chains
        pygame.draw.circle(far, _alpha(accent, 115), (int(LAYER_W * 0.28), int(LAYER_H * 0.28)), 88)
        for i in range(4):
            tx = 160 + i * 390 + rng.uniform(-30, 30)
            tw = rng.randint(90, 136)
            th = rng.randint(310, 500)
            by = int(LAYER_H * 0.88)
            ty = by - th
            pygame.draw.rect(mid, _alpha(mid_color, 215), (int(tx - tw // 2), ty, tw, th))
            # crenellations / battlements
            for c in range(0, tw, 24):
                pygame.draw.rect(mid, _alpha(mid_color, 225), (int(tx - tw // 2 + c), ty - 16, 14, 16))
            # glowing lancet window
            pygame.draw.rect(mid, _alpha(accent, 175), (int(tx - 10), ty + 55, 20, 56), border_radius=10)
            # spire roof on alternate towers
            if i % 2 == 0:
                pygame.draw.polygon(mid, _alpha(mid_color, 225),
                                    [(tx - tw // 2 - 8, ty), (tx, ty - 95), (tx + tw // 2 + 8, ty)])
        # hanging iron chains from top
        for i in range(7):
            cx = 90 + i * 225
            clen = rng.randint(140, 310)
            for y in range(0, clen, 16):
                pygame.draw.ellipse(mid, _alpha(mid_color, 190), (cx - 5, y, 10, 14), 2)

    elif biome_index == 9:  # AETHER HEIGHTS — Floating sky-islands, cloud banks & waterfalls
        for i in range(6):
            cx = 130 + i * 260
            cy = int(LAYER_H * 0.76 + (i % 2) * 34)
            pygame.draw.ellipse(far, _alpha(accent2, 55), (cx - 160, cy - 45, 320, 95))
        for i in range(4):
            ix = 180 + i * 380 + rng.uniform(-40, 40)
            iy = rng.uniform(210, 390)
            iw = rng.uniform(110, 175)
            ih = rng.uniform(95, 165)
            island = [(ix - iw, iy), (ix + iw, iy), (ix + iw * 0.35, iy + ih * 0.6),
                      (ix, iy + ih), (ix - iw * 0.4, iy + ih * 0.55)]
            pygame.draw.polygon(mid, _alpha(mid_color, 205), island)
            pygame.draw.line(mid, _alpha(accent, 165), (ix - iw, iy), (ix + iw, iy), 4)
            # sky-temple pillars on the floating island
            for p in (-1, 0, 1):
                pygame.draw.rect(mid, _alpha(mid_color, 195), (int(ix + p * 26 - 5), int(iy - 48), 10, 48))
            pygame.draw.polygon(mid, _alpha(mid_color, 205),
                                [(ix - 42, iy - 48), (ix, iy - 72), (ix + 42, iy - 48)])
            # cascading waterfall mist
            pygame.draw.rect(mid, _alpha(accent, 90), (int(ix + 12), int(iy + 4), 14, 210))

    else:  # 0: VERDANT HOLLOW — Classic ancient bramble trees & thorny arches
        _ridge(far, rng, far_color, LAYER_H * 0.62, 34, 110)
        _ridge(far, rng, color_lerp(fog, sky_bottom, 0.30), LAYER_H * 0.73, 46, 90)
        for i in range(5):
            x = 120 + i * (LAYER_W - 240) / 4 + rng.uniform(-70, 70)
            h = rng.uniform(220, 430)
            _spire(far, rng, x, LAYER_H * 0.78, rng.uniform(45, 95), h,
                   far_color, 130, palette["thorn_dark"])
        _ridge(far, rng, far_color, LAYER_H * 0.86, 26, 120)
        for i in range(4):
            x = 160 + i * (LAYER_W - 320) / 3 + rng.uniform(-70, 70)
            h = rng.uniform(330, 560)
            _tree(mid, rng, x, LAYER_H * 0.86, h, rng.uniform(26, 48),
                  mid_color, 175, thorn_muted)
        for _ in range(2):
            ax = rng.uniform(240, LAYER_W - 240)
            ay = LAYER_H * 0.58
            w = rng.uniform(100, 190)
            pts = []
            for i in range(13):
                t = i / 12
                pts.append((ax - w + 2 * w * t, ay - math.sin(t * math.pi) * rng.uniform(90, 150)))
            pygame.draw.lines(mid, _alpha(mid_color, 120), False, pts, 10)

    # floating motes of light
    for _ in range(34):
        x = rng.uniform(80, LAYER_W - 80)
        y = rng.uniform(LAYER_H * 0.20, LAYER_H * 0.85)
        a = rng.randint(45, 120)
        r = rng.randint(1, 3)
        pygame.draw.circle(mid, _alpha(accent, a), (int(x), int(y)), r)
        pygame.draw.circle(mid, _alpha(accent, max(10, a // 4)), (int(x), int(y)), r + 3, 1)

    # ---- near ------------------------------------------------------------
    for _ in range(5):
        x = rng.uniform(120, LAYER_W - 120)
        length = rng.uniform(60, 190)
        pts = [(x - 24, 0), (x + 22, 0)]
        for i in range(8):
            t = i / 7
            pts.append((x + math.sin(t * 3.4) * 16, length * t))
        pygame.draw.polygon(near, _alpha(near_color, 215), pts)

    x = -40
    while x < LAYER_W + 40:
        r = rng.uniform(30, 80)
        pygame.draw.circle(near, _alpha(near_color, 200),
                           (int(x), int(LAYER_H - r * 0.3)), int(r))
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
