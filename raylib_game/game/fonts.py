"""Font loading and text-drawing helpers."""

from __future__ import annotations

import math
from functools import lru_cache

import raylib as rl

from .config import FONT_DIR, WHITE, alpha


class FontBook:
    """Loads the bundled display/body fonts with a safe fallback."""

    def __init__(self) -> None:
        self.display = self._load("Orbitron.ttf", 96)
        self.bold = self._load("Rajdhani-Bold.ttf", 64)
        self.body = self._load("Rajdhani-Medium.ttf", 48)
        self.small = self._load("Rajdhani-Medium.ttf", 30)
        self._width_cache: dict[tuple[int, str, int, int], float] = {}
        self._fallback = False

    def _load(self, filename: str, size: int):
        path = FONT_DIR / filename
        if path.exists():
            try:
                font = rl.LoadFontEx(str(path).encode("utf-8"), size, rl.ffi.NULL, 0)
                if font.texture.width > 0:
                    rl.SetTextureFilter(font.texture, rl.TEXTURE_FILTER_BILINEAR)
                    return font
            except Exception:
                pass
        self._fallback = True
        return rl.GetFontDefault()

    @property
    def using_fallback(self) -> bool:
        return self._fallback

    # ------------------------------------------------------------------
    # Measurement
    # ------------------------------------------------------------------
    def width(self, font, text: str, size: float, spacing: float = 0.0) -> float:
        key = (id(font), text, int(round(size)), int(round(spacing)))
        cached = self._width_cache.get(key)
        if cached is not None:
            return cached
        if not text:
            return 0.0
        measured = rl.MeasureTextEx(font, text.encode("utf-8", "replace"), float(size), float(spacing))
        result = float(measured.x)
        if len(self._width_cache) > 2500:
            self._width_cache.clear()
        self._width_cache[key] = result
        return result

    def height(self, size: float) -> float:
        return size * 0.82

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw(
        self,
        font,
        text: str,
        x: float,
        y: float,
        size: float,
        color=WHITE,
        spacing: float = 0.0,
        opacity: int = 255,
    ) -> None:
        if not text:
            return
        if opacity < 255:
            color = (color[0], color[1], color[2], int(max(0, min(255, color[3] * opacity / 255))))
        rl.DrawTextEx(font, text.encode("utf-8", "replace"), (float(x), float(y)), float(size), float(spacing), color)

    def draw_right(
        self,
        font,
        text: str,
        right_x: float,
        y: float,
        size: float,
        color=WHITE,
        spacing: float = 0.0,
        opacity: int = 255,
    ) -> None:
        self.draw(font, text, right_x - self.width(font, text, size, spacing), y, size, color, spacing, opacity)

    def draw_center(
        self,
        font,
        text: str,
        center_x: float,
        y: float,
        size: float,
        color=WHITE,
        spacing: float = 0.0,
        opacity: int = 255,
    ) -> None:
        self.draw(font, text, center_x - self.width(font, text, size, spacing) * 0.5, y, size, color, spacing, opacity)

    def draw_shadow(
        self,
        font,
        text: str,
        x: float,
        y: float,
        size: float,
        color=WHITE,
        shadow=(0, 0, 0, 180),
        offset: float = 2.0,
        spacing: float = 0.0,
    ) -> None:
        self.draw(font, text, x + offset, y + offset, size, shadow, spacing)
        self.draw(font, text, x, y, size, color, spacing)

    def draw_center_shadow(
        self,
        font,
        text: str,
        center_x: float,
        y: float,
        size: float,
        color=WHITE,
        shadow=(0, 0, 0, 180),
        offset: float = 2.0,
        spacing: float = 0.0,
    ) -> None:
        x = center_x - self.width(font, text, size, spacing) * 0.5
        self.draw_shadow(font, text, x, y, size, color, shadow, offset, spacing)

    def draw_glow(
        self,
        font,
        text: str,
        x: float,
        y: float,
        size: float,
        color,
        glow_color,
        strength: int = 3,
        spacing: float = 0.0,
    ) -> None:
        """Cheap neon glow made from a few offset copies."""
        for offset in range(strength, 0, -1):
            fade = alpha(glow_color, max(8, 34 // offset))
            for dx, dy in ((-offset, 0), (offset, 0), (0, -offset), (0, offset)):
                self.draw(font, text, x + dx, y + dy, size, fade, spacing)
        self.draw(font, text, x, y, size, color, spacing)

    def draw_center_glow(
        self,
        font,
        text: str,
        center_x: float,
        y: float,
        size: float,
        color,
        glow_color,
        strength: int = 3,
        spacing: float = 0.0,
    ) -> None:
        x = center_x - self.width(font, text, size, spacing) * 0.5
        self.draw_glow(font, text, x, y, size, color, glow_color, strength, spacing)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def wrap(self, font, text: str, size: float, max_width: float, spacing: float = 0.0) -> list[str]:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = word if not current else current + " " + word
            if self.width(font, candidate, size, spacing) <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def draw_wrapped(
        self,
        font,
        text: str,
        x: float,
        y: float,
        size: float,
        max_width: float,
        color=WHITE,
        line_gap: float = 1.25,
        spacing: float = 0.0,
        opacity: int = 255,
    ) -> float:
        line_h = size * line_gap
        for index, line in enumerate(self.wrap(font, text, size, max_width, spacing)):
            self.draw(font, line, x, y + index * line_h, size, color, spacing, opacity)
        return y + len(self.wrap(font, text, size, max_width, spacing)) * line_h

    def unload(self) -> None:
        fallback = rl.GetFontDefault()
        for font in (self.display, self.bold, self.body, self.small):
            try:
                if font.texture.id != fallback.texture.id:
                    rl.UnloadFont(font)
            except Exception:
                pass


def with_opacity(color, opacity: int):
    return (color[0], color[1], color[2], int(max(0, min(255, opacity))))


def format_number(value: int) -> str:
    return f"{int(value):,}"


def format_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    minutes = int(seconds // 60)
    rest = seconds - minutes * 60
    return f"{minutes:02d}:{rest:05.2f}"
