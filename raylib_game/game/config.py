"""Global configuration, color helpers, and small math utilities."""

from __future__ import annotations

import math
import os
from pathlib import Path

from . import raycompat  # noqa: F401  (patches raylib's int-only drawing calls)

# ---------------------------------------------------------------------------
# Presentation
# ---------------------------------------------------------------------------
GAME_TITLE = "NOVA STRIKE"
GAME_SUBTITLE = "ECLIPSE PROTOCOL"
WINDOW_W = 1280
WINDOW_H = 720
WORLD_W = 640
WORLD_H = 360
COLUMN_W = 2
FOV = math.radians(72.0)
PROJ_PLANE = (WORLD_W * 0.5) / math.tan(FOV * 0.5)
TARGET_FPS = 60
MAX_FRAME_TIME = 0.05

BASE_DIR = Path(__file__).resolve().parent.parent
ASSET_DIR = BASE_DIR / "assets"
FONT_DIR = ASSET_DIR / "fonts"
AUDIO_DIR = ASSET_DIR / "audio"
SAVE_PATH = BASE_DIR / "savegame.json"
SCREENSHOT_DIR = BASE_DIR / "screenshots"

# Palette (RGBA tuples are passed directly to raylib).
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
CLEAR = (0, 0, 0, 0)
INK = (7, 10, 20, 255)
NAVY = (11, 17, 34, 255)
SLATE = (23, 33, 54, 255)
STEEL = (46, 60, 84, 255)
MIST = (151, 170, 195, 255)
PAPER = (234, 242, 250, 255)
GOLD = (255, 196, 76, 255)
ORANGE = (255, 126, 48, 255)
RED = (255, 67, 88, 255)
CRIMSON = (196, 38, 63, 255)
CYAN = (72, 231, 255, 255)
TEAL = (35, 180, 188, 255)
BLUE = (68, 139, 255, 255)
VIOLET = (162, 92, 255, 255)
MAGENTA = (255, 74, 181, 255)
GREEN = (93, 245, 169, 255)

# UI accent used by menus. Levels can override this with their own accent.
UI_ACCENT = CYAN
UI_WARN = ORANGE
UI_DANGER = RED


def clamp(value: float, lo: float, hi: float) -> float:
    return lo if value < lo else hi if value > hi else value


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def inv_lerp(a: float, b: float, v: float) -> float:
    if abs(b - a) < 1e-9:
        return 0.0
    return clamp((v - a) / (b - a), 0.0, 1.0)


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    t = inv_lerp(edge0, edge1, x)
    return t * t * (3.0 - 2.0 * t)


def approach(current: float, target: float, speed: float, dt: float) -> float:
    delta = target - current
    step = speed * dt
    if abs(delta) <= step:
        return target
    return current + math.copysign(step, delta)


def angle_difference(a: float, b: float) -> float:
    return (a - b + math.pi) % (math.tau) - math.pi


def shade(color: tuple[int, int, int, int], factor: float, alpha: int | None = None) -> tuple[int, int, int, int]:
    return (
        int(clamp(color[0] * factor, 0, 255)),
        int(clamp(color[1] * factor, 0, 255)),
        int(clamp(color[2] * factor, 0, 255)),
        color[3] if alpha is None else int(clamp(alpha, 0, 255)),
    )


def alpha(color: tuple[int, int, int, int], value: int) -> tuple[int, int, int, int]:
    return (color[0], color[1], color[2], int(clamp(value, 0, 255)))


def mix_color(
    a: tuple[int, int, int, int],
    b: tuple[int, int, int, int],
    t: float,
    alpha_value: int | None = None,
) -> tuple[int, int, int, int]:
    t = clamp(t, 0.0, 1.0)
    return (
        int(lerp(a[0], b[0], t)),
        int(lerp(a[1], b[1], t)),
        int(lerp(a[2], b[2], t)),
        int(lerp(a[3], b[3], t)) if alpha_value is None else int(clamp(alpha_value, 0, 255)),
    )


def tint(brightness: float, color: tuple[int, int, int, int] = WHITE) -> tuple[int, int, int, int]:
    return (
        int(clamp(color[0] * brightness, 0, 255)),
        int(clamp(color[1] * brightness, 0, 255)),
        int(clamp(color[2] * brightness, 0, 255)),
        color[3],
    )


def pulse(time_value: float, speed: float = 1.0, lo: float = 0.0, hi: float = 1.0) -> float:
    wave = 0.5 + 0.5 * math.sin(time_value * speed * math.tau)
    return lo + (hi - lo) * wave


def safe_int(value: float) -> int:
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return 0


def ensure_dirs() -> None:
    for path in (AUDIO_DIR, SCREENSHOT_DIR):
        path.mkdir(parents=True, exist_ok=True)


def relative_asset(*parts: str) -> str:
    """Return an absolute filesystem path as a UTF-8 string."""
    return os.path.join(str(ASSET_DIR), *parts)
