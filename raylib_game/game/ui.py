"""All 2D presentation: menus, HUD, weapon viewmodel, and screen effects."""

from __future__ import annotations

import math
import random

import raylib as rl

from .config import (
    BLACK,
    BLUE,
    CLEAR,
    CRIMSON,
    CYAN,
    GOLD,
    GREEN,
    INK,
    MAGENTA,
    MIST,
    NAVY,
    ORANGE,
    PAPER,
    RED,
    SCREENSHOT_DIR,
    SLATE,
    STEEL,
    TEAL,
    VIOLET,
    WHITE,
    WINDOW_H,
    WINDOW_W,
    WORLD_H,
    WORLD_W,
    alpha,
    clamp,
    lerp,
    mix_color,
    pulse,
    shade,
    smoothstep,
)
from .entities import ENEMY_KINDS, WEAPONS
from .fonts import format_number, format_time
from .levels import LEVELS, THREAT_COLORS

SCREEN_CENTER_X = WINDOW_W // 2
SCREEN_CENTER_Y = WINDOW_H // 2


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def poly(points, color) -> None:
    if len(points) < 3:
        return
    area = 0.0
    for index, point in enumerate(points):
        nx, ny = points[(index + 1) % len(points)]
        area += point[0] * ny - nx * point[1]
    if area > 0:
        points = list(reversed(points))
    for index in range(1, len(points) - 1):
        rl.DrawTriangle(points[0], points[index], points[index + 1], color)


def poly_outline(points, color, thickness: float = 1.0) -> None:
    for index in range(len(points)):
        a = points[index]
        b = points[(index + 1) % len(points)]
        rl.DrawLineEx(a, b, thickness, color)


def cut_panel_points(x: float, y: float, w: float, h: float, cut: float = 12.0):
    return [
        (x + cut, y),
        (x + w, y),
        (x + w, y + h - cut),
        (x + w - cut, y + h),
        (x, y + h),
        (x, y + cut),
    ]


def draw_cut_panel(x, y, w, h, fill, border, cut=12.0, border_width=1.5, accent_line=True) -> None:
    points = cut_panel_points(x, y, w, h, cut)
    poly(points, fill)
    poly_outline(points, border, border_width)
    if accent_line:
        rl.DrawLineEx((x + cut + 4, y + 1), (x + cut + 74, y + 1), max(1.0, border_width), border)
        rl.DrawLineEx((x + w - 2, y + h - cut - 2), (x + w - 2, y + h - 24), max(1.0, border_width), border)


def draw_bracket_corners(x, y, w, h, color, size=14.0, thickness=2.0) -> None:
    rl.DrawLineEx((x, y), (x + size, y), thickness, color)
    rl.DrawLineEx((x, y), (x, y + size), thickness, color)
    rl.DrawLineEx((x + w, y), (x + w - size, y), thickness, color)
    rl.DrawLineEx((x + w, y), (x + w, y + size), thickness, color)
    rl.DrawLineEx((x, y + h), (x + size, y + h), thickness, color)
    rl.DrawLineEx((x, y + h), (x, y + h - size), thickness, color)
    rl.DrawLineEx((x + w, y + h), (x + w - size, y + h), thickness, color)
    rl.DrawLineEx((x + w, y + h), (x + w, y + h - size), thickness, color)


def dim(color, amount: float):
    return shade(color, amount, color[3])


def with_alpha(color, value: int):
    return (color[0], color[1], color[2], int(clamp(value, 0, 255)))


def _star_points(cx, cy, outer, inner, points=8, rotation=-math.pi / 2):
    result = []
    for index in range(points * 2):
        angle = rotation + index * math.pi / points
        radius = outer if index % 2 == 0 else inner
        result.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
    return result


def _hex_points(cx, cy, radius, rotation=0.0):
    return [
        (
            cx + math.cos(rotation + index * math.tau / 6) * radius,
            cy + math.sin(rotation + index * math.tau / 6) * radius,
        )
        for index in range(6)
    ]


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
class UI:
    def __init__(self, fonts, textures) -> None:
        self.fonts = fonts
        self.textures = textures
        self.stars = self._make_stars()
        self.rain = self._make_rain()
        self.city_back = self._make_city(seed=1337, width=WINDOW_W + 400, base_height=150, count=32)
        self.city_front = self._make_city(seed=9001, width=WINDOW_W + 300, base_height=250, count=22)
        self.title_logo_width = 0.0

    # ------------------------------------------------------------------
    # Static background data
    # ------------------------------------------------------------------
    def _make_stars(self):
        rng = random.Random(72610)
        return [
            (
                rng.uniform(0, WINDOW_W),
                rng.uniform(0, WINDOW_H * 0.7),
                rng.uniform(0.6, 2.1),
                rng.uniform(0.4, 2.1),
                rng.uniform(0, math.tau),
            )
            for _ in range(130)
        ]

    def _make_rain(self):
        rng = random.Random(8819)
        return [
            (
                rng.uniform(-100, WINDOW_W + 100),
                rng.uniform(0, WINDOW_H),
                rng.uniform(14, 32),
                rng.uniform(250, 620),
                rng.uniform(40, 120),
            )
            for _ in range(90)
        ]

    def _make_city(self, seed, width, base_height, count):
        rng = random.Random(seed)
        buildings = []
        x = -100.0
        for index in range(count):
            w = rng.uniform(36, 112)
            h = rng.uniform(base_height * 0.32, base_height)
            windows = []
            for wy in range(int(h // 22)):
                for wx in range(max(1, int(w // 16))):
                    if rng.random() < 0.42:
                        windows.append((6 + wx * 16, 14 + wy * 22, rng.random() < 0.2))
            buildings.append((x, w, h, windows))
            x += w + rng.uniform(6, 25)
        return buildings

    def draw_city(self, base_y, offset, dark, accent, windows_alpha=80, alpha_value=255, front=False):
        for index, (bx, bw, bh, windows) in enumerate(self.city_front if front else self.city_back):
            x = bx - offset
            if x + bw < -10 or x > WINDOW_W + 10:
                continue
            color = (dark[0], dark[1], dark[2], alpha_value)
            rl.DrawRectangleRec((x, base_y - bh, bw, bh + 4), color)
            # Rooftop details.
            if index % 4 == 0:
                rl.DrawRectangleRec((x + bw * 0.45, base_y - bh - 18, 2, 18), color)
                rl.DrawCircleV((x + bw * 0.45 + 1, base_y - bh - 20), 2.0, with_alpha(accent, windows_alpha))
            for wx, wy, bright in windows:
                wx_screen = x + wx
                if -2 < wx_screen < WINDOW_W + 2:
                    wc = with_alpha(accent if bright else mix_color(accent, MIST, 0.4, 255), windows_alpha)
                    rl.DrawRectangle(int(wx_screen), int(base_y - bh + wy), 3, 4, wc)
            # Neon sign strip.
            if index % 7 == 3:
                rl.DrawRectangle(int(x + bw * 0.15), int(base_y - bh * 0.55), 3, int(bh * 0.25), with_alpha(accent, windows_alpha))

    # ------------------------------------------------------------------
    # Backgrounds
    # ------------------------------------------------------------------
    def draw_title_background(self, time_value: float) -> None:
        rl.DrawRectangleGradientV(0, 0, WINDOW_W, WINDOW_H, (4, 7, 18, 255), (18, 24, 48, 255))
        # Nebula blooms.
        rl.BeginBlendMode(rl.BLEND_ADDITIVE)
        rl.DrawCircleGradient((240, 270), 390, (23, 111, 147, 28), CLEAR)
        rl.DrawCircleGradient((1000, 190), 300, (115, 45, 126, 25), CLEAR)
        rl.DrawCircleGradient((820, 620), 340, (31, 50, 108, 22), CLEAR)
        rl.EndBlendMode()

        for x, y, size, speed, phase in self.stars:
            twinkle = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(time_value * speed + phase))
            color = with_alpha(WHITE, int(30 + 150 * twinkle))
            rl.DrawCircleV((x, y), size * (0.7 + 0.3 * twinkle), color)

        # Giant insignia watermark.
        self.draw_emblem(650, 380, 280, time_value, alpha_value=20, ring_alpha=30)

        # Atmospheric haze behind the skyline.
        rl.BeginBlendMode(rl.BLEND_ADDITIVE)
        rl.DrawRectangleGradientV(0, 430, WINDOW_W, 290, CLEAR, (28, 82, 115, 60))
        rl.EndBlendMode()

        # Parallax city layers.
        self.draw_city(735, 24, (8, 12, 24, 255), CYAN, windows_alpha=45, alpha_value=230, front=False)
        self.draw_city(760, 52, (5, 8, 18, 255), CYAN, windows_alpha=70, alpha_value=255, front=True)
        # Street-level glow.
        rl.BeginBlendMode(rl.BLEND_ADDITIVE)
        for x in range(0, WINDOW_W, 80):
            rl.DrawRectangleGradientV(x, 650, 2, 70, (54, 231, 255, 30), CLEAR)
        rl.EndBlendMode()

    def draw_themed_background(self, theme, time_value: float, dim_amount: float = 0.65) -> None:
        top = mix_color(theme.sky_high, BLACK, dim_amount, 255)
        bottom = mix_color(theme.sky_low, theme.fog, 0.55, 255)
        rl.DrawRectangleGradientV(0, 0, WINDOW_W, WINDOW_H, top, bottom)
        rl.BeginBlendMode(rl.BLEND_ADDITIVE)
        rl.DrawCircleGradient((250, 250), 360, (*theme.accent[:3], 24), CLEAR)
        rl.DrawCircleGradient((1110, 580), 310, (*theme.accent_2[:3], 20), CLEAR)
        rl.EndBlendMode()
        # Perspective grid floor.
        horizon = int(WINDOW_H * 0.62)
        rl.DrawRectangleGradientV(0, horizon, WINDOW_W, WINDOW_H - horizon, (*theme.floor_far[:3], 210), (*theme.floor_near[:3], 255))
        rl.BeginBlendMode(rl.BLEND_ADDITIVE)
        for index in range(9):
            y = horizon + int((index + 1) ** 1.7 * 5.5)
            if y >= WINDOW_H:
                break
            rl.DrawRectangle(0, y, WINDOW_W, 1, (*theme.accent[:3], 18))
        for x in range(-400, WINDOW_W + 400, 90):
            rl.DrawLineEx((SCREEN_CENTER_X, horizon), (x, WINDOW_H), 1.0, (*theme.accent[:3], 10))
        rl.EndBlendMode()
        # Huge translucent sector watermark lines.
        for index in range(3):
            y = 170 + index * 165
            rl.DrawRectangle(0, y, WINDOW_W, 1, (*theme.accent[:3], 18))
        rl.DrawCircleLines(1100, 120, 160, (*theme.accent[:3], 18))

    def draw_emblem(self, cx: float, cy: float, radius: float, time_value: float, alpha_value=150, ring_alpha=90) -> None:
        color = with_alpha(CYAN, alpha_value)
        gold = with_alpha(GOLD, alpha_value)
        # Outer rings.
        rl.DrawCircleLines(int(cx), int(cy), radius, with_alpha(CYAN, ring_alpha))
        rl.DrawCircleLines(int(cx), int(cy), radius * 0.84, with_alpha(GOLD, ring_alpha))
        for index in range(3):
            angle = time_value * 0.12 + index * math.tau / 3
            x = cx + math.cos(angle) * radius * 0.94
            y = cy + math.sin(angle) * radius * 0.94
            rl.DrawCircleV((x, y), 2.5, with_alpha(GOLD, 150))
        # Shield silhouette.
        shield = [
            (cx, cy - radius * 0.62),
            (cx + radius * 0.48, cy - radius * 0.32),
            (cx + radius * 0.35, cy + radius * 0.36),
            (cx, cy + radius * 0.68),
            (cx - radius * 0.35, cy + radius * 0.36),
            (cx - radius * 0.48, cy - radius * 0.32),
        ]
        poly(shield, with_alpha(CYAN, max(8, alpha_value // 5)))
        poly_outline(shield, with_alpha(CYAN, ring_alpha), 1.5)
        # Star.
        star = _star_points(cx, cy, radius * 0.52, radius * 0.21, 8, -math.pi / 2 + time_value * 0.03)
        poly(star, with_alpha(GOLD, max(8, alpha_value // 6)))
        poly_outline(star, with_alpha(GOLD, ring_alpha + 20), 1.3)
        # Hero chevrons.
        for index in range(3):
            y = cy + radius * (0.02 + index * 0.13)
            rl.DrawLineEx((cx - radius * 0.3, y), (cx, y + radius * 0.11), 2.0, with_alpha(CYAN, alpha_value))
            rl.DrawLineEx((cx, y + radius * 0.11), (cx + radius * 0.3, y), 2.0, with_alpha(CYAN, alpha_value))

    # ------------------------------------------------------------------
    # Layout methods (shared by drawing and input)
    # ------------------------------------------------------------------
    def title_option_rect(self, index: int, count: int):
        x = 828
        y = 286 + index * 60
        return (x, y, 392, 52)

    def mission_card_rect(self, index: int):
        col = index % 2
        row = index // 2
        return (84 + col * 558, 176 + row * 244, 528, 214)

    def menu_rect(self, index: int, count: int, top: float):
        width = 384
        height = 52
        gap = 10
        x = SCREEN_CENTER_X - width * 0.5
        y = top + index * (height + gap)
        return (x, y, width, height)

    def pause_option_rect(self, index: int, count: int):
        return self.menu_rect(index, count, 332)

    def complete_option_rect(self, index: int, count: int):
        return self.menu_rect(index, count, 522)

    def gameover_option_rect(self, index: int, count: int):
        return self.menu_rect(index, count, 470)

    def victory_option_rect(self, index: int, count: int):
        return self.menu_rect(index, count, 590)

    def briefing_deploy_rect(self):
        return (88, 638, 436, 52)

    def briefing_back_rect(self):
        return (548, 638, 210, 52)

    def controls_back_rect(self):
        return (SCREEN_CENTER_X - 150, 640, 300, 48)

    # ------------------------------------------------------------------
    # Title
    # ------------------------------------------------------------------
    def draw_title(self, game) -> None:
        time_value = game.time
        self.draw_title_background(time_value)

        # Top rail.
        rl.DrawRectangle(0, 0, WINDOW_W, 3, CYAN)
        rl.DrawRectangle(0, 3, WINDOW_W * 0.34, 1, GOLD)
        self.fonts.draw(self.fonts.small, "AEGIS CORPS // PRIORITY TRANSMISSION", 44, 24, 14, with_alpha(CYAN, 190), 1.5)
        self.fonts.draw_right(self.fonts.small, "EARTH // 2187", WINDOW_W - 44, 24, 14, with_alpha(MIST, 140), 1.5)
        rl.DrawLineEx((44, 48), (WINDOW_W - 44, 48), 1.0, with_alpha(STEEL, 160))

        # Logo block.
        self.fonts.draw(self.fonts.small, "PROJECT // NOVA-7", 92, 92, 16, with_alpha(GOLD, 210), 2.5)
        self.fonts.draw_glow(self.fonts.display, "NOVA", 84, 112, 116, WHITE, CYAN, 4, 2.0)
        self.fonts.draw_glow(self.fonts.display, "STRIKE", 84, 210, 116, GOLD, ORANGE, 5, 2.0)
        rl.DrawRectangleGradientH(88, 330, 430, 3, CYAN, GOLD)
        self.fonts.draw(self.fonts.bold, "ECLIPSE PROTOCOL", 92, 344, 29, with_alpha(PAPER, 230), 4.0)
        self.fonts.draw(self.fonts.body, "ONE HERO. FOUR SECTORS. ZERO MERCY.", 92, 386, 18, with_alpha(MIST, 195), 1.8)
        self.fonts.draw(self.fonts.body, "Neon City is dying. Overlord Vex owns the dawn.", 92, 412, 17, with_alpha(MIST, 140), 1.2)

        # Small live-status strip.
        status_y = 608
        rl.DrawRectangle(80, status_y - 10, 470, 48, (3, 7, 14, 170))
        rl.DrawRectangle(88, status_y, 446, 1, with_alpha(STEEL, 170))
        self.fonts.draw(self.fonts.small, "THREAT NETWORK", 92, status_y + 14, 13, with_alpha(CYAN, 160), 1.6)
        rl.DrawCircleV((198, status_y + 20), 3, RED if math.sin(time_value * 3) > 0 else with_alpha(RED, 80))
        self.fonts.draw(self.fonts.small, "ONLINE", 208, status_y + 13, 13, with_alpha(RED, 190), 1.5)
        self.fonts.draw_right(self.fonts.small, f"BEST SCORE  {format_number(game.best_score)}", 534, status_y + 13, 13, with_alpha(GOLD, 185), 1.2)

        # Menu header.
        self.fonts.draw(self.fonts.small, "SELECT PROTOCOL", 828, 250, 14, with_alpha(CYAN, 210), 2.6)
        self.fonts.draw_right(self.fonts.small, "MISSION UPLINK", 1220, 250, 12, with_alpha(MIST, 110), 1.5)
        rl.DrawLineEx((828, 272), (1220, 272), 1.0, with_alpha(STEEL, 180))

        for index, option in enumerate(game.title_options):
            x, y, w, h = self.title_option_rect(index, len(game.title_options))
            selected = index == game.title_selection
            self._draw_menu_row(
                x,
                y,
                w,
                h,
                index + 1,
                option["label"],
                option.get("sub", ""),
                selected,
                accent=CYAN,
                time_value=time_value,
                disabled=option.get("disabled", False),
            )

        # Footer.
        rl.DrawRectangleGradientV(0, 642, WINDOW_W, 78, (2, 5, 11, 90), (2, 5, 11, 240))
        rl.DrawRectangle(0, 662, WINDOW_W, 58, (2, 5, 11, 210))
        rl.DrawLineEx((44, 650), (WINDOW_W - 44, 650), 1.0, with_alpha(CYAN, 70))
        self.fonts.draw(self.fonts.small, "WASD  MOVE", 92, 678, 12, with_alpha(MIST, 210), 1.3)
        self.fonts.draw(self.fonts.small, "MOUSE  AIM", 232, 678, 12, with_alpha(MIST, 210), 1.3)
        self.fonts.draw(self.fonts.small, "LMB  FIRE", 372, 678, 12, with_alpha(MIST, 210), 1.3)
        self.fonts.draw(self.fonts.small, "ENTER  SELECT", 500, 678, 12, with_alpha(MIST, 210), 1.3)
        self.fonts.draw_right(self.fonts.small, "v1.0 // ORIGINAL HERO IP", WINDOW_W - 44, 678, 12, with_alpha(MIST, 120), 1.2)

        # Rain layer on top of the city.
        self._draw_rain(time_value, alpha_value=18)

        self.draw_scanlines(9)

    def _draw_menu_row(
        self,
        x,
        y,
        w,
        h,
        number,
        label,
        sub,
        selected,
        accent,
        time_value,
        disabled=False,
    ) -> None:
        text_color = WHITE if selected else PAPER
        if disabled:
            text_color = with_alpha(MIST, 80)
        fill = with_alpha((8, 15, 27, 255), 218 if selected else 110)
        border = with_alpha(accent, 220 if selected else 55)
        if selected:
            # Soft selection bloom.
            rl.BeginBlendMode(rl.BLEND_ADDITIVE)
            rl.DrawRectangleGradientH(int(x - 16), int(y), int(w + 40), int(h), (*accent[:3], 24), CLEAR)
            rl.EndBlendMode()
        draw_cut_panel(x, y, w, h, fill, border, 10, 1.4 if selected else 1.0, selected)
        if selected:
            rl.DrawRectangle(int(x + 2), int(y + 8), 3, int(h - 16), accent)
            chevron_x = x + 18 + math.sin(time_value * 5) * 2
            rl.DrawTriangle(
                (chevron_x, y + h * 0.5 - 8),
                (chevron_x, y + h * 0.5 + 8),
                (chevron_x + 10, y + h * 0.5),
                accent,
            )
        self.fonts.draw(self.fonts.small, f"{number:02d}", x + 40, y + 17, 14, with_alpha(accent if selected else MIST, 210), 1.5)
        self.fonts.draw(self.fonts.bold, label, x + 78, y + 8, 24, text_color, 2.0)
        if sub:
            self.fonts.draw(self.fonts.small, sub, x + 78, y + 34, 12, with_alpha(MIST, 140 if selected else 85), 1.2)
        # Arrow cap.
        rl.DrawLineEx((x + w - 42, y + 14), (x + w - 14, y + 14), 1.0, with_alpha(accent, 130 if selected else 40))
        rl.DrawLineEx((x + w - 42, y + h - 14), (x + w - 14, y + h - 14), 1.0, with_alpha(accent, 130 if selected else 40))

    # ------------------------------------------------------------------
    # Mission select
    # ------------------------------------------------------------------
    def draw_mission_select(self, game) -> None:
        time_value = game.time
        theme = LEVELS[min(3, max(0, game.highest_unlocked))].theme
        self.draw_themed_background(theme, time_value, 0.72)
        rl.DrawRectangle(0, 0, WINDOW_W, 3, theme.accent)
        self.fonts.draw(self.fonts.small, "AEGIS ARCHIVE // MISSION CONTROL", 72, 30, 14, with_alpha(theme.accent, 220), 2.0)
        self.fonts.draw_right(self.fonts.small, f"CLEARED {game.cleared_count}/{len(LEVELS)}", WINDOW_W - 72, 30, 14, with_alpha(MIST, 160), 1.6)
        rl.DrawLineEx((72, 56), (WINDOW_W - 72, 56), 1.0, with_alpha(STEEL, 140))

        self.fonts.draw_glow(self.fonts.display, "MISSION SELECT", 68, 74, 52, WHITE, theme.accent, 2, 2.0)
        self.fonts.draw(
            self.fonts.body,
            "Choose a sector. Completed sectors can be replayed for a higher score.",
            72,
            140,
            17,
            with_alpha(MIST, 175),
            1.0,
        )

        for index, level in enumerate(LEVELS):
            x, y, w, h = self.mission_card_rect(index)
            selected = index == game.mission_selection
            unlocked = index <= game.highest_unlocked
            self._draw_mission_card(game, index, level, x, y, w, h, selected, unlocked, time_value)

        # Footer controls.
        self.fonts.draw(self.fonts.small, "ARROWS  NAVIGATE", 72, 684, 13, with_alpha(MIST, 150), 1.5)
        self.fonts.draw(self.fonts.small, "ENTER  OPEN BRIEFING", 248, 684, 13, with_alpha(CYAN, 190), 1.5)
        self.fonts.draw(self.fonts.small, "ESC  BACK", 478, 684, 13, with_alpha(MIST, 130), 1.5)
        self.fonts.draw_right(self.fonts.small, "LOCKS RELEASE AS SECTORS ARE CLEARED", WINDOW_W - 72, 684, 12, with_alpha(MIST, 100), 1.2)

        self.draw_scanlines(8)

    def _draw_mission_card(self, game, index, level, x, y, w, h, selected, unlocked, time_value) -> None:
        theme = level.theme
        accent = theme.accent if unlocked else with_alpha(MIST, 80)
        fill = with_alpha((7, 14, 26, 255), 228 if selected else 178)
        border = with_alpha(accent, 235 if selected else 62)
        if selected and unlocked:
            rl.BeginBlendMode(rl.BLEND_ADDITIVE)
            rl.DrawRectangleGradientH(int(x - 10), int(y + 10), int(w + 20), int(h - 20), (*accent[:3], 22), CLEAR)
            rl.EndBlendMode()
        draw_cut_panel(x, y, w, h, fill, border, 16, 2.0 if selected else 1.0, selected)
        draw_bracket_corners(x + 8, y + 8, w - 16, h - 16, with_alpha(accent, 140 if selected else 34), 18, 1.4)

        # Mini-map preview.
        preview_x, preview_y, preview_w, preview_h = x + 18, y + 24, 154, 154
        rl.DrawRectangleRounded((preview_x, preview_y, preview_w, preview_h), 0.04, 4, (4, 8, 16, 230))
        cell = min(preview_w / len(level.rows[0]), preview_h / len(level.rows))
        for my, row in enumerate(level.rows):
            for mx, char in enumerate(row):
                if char in "#MNC":
                    color = {
                        "#": with_alpha(theme.wall_base, 220 if unlocked else 80),
                        "M": with_alpha(theme.wall_metal, 220 if unlocked else 70),
                        "N": with_alpha(theme.accent, 175 if unlocked else 55),
                        "C": with_alpha(theme.hazard, 165 if unlocked else 45),
                    }[char]
                    rl.DrawRectangle(
                        int(preview_x + mx * cell),
                        int(preview_y + my * cell),
                        max(1, int(cell + 0.5)),
                        max(1, int(cell + 0.5)),
                        color,
                    )
        if unlocked:
            # Player start and extraction dots.
            start = (int(preview_x + (level.start[0]) * cell), int(preview_y + (level.start[1]) * cell))
            end = (int(preview_x + (level.exit[0]) * cell), int(preview_y + (level.exit[1]) * cell))
            rl.DrawCircleV(start, 3.0, CYAN)
            rl.DrawCircleLines(end[0], end[1], 4.0, theme.accent)
        else:
            rl.DrawRectangleRec((preview_x, preview_y, preview_w, preview_h), (4, 7, 13, 180))
            lock_x, lock_y = preview_x + preview_w / 2, preview_y + preview_h / 2
            rl.DrawRectangle(int(lock_x - 13), int(lock_y - 2), 26, 22, with_alpha(MIST, 100))
            rl.DrawCircleLines(int(lock_x), int(lock_y - 4), 10, with_alpha(MIST, 100))
            self.fonts.draw_center(self.fonts.small, "LOCKED", lock_x, lock_y + 30, 12, with_alpha(MIST, 150), 2.0)

        # Mission text.
        tx = x + 194
        self.fonts.draw(self.fonts.small, f"MISSION {index + 1:02d} // {level.code.split(' // ')[-1]}", tx, y + 24, 12, with_alpha(accent, 220), 1.7)
        self.fonts.draw(self.fonts.bold, level.name, tx, y + 44, 30, WHITE if unlocked else with_alpha(MIST, 90), 1.6)
        self.fonts.draw(self.fonts.small, level.subtitle, tx, y + 80, 12, with_alpha(MIST, 130 if unlocked else 60), 1.1)

        if unlocked:
            threat = THREAT_COLORS.get(level.threat_level, ORANGE)
            rl.DrawRectangle(int(tx), int(y + 104), 3, 17, threat)
            self.fonts.draw(self.fonts.small, f"THREAT {level.threat_level}", tx + 10, y + 105, 12, with_alpha(threat, 230), 1.4)
            hostiles = len(level.enemies) + (1 if level.boss else 0)
            self.fonts.draw(self.fonts.small, f"HOSTILES {hostiles:02d}   INTEL 03", tx, y + 130, 12, with_alpha(MIST, 150), 1.2)
            score = game.best_score_for(index)
            if score:
                self.fonts.draw(self.fonts.small, f"BEST {format_number(score)}", tx, y + 152, 12, with_alpha(GOLD, 185), 1.2)
            cleared = index in game.cleared_missions
            if cleared:
                self.fonts.draw_right(self.fonts.bold, "CLEARED", x + w - 24, y + 24, 14, with_alpha(GREEN, 210), 2.0)
                self.fonts.draw_right(self.fonts.small, f"RANK {game.rank_for(index)}", x + w - 24, y + 44, 12, with_alpha(GOLD, 170), 1.4)
            else:
                self.fonts.draw_right(self.fonts.small, "UNRESOLVED", x + w - 24, y + 24, 12, with_alpha(ORANGE, 170), 1.5)
        else:
            self.fonts.draw(self.fonts.small, f"ACCESS DENIED", tx, y + 108, 13, with_alpha(RED, 160), 2.0)
            self.fonts.draw(self.fonts.small, f"CLEAR SECTOR {index:02d} TO UNLOCK", tx, y + 132, 12, with_alpha(MIST, 100), 1.2)

        if selected and unlocked and math.sin(time_value * 4.0) > 0:
            rl.DrawRectangle(int(x + w - 8), int(y + 18), 3, int(h - 36), accent)

    # ------------------------------------------------------------------
    # Briefing
    # ------------------------------------------------------------------
    def draw_briefing(self, game) -> None:
        level = LEVELS[game.briefing_level]
        theme = level.theme
        self.draw_themed_background(theme, game.time, 0.72)
        # Top rail.
        rl.DrawRectangle(0, 0, WINDOW_W, 3, theme.accent)
        self.fonts.draw(self.fonts.small, "AEGIS CORPS // MISSION BRIEFING", 66, 28, 14, with_alpha(theme.accent, 220), 2.0)
        self.fonts.draw_right(self.fonts.small, f"TRANSMISSION {game.briefing_level + 1:02d}/04  //  DECRYPTED", WINDOW_W - 66, 28, 12, with_alpha(MIST, 140), 1.4)
        rl.DrawLineEx((66, 54), (WINDOW_W - 66, 54), 1.0, with_alpha(STEEL, 150))

        # Giant sector numeral.
        self.fonts.draw(self.fonts.display, f"{game.briefing_level + 1:02d}", 64, 68, 92, with_alpha(theme.accent, 34), 2.0)
        self.fonts.draw(self.fonts.small, level.code, 70, 174, 14, with_alpha(theme.accent, 220), 2.2)
        self.fonts.draw_glow(self.fonts.display, level.name, 66, 194, 58, WHITE, theme.accent, 2, 2.0)
        self.fonts.draw(self.fonts.bold, level.subtitle, 70, 264, 19, with_alpha(theme.accent_2, 230), 2.3)
        rl.DrawLineEx((70, 298), (710, 298), 1.0, with_alpha(theme.accent, 100))

        # Story panel.
        draw_cut_panel(66, 322, 644, 258, with_alpha((5, 10, 20, 255), 208), with_alpha(theme.accent, 80), 16, 1.2)
        self.fonts.draw(self.fonts.small, "SITUATION REPORT", 92, 342, 12, with_alpha(MIST, 130), 2.0)
        self.fonts.draw_wrapped(
            self.fonts.body,
            level.briefing,
            92,
            370,
            20,
            588,
            with_alpha(PAPER, 215),
            1.4,
            0.3,
        )
        self.fonts.draw(self.fonts.small, "PRIMARY DIRECTIVE", 92, 502, 12, with_alpha(theme.accent, 200), 2.0)
        self.fonts.draw(self.fonts.bold, level.directive, 92, 522, 19, WHITE, 1.8)
        # Directive accent.
        rl.DrawRectangle(72, 520, 4, 26, theme.accent)

        # Hint panel.
        draw_cut_panel(66, 598, 644, 40, with_alpha((8, 15, 26, 255), 220), with_alpha(theme.accent_2, 80), 8, 1.0, False)
        self.fonts.draw(self.fonts.small, "FIELD TIP", 84, 608, 12, with_alpha(theme.accent_2, 220), 1.8)
        self.fonts.draw(self.fonts.small, level.hint, 170, 608, 12, with_alpha(MIST, 215), 0.6)

        # Right dossier panel.
        right_x = 744
        draw_cut_panel(right_x, 78, 466, 474, with_alpha((5, 10, 20, 255), 210), with_alpha(theme.accent, 80), 16, 1.2)
        self.fonts.draw(self.fonts.small, "SECTOR DOSSIER", right_x + 24, 98, 12, with_alpha(MIST, 130), 2.0)
        # Mini map.
        mx, my, mw = right_x + 24, 126, 190
        mh = 190
        rl.DrawRectangleRounded((mx, my, mw, mh), 0.02, 4, (3, 7, 13, 220))
        cell = min(mw / len(level.rows[0]), mh / len(level.rows))
        for yy, row in enumerate(level.rows):
            for xx, char in enumerate(row):
                if char in "#MNC":
                    color = {
                        "#": with_alpha(theme.wall_base, 220),
                        "M": with_alpha(theme.wall_metal, 220),
                        "N": with_alpha(theme.accent, 150),
                        "C": with_alpha(theme.hazard, 160),
                    }[char]
                    rl.DrawRectangle(int(mx + xx * cell), int(my + yy * cell), max(1, int(cell + 0.5)), max(1, int(cell + 0.5)), color)
        rl.DrawCircleV((mx + level.start[0] * cell, my + level.start[1] * cell), 3.2, CYAN)
        rl.DrawCircleLines(int(mx + level.exit[0] * cell), int(my + level.exit[1] * cell), 4.0, theme.accent)
        self.fonts.draw(self.fonts.small, "TACTICAL LAYOUT", right_x + 24, 326, 11, with_alpha(MIST, 110), 1.8)

        # Stats beside the map.
        stats_x = right_x + 236
        threat = THREAT_COLORS.get(level.threat_level, ORANGE)
        self.fonts.draw(self.fonts.small, "THREAT", stats_x, 128, 11, with_alpha(MIST, 115), 1.6)
        self.fonts.draw(self.fonts.bold, level.threat_level, stats_x, 146, 21, threat, 1.4)
        self.fonts.draw(self.fonts.small, "HOSTILES", stats_x, 184, 11, with_alpha(MIST, 115), 1.6)
        self.fonts.draw(self.fonts.bold, f"{len(level.enemies) + (1 if level.boss else 0):02d}", stats_x, 202, 21, PAPER, 1.4)
        self.fonts.draw(self.fonts.small, "INTEL", stats_x, 240, 11, with_alpha(MIST, 115), 1.6)
        self.fonts.draw(self.fonts.bold, "03 SHARDS", stats_x, 258, 18, GOLD, 1.2)
        self.fonts.draw(self.fonts.small, "BEST SCORE", stats_x, 296, 11, with_alpha(MIST, 115), 1.6)
        self.fonts.draw(self.fonts.bold, format_number(game.best_score_for(game.briefing_level)), stats_x, 314, 16, PAPER, 1.0)
        if level.boss:
            self.fonts.draw(self.fonts.small, "BOSS", stats_x, 348, 11, with_alpha(VIOLET, 180), 1.6)
            self.fonts.draw(self.fonts.bold, level.boss_name, stats_x, 366, 14, VIOLET, 1.0)
        else:
            self.fonts.draw(self.fonts.small, "CLEARANCE", stats_x, 348, 11, with_alpha(MIST, 115), 1.6)
            self.fonts.draw(self.fonts.bold, "HERO", stats_x, 366, 16, GOLD, 1.4)

        # Loadout.
        self.fonts.draw(self.fonts.small, "AVAILABLE LOADOUT", right_x + 24, 374, 11, with_alpha(MIST, 120), 1.8)
        unlocked_weapons = [w for w in WEAPONS if w.unlock_mission <= game.highest_unlocked or game.briefing_level >= w.unlock_mission]
        for wi, weapon in enumerate(unlocked_weapons):
            row_y = 396 + wi * 30
            rl.DrawRectangle(right_x + 24, row_y + 6, 4, 16, weapon.color)
            self.fonts.draw(self.fonts.small, f"{wi + 1}", right_x + 38, row_y + 4, 12, with_alpha(MIST, 130), 1.0)
            self.fonts.draw(self.fonts.bold, weapon.name, right_x + 56, row_y + 1, 16, with_alpha(PAPER, 220), 1.0)
            self.fonts.draw_right(self.fonts.small, f"{weapon.damage:.0f} DMG", right_x + 442, row_y + 4, 11, with_alpha(weapon.color, 200), 1.0)
        if not unlocked_weapons:
            self.fonts.draw(self.fonts.small, "PULSE BLASTER", right_x + 24, 396, 16, PAPER, 1.0)

        # Footer action.
        deploy = self.briefing_deploy_rect()
        draw_cut_panel(*deploy, with_alpha(theme.accent, 38), with_alpha(theme.accent, 230), 10, 1.8)
        self.fonts.draw(self.fonts.bold, "DEPLOY TO SECTOR", deploy[0] + 26, deploy[1] + 12, 23, WHITE, 1.5)
        self.fonts.draw_right(self.fonts.small, "ENTER // CONFIRM", deploy[0] + deploy[2] - 22, deploy[1] + 18, 12, with_alpha(theme.accent, 220), 1.4)
        back = self.briefing_back_rect()
        draw_cut_panel(*back, with_alpha((7, 14, 26, 255), 180), with_alpha(STEEL, 160), 10, 1.0, False)
        self.fonts.draw_center(self.fonts.small, "ESC  BACK", back[0] + back[2] * 0.5, back[1] + 18, 13, with_alpha(MIST, 190), 1.4)
        self.draw_scanlines(8)

    # ------------------------------------------------------------------
    # Controls
    # ------------------------------------------------------------------
    def draw_controls(self, game) -> None:
        theme = LEVELS[min(game.briefing_level, 3)].theme
        self.draw_themed_background(theme, game.time, 0.76)
        self.fonts.draw(self.fonts.small, "AEGIS COMBAT MANUAL // NOVA-7", 70, 32, 14, with_alpha(theme.accent, 220), 2.0)
        self.fonts.draw_glow(self.fonts.display, "FIELD CONTROLS", 64, 74, 54, WHITE, theme.accent, 2, 2.0)
        self.fonts.draw(self.fonts.body, "Everything you need to survive the Eclipse Protocol.", 70, 146, 18, with_alpha(MIST, 180), 1.0)
        rl.DrawLineEx((70, 180), (WINDOW_W - 70, 180), 1.0, with_alpha(STEEL, 150))

        columns = [
            (
                72,
                "MOVEMENT & VISION",
                [
                    ("W A S D", "Move through the sector"),
                    ("MOUSE", "Look around"),
                    ("SHIFT", "Hero dash // short invulnerability"),
                    ("RIGHT MOUSE", "Aim down sights // tighter spread"),
                ],
                CYAN,
            ),
            (
                470,
                "COMBAT",
                [
                    ("LEFT MOUSE", "Fire equipped weapon"),
                    ("1 / 2 / 3", "Switch weapon"),
                    ("MOUSE WHEEL", "Cycle weapon"),
                    ("F12", "Capture a screenshot"),
                ],
                ORANGE,
            ),
            (
                868,
                "SUPER POWERS",
                [
                    ("E", "AEGIS shield // 10s cooldown"),
                    ("Q", "NOVA BLAST when charged"),
                    ("M", "Mute audio"),
                    ("ESC", "Pause / abort mission"),
                ],
                MAGENTA,
            ),
        ]
        for index, (col_x, title, rows, accent) in enumerate(columns):
            draw_cut_panel(col_x, 208, 350, 326, with_alpha((5, 10, 20, 255), 210), with_alpha(accent, 80), 14, 1.2)
            self.fonts.draw(self.fonts.small, f"0{index + 1} // {title}", col_x + 24, 228, 12, with_alpha(accent, 220), 1.8)
            rl.DrawLineEx((col_x + 24, 254), (col_x + 326, 254), 1.0, with_alpha(accent, 50))
            for ri, (key, description) in enumerate(rows):
                y = 276 + ri * 60
                draw_cut_panel(col_x + 22, y, 92, 34, with_alpha(accent, 24), with_alpha(accent, 100), 7, 1.0, False)
                self.fonts.draw_center(self.fonts.bold, key, col_x + 68, y + 8, 14, accent, 1.0)
                self.fonts.draw_wrapped(
                    self.fonts.small,
                    description,
                    col_x + 128,
                    y + 5,
                    12,
                    202,
                    with_alpha(PAPER, 205),
                    1.3,
                    0.2,
                )

        draw_cut_panel(72, 552, 1136, 68, with_alpha((5, 10, 20, 255), 190), with_alpha(theme.accent, 60), 12, 1.0)
        self.fonts.draw(self.fonts.small, "HERO PROTOCOL", 96, 566, 12, with_alpha(theme.accent, 220), 1.8)
        self.fonts.draw(
            self.fonts.body,
            "Dash to break enemy aim. AEGIS blunts damage. NOVA BLAST clears a room when the meter is full. "
            "Shield regenerates after 3 seconds without damage.",
            96,
            588,
            15,
            with_alpha(MIST, 190),
            0.5,
        )

        back = self.controls_back_rect()
        draw_cut_panel(*back, with_alpha(theme.accent, 32), with_alpha(theme.accent, 210), 8, 1.5)
        self.fonts.draw_center(self.fonts.bold, "ENTER / ESC  RETURN", back[0] + back[2] / 2, back[1] + 14, 16, WHITE, 1.4)
        self.draw_scanlines(8)

    # ------------------------------------------------------------------
    # Generic option screen
    # ------------------------------------------------------------------
    def _draw_option_list(self, game, options, selected, accent, top, time_value) -> None:
        for index, option in enumerate(options):
            x, y, w, h = self.menu_rect(index, len(options), top)
            self._draw_menu_row(
                x,
                y,
                w,
                h,
                index + 1,
                option["label"],
                option.get("sub", ""),
                index == selected,
                accent,
                time_value,
                option.get("disabled", False),
            )

    def draw_pause(self, game) -> None:
        # Darken the frozen battlefield.
        rl.DrawRectangle(0, 0, WINDOW_W, WINDOW_H, (3, 6, 14, 210))
        theme = game.level_def.theme
        rl.BeginBlendMode(rl.BLEND_ADDITIVE)
        rl.DrawCircleGradient((SCREEN_CENTER_X, 300), 360, (*theme.accent[:3], 22), CLEAR)
        rl.EndBlendMode()
        self.fonts.draw_center_glow(self.fonts.display, "SYSTEM PAUSED", SCREEN_CENTER_X, 142, 58, WHITE, theme.accent, 3, 2.0)
        self.fonts.draw_center(self.fonts.body, f"{game.level_def.name} // {game.objective_short()}", SCREEN_CENTER_X, 216, 18, with_alpha(MIST, 190), 1.0)
        draw_bracket_corners(258, 118, 764, 520, with_alpha(theme.accent, 90), 22, 1.5)
        self._draw_option_list(game, game.pause_options, game.pause_selection, theme.accent, 332, game.time)
        self.fonts.draw_center(self.fonts.small, "ESC  RESUME", SCREEN_CENTER_X, 676, 12, with_alpha(MIST, 130), 1.4)

    def draw_complete(self, game) -> None:
        stats = game.mission_stats
        theme = game.level_def.theme
        rl.DrawRectangle(0, 0, WINDOW_W, WINDOW_H, (3, 7, 14, 255))
        # Radial celebration rays.
        rl.BeginBlendMode(rl.BLEND_ADDITIVE)
        for index in range(14):
            angle = index * math.tau / 14 + game.time * 0.03
            x2 = SCREEN_CENTER_X + math.cos(angle) * 900
            y2 = 330 + math.sin(angle) * 900
            rl.DrawLineEx((SCREEN_CENTER_X, 330), (x2, y2), 2.0, (*theme.accent[:3], 11))
        rl.DrawCircleGradient((SCREEN_CENTER_X, 330), 440, (*theme.accent[:3], 30), CLEAR)
        rl.EndBlendMode()
        self.fonts.draw_center(self.fonts.small, "MISSION COMPLETE // AEGIS COMMAND", SCREEN_CENTER_X, 88, 14, with_alpha(theme.accent, 210), 2.4)
        self.fonts.draw_center_glow(self.fonts.display, "SECTOR CLEARED", SCREEN_CENTER_X, 116, 68, WHITE, theme.accent, 4, 2.0)
        self.fonts.draw_center(self.fonts.bold, f"SECTOR {game.current_level_index + 1:02d} // {game.level_def.name}", SCREEN_CENTER_X, 200, 24, GOLD, 2.0)
        rl.DrawLineEx((300, 240), (980, 240), 1.0, with_alpha(theme.accent, 95))

        # Stats columns.
        stat_entries = [
            ("SCORE", format_number(stats.get("score", 0)), GOLD),
            ("TIME", format_time(stats.get("time", 0.0)), PAPER),
            ("ACCURACY", f"{stats.get('accuracy', 0.0):.0f}%", CYAN),
            ("HOSTILES", f"{stats.get('kills', 0):02d}", RED),
            ("INTEL", f"{stats.get('intel', 0)}/3", ORANGE),
            ("RANK", stats.get("rank", "C"), VIOLET),
        ]
        for index, (label, value, color) in enumerate(stat_entries):
            col = index % 3
            row = index // 3
            x = 300 + col * 240
            y = 274 + row * 98
            draw_cut_panel(x, y, 208, 78, with_alpha((7, 14, 26, 255), 190), with_alpha(color, 80), 8, 1.0, False)
            self.fonts.draw(self.fonts.small, label, x + 18, y + 13, 11, with_alpha(MIST, 120), 1.7)
            self.fonts.draw(self.fonts.bold, value, x + 18, y + 34, 28, color, 1.2)

        if stats.get("new_best"):
            self.fonts.draw_center(self.fonts.small, "NEW SECTOR RECORD", SCREEN_CENTER_X, 474, 13, GOLD, 2.0)
        self._draw_option_list(game, game.complete_options, game.complete_selection, theme.accent, 522, game.time)
        self.draw_scanlines(8)

    def draw_game_over(self, game) -> None:
        theme = game.level_def.theme
        rl.DrawRectangle(0, 0, WINDOW_W, WINDOW_H, (9, 3, 7, 242))
        rl.BeginBlendMode(rl.BLEND_ADDITIVE)
        rl.DrawCircleGradient((SCREEN_CENTER_X, 300), 420, (120, 12, 30, 34), CLEAR)
        rl.EndBlendMode()
        # Broken hero emblem.
        self.draw_emblem(SCREEN_CENTER_X, 240, 150, game.time, alpha_value=25, ring_alpha=55)
        self.fonts.draw_center(self.fonts.small, "SIGNAL LOST // AEGIS NETWORK", SCREEN_CENTER_X, 104, 14, with_alpha(RED, 200), 2.4)
        self.fonts.draw_center_glow(self.fonts.display, "NOVA DOWN", SCREEN_CENTER_X, 132, 74, WHITE, RED, 4, 2.0)
        self.fonts.draw_center(self.fonts.body, "The city still needs a hero. Get back up.", SCREEN_CENTER_X, 232, 19, with_alpha(MIST, 170), 1.0)
        rl.DrawLineEx((380, 276), (900, 276), 1.0, with_alpha(RED, 80))
        self._draw_option_list(game, game.gameover_options, game.gameover_selection, RED, 470, game.time)
        self.draw_scanlines(8)

    def draw_victory(self, game) -> None:
        time_value = game.time
        rl.DrawRectangleGradientV(0, 0, WINDOW_W, WINDOW_H, (4, 8, 18, 255), (38, 20, 44, 255))
        rl.BeginBlendMode(rl.BLEND_ADDITIVE)
        for index in range(8):
            angle = index * math.tau / 8 + time_value * 0.02
            x = SCREEN_CENTER_X + math.cos(angle) * 420
            y = 330 + math.sin(angle) * 300
            rl.DrawCircleGradient((x, y), 130, (*[CYAN, GOLD, MAGENTA][index % 3][:3], 18), CLEAR)
        rl.EndBlendMode()
        self.draw_emblem(SCREEN_CENTER_X, 222, 176, time_value, alpha_value=70, ring_alpha=100)
        self.fonts.draw_center(self.fonts.small, "AEGIS TRANSMISSION // ALL SECTORS SECURED", SCREEN_CENTER_X, 66, 14, with_alpha(CYAN, 220), 2.4)
        self.fonts.draw_center_glow(self.fonts.display, "CITY LIBERATED", SCREEN_CENTER_X, 84, 66, WHITE, GOLD, 4, 2.0)
        self.fonts.draw_center(self.fonts.bold, "THE ECLIPSE PROTOCOL IS OVER", SCREEN_CENTER_X, 168, 20, with_alpha(GOLD, 230), 2.6)
        self.fonts.draw_wrapped(
            self.fonts.body,
            "Overlord Vex has fallen. The reactor is stable, the skyline is breathing, and Neon City remembers the hero who came back.",
            SCREEN_CENTER_X - 330,
            408,
            18,
            660,
            with_alpha(PAPER, 200),
            1.4,
            0.4,
        )
        # Campaign totals.
        totals = game.campaign_totals
        y = 500
        for index, (label, value, color) in enumerate(
            [
                ("TOTAL SCORE", format_number(totals.get("score", 0)), GOLD),
                ("KILLS", f"{totals.get('kills', 0)}", RED),
                ("INTEL", f"{totals.get('intel', 0)}/12", ORANGE),
                ("BEST COMBO", f"x{totals.get('best_combo', 1.0):.1f}", MAGENTA),
            ]
        ):
            x = 218 + index * 296
            self.fonts.draw_center(self.fonts.small, label, x, 500, 11, with_alpha(MIST, 120), 1.5)
            self.fonts.draw_center(self.fonts.bold, value, x, 520, 27, color, 1.0)
        if totals.get("new_best"):
            self.fonts.draw_center(self.fonts.small, "NEW ALL-TIME CAMPAIGN RECORD", SCREEN_CENTER_X, 566, 13, GOLD, 2.0)
        self._draw_option_list(game, game.victory_options, game.victory_selection, GOLD, 590, time_value)
        self._draw_rain(time_value, alpha_value=8)
        self.draw_scanlines(8)

    # ------------------------------------------------------------------
    # Weather / overlays
    # ------------------------------------------------------------------
    def _draw_rain(self, time_value: float, alpha_value: int = 22) -> None:
        rl.BeginBlendMode(rl.BLEND_ADDITIVE)
        for x, y, length, speed, drift in self.rain:
            yy = (y + time_value * speed) % (WINDOW_H + 80) - 40
            xx = (x + time_value * drift) % (WINDOW_W + 120) - 60
            rl.DrawLineEx((xx, yy), (xx - 4, yy + length), 1.0, (150, 210, 230, alpha_value))
        rl.EndBlendMode()

    def draw_scanlines(self, alpha_value: int = 10, step: int = 3) -> None:
        color = (0, 0, 0, alpha_value)
        for y in range(0, WINDOW_H, step):
            rl.DrawRectangle(0, y, WINDOW_W, 1, color)

    def draw_screen_effects(self, game) -> None:
        # World vignette (shared by every state).
        if self.textures.vignette is not None:
            rl.DrawTexturePro(
                self.textures.vignette,
                (0, 0, WORLD_W, WORLD_H),
                (0, 0, WINDOW_W, WINDOW_H),
                (0, 0),
                0.0,
                WHITE,
            )
        # Very light CRT treatment.
        self.draw_scanlines(7, 4)
        # Fade transition.
        if game.fade_alpha > 0.001:
            rl.DrawRectangle(0, 0, WINDOW_W, WINDOW_H, (0, 0, 0, int(clamp(game.fade_alpha, 0, 1) * 255)))

    # ------------------------------------------------------------------
    # Gameplay overlays
    # ------------------------------------------------------------------
    def draw_gameplay_overlay(self, game) -> None:
        player = game.player
        time_value = game.time
        # Damage flash.
        if player.hit_flash > 0.01:
            value = int(46 * clamp(player.hit_flash, 0, 1))
            rl.DrawRectangle(0, 0, WINDOW_W, WINDOW_H, (255, 44, 64, value))
        # Low health warning.
        if player.health <= 33.0 and player.health > 0:
            intensity = smoothstep(33.0, 6.0, player.health)
            pulse_value = 0.55 + 0.45 * math.sin(time_value * 6.0)
            edge = int((32 + 38 * pulse_value) * intensity)
            rl.DrawRectangleGradientH(0, 0, 170, WINDOW_H, (150, 0, 18, edge), CLEAR)
            rl.DrawRectangleGradientH(WINDOW_W - 170, 0, 170, WINDOW_H, CLEAR, (150, 0, 18, edge))
            rl.DrawRectangleGradientV(0, 0, WINDOW_W, 110, (150, 0, 18, edge // 2), CLEAR)
            rl.DrawRectangleGradientV(0, WINDOW_H - 150, WINDOW_W, 150, CLEAR, (150, 0, 18, edge))
        # Plasma hazard wash.
        if getattr(game, "player_in_hazard", False):
            glow = int(24 + 12 * math.sin(time_value * 9.0))
            rl.DrawRectangleGradientV(0, WINDOW_H - 190, WINDOW_W, 190, CLEAR, (255, 72, 28, glow))
            self.fonts.draw_center(self.fonts.bold, "PLASMA BURN", SCREEN_CENTER_X, WINDOW_H - 118, 17, ORANGE, 2.0)
        # Aegis bubble.
        if player.aegis_time > 0:
            remaining = clamp(player.aegis_time / 3.2, 0.0, 1.0)
            radius = 285 + 30 * (1.0 - remaining)
            rl.BeginBlendMode(rl.BLEND_ADDITIVE)
            rl.DrawCircleGradient((SCREEN_CENTER_X, SCREEN_CENTER_Y), radius + 45, (42, 227, 255, 28), CLEAR)
            rl.EndBlendMode()
            hex_points = _hex_points(SCREEN_CENTER_X, SCREEN_CENTER_Y, radius, time_value * 0.25)
            poly_outline(hex_points, (86, 236, 255, int(80 + 80 * remaining)), 2.0)
            for index in range(6):
                angle = time_value * 0.8 + index * math.tau / 6
                rl.DrawLineEx(
                    (SCREEN_CENTER_X + math.cos(angle) * 80, SCREEN_CENTER_Y + math.sin(angle) * 80),
                    (SCREEN_CENTER_X + math.cos(angle) * (radius - 10), SCREEN_CENTER_Y + math.sin(angle) * (radius - 10)),
                    1.0,
                    (60, 220, 255, 28),
                )
            self.fonts.draw_center(self.fonts.small, "AEGIS ACTIVE", SCREEN_CENTER_X, 485, 12, (137, 246, 255, 210), 2.2)
        # Nova shockwave bloom.
        if getattr(game, "nova_flash", 0.0) > 0:
            amount = clamp(game.nova_flash, 0.0, 1.0)
            rl.BeginBlendMode(rl.BLEND_ADDITIVE)
            rl.DrawCircleGradient((SCREEN_CENTER_X, SCREEN_CENTER_Y), 160 + 520 * (1 - amount), (255, 171, 236, int(90 * amount)), CLEAR)
            rl.EndBlendMode()

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------
    def _bar(self, x, y, w, h, ratio, color, back=(12, 20, 33, 235), segments=12, border=None) -> None:
        ratio = clamp(ratio, 0.0, 1.0)
        rl.DrawRectangle(int(x), int(y), int(w), int(h), back)
        if ratio > 0:
            rl.DrawRectangleGradientH(int(x), int(y), max(1, int(w * ratio)), int(h), dim(color, 0.65), color)
            # Glossy top edge.
            rl.DrawRectangle(int(x), int(y), max(1, int(w * ratio)), max(1, int(h * 0.24)), with_alpha(WHITE, 45))
        for index in range(1, segments):
            sx = int(x + w * index / segments)
            rl.DrawLineEx((sx, y), (sx, y + h), 1.0, (2, 6, 12, 150))
        rl.DrawRectangleLines(int(x), int(y), int(w), int(h), border if border else with_alpha(STEEL, 150))

    def draw_hud(self, game) -> None:
        player = game.player
        theme = game.level_def.theme
        time_value = game.time
        # Intro letterbox/banner.
        self._draw_mission_panel(game, theme)
        self._draw_boss_bar(game, theme)
        self._draw_minimap(game, theme)
        self._draw_combo(game, theme)
        self._draw_vitals(game, theme)
        self._draw_energy(game, theme)
        self._draw_abilities(game, theme)
        self._draw_crosshair(game)
        self._draw_waypoint(game, theme)
        self._draw_hud_events(game)
        if game.intro_timer > 0:
            self._draw_intro_banner(game, theme)

    def _draw_mission_panel(self, game, theme) -> None:
        x, y, w, h = WINDOW_W - 1246, 22, 374, 102
        draw_cut_panel(x, y, w, h, (5, 11, 21, 205), with_alpha(theme.accent, 120), 12, 1.2)
        rl.DrawRectangle(x + 2, y + 10, 3, h - 20, theme.accent)
        self.fonts.draw(self.fonts.small, game.level_def.code, x + 20, y + 12, 11, with_alpha(theme.accent, 220), 1.6)
        self.fonts.draw_right(self.fonts.small, f"{format_time(game.level_time)}", x + w - 18, y + 12, 11, with_alpha(MIST, 150), 1.0)
        objective = game.objective_text()
        self.fonts.draw(self.fonts.bold, objective, x + 20, y + 32, 22, WHITE, 1.2)
        alive = game.hostiles_remaining()
        if game.boss and not game.boss.dead:
            detail = f"VEX GUARD {alive:02d}   INTEL {game.intel_collected}/{game.intel_total}"
        elif game.portal_active:
            detail = f"BEACON ONLINE   INTEL {game.intel_collected}/{game.intel_total}"
        else:
            detail = f"HOSTILES {alive:02d}   INTEL {game.intel_collected}/{game.intel_total}"
        self.fonts.draw(self.fonts.small, detail, x + 20, y + 62, 12, with_alpha(MIST, 200), 1.2)
        self.fonts.draw_right(self.fonts.small, f"SCORE {format_number(game.score_earned)}", x + w - 18, y + 62, 11, with_alpha(GOLD, 195), 1.0)
        total = max(1, game.total_enemies, game.kills + alive)
        killed = max(0, game.kills)
        bar_w = w - 40
        self._bar(x + 20, y + 82, bar_w, 4, killed / total, theme.accent, (8, 15, 26, 210), 20, with_alpha(theme.accent, 35))

    def _draw_boss_bar(self, game, theme) -> None:
        boss = game.boss
        if not boss or boss.dead:
            return
        x, y, w, h = 428, 22, 438, 66
        fill = (6, 8, 17, 218)
        border = with_alpha(VIOLET, 150)
        draw_cut_panel(x, y, w, h, fill, border, 12, 1.2)
        self.fonts.draw(self.fonts.small, "THREAT OMEGA // TITAN CLASS", x + 18, y + 10, 10, with_alpha(VIOLET, 210), 1.8)
        self.fonts.draw(self.fonts.bold, boss.kind.name, x + 18, y + 24, 17, WHITE, 1.2)
        self.fonts.draw_right(self.fonts.small, f"PHASE {boss.phase}/3", x + w - 16, y + 11, 10, with_alpha(MIST, 160), 1.2)
        ratio = boss.hp / max(1.0, boss.max_hp)
        self._bar(x + 18, y + 48, w - 36, 8, ratio, VIOLET, (17, 9, 26, 210), 18, with_alpha(VIOLET, 90))
        if boss.invulnerable > 0:
            self.fonts.draw_right(self.fonts.small, "CORE SHIELDED", x + w - 16, y + 31, 10, with_alpha(CYAN, 200), 1.2)
        elif boss.phase > 1:
            self.fonts.draw_right(self.fonts.small, "CORE EXPOSED", x + w - 16, y + 31, 10, with_alpha(GOLD, 190), 1.2)

    def _draw_minimap(self, game, theme) -> None:
        x, y, w, h = 1014, 22, 238, 252
        draw_cut_panel(x, y, w, h, (4, 9, 17, 205), with_alpha(theme.accent, 110), 10, 1.0, False)
        self.fonts.draw(self.fonts.small, "TAC-MAP", x + 16, y + 11, 11, with_alpha(theme.accent, 210), 1.8)
        self.fonts.draw_right(self.fonts.small, f"SECTOR {game.current_level_index + 1:02d}", x + w - 16, y + 11, 10, with_alpha(MIST, 120), 1.2)
        mx, my, mw, mh = x + 16, y + 32, w - 32, 194
        cell = min(mw / 22, mh / 22)
        # Floor grid background.
        rl.DrawRectangle(int(mx), int(my), int(cell * 22), int(cell * 22), (4, 8, 15, 225))
        for gy in range(23):
            gy_y = int(my + gy * cell)
            rl.DrawLineEx((mx, gy_y), (mx + cell * 22, gy_y), 1.0, (26, 44, 61, 70))
        for gx in range(23):
            gx_x = int(mx + gx * cell)
            rl.DrawLineEx((gx_x, my), (gx_x, my + cell * 22), 1.0, (26, 44, 61, 70))
        game_map = game.game_map
        for my_index, row in enumerate(game_map.rows):
            for mx_index, char in enumerate(row):
                px = int(mx + mx_index * cell)
                py = int(my + my_index * cell)
                if char in "#MNC":
                    color = {
                        "#": with_alpha(theme.wall_base, 195),
                        "M": with_alpha(theme.wall_metal, 190),
                        "N": with_alpha(theme.accent, 125),
                        "C": with_alpha(theme.hazard, 150),
                    }[char]
                    rl.DrawRectangle(px, py, max(1, int(cell + 0.5)), max(1, int(cell + 0.5)), color)
                elif char == "!":
                    rl.DrawRectangle(px, py, max(1, int(cell + 0.5)), max(1, int(cell + 0.5)), with_alpha(theme.hazard, 80))
        # Pickups and intel.
        for shard in game.intel_shards:
            if shard.collected:
                continue
            px = int(mx + shard.x * cell)
            py = int(my + shard.y * cell)
            rl.DrawRectangle(px - 1, py - 1, 3, 3, GOLD)
        for pickup in game.pickups:
            if pickup.dead:
                continue
            px = int(mx + pickup.x * cell)
            py = int(my + pickup.y * cell)
            color = {"health": GREEN, "ammo": ORANGE, "nova": MAGENTA}.get(pickup.kind, MIST)
            rl.DrawRectangle(px, py, 2, 2, color)
        # Portal.
        ex, ey = game.level_def.exit
        portal_x = int(mx + ex * cell)
        portal_y = int(my + ey * cell)
        if game.portal_active:
            rl.DrawCircleLines(portal_x, portal_y, 4.5, theme.accent)
            rl.DrawCircleV((portal_x, portal_y), 2.0, theme.accent)
        else:
            rl.DrawCircleLines(portal_x, portal_y, 3.5, with_alpha(MIST, 65))
        # Enemies.
        for enemy in game.enemies:
            if enemy.dead:
                continue
            dx = enemy.x - game.player.x
            dy = enemy.y - game.player.y
            if not enemy.alerted and math.hypot(dx, dy) > 10.0:
                continue
            px = int(mx + enemy.x * cell)
            py = int(my + enemy.y * cell)
            color = theme.accent_2 if not enemy.is_boss else VIOLET
            if enemy.is_boss:
                rl.DrawCircleV((px, py), 4.0, VIOLET)
                rl.DrawCircleLines(px, py, 7.0, with_alpha(VIOLET, 120))
            else:
                rl.DrawCircleV((px, py), 2.4 if enemy.alerted else 1.5, color if enemy.alerted else with_alpha(color, 90))
        # Player triangle.
        px = mx + game.player.x * cell
        py = my + game.player.y * cell
        dir_x = math.cos(game.player.angle)
        dir_y = math.sin(game.player.angle)
        perp_x = -dir_y
        perp_y = dir_x
        tri = [
            (px + dir_x * 7, py + dir_y * 7),
            (px - dir_x * 5 + perp_x * 4, py - dir_y * 5 + perp_y * 4),
            (px - dir_x * 5 - perp_x * 4, py - dir_y * 5 - perp_y * 4),
        ]
        poly(tri, CYAN)
        rl.DrawCircleV((px, py), 1.2, WHITE)
        self.fonts.draw(self.fonts.small, "TAC-NET // LIVE", x + 16, y + 234, 9, with_alpha(MIST, 100), 1.3)
        self.fonts.draw_right(self.fonts.small, "M", x + w - 16, y + 234, 9, with_alpha(MIST, 80), 1.0)

    def _draw_combo(self, game, theme) -> None:
        if game.combo <= 1:
            return
        x = 1250
        y = 292
        multiplier = game.combo_multiplier()
        color = mix_color(theme.accent, GOLD, clamp((multiplier - 1.0) / 3.0, 0.0, 1.0), 255)
        self.fonts.draw_right(self.fonts.display, f"x{multiplier:.1f}", x, y, 36, color, 1.0)
        self.fonts.draw_right(self.fonts.small, f"{game.combo} KILL CHAIN", x, y + 42, 11, with_alpha(MIST, 160), 1.6)
        ratio = clamp(game.combo_timer / 3.0, 0.0, 1.0)
        rl.DrawRectangle(x - 160, int(y + 62), 160, 4, (12, 20, 33, 220))
        rl.DrawRectangleGradientH(x - 160, int(y + 62), max(1, int(160 * ratio)), 4, dim(color, 0.5), color)

    def _draw_vitals(self, game, theme) -> None:
        player = game.player
        x, y, w, h = 34, 590, 352, 108
        low = player.health <= 33.0
        border = with_alpha(RED, 165 if low else 75)
        draw_cut_panel(x, y, w, h, (5, 10, 20, 212), border, 12, 1.1)
        self.fonts.draw(self.fonts.small, "NOVA-7 // VITALS", x + 18, y + 12, 10, with_alpha(MIST, 160), 1.5)
        shield_ratio = player.shield / player.max_shield
        self.fonts.draw_right(self.fonts.small, f"SHIELD {int(player.shield):03d}", x + w - 18, y + 12, 10, with_alpha(CYAN, 190), 1.2)
        health_color = RED if low else GREEN
        self.fonts.draw(self.fonts.display, f"{int(math.ceil(player.health)):03d}", x + 18, y + 28, 34, health_color, 1.0)
        self.fonts.draw(self.fonts.small, "HEALTH", x + 92, y + 44, 10, with_alpha(MIST, 115), 1.6)
        self._bar(x + 152, y + 34, 176, 16, player.health / player.max_health, health_color, (13, 18, 29, 235), 10)
        self._bar(x + 18, y + 72, w - 36, 8, shield_ratio, CYAN, (10, 22, 31, 235), 14, with_alpha(CYAN, 80))
        status = "AEGIS READY" if player.aegis_cooldown <= 0 else f"AEGIS {int(player.aegis_cooldown)}s"
        self.fonts.draw(self.fonts.small, status, x + 18, y + 86, 9, with_alpha(CYAN if player.aegis_cooldown <= 0 else MIST, 150), 1.2)
        self.fonts.draw_right(self.fonts.small, "SHIELD RECHARGES OUT OF COMBAT", x + w - 18, y + 86, 9, with_alpha(MIST, 80), 0.8)

    def _draw_energy(self, game, theme) -> None:
        player = game.player
        weapon = player.weapon
        x, y, w, h = 894, 590, 352, 108
        draw_cut_panel(x, y, w, h, (5, 10, 20, 212), with_alpha(weapon.color, 100), 12, 1.1)
        self.fonts.draw(self.fonts.small, "WEAPON // ENERGY CELL", x + 18, y + 12, 10, with_alpha(MIST, 160), 1.6)
        self.fonts.draw_right(self.fonts.small, f"COST {weapon.ammo_cost}", x + w - 18, y + 12, 10, with_alpha(weapon.color, 180), 1.2)
        self.fonts.draw(self.fonts.bold, weapon.name, x + 18, y + 28, 19, WHITE, 1.4)
        self.fonts.draw(self.fonts.display, f"{player.energy:03d}", x + w - 18 - self.fonts.width(self.fonts.display, f"{player.energy:03d}", 30, 1.0), y + 50, 30, weapon.color, 1.0)
        energy_ratio = player.energy / player.max_energy
        self._bar(x + 18, y + 60, w - 36, 12, energy_ratio, weapon.color, (13, 18, 29, 235), 14)
        # Weapon slots.
        sx = x + 18
        for index in range(3):
            slot_w = 48
            slot_x = sx + index * 54
            slot_y = y + 80
            unlocked = index < player.weapon_count
            active = index == player.weapon_index
            wpn = WEAPONS[index]
            if active:
                rl.DrawRectangle(int(slot_x), int(slot_y), slot_w, 17, with_alpha(wpn.color, 55))
                rl.DrawRectangleLines(int(slot_x), int(slot_y), slot_w, 17, with_alpha(wpn.color, 220))
            else:
                rl.DrawRectangleLines(int(slot_x), int(slot_y), slot_w, 17, with_alpha(STEEL, 100 if unlocked else 40))
            color = wpn.color if unlocked else with_alpha(MIST, 55)
            self.fonts.draw(self.fonts.small, f"{index + 1} {wpn.short_name}", slot_x + 4, slot_y + 2, 9, color, 0.5)
        self.fonts.draw_right(self.fonts.small, "AUTO" if weapon.automatic else "SINGLE", x + w - 18, y + 83, 9, with_alpha(MIST, 100), 1.2)

    def _draw_ability_tile(self, x, y, size, key, label, ratio, cooldown, ready, color, icon):
        rl.DrawRectangle(int(x), int(y), int(size), int(size), (5, 10, 20, 220))
        rl.DrawRectangleLines(int(x), int(y), int(size), int(size), with_alpha(color, 190 if ready else 65))
        if cooldown:
            overlay_h = int(size * clamp(1.0 - ratio, 0, 1))
            rl.DrawRectangle(int(x), int(y), int(size), overlay_h, (0, 0, 0, 135))
        if ready:
            rl.BeginBlendMode(rl.BLEND_ADDITIVE)
            rl.DrawCircleGradient((x + size / 2, y + size / 2), size * 0.55, (*color[:3], 28), CLEAR)
            rl.EndBlendMode()
        self.fonts.draw(self.fonts.small, key, x + 5, y + 3, 9, with_alpha(color if ready else MIST, 200 if ready else 90), 1.0)
        icon(x + size / 2, y + size / 2 + 4, color if ready else with_alpha(MIST, 65), size * 0.3)
        self.fonts.draw_center(self.fonts.small, label, x + size / 2, y + size - 14, 9, with_alpha(PAPER if ready else MIST, 190 if ready else 90), 0.8)

    def _draw_abilities(self, game, theme) -> None:
        player = game.player
        base_x = 420
        base_y = 622
        size = 58
        # Dash.
        dash_ready = player.dash_cooldown <= 0
        dash_ratio = 1.0 - clamp(player.dash_cooldown / 2.2, 0, 1)
        self._draw_ability_tile(
            base_x, base_y, size, "SHIFT", "DASH", dash_ratio, player.dash_cooldown > 0, dash_ready,
            CYAN, self._icon_dash,
        )
        # Aegis.
        aegis_ready = player.aegis_cooldown <= 0
        aegis_ratio = 1.0 - clamp(player.aegis_cooldown / 10.0, 0, 1)
        self._draw_ability_tile(
            base_x + 66, base_y, size, "E", "AEGIS", aegis_ratio, player.aegis_cooldown > 0, aegis_ready,
            (68, 226, 255, 255), self._icon_aegis,
        )
        # Nova.
        nova_ready = player.nova >= 100.0
        self._draw_ability_tile(
            base_x + 132, base_y, size, "Q", "NOVA", player.nova / 100.0, not nova_ready, nova_ready,
            MAGENTA, self._icon_nova,
        )
        # Nova meter.
        meter_x = 632
        meter_y = 648
        meter_w = 238
        self.fonts.draw(self.fonts.small, "NOVA BLAST", meter_x, meter_y - 18, 10, with_alpha(MAGENTA, 190), 1.8)
        percent = int(player.nova)
        self.fonts.draw_right(self.fonts.small, f"{percent:03d}%", meter_x + meter_w, meter_y - 18, 10, with_alpha(MAGENTA, 190), 1.0)
        if nova_ready:
            glow = 0.55 + 0.45 * math.sin(game.time * 5.0)
            rl.DrawRectangle(int(meter_x - 2), int(meter_y - 2), meter_w + 4, 14, with_alpha(MAGENTA, int(35 * glow)))
        self._bar(meter_x, meter_y, meter_w, 10, player.nova / 100.0, MAGENTA, (14, 10, 26, 235), 20, with_alpha(MAGENTA, 90))
        if nova_ready:
            self.fonts.draw_center(self.fonts.small, "READY // PRESS Q", meter_x + meter_w / 2, meter_y + 16, 10, MAGENTA, 1.6)

    def _icon_dash(self, cx, cy, color, size) -> None:
        for index in range(3):
            offset = index * size * 0.45 - size * 0.45
            pts = [(cx + offset - size * 0.4, cy - size), (cx + offset + size * 0.35, cy), (cx + offset - size * 0.4, cy + size)]
            rl.DrawLineEx(pts[0], pts[1], 2.0, color)
            rl.DrawLineEx(pts[1], pts[2], 2.0, color)

    def _icon_aegis(self, cx, cy, color, size) -> None:
        hex_points = _hex_points(cx, cy, size, math.pi / 6)
        poly_outline(hex_points, color, 2.0)
        inner = _hex_points(cx, cy, size * 0.55, math.pi / 6)
        poly_outline(inner, color, 1.2)

    def _icon_nova(self, cx, cy, color, size) -> None:
        star = _star_points(cx, cy, size, size * 0.42, 8)
        poly(star, color)

    def _draw_crosshair(self, game) -> None:
        player = game.player
        weapon = player.weapon
        spread = 9.0 + player.move_amount * 7.0 + player.recoil * 26.0 + weapon.spread * 90.0
        spread *= 1.0 - player.ads_blend * 0.45
        cx = SCREEN_CENTER_X
        cy = SCREEN_CENTER_Y
        base_color = with_alpha(weapon.color, 210)
        if player.ads:
            spread *= 0.65
            rl.DrawCircleLines(int(cx), int(cy), int(7 + spread * 0.3), 1.2, with_alpha(weapon.color, 130))
        gap = spread
        length = 8 if not player.ads else 6
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rl.DrawLineEx((cx + dx * gap, cy + dy * gap), (cx + dx * (gap + length), cy + dy * (gap + length)), 2.0, base_color)
        rl.DrawCircleV((cx, cy), 1.4, with_alpha(WHITE, 220))
        if game.hit_marker_timer > 0:
            value = clamp(game.hit_marker_timer / 0.13, 0.0, 1.0)
            color = with_alpha(WHITE, int(240 * value))
            cross = 8 + (1 - value) * 6
            for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                rl.DrawLineEx((cx + dx * 4, cy + dy * 4), (cx + dx * cross, cy + dy * cross), 2.0, color)
        # Damage direction marker.
        if player.hit_flash > 0.1:
            rel = (player.damage_direction - player.angle) % math.tau
            radius = 94
            arc = []
            for index in range(7):
                angle = rel - 0.22 + index * 0.074
                arc.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
            for index in range(len(arc) - 1):
                rl.DrawLineEx(arc[index], arc[index + 1], 3.0, with_alpha(RED, int(200 * player.hit_flash)))

    def _draw_waypoint(self, game, theme) -> None:
        if not game.portal_active:
            return
        exit_x, exit_y = game.level_def.exit
        projection = game.renderer.project(game.player, exit_x, exit_y, 0.7)
        distance = math.hypot(exit_x - game.player.x, exit_y - game.player.y)
        if projection:
            sx, sy, depth, line_h = projection
            screen_x = sx * 2.0
            screen_y = sy * 2.0
            if 80 < screen_x < WINDOW_W - 80 and 110 < screen_y < WINDOW_H - 150:
                # Distance brackets around the portal.
                size = 20 + math.sin(game.time * 3.0) * 3
                pts = [(screen_x, screen_y - size), (screen_x + size, screen_y), (screen_x, screen_y + size), (screen_x - size, screen_y)]
                poly_outline(pts, with_alpha(theme.accent, 190), 1.5)
                self.fonts.draw_center(self.fonts.small, f"EXTRACTION {distance:.0f}m", screen_x, screen_y - size - 18, 11, with_alpha(theme.accent, 200), 1.3)
        else:
            # Off-screen beacon hint.
            angle = math.atan2(exit_y - game.player.y, exit_x - game.player.x) - game.player.angle
            angle = (angle + math.pi) % math.tau - math.pi
            edge_x = SCREEN_CENTER_X + math.sin(angle) * 360
            edge_y = SCREEN_CENTER_Y + 250
            self.fonts.draw_center(self.fonts.small, f"BEACON {distance:.0f}m", clamp(edge_x, 120, WINDOW_W - 120), edge_y, 11, with_alpha(theme.accent, 160), 1.2)

    def _draw_hud_events(self, game) -> None:
        y = 134
        for event in game.hud_events:
            if event.dead:
                continue
            life_ratio = clamp(event.life / max(0.001, event.max_life), 0, 1)
            fade = min(1.0, life_ratio * 3.0)
            if event.big:
                width = min(WINDOW_W - 240, 160 + self.fonts.width(self.fonts.bold, event.text, 20, 1.0))
                alpha_value = int(220 * fade)
                rl.DrawRectangle(
                    int(SCREEN_CENTER_X - width / 2),
                    int(y - 6),
                    int(width),
                    26,
                    (5, 10, 20, int(160 * fade)),
                )
                rl.DrawRectangleGradientH(
                    int(SCREEN_CENTER_X - width / 2),
                    int(y - 7),
                    int(width),
                    1,
                    CLEAR,
                    with_alpha(event.color, alpha_value),
                )
                self.fonts.draw_center(self.fonts.bold, event.text, SCREEN_CENTER_X, y - 3, 20, with_alpha(event.color, alpha_value), 1.2)
                y += 30
            else:
                self.fonts.draw_center(self.fonts.small, event.text, SCREEN_CENTER_X, y, 12, with_alpha(event.color, int(210 * fade)), 1.2)
                y += 19

    def _draw_intro_banner(self, game, theme) -> None:
        duration = 3.4
        progress = clamp(game.intro_timer / duration, 0.0, 1.0)
        elapsed = 1.0 - progress
        # Slide in and out with eased edges.
        visible = min(1.0, elapsed * 5.0, progress * 5.0)
        if visible <= 0:
            return
        bar_h = 50
        y1 = 248 - bar_h // 2
        rl.DrawRectangle(0, y1, WINDOW_W, bar_h, (4, 8, 16, int(190 * visible)))
        rl.DrawRectangle(0, y1, WINDOW_W, 2, with_alpha(theme.accent, int(200 * visible)))
        rl.DrawRectangle(0, y1 + bar_h - 2, WINDOW_W, 2, with_alpha(theme.accent, int(200 * visible)))
        self.fonts.draw_center(self.fonts.display, game.level_def.name, SCREEN_CENTER_X, y1 + 10, 30, with_alpha(WHITE, int(235 * visible)), 2.0)
        self.fonts.draw_center(self.fonts.small, game.level_def.subtitle, SCREEN_CENTER_X, y1 + bar_h + 12, 12, with_alpha(theme.accent, int(200 * visible)), 2.0)

    # ------------------------------------------------------------------
    # First-person weapon
    # ------------------------------------------------------------------
    def draw_weapon(self, game) -> None:
        player = game.player
        if player is None:
            return
        weapon = player.weapon
        time_value = game.time
        ads = player.ads_blend
        bob = math.sin(player.bob_time * 2.0) * 12.0 * player.move_amount
        bob_y = abs(math.cos(player.bob_time * 2.0)) * 7.0 * player.move_amount
        breathe = math.sin(time_value * 1.6) * 2.0
        recoil = player.recoil
        base_x = lerp(950.0, 860.0, ads) + bob * (1 - ads * 0.65) + recoil * 26.0
        base_y = lerp(670.0, 640.0, ads) + bob_y + breathe + recoil * 92.0
        base_x += math.sin(player.bob_time) * 4.0 * player.move_amount
        scale = lerp(1.0, 0.94, ads)
        direction = (-0.755, -0.656)
        perp = (-direction[1], direction[0])

        def gp(along: float, across: float):
            return (
                base_x + (direction[0] * along + perp[0] * across) * scale,
                base_y + (direction[1] * along + perp[1] * across) * scale,
            )

        # Rear forearm (mostly hidden by the ammo HUD, as in a classic FPS).
        grip = gp(45, 42)
        shoulder = (grip[0] + 300, grip[1] + 320)
        arm = [
            (grip[0] - 30, grip[1] - 18),
            (grip[0] + 40, grip[1] + 2),
            (shoulder[0] + 70, shoulder[1] + 80),
            (shoulder[0] - 120, shoulder[1] + 100),
            (grip[0] - 8, grip[1] + 130),
        ]
        poly(arm, (46, 14, 28, 255))
        poly(
            [
                (arm[0][0] + 14, arm[0][1] + 4),
                (arm[1][0] - 4, arm[1][1] + 8),
                (arm[2][0] - 10, arm[2][1] + 10),
                (arm[4][0] + 18, arm[4][1] - 4),
            ],
            (151, 35, 54, 255),
        )
        poly_outline(arm, (12, 8, 15, 255), 3.0)
        rl.DrawLineEx(gp(20, 34), gp(110, 34), 3.0, GOLD)

        # Stock and receiver body.
        stock = [gp(-104, -20), gp(-40, -36), gp(-18, 22), gp(-62, 62), gp(-112, 32)]
        poly(stock, (24, 27, 39, 255))
        poly_outline(stock, (7, 9, 14, 255), 4.0 * scale)

        if weapon.key == "scatter":
            hull = [gp(-72, -34), gp(-4, -56), gp(172, -50), gp(214, -24), gp(214, 32), gp(154, 60), gp(22, 66), gp(-66, 36)]
            barrel = [gp(202, -30), gp(342, -24), gp(348, 26), gp(202, 32)]
            top_panel = [gp(-6, -54), gp(88, -60), gp(190, -44), gp(204, -30), gp(74, -34)]
            cowl = [gp(0, -56), gp(80, -61), gp(194, -44), gp(198, -24), gp(56, -26), gp(-14, -36)]
            side_panel = [gp(16, -20), gp(172, -24), gp(162, 26), gp(34, 34), gp(-10, 14)]
            accent_rail_a = gp(28, 8)
            accent_rail_b = gp(186, 14)
        elif weapon.key == "lance":
            hull = [gp(-82, -22), gp(-8, -42), gp(184, -34), gp(222, -14), gp(222, 16), gp(164, 36), gp(20, 46), gp(-72, 26)]
            barrel = [gp(214, -10), gp(430, -8), gp(434, 10), gp(214, 12)]
            top_panel = [gp(-8, -40), gp(96, -46), gp(206, -30), gp(218, -18), gp(80, -22)]
            cowl = [gp(0, -42), gp(84, -47), gp(202, -31), gp(194, -16), gp(60, -22), gp(-12, -30)]
            side_panel = [gp(18, -10), gp(174, -14), gp(164, 22), gp(34, 30), gp(-10, 12)]
            accent_rail_a = gp(30, 2)
            accent_rail_b = gp(198, 6)
        else:
            hull = [gp(-76, -28), gp(-6, -48), gp(162, -42), gp(208, -22), gp(208, 24), gp(152, 50), gp(20, 56), gp(-68, 30)]
            barrel = [gp(196, -16), gp(342, -12), gp(348, 12), gp(196, 18)]
            top_panel = [gp(-8, -46), gp(92, -52), gp(190, -36), gp(204, -24), gp(76, -28)]
            cowl = [gp(-2, -47), gp(82, -53), gp(188, -35), gp(184, -19), gp(56, -24), gp(-14, -34)]
            side_panel = [gp(18, -12), gp(166, -16), gp(156, 30), gp(36, 36), gp(-10, 16)]
            accent_rail_a = gp(30, 4)
            accent_rail_b = gp(184, 8)

        poly(hull, (28, 34, 49, 255))
        poly_outline(hull, (5, 7, 12, 255), 5.0 * scale)
        poly(stock, (24, 27, 39, 255))
        poly_outline(stock, (7, 9, 14, 255), 3.0 * scale)
        # Lower receiver highlight.
        rl.DrawLineEx(gp(-12, 42), gp(170, 46), 2.0 * scale, (72, 77, 92, 255))

        # Ceramic side plate.
        poly(side_panel, (119, 126, 141, 255))
        poly_outline(side_panel, (31, 34, 45, 255), 2.0 * scale)
        poly([gp(28, -4), gp(150, -8), gp(144, 14), gp(40, 22)], (173, 179, 190, 255))
        # Crimson armored cowl.
        poly(cowl, (147, 34, 54, 255))
        poly_outline(cowl, (231, 170, 78, 255), 2.0 * scale)
        poly([gp(16, -41), gp(82, -45), gp(170, -31), gp(166, -25), gp(62, -31)], (213, 72, 80, 255))
        # Gold and accent seams.
        rl.DrawLineEx(gp(24, 25), gp(160, 27), 3.0 * scale, GOLD)
        rl.DrawLineEx(accent_rail_a, accent_rail_b, 3.6 * scale, weapon.color)
        rl.DrawLineEx(gp(46, 44), gp(172, 46), 2.0 * scale, (71, 78, 92, 255))

        # Barrel and muzzle.
        poly(barrel, (23, 27, 39, 255))
        poly_outline(barrel, (5, 7, 12, 255), 4.0 * scale)
        if weapon.key == "scatter":
            for across in (-22, 0, 22):
                center = gp(338, across)
                rl.DrawCircleV(center, 8.0 * scale, (7, 9, 15, 255))
                rl.DrawCircleV(center, 5.0 * scale, (62, 44, 40, 255))
                rl.DrawCircleV(center, 2.2 * scale, weapon.color)
            rl.DrawLineEx(gp(202, -30), gp(336, -28), 2.0 * scale, (109, 100, 102, 255))
            rl.DrawLineEx(gp(202, 30), gp(342, 26), 2.0 * scale, (87, 79, 81, 255))
        else:
            center = gp(344, 0)
            rl.DrawCircleV(center, 7.0 * scale, (6, 8, 14, 255))
            rl.DrawCircleV(center, 4.0 * scale, weapon.color)
            rl.DrawLineEx(gp(214, -10), gp(336, -8), 2.0 * scale, (105, 101, 110, 255))
            rl.DrawLineEx(gp(214, 10), gp(342, 8), 2.0 * scale, (80, 77, 87, 255))
        if weapon.key == "lance":
            for index in range(5):
                along = 244 + index * 36
                rl.DrawLineEx(gp(along, -12), gp(along, 14), 3.0 * scale, with_alpha(weapon.color, 150))
                rl.DrawCircleV(gp(along, 1), 2.2 * scale, weapon.color)

        # Top rail and sight.
        poly([gp(-2, -54), gp(92, -59), gp(192, -43), gp(188, -38), gp(88, -53), gp(-4, -48)], (66, 74, 91, 255))
        rl.DrawLineEx(gp(20, -58), gp(80, -62), 2.0 * scale, (128, 139, 158, 255))
        sight = gp(140, -50)
        rl.DrawCircleV(sight, 4.0 * scale, (9, 11, 17, 255))
        rl.DrawCircleV(sight, 1.8 * scale, weapon.color)

        # Energy cell / core.
        if weapon.key != "lance":
            core = gp(112, 8)
            glow_value = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(time_value * 4.0))
            rl.BeginBlendMode(rl.BLEND_ADDITIVE)
            rl.DrawCircleGradient(core, 27 * scale, (*weapon.muzzle_color[:3], int(95 * glow_value)), CLEAR)
            rl.EndBlendMode()
            rl.DrawCircleV(core, 11 * scale, (13, 14, 21, 255))
            rl.DrawCircleV(core, 7.5 * scale, with_alpha(weapon.color, 245))
            rl.DrawCircleV(core, 3.0 * scale, WHITE)
            rl.DrawLineEx(gp(94, 26), gp(136, 28), 2.0 * scale, (54, 41, 46, 255))
        else:
            core = gp(300, 0)
            rl.BeginBlendMode(rl.BLEND_ADDITIVE)
            rl.DrawCircleGradient(core, 24 * scale, (*weapon.muzzle_color[:3], 80), CLEAR)
            rl.EndBlendMode()
            rl.DrawCircleV(core, 5.0 * scale, weapon.color)

        # Trigger guard and grip.
        poly([gp(38, 34), gp(88, 32), gp(112, 106), gp(58, 112)], (20, 23, 34, 255))
        poly_outline([gp(38, 34), gp(88, 32), gp(112, 106), gp(58, 112)], (5, 7, 12, 255), 2.0 * scale)
        rl.DrawLineEx(gp(52, 52), gp(98, 50), 2.0 * scale, (92, 80, 91, 255))
        rl.DrawCircleV(gp(246, 14), 3.0 * scale, GOLD)

        # Support hand gripping the fore-end.
        support = gp(198, 2)
        fore = gp(236, 82)
        arm_support = [
            (support[0] - 24, support[1] - 16),
            (support[0] + 24, support[1] - 12),
            (fore[0] + 42, fore[1] + 74),
            (fore[0] - 34, fore[1] + 84),
        ]
        poly(arm_support, (99, 24, 39, 255))
        poly_outline(arm_support, (21, 9, 16, 255), 2.2 * scale)
        rl.DrawCircleV(support, 18 * scale, (39, 15, 24, 255))
        rl.DrawCircleV((support[0] - 2, support[1] - 2), 14.5 * scale, (174, 44, 59, 255))
        rl.DrawCircleV((support[0] - 5, support[1] - 5), 8.5 * scale, (213, 72, 80, 255))
        for finger_index in range(4):
            finger = gp(186 + finger_index * 10, -10 + finger_index * 2)
            rl.DrawCircleV(finger, 5.6 * scale, (224, 88, 91, 255))
            rl.DrawLineEx(finger, (finger[0] - 8 * scale, finger[1] + 9 * scale), 1.0 * scale, (75, 24, 31, 255))
        rl.DrawLineEx((support[0] - 15, support[1] + 8), (support[0] + 10, support[1] + 3), 3.0 * scale, GOLD)

        # Muzzle flash.
        if player.muzzle_flash > 0.02:
            flash = clamp(player.muzzle_flash, 0.0, 1.0)
            muzzle = gp(358 if weapon.key != "lance" else 440, 0)
            rng = random.Random(int(game.time * 60))
            rl.BeginBlendMode(rl.BLEND_ADDITIVE)
            rl.DrawCircleGradient(muzzle, 86 * flash, (*weapon.muzzle_color[:3], int(150 * flash)), CLEAR)
            rl.EndBlendMode()
            points = []
            for index in range(10):
                angle = index * math.tau / 10 + rng.uniform(-0.12, 0.12)
                radius = (38 if index % 2 == 0 else 12) * flash
                points.append((muzzle[0] + math.cos(angle) * radius, muzzle[1] + math.sin(angle) * radius))
            poly(points, with_alpha(weapon.muzzle_color, int(225 * flash)))
            poly(_star_points(muzzle[0], muzzle[1], 22 * flash, 8 * flash, 6, game.time), WHITE)
            rl.DrawCircleV(muzzle, 8 * scale * flash, (255, 250, 225, 255))
