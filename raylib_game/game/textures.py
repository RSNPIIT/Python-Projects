"""Procedural textures: walls, enemy sprites, pickups, and screen overlays."""

from __future__ import annotations

import math

import raylib as rl

from .config import (
    BLACK,
    CLEAR,
    CYAN,
    GOLD,
    GREEN,
    MAGENTA,
    ORANGE,
    RED,
    WHITE,
    WORLD_H,
    WORLD_W,
    clamp,
    lerp,
    mix_color,
    shade,
)
from .levels import Theme


# ---------------------------------------------------------------------------
# Small drawing helpers
# ---------------------------------------------------------------------------
def _poly(points, color) -> None:
    if len(points) < 3:
        return
    # Raylib culls clockwise triangles; normalize polygon winding first.
    area = 0.0
    for index, point in enumerate(points):
        nx, ny = points[(index + 1) % len(points)]
        area += point[0] * ny - nx * point[1]
    if area > 0:
        points = list(reversed(points))
    for index in range(1, len(points) - 1):
        rl.DrawTriangle(points[0], points[index], points[index + 1], color)


def _poly_line(points, color, thickness: float = 2.0) -> None:
    for index in range(len(points)):
        a = points[index]
        b = points[(index + 1) % len(points)]
        rl.DrawLineEx(a, b, thickness, color)


class Pen:
    """Maps a convenient logical sprite canvas to a larger render target."""

    def __init__(self, width: int, height: int, logical_w: float, logical_h: float) -> None:
        self.w = width
        self.h = height
        self.sx = width / logical_w
        self.sy = height / logical_h

    def p(self, x: float, y: float):
        return (x * self.sx, y * self.sy)

    def poly(self, points, color) -> None:
        _poly([self.p(x, y) for x, y in points], color)

    def outline(self, points, color, thickness: float = 1.0) -> None:
        _poly_line([self.p(x, y) for x, y in points], color, thickness * self.sx)

    def rect(self, x: float, y: float, w: float, h: float, color) -> None:
        rl.DrawRectangleRec((x * self.sx, y * self.sy, w * self.sx, h * self.sy), color)

    def circle(self, x: float, y: float, radius: float, color) -> None:
        rl.DrawCircleV(self.p(x, y), radius * self.sx, color)

    def ring(self, x: float, y: float, inner: float, outer: float, start: float, end: float, segments: int, color) -> None:
        rl.DrawRing(
            self.p(x, y),
            inner * self.sx,
            outer * self.sx,
            start,
            end,
            segments,
            color,
        )

    def line(self, x1: float, y1: float, x2: float, y2: float, thickness: float, color) -> None:
        rl.DrawLineEx(self.p(x1, y1), self.p(x2, y2), thickness * self.sx, color)

    def ellipse(self, x: float, y: float, rx: float, ry: float, color) -> None:
        rl.DrawEllipseV(self.p(x, y), rx * self.sx, ry * self.sy, color)

    def glow(self, x: float, y: float, radius: float, color) -> None:
        rl.DrawCircleGradient(self.p(x, y), radius * self.sx, color, CLEAR)

    def blend(self, additive: bool = True) -> None:
        rl.BeginBlendMode(rl.BLEND_ADDITIVE if additive else rl.BLEND_ALPHA)

    def end_blend(self) -> None:
        rl.EndBlendMode()


def _image_from_pixels(width: int, height: int, data: bytes | bytearray):
    image = rl.GenImageColor(width, height, CLEAR)
    buffer = rl.ffi.buffer(image.data, width * height * 4)
    buffer[:] = bytes(data)
    return image


def _texture_from_pixels(width: int, height: int, data: bytes | bytearray, point_filter: bool = True):
    image = _image_from_pixels(width, height, data)
    texture = rl.LoadTextureFromImage(image)
    rl.UnloadImage(image)
    rl.SetTextureFilter(texture, rl.TEXTURE_FILTER_POINT if point_filter else rl.TEXTURE_FILTER_BILINEAR)
    return texture


def _sprite_texture(logical_w: int, logical_h: int, draw_fn, supersample: int = 2):
    width = logical_w * supersample
    height = logical_h * supersample
    target = rl.LoadRenderTexture(width, height)
    rl.BeginTextureMode(target)
    rl.ClearBackground(CLEAR)
    pen = Pen(width, height, logical_w, logical_h)
    draw_fn(pen)
    rl.EndTextureMode()
    image = rl.LoadImageFromTexture(target.texture)
    source = bytes(rl.ffi.buffer(image.data, image.width * image.height * 4))
    src_w, src_h = image.width, image.height
    output = bytearray(logical_w * logical_h * 4)
    # RenderTexture readback is vertically inverted.  Flip and downsample in
    # one pass, which also antialiases the vector sprite art.
    for y in range(logical_h):
        sy_base = (src_h - 1) - y * supersample
        for x in range(logical_w):
            r = g = b = a = 0
            for oy in range(supersample):
                sy = sy_base - oy
                if sy < 0:
                    sy = 0
                row = sy * src_w
                for ox in range(supersample):
                    sx = x * supersample + ox
                    if sx >= src_w:
                        sx = src_w - 1
                    index = (row + sx) * 4
                    r += source[index]
                    g += source[index + 1]
                    b += source[index + 2]
                    a += source[index + 3]
            divisor = supersample * supersample
            out_index = (y * logical_w + x) * 4
            output[out_index : out_index + 4] = bytes(
                (r // divisor, g // divisor, b // divisor, a // divisor)
            )
    rl.UnloadImage(image)
    rl.UnloadRenderTexture(target)
    return _texture_from_pixels(logical_w, logical_h, output, point_filter=False)


def _hash(x: int, y: int, seed: int) -> float:
    value = (x * 374761393 + y * 668265263 + seed * 1442695041) & 0xFFFFFFFF
    value = (value ^ (value >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((value ^ (value >> 16)) & 255) / 255.0


def _scale(color, factor: float):
    return shade(color, factor, 255)


def _mix(a, b, t: float):
    return mix_color(a, b, t, 255)


# ---------------------------------------------------------------------------
# Wall textures (64x64 pixel panels)
# ---------------------------------------------------------------------------
def _wall_pixels(kind: int, theme: Theme) -> bytearray:
    size = 64
    data = bytearray(size * size * 4)
    base = theme.wall_base
    dark = theme.wall_dark
    light = theme.wall_light
    metal = theme.wall_metal
    accent = theme.accent
    accent_2 = theme.accent_2

    for y in range(size):
        for x in range(size):
            n = _hash(x, y, kind * 97 + 13)
            grain = 0.90 + n * 0.15
            if kind == 1:
                color = _scale(base, grain * (1.04 - y / 180.0))
                if x % 16 == 0 or y % 16 == 0:
                    color = _scale(dark, 1.0 + n * 0.08)
                elif x % 16 == 1 or y % 16 == 1:
                    color = _scale(light, 0.55)
                if (x % 16 in (3, 12)) and (y % 16 in (3, 12)):
                    color = _scale(light, 1.15)
                if 43 <= y <= 49:
                    color = accent if ((x + y) // 6) % 2 == 0 else _scale(dark, 0.85)
                    if y in (43, 49):
                        color = _scale(dark, 0.6)
                if 52 <= y <= 55 and x % 8 < 5:
                    color = _mix(metal, dark, 0.65)
                if y > 57:
                    color = _scale(color, 0.76)
                if x in (30, 31) and 8 < y < 24:
                    color = _scale(light, 0.9)
            elif kind == 2:
                rib = x % 8
                if rib == 0:
                    color = _scale(dark, 0.8)
                elif rib in (1, 2):
                    color = _scale(metal, 1.12)
                elif rib == 3:
                    color = _scale(light, 0.62)
                elif rib == 7:
                    color = _scale(dark, 1.15)
                else:
                    color = _scale(metal, 0.86 + n * 0.10)
                if y % 24 == 0 or y % 24 == 1:
                    color = _scale(dark, 0.75)
                if y % 24 == 2:
                    color = _scale(light, 0.48)
                if 28 <= y <= 33:
                    color = _scale(dark, 0.7 if x % 4 < 2 else 1.0)
                if 30 <= y <= 31 and x % 8 in (4, 5):
                    color = _mix(accent, metal, 0.35)
                if 8 <= y <= 10:
                    color = _scale(accent_2, 0.75)
                if (x % 16 == 8) and (y % 24 in (10, 11)):
                    color = _scale(light, 1.25)
            elif kind == 3:
                pane_x = x % 16
                pane_y = y % 16
                color = _scale(dark, 0.9 + n * 0.12)
                if pane_x in (0, 1) or pane_y in (0, 1):
                    color = _scale(metal, 0.55)
                elif pane_x in (14, 15) or pane_y in (14, 15):
                    color = _scale(metal, 0.36)
                else:
                    # Glowing window depth and a diagonal reflection.
                    glow = 0.06 + 0.08 * (1.0 - abs((pane_x - 8) / 8.0))
                    color = _mix(color, accent, glow)
                    if (pane_x + pane_y) % 16 in (2, 3):
                        color = _mix(color, accent_2, 0.22)
                if y in (6, 7):
                    color = _mix(accent, WHITE, 0.18)
                if y in (55, 56):
                    color = _scale(accent_2, 0.8)
                if x % 16 == 8 and 20 < y < 42:
                    color = _scale(light, 0.7)
            else:
                color = _scale(dark, 0.75 + n * 0.15)
                vein = math.sin(x * 0.30 + math.sin(y * 0.16) * 3.1 + kind) * 6.5
                if abs((y - 32) - vein) < 1.7:
                    color = _mix(base, accent, 0.58 + n * 0.3)
                if abs((x - 32) - math.sin(y * 0.22) * 7.5) < 0.9:
                    color = _mix(color, accent_2, 0.55)
                node_dist = math.hypot((x - 20) * 0.8, y - 22) + n * 1.2
                if node_dist < 4.8:
                    color = _mix(accent, WHITE, 0.35 * (1 - node_dist / 5.0))
                if 50 < y < 54 and 8 < x < 56:
                    color = _scale(metal, 0.55)
                if x % 32 == 0:
                    color = _scale(dark, 0.7)
            index = (y * size + x) * 4
            data[index : index + 4] = bytes((color[0], color[1], color[2], 255))
    return data


def _make_wall_textures(theme: Theme) -> dict[int, object]:
    return {kind: _texture_from_pixels(64, 64, _wall_pixels(kind, theme)) for kind in (1, 2, 3, 4)}


# ---------------------------------------------------------------------------
# Enemy sprite art
# ---------------------------------------------------------------------------
TROOPER_ARMOR = (52, 36, 49, 255)
TROOPER_RED = (176, 42, 62, 255)
TROOPER_LIGHT = (233, 85, 89, 255)
TROOPER_METAL = (92, 80, 91, 255)
TROOPER_GLOW = (255, 82, 76, 255)
TROOPER_DARK = (18, 13, 23, 255)


def _draw_trooper(pen: Pen, frame: int) -> None:
    shift = -1.0 if frame else 0.0
    pen.blend(True)
    pen.glow(36, 65, 18, (255, 57, 62, 80))
    pen.glow(36, 27, 11, (255, 87, 51, 55))
    pen.end_blend()

    # Rear arm and rifle.
    pen.poly([(48, 53), (61, 61), (56, 68), (43, 60)], TROOPER_DARK)
    pen.poly([(53, 61), (68, 68), (66, 75), (49, 68)], (35, 30, 39, 255))
    pen.poly([(64, 69), (74, 72), (73, 77), (62, 75)], (18, 20, 27, 255))
    pen.circle(72, 74, 2.2 + 0.6 * frame, TROOPER_GLOW)
    pen.line(56, 64, 70, 72, 1.4, (118, 91, 104, 255))

    # Legs.
    lx = 4.0 if frame else 0.0
    rx = -3.0 if frame else 0.0
    pen.poly([(27 - lx, 66), (36 - lx, 66), (34 - lx, 91), (24 - lx, 92)], TROOPER_DARK)
    pen.poly([(25 - lx, 91), (34 - lx, 91), (36 - lx, 106), (21 - lx, 106)], (43, 33, 47, 255))
    pen.poly([(24 - lx, 100), (35 - lx, 100), (36 - lx, 108), (22 - lx, 108)], TROOPER_METAL)
    pen.poly([(39 + rx, 66), (49 + rx, 66), (52 + rx, 91), (41 + rx, 92)], TROOPER_DARK)
    pen.poly([(42 + rx, 91), (52 + rx, 91), (53 + rx, 106), (39 + rx, 106)], (43, 33, 47, 255))
    pen.poly([(41 + rx, 100), (53 + rx, 100), (54 + rx, 108), (39 + rx, 108)], TROOPER_METAL)
    pen.line(28 - lx, 82, 34 - lx, 82, 1.8, TROOPER_RED)
    pen.line(43 + rx, 82, 50 + rx, 82, 1.8, TROOPER_RED)

    # Torso silhouette and armor plates.
    pen.poly([(18, 38), (54, 38), (59, 56), (52, 75), (20, 75), (13, 56)], TROOPER_DARK)
    pen.poly([(21, 40 + shift), (36, 36 + shift), (51, 40 + shift), (49, 61), (40, 71), (32, 71), (23, 61)], TROOPER_ARMOR)
    pen.poly([(24, 43 + shift), (35, 40 + shift), (34, 55), (28, 58), (22, 52)], (77, 47, 55, 255))
    pen.poly([(38, 40 + shift), (49, 43 + shift), (50, 52), (44, 58), (36, 55)], (101, 48, 59, 255))
    pen.poly([(28, 51), (36, 48), (44, 52), (42, 64), (30, 64)], TROOPER_RED)
    pen.poly([(33, 52), (39, 51), (41, 62), (31, 62)], TROOPER_LIGHT)
    pen.circle(36, 55, 2.4, (255, 204, 151, 255))
    pen.line(24, 57, 33, 58, 1.4, TROOPER_METAL)
    pen.line(39, 58, 49, 57, 1.4, TROOPER_METAL)

    # Belt and hip plates.
    pen.poly([(22, 68), (50, 68), (48, 76), (24, 76)], (38, 28, 43, 255))
    pen.poly([(31, 69), (36, 69), (36, 77), (31, 77)], TROOPER_RED)
    pen.circle(26, 72, 1.8, GOLD)
    pen.circle(46, 72, 1.8, GOLD)

    # Pauldrons.
    pen.poly([(13, 39), (26, 34), (29, 45), (20, 50)], TROOPER_DARK)
    pen.poly([(15, 39), (25, 36), (27, 44), (19, 48)], TROOPER_RED)
    pen.line(18, 40, 24, 38, 1.4, TROOPER_LIGHT)
    pen.poly([(46, 34), (59, 39), (56, 50), (47, 45)], TROOPER_DARK)
    pen.poly([(47, 36), (57, 39), (55, 48), (47, 44)], TROOPER_RED)
    pen.line(48, 38, 54, 40, 1.4, TROOPER_LIGHT)

    # Helmet and visor.
    pen.poly([(27, 20), (45, 20), (49, 30), (45, 38), (27, 38), (23, 30)], TROOPER_DARK)
    pen.poly([(28, 22), (44, 22), (47, 29), (43, 35), (29, 35), (25, 29)], (61, 45, 60, 255))
    pen.poly([(28, 15), (36, 11), (44, 15), (43, 22), (29, 22)], TROOPER_METAL)
    pen.poly([(29, 23), (43, 23), (41, 28), (31, 28)], (28, 17, 24, 255))
    pen.line(31, 26, 41, 26, 2.6, TROOPER_GLOW)
    pen.circle(36, 26, 1.5, (255, 210, 160, 255))
    pen.line(27, 31, 25, 37, 2.0, TROOPER_RED)
    pen.line(45, 31, 47, 37, 2.0, TROOPER_RED)

    # Chest and arm highlights.
    pen.line(18, 48, 16, 60, 1.6, (117, 75, 88, 255))
    pen.poly([(17, 50), (24, 54), (22, 63), (15, 58)], (57, 41, 50, 255))
    pen.poly([(56, 50), (49, 54), (51, 63), (58, 58)], (57, 41, 50, 255))
    pen.circle(16, 57, 1.3, TROOPER_GLOW)


def _draw_drone(pen: Pen, frame: int) -> None:
    tilt = 2.0 if frame else -2.0
    pen.blend(True)
    pen.glow(42, 44, 34, (255, 48, 74, 65))
    pen.glow(42, 70, 17, (70, 230, 255, 45))
    pen.end_blend()

    # Energy vanes.
    pen.poly([(16, 38), (32, 30), (34, 43), (21, 50)], (34, 27, 43, 255))
    pen.poly([(68, 38 + tilt), (52, 30), (50, 43), (63, 50)], (34, 27, 43, 255))
    pen.line(18, 40, 31, 34, 2.0, (108, 54, 71, 255))
    pen.line(66, 40, 53, 34, 2.0, (108, 54, 71, 255))

    # Hover thrusters.
    pen.poly([(29, 56), (38, 58), (36, 65), (30, 64)], (32, 35, 42, 255))
    pen.poly([(46, 58), (55, 56), (54, 64), (48, 65)], (32, 35, 42, 255))
    pen.blend(True)
    pen.glow(33, 69, 6 + frame, (66, 230, 255, 110))
    pen.glow(51, 69, 6 + (1 - frame), (66, 230, 255, 110))
    pen.end_blend()

    # Chassis layers.
    pen.poly([(42, 18), (62, 32), (58, 51), (42, 60), (26, 51), (22, 32)], (16, 14, 23, 255))
    pen.poly([(42, 22), (58, 33), (55, 48), (42, 55), (29, 48), (26, 33)], (54, 37, 51, 255))
    pen.poly([(42, 26), (54, 34), (51, 45), (42, 50), (33, 45), (30, 34)], (36, 29, 42, 255))
    pen.poly([(42, 31), (50, 36), (48, 43), (42, 46), (36, 43), (34, 36)], (104, 46, 58, 255))

    # Eye.
    pen.circle(42, 38, 8.5, (29, 16, 25, 255))
    pen.circle(42, 38, 6.5, (150, 36, 49, 255))
    pen.circle(42, 38, 4.2, TROOPER_GLOW)
    pen.circle(42, 38, 1.5, (255, 226, 198, 255))
    pen.line(33, 32, 37, 30, 1.2, (142, 94, 106, 255))
    pen.line(51, 32, 47, 30, 1.2, (142, 94, 106, 255))

    # Antennae and plating.
    pen.line(42, 17, 42, 9, 1.5, (103, 82, 100, 255))
    pen.circle(42, 8, 2.0 + frame * 0.3, MAGENTA)
    pen.line(25, 34, 20, 30 + tilt, 1.5, (110, 75, 95, 255))
    pen.line(59, 34, 64, 30 - tilt, 1.5, (110, 75, 95, 255))
    pen.line(33, 50, 42, 56, 1.6, (127, 55, 69, 255))
    pen.line(51, 50, 42, 56, 1.6, (127, 55, 69, 255))


def _draw_brute(pen: Pen, frame: int) -> None:
    shift = 2.0 if frame else 0.0
    pen.blend(True)
    pen.glow(56, 74, 38, (255, 62, 48, 70))
    pen.glow(56, 54, 22, (255, 117, 46, 55))
    pen.end_blend()

    # Legs.
    pen.poly([(38, 91), (53, 91), (49, 128), (34, 129)], (23, 18, 27, 255))
    pen.poly([(61, 91), (77, 91), (82, 127), (66, 130)], (23, 18, 27, 255))
    pen.poly([(34, 119), (49, 117), (53, 134), (29, 136)], (58, 44, 54, 255))
    pen.poly([(65, 118), (81, 119), (86, 136), (62, 135)], (58, 44, 54, 255))
    pen.poly([(30, 130), (53, 130), (54, 140), (27, 140)], (86, 65, 71, 255))
    pen.poly([(63, 131), (86, 131), (87, 141), (60, 141)], (86, 65, 71, 255))
    pen.line(39, 106, 47, 104, 2.0, TROOPER_RED)
    pen.line(68, 104, 78, 106, 2.0, TROOPER_RED)

    # Back and torso silhouette.
    pen.poly([(26, 48), (86, 48), (94, 72), (83, 99), (29, 99), (18, 72)], (17, 13, 21, 255))
    pen.poly([(31, 51 + shift), (56, 43 + shift), (81, 51 + shift), (86, 70), (77, 93), (35, 93), (26, 70)], (58, 40, 49, 255))
    pen.poly([(35, 55 + shift), (56, 49 + shift), (77, 55 + shift), (80, 68), (72, 86), (40, 86), (32, 68)], (82, 48, 54, 255))
    pen.poly([(43, 56), (56, 53), (69, 57), (71, 69), (65, 82), (47, 82), (41, 69)], (113, 44, 50, 255))
    pen.poly([(49, 60), (56, 57), (63, 60), (65, 69), (56, 75), (47, 69)], (158, 53, 51, 255))
    pen.circle(56, 66, 7.5, (44, 22, 25, 255))
    pen.circle(56, 66, 5.3, (255, 94, 52, 255))
    pen.circle(56, 66, 2.5, (255, 222, 170, 255))

    # Huge shoulder plates.
    pen.poly([(11, 51), (34, 40), (42, 58), (28, 72), (13, 68)], (18, 14, 22, 255))
    pen.poly([(14, 51), (33, 43), (38, 56), (27, 68), (16, 64)], (92, 52, 57, 255))
    pen.poly([(18, 51), (31, 46), (33, 54), (24, 62), (19, 60)], (150, 62, 62, 255))
    pen.line(17, 64, 29, 71, 1.8, (56, 40, 48, 255))
    pen.poly([(78, 52), (101, 44), (99, 68), (84, 72), (71, 58)], (18, 14, 22, 255))
    pen.poly([(79, 53), (98, 46), (96, 64), (83, 68), (73, 57)], (92, 52, 57, 255))
    pen.poly([(82, 53), (96, 48), (94, 58), (83, 63), (76, 58)], (150, 62, 62, 255))

    # Left cannon arm.
    pen.poly([(16, 64), (33, 67), (34, 82), (18, 84)], (36, 26, 33, 255))
    pen.poly([(12, 78), (33, 76), (34, 88), (11, 91)], (55, 47, 53, 255))
    pen.poly([(4, 81), (16, 81), (16, 92), (3, 92)], (25, 23, 29, 255))
    pen.circle(5, 86, 2.5, TROOPER_GLOW)
    pen.line(17, 81, 31, 80, 1.3, (143, 75, 72, 255))

    # Head and tusks.
    pen.poly([(48, 33), (65, 33), (69, 44), (62, 53), (50, 52), (44, 43)], (17, 13, 21, 255))
    pen.poly([(49, 35), (63, 35), (66, 43), (60, 49), (51, 48), (47, 43)], (100, 59, 61, 255))
    pen.poly([(50, 40), (63, 40), (61, 45), (52, 45)], (29, 19, 25, 255))
    pen.line(52, 42, 61, 42, 2.2, (255, 141, 74, 255))
    pen.poly([(45, 43), (49, 42), (47, 51), (43, 48)], (215, 188, 140, 255))
    pen.poly([(66, 43), (62, 42), (64, 51), (69, 48)], (215, 188, 140, 255))

    # Surface damage and trim.
    pen.line(30, 57, 36, 62, 1.3, (49, 34, 40, 255))
    pen.line(74, 61, 81, 65, 1.3, (49, 34, 40, 255))
    pen.circle(34, 72, 2.0, GOLD)
    pen.circle(78, 72, 2.0, GOLD)
    pen.line(44, 84, 69, 84, 2.0, (53, 35, 41, 255))


def _draw_boss(pen: Pen, frame: int) -> None:
    pulse = 1.0 + 0.12 * math.sin(frame * math.pi)
    pen.blend(True)
    pen.glow(85, 112, 64 * pulse, (166, 80, 255, 55))
    pen.glow(85, 88, 35, (255, 88, 192, 55))
    pen.glow(85, 142, 44, (255, 183, 64, 30))
    pen.end_blend()

    # Cape / wing silhouette.
    pen.poly([(33, 60), (9, 112), (24, 188), (58, 163), (62, 84)], (25, 17, 37, 255))
    pen.poly([(137, 60), (161, 112), (146, 188), (112, 163), (108, 84)], (25, 17, 37, 255))
    pen.line(20, 120, 33, 172, 2.0, (57, 38, 83, 255))
    pen.line(150, 120, 137, 172, 2.0, (57, 38, 83, 255))

    # Legs and boots.
    pen.poly([(61, 143), (82, 143), (76, 198), (53, 200)], (18, 13, 26, 255))
    pen.poly([(89, 143), (110, 143), (118, 200), (95, 198)], (18, 13, 26, 255))
    pen.poly([(52, 187), (77, 185), (82, 211), (46, 213)], (40, 29, 54, 255))
    pen.poly([(94, 185), (119, 187), (125, 213), (89, 211)], (40, 29, 54, 255))
    pen.poly([(48, 204), (80, 204), (82, 217), (43, 218)], (83, 62, 48, 255))
    pen.poly([(91, 204), (123, 204), (128, 218), (89, 217)], (83, 62, 48, 255))
    pen.line(64, 166, 76, 164, 2.0, GOLD)
    pen.line(95, 164, 107, 166, 2.0, GOLD)

    # Torso.
    pen.poly([(44, 71), (126, 71), (139, 103), (123, 153), (47, 153), (31, 103)], (14, 11, 22, 255))
    pen.poly([(51, 76 + (1 if frame else 0)), (118, 76), (131, 102), (115, 144), (55, 144), (39, 102)], (47, 33, 66, 255))
    pen.poly([(57, 82), (112, 82), (122, 101), (109, 134), (61, 134), (48, 101)], (73, 44, 91, 255))
    pen.poly([(69, 87), (101, 87), (110, 103), (97, 126), (73, 126), (60, 103)], (40, 25, 56, 255))

    # Core.
    pen.circle(85, 105, 21, (24, 14, 34, 255))
    pen.circle(85, 105, 17, (122, 47, 117, 255))
    pen.circle(85, 105, 13, (229, 66, 175, 255))
    pen.circle(85, 105, 8, (255, 133, 226, 255))
    pen.circle(85, 105, 3.5, WHITE)
    for angle in (0, 60, 120, 180, 240, 300):
        rad = math.radians(angle + frame * 8)
        x1 = 85 + math.cos(rad) * 24
        y1 = 105 + math.sin(rad) * 24
        x2 = 85 + math.cos(rad) * 32
        y2 = 105 + math.sin(rad) * 32
        pen.line(x1, y1, x2, y2, 2.0, (199, 118, 255, 255))

    # Shoulder towers.
    pen.poly([(25, 74), (51, 58), (64, 79), (49, 104), (28, 99)], (14, 11, 22, 255))
    pen.poly([(29, 75), (50, 63), (59, 80), (47, 98), (32, 94)], (65, 43, 82, 255))
    pen.poly([(34, 75), (49, 68), (54, 78), (45, 90), (35, 87)], (97, 62, 112, 255))
    pen.line(33, 78, 42, 69, 2.0, GOLD)
    pen.circle(32, 83, 3.0, (255, 194, 84, 255))
    pen.poly([(119, 58), (145, 74), (142, 99), (121, 104), (106, 79)], (14, 11, 22, 255))
    pen.poly([(121, 63), (140, 75), (138, 94), (123, 98), (112, 80)], (65, 43, 82, 255))
    pen.poly([(123, 68), (137, 75), (135, 89), (126, 93), (117, 79)], (97, 62, 112, 255))
    pen.line(137, 78, 128, 69, 2.0, GOLD)
    pen.circle(138, 83, 3.0, (255, 194, 84, 255))

    # Arms and arm cannons.
    pen.poly([(32, 97), (52, 103), (48, 127), (32, 135), (22, 121)], (24, 18, 34, 255))
    pen.poly([(21, 121), (42, 113), (50, 132), (41, 151), (18, 143)], (47, 33, 62, 255))
    pen.poly([(11, 136), (36, 139), (38, 153), (9, 156)], (22, 19, 29, 255))
    pen.circle(11, 147, 4.5, (255, 102, 210, 255))
    pen.circle(11, 147, 2.0, (255, 218, 247, 255))
    pen.poly([(118, 103), (138, 97), (148, 121), (138, 135), (118, 127)], (24, 18, 34, 255))
    pen.poly([(130, 113), (151, 121), (150, 143), (127, 151), (118, 132)], (47, 33, 62, 255))
    pen.poly([(139, 137), (161, 135), (164, 151), (140, 155)], (22, 19, 29, 255))
    pen.circle(160, 145, 4.5, (255, 102, 210, 255))
    pen.circle(160, 145, 2.0, (255, 218, 247, 255))

    # Helmet and horns.
    pen.poly([(66, 36), (104, 36), (111, 53), (102, 72), (68, 72), (59, 53)], (13, 10, 20, 255))
    pen.poly([(69, 40), (101, 40), (106, 53), (98, 67), (72, 67), (64, 53)], (58, 41, 74, 255))
    pen.poly([(73, 47), (97, 47), (101, 54), (93, 60), (77, 60), (69, 54)], (21, 15, 29, 255))
    pen.line(77, 53, 93, 53, 3.2, (255, 104, 219, 255))
    pen.circle(79, 53, 2.0, (255, 231, 244, 255))
    pen.circle(91, 53, 2.0, (255, 231, 244, 255))
    pen.poly([(64, 38), (53, 12), (68, 24), (78, 37)], (83, 61, 48, 255))
    pen.poly([(106, 38), (117, 12), (102, 24), (92, 37)], (83, 61, 48, 255))
    pen.line(61, 28, 54, 14, 2.0, (212, 166, 92, 255))
    pen.line(109, 28, 116, 14, 2.0, (212, 166, 92, 255))

    # Gold trim details.
    for x1, y1, x2, y2 in [
        (57, 84, 50, 96),
        (113, 84, 120, 96),
        (61, 134, 72, 146),
        (109, 134, 98, 146),
    ]:
        pen.line(x1, y1, x2, y2, 1.8, (211, 167, 92, 255))
    pen.circle(85, 187, 3.0, GOLD)


def _draw_pickup_health(pen: Pen) -> None:
    pen.blend(True)
    pen.glow(24, 24, 22, (81, 255, 188, 80))
    pen.end_blend()
    pen.circle(24, 24, 14, (18, 57, 49, 255))
    pen.circle(24, 24, 12, (33, 108, 87, 255))
    pen.ring(24, 24, 13, 16, 0, 360, 24, (80, 240, 189, 255))
    pen.rect(21, 14, 6, 20, (197, 255, 231, 255))
    pen.rect(14, 21, 20, 6, (197, 255, 231, 255))
    pen.circle(24, 24, 3, (255, 255, 255, 255))


def _draw_pickup_ammo(pen: Pen) -> None:
    pen.blend(True)
    pen.glow(24, 24, 22, (255, 169, 70, 80))
    pen.end_blend()
    pen.poly([(14, 9), (34, 9), (36, 37), (12, 37)], (64, 38, 20, 255))
    pen.poly([(17, 12), (31, 12), (32, 34), (16, 34)], (138, 76, 27, 255))
    pen.rect(19, 15, 10, 3, (255, 222, 150, 255))
    pen.poly([(25, 14), (19, 25), (24, 25), (20, 34), (30, 21), (25, 21)], (255, 219, 112, 255))
    pen.ring(24, 24, 15, 18, 30, 330, 20, (255, 148, 57, 255))


def _draw_pickup_nova(pen: Pen) -> None:
    pen.blend(True)
    pen.glow(24, 24, 24, (255, 88, 226, 90))
    pen.end_blend()
    points = []
    for index in range(8):
        angle = -math.pi / 2 + index * math.pi / 4
        radius = 15 if index % 2 == 0 else 6
        points.append((24 + math.cos(angle) * radius, 24 + math.sin(angle) * radius))
    pen.poly(points, (92, 31, 95, 255))
    points = []
    for index in range(8):
        angle = -math.pi / 2 + index * math.pi / 4
        radius = 11 if index % 2 == 0 else 4
        points.append((24 + math.cos(angle) * radius, 24 + math.sin(angle) * radius))
    pen.poly(points, (255, 91, 215, 255))
    pen.circle(24, 24, 4.5, (255, 225, 251, 255))
    pen.ring(24, 24, 16, 19, 0, 360, 28, (206, 99, 255, 255))


def _draw_pickup_intel(pen: Pen) -> None:
    pen.blend(True)
    pen.glow(24, 24, 22, (255, 210, 92, 75))
    pen.end_blend()
    pen.poly([(24, 7), (39, 17), (34, 38), (14, 38), (9, 17)], (74, 55, 25, 255))
    pen.poly([(24, 11), (35, 19), (31, 34), (17, 34), (13, 19)], (193, 137, 43, 255))
    pen.poly([(24, 15), (31, 20), (28, 31), (20, 31), (17, 20)], (255, 210, 102, 255))
    pen.line(24, 15, 24, 31, 1.5, (255, 246, 203, 255))
    pen.ring(24, 24, 17, 19, 0, 360, 30, (255, 190, 70, 255))


# ---------------------------------------------------------------------------
# Screen overlays
# ---------------------------------------------------------------------------
def _vignette_pixels(width: int, height: int) -> bytearray:
    data = bytearray(width * height * 4)
    cx = width * 0.5
    cy = height * 0.5
    max_dist = math.hypot(cx, cy)
    for y in range(height):
        for x in range(width):
            dx = (x - cx) / cx
            dy = (y - cy) / cy
            dist = math.sqrt(dx * dx * 0.82 + dy * dy * 1.12)
            value = clamp((dist - 0.55) / 0.85, 0.0, 1.0)
            alpha_value = int(215 * value * value)
            index = (y * width + x) * 4
            data[index : index + 4] = bytes((0, 0, 0, alpha_value))
    return data


# ---------------------------------------------------------------------------
# Public texture library
# ---------------------------------------------------------------------------
class TextureLibrary:
    def __init__(self) -> None:
        self.wall_sets: dict[str, dict[int, object]] = {}
        self.enemy: dict[str, list] = {}
        self.pickups: dict[str, object] = {}
        self.vignette = None
        self.reload()

    def reload(self) -> None:
        self.unload()
        self.vignette = _texture_from_pixels(WORLD_W, WORLD_H, _vignette_pixels(WORLD_W, WORLD_H), False)
        self._make_enemy_sprites()
        self.pickups = {
            "health": _sprite_texture(48, 48, _draw_pickup_health),
            "ammo": _sprite_texture(48, 48, _draw_pickup_ammo),
            "nova": _sprite_texture(48, 48, _draw_pickup_nova),
            "intel": _sprite_texture(48, 48, _draw_pickup_intel),
        }

    def _make_enemy_sprites(self) -> None:
        self.enemy = {
            "trooper": [
                _sprite_texture(72, 112, lambda p, frame=0: _draw_trooper(p, frame)),
                _sprite_texture(72, 112, lambda p, frame=1: _draw_trooper(p, frame)),
            ],
            "drone": [
                _sprite_texture(84, 84, lambda p, frame=0: _draw_drone(p, frame)),
                _sprite_texture(84, 84, lambda p, frame=1: _draw_drone(p, frame)),
            ],
            "brute": [
                _sprite_texture(112, 150, lambda p, frame=0: _draw_brute(p, frame)),
                _sprite_texture(112, 150, lambda p, frame=1: _draw_brute(p, frame)),
            ],
            "boss": [
                _sprite_texture(170, 220, lambda p, frame=0: _draw_boss(p, frame), supersample=2),
                _sprite_texture(170, 220, lambda p, frame=1: _draw_boss(p, frame), supersample=2),
            ],
        }

    def walls_for(self, theme: Theme):
        if theme.key not in self.wall_sets:
            self.wall_sets[theme.key] = _make_wall_textures(theme)
        return self.wall_sets[theme.key]

    def unload(self) -> None:
        for wall_set in self.wall_sets.values():
            for texture in wall_set.values():
                rl.UnloadTexture(texture)
        self.wall_sets.clear()
        for frames in self.enemy.values():
            for texture in frames:
                rl.UnloadTexture(texture)
        self.enemy.clear()
        for texture in self.pickups.values():
            rl.UnloadTexture(texture)
        self.pickups.clear()
        if self.vignette is not None:
            rl.UnloadTexture(self.vignette)
            self.vignette = None
