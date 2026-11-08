"""Small maths, colour and drawing helpers shared by the whole game."""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
import pygame

# ---------------------------------------------------------------------------
# Maths
# ---------------------------------------------------------------------------


def clamp(value: float, lo: float, hi: float) -> float:
    return lo if value < lo else hi if value > hi else value


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def inv_lerp(a: float, b: float, value: float) -> float:
    if b == a:
        return 0.0
    return clamp((value - a) / (b - a), 0.0, 1.0)


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    t = inv_lerp(edge0, edge1, x)
    return t * t * (3.0 - 2.0 * t)


def ease_out_cubic(t: float) -> float:
    return 1.0 - (1.0 - t) ** 3


def ease_in_out(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def exp_smooth(current: float, target: float, rate: float, dt: float) -> float:
    return target + (current - target) * math.exp(-rate * dt)


def sign(value: float) -> int:
    return (value > 0) - (value < 0)


def approach(value: float, target: float, amount: float) -> float:
    if value < target:
        return min(value + amount, target)
    return max(value - amount, target)


def angle_to(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.atan2(y2 - y1, x2 - x1)


# ---------------------------------------------------------------------------
# Colour
# ---------------------------------------------------------------------------


def to01(color: tuple[int, int, int]) -> tuple[float, float, float]:
    return (color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)


def color_lerp(a, b, t: float) -> tuple[int, int, int]:
    t = clamp(t, 0.0, 1.0)
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def color_scale(color, k: float) -> tuple[int, int, int]:
    return (
        int(clamp(color[0] * k, 0, 255)),
        int(clamp(color[1] * k, 0, 255)),
        int(clamp(color[2] * k, 0, 255)),
    )


def mix_color(a, b, amount=0.5):
    """Alias used by effect-heavy code, kept readable."""
    return color_lerp(a, b, amount)


def palette_lerp(a: dict, b: dict, t: float) -> dict:
    """Blend two biome palettes, preserving the name of the target."""
    out = dict(a)
    for key, value in a.items():
        other = b.get(key)
        if isinstance(other, tuple) and len(value) == 3:
            out[key] = color_lerp(value, other, t)
    out["name"] = b["name"]
    out["tagline"] = b["tagline"]
    return out


# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------


@lru_cache(maxsize=64)
def font(name: str, size: int, bold: bool = False) -> pygame.font.Font:
    try:
        f = pygame.font.SysFont(name, size, bold=bold)
    except Exception:
        f = pygame.font.Font(None, size)
    return f


_TEXT_CACHE: dict[tuple, pygame.Surface] = {}


def text(
    value: str,
    f: pygame.font.Font,
    color,
    shadow=None,
    shadow_offset: int = 2,
) -> pygame.Surface:
    key = (value, id(f), tuple(color), tuple(shadow) if shadow else None, shadow_offset)
    hit = _TEXT_CACHE.get(key)
    if hit is not None:
        return hit
    base = f.render(value, True, color)
    if shadow is not None:
        sh = f.render(value, True, shadow)
        out = pygame.Surface(
            (base.get_width() + shadow_offset, base.get_height() + shadow_offset),
            pygame.SRCALPHA,
        )
        out.blit(sh, (shadow_offset, shadow_offset))
        out.blit(base, (0, 0))
        base = out
    if len(_TEXT_CACHE) > 512:
        _TEXT_CACHE.clear()
    _TEXT_CACHE[key] = base
    return base


def draw_text(
    surface: pygame.Surface,
    value: str,
    f: pygame.font.Font,
    color,
    pos,
    anchor: str = "topleft",
    shadow=(0, 0, 0),
    shadow_offset: int = 2,
) -> pygame.Rect:
    img = text(value, f, color, shadow, shadow_offset)
    rect = img.get_rect(**{anchor: pos})
    surface.blit(img, rect)
    return rect


def draw_text_spaced(
    surface: pygame.Surface,
    value: str,
    f: pygame.font.Font,
    color,
    pos,
    spacing: int = 6,
    anchor: str = "topleft",
    shadow=(0, 0, 0),
    shadow_offset: int = 3,
) -> pygame.Rect:
    """Draw text with extra letter spacing; nice for the logo / headings."""
    glyphs = []
    width = 0
    height = 0
    for ch in value:
        g = text(ch, f, color, shadow, shadow_offset)
        glyphs.append(g)
        width += g.get_width() + spacing
        height = max(height, g.get_height())
    width = max(0, width - spacing)
    rect = pygame.Rect(0, 0, width, height)
    setattr(rect, anchor, pos)
    x = rect.left
    for g in glyphs:
        surface.blit(g, (x, rect.top))
        x += g.get_width() + spacing
    return rect


# ---------------------------------------------------------------------------
# Glow sprites (cached, generated with numpy)
# ---------------------------------------------------------------------------

_GLOW_CACHE: dict[tuple, pygame.Surface] = {}


def glow_surface(radius: int, color, power: float = 2.0, alpha: int = 255) -> pygame.Surface:
    """A soft radial sprite.  Alpha is quantised so the cache stays small."""
    radius = max(2, int(radius))
    alpha = int(clamp(alpha, 0, 255) // 16 * 16)
    key = (radius, tuple(color), round(power, 1), alpha)
    hit = _GLOW_CACHE.get(key)
    if hit is not None:
        return hit

    size = radius * 2 + 2
    yy, xx = np.mgrid[0:size, 0:size]
    cx = cy = radius
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / max(1.0, radius)
    falloff = np.clip(1.0 - dist, 0.0, 1.0) ** power
    arr = np.zeros((size, size, 4), dtype=np.uint8)
    arr[..., 0] = color[0]
    arr[..., 1] = color[1]
    arr[..., 2] = color[2]
    arr[..., 3] = (falloff * alpha).astype(np.uint8)
    surf = pygame.image.frombuffer(arr.tobytes(), (size, size), "RGBA").copy()
    if len(_GLOW_CACHE) > 900:
        _GLOW_CACHE.clear()
    _GLOW_CACHE[key] = surf
    return surf


def draw_glow(surface: pygame.Surface, center, radius: int, color, alpha: int = 160,
              power: float = 2.0, additive: bool = False) -> None:
    if alpha <= 4:
        return
    sprite = glow_surface(radius, color, power, alpha)
    flags = pygame.BLEND_RGBA_ADD if additive else 0
    surface.blit(sprite, (int(center[0]) - radius, int(center[1]) - radius),
                 special_flags=flags)


def draw_shadow(surface: pygame.Surface, center, size, alpha: int = 80) -> None:
    w, h = int(size[0]), int(size[1])
    if w <= 0 or h <= 0:
        return
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (0, 0, 0, alpha), surf.get_rect())
    surface.blit(surf, (int(center[0] - w / 2), int(center[1] - h / 2)))


# ---------------------------------------------------------------------------
# Shapes
# ---------------------------------------------------------------------------


def polygon_alpha(surface: pygame.Surface, color, points, alpha: int = 255) -> None:
    if alpha >= 255:
        pygame.draw.polygon(surface, color, points)
        return
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, x1 = int(min(xs)), int(max(xs)) + 1
    y0, y1 = int(min(ys)), int(max(ys)) + 1
    if x1 <= x0 or y1 <= y0:
        return
    tmp = pygame.Surface((x1 - x0, y1 - y0), pygame.SRCALPHA)
    pygame.draw.polygon(tmp, (*color, alpha), [(p[0] - x0, p[1] - y0) for p in points])
    surface.blit(tmp, (x0, y0))


def rounded_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    fill,
    alpha: int = 210,
    border=None,
    border_alpha: int = 255,
    radius: int = 12,
    border_width: int = 1,
) -> None:
    rect = pygame.Rect(rect)
    tmp = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(tmp, (*fill, alpha), tmp.get_rect(), border_radius=radius)
    if border is not None:
        pygame.draw.rect(tmp, (*border, border_alpha), tmp.get_rect(),
                         width=border_width, border_radius=radius)
    surface.blit(tmp, rect.topleft)


def line_alpha(surface, color, start, end, width=1, alpha=255):
    if alpha >= 255:
        pygame.draw.line(surface, color, start, end, width)
        return
    x0, x1 = int(min(start[0], end[0])), int(max(start[0], end[0])) + 1
    y0, y1 = int(min(start[1], end[1])), int(max(start[1], end[1])) + 1
    tmp = pygame.Surface((x1 - x0 + 2, y1 - y0 + 2), pygame.SRCALPHA)
    pygame.draw.line(tmp, (*color, alpha), (start[0] - x0, start[1] - y0),
                     (end[0] - x0, end[1] - y0), width)
    surface.blit(tmp, (x0, y0))


def heart_points(cx: float, cy: float, size: float) -> list[tuple[float, float]]:
    """A chunky, readable heart polygon."""
    s = size / 2.0
    return [
        (cx, cy + s * 0.95),
        (cx - s * 0.92, cy - s * 0.05),
        (cx - s * 0.9, cy - s * 0.55),
        (cx - s * 0.5, cy - s * 0.9),
        (cx, cy - s * 0.45),
        (cx + s * 0.5, cy - s * 0.9),
        (cx + s * 0.9, cy - s * 0.55),
        (cx + s * 0.92, cy - s * 0.05),
    ]


def draw_heart(surface, center, size, color, glow=None, alpha=255):
    pts = heart_points(center[0], center[1], size)
    if alpha < 255:
        polygon_alpha(surface, color, pts, alpha)
    else:
        pygame.draw.polygon(surface, color, pts)
    if glow:
        draw_glow(surface, center, int(size * 0.9), glow, 44, 2.4)


def format_score(value: int) -> str:
    return f"{value:,}"


def format_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    if seconds < 10:
        return f"{seconds:4.1f}"
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"
