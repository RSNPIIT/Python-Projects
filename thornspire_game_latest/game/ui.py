"""HUD, title screen, pause menu and results — all drawn on top of the GL frame."""

from __future__ import annotations

import math

import numpy as np
import pygame

from .constants import (
    FONT_MONO,
    FONT_TITLE,
    FONT_UI,
    FONT_UI_CONDENSED,
    MAX_ARMOR,
    MAX_HEARTS,
    SCREEN_H,
    SCREEN_W,
    TITLE,
    UI as UI_COLORS,
    BIOMES,
    HERO_CLOAKS,
    HERO_SCARFS,
    HERO_HEADGEARS,
    HERO_TRAILS,
    DIFFICULTIES,
    DIFFICULTY_MODES,
    TOTAL_LEVELS,
)
from .level import level_biome_index
from .utils import (
    clamp,
    color_lerp,
    draw_glow,
    draw_heart,
    draw_text,
    draw_text_spaced,
    font,
    format_score,
    format_time,
    heart_points,
    rounded_panel,
    text,
)


class UI:
    def __init__(self) -> None:
        self.f_title = font(FONT_TITLE, 92, bold=True)
        self.f_title_sub = font(FONT_UI, 15, bold=True)
        self.f_h1 = font(FONT_UI_CONDENSED, 54, bold=True)
        self.f_h2 = font(FONT_UI_CONDENSED, 34, bold=True)
        self.f_menu = font(FONT_UI, 27, bold=True)
        self.f_menu_small = font(FONT_UI, 15)
        self.f_menu_num = font(FONT_MONO, 13)
        self.f_label = font(FONT_UI, 11, bold=True)
        self.f_hud_num = font(FONT_UI_CONDENSED, 36, bold=True)
        self.f_score = font(FONT_UI_CONDENSED, 42, bold=True)
        self.f_score_label = font(FONT_UI, 11, bold=True)
        self.f_body = font(FONT_UI, 16)
        self.f_small = font(FONT_UI, 13)
        self.f_tiny = font(FONT_UI, 11)
        self.f_banner = font(FONT_UI_CONDENSED, 30, bold=True)
        self.f_banner_sub = font(FONT_UI, 13)
        self.f_key = font(FONT_MONO, 12, bold=True)
        self.f_float = font(FONT_UI_CONDENSED, 16, bold=True)
        self._left_shade = self._build_left_shade()

    # ------------------------------------------------------------------
    def _build_left_shade(self) -> pygame.Surface:
        surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for x in range(SCREEN_W):
            t = clamp(x / 1060.0, 0.0, 1.0)
            a = int(232 * (1.0 - t * t) ** 1.15)
            if a:
                pygame.draw.line(surf, (2, 6, 8, a), (x, 0), (x, SCREEN_H))
        # subtle vignette top and bottom
        top = pygame.Surface((SCREEN_W, 160), pygame.SRCALPHA)
        for y in range(160):
            a = int(80 * (1 - y / 160) ** 1.6)
            pygame.draw.line(top, (2, 5, 7, a), (0, y), (SCREEN_W, y))
        surf.blit(top, (0, 0))
        return surf

    # ------------------------------------------------------------------
    # shared decorations
    # ------------------------------------------------------------------
    def _pill(self, screen, rect, accent, alpha=150):
        rounded_panel(screen, rect, UI_COLORS["panel"], alpha, accent, 90, 10, 1)

    def _label(self, screen, value, pos, color=None, anchor="topleft", spacing=None):
        col = color or UI_COLORS["muted"]
        if spacing:
            draw_text_spaced(screen, value, self.f_label, col, pos, spacing,
                             anchor=anchor, shadow=None)
        else:
            draw_text(screen, value, self.f_label, col, pos, anchor=anchor,
                      shadow=(0, 0, 0), shadow_offset=1)

    def _keycap(self, screen, x, y, label, width=None):
        w = width or max(38, int(len(label) * 8.2 + 16))
        rect = pygame.Rect(x, y, w, 24)
        rounded_panel(screen, rect, (18, 26, 28), 170, UI_COLORS["muted"], 70, 5, 1)
        draw_text(screen, label, self.f_key, UI_COLORS["ivory"], rect.center, anchor="center",
                  shadow=None)
        return w

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------
    def draw_hud(self, screen, game) -> None:
        player = game.player
        p = game.palette
        accent = p["accent"]
        # ----- left: hearts + currency
        panel = pygame.Rect(24, 20, 344, 84)
        self._pill(screen, panel, accent, 205)
        for i in range(MAX_HEARTS):
            cx = 46 + i * 28
            cy = 42
            if i < player.hearts:
                draw_heart(screen, (cx, cy), 18, (255, 112, 140), glow=None)
                pygame.draw.circle(screen, (255, 210, 220), (int(cx - 3), int(cy - 4)), 2)
            else:
                pts = heart_points(cx, cy, 18)
                pygame.draw.polygon(screen, (48, 58, 58), pts)
                pygame.draw.polygon(screen, (28, 34, 36), pts, 1)
        # armor slots
        draw_text(screen, "ARMOR", self.f_tiny, UI_COLORS["dim"], (194, 26), shadow=None)
        for i in range(MAX_ARMOR):
            self._shield_icon(screen, (202 + i * 22, 56), 8.5, i < player.armor)
        # coins
        self._coin_icon(screen, (44, 80), 9)
        draw_text(screen, f"{game.coins}", font(FONT_UI_CONDENSED, 20, bold=True),
                  UI_COLORS["ivory"], (60, 70), shadow=(0, 0, 0), shadow_offset=1)
        self._gem_icon(screen, (142, 80), 9)
        draw_text(screen, f"{game.gems}", font(FONT_UI_CONDENSED, 20, bold=True),
                  UI_COLORS["ivory"], (158, 70), shadow=(0, 0, 0), shadow_offset=1)
        if game.mode == "trial":
            self._chrono_icon(screen, (234, 80), 8)
            draw_text(screen, f"{game.chronos}", font(FONT_UI_CONDENSED, 20, bold=True),
                      UI_COLORS["ivory"], (250, 70), shadow=(0, 0, 0), shadow_offset=1)
        draw_text(screen, "DASH", self.f_tiny, UI_COLORS["dim"], (296, 30), shadow=None)
        bar = pygame.Rect(296, 48, 60, 5)
        pygame.draw.rect(screen, (30, 38, 38), bar, border_radius=2)
        ready = 1.0 - clamp(player.dash_cooldown / 0.85, 0.0, 1.0)
        fill = pygame.Rect(bar.x, bar.y, int(bar.w * ready), bar.h)
        if fill.w:
            pygame.draw.rect(screen, accent if ready >= 1 else (120, 150, 140), fill,
                             border_radius=2)
        draw_text(screen, "SHIFT", self.f_tiny, UI_COLORS["dim"], (296, 60), shadow=None)

        # ----- center: score + combo
        cx = SCREEN_W // 2
        self._label(screen, "SCORE", (cx, 24), UI_COLORS["muted"], "midtop", spacing=4)
        score_col = UI_COLORS["ivory"]
        draw_text(screen, format_score(game.score), self.f_score, score_col,
                  (cx, 38), anchor="midtop", shadow=(0, 0, 0), shadow_offset=2)
        if game.combo_mult > 1 and game.combo_count > 0:
            mult = game.combo_mult
            label = f"x{mult}"
            col = color_lerp(accent, UI_COLORS["gold"], (mult - 1) / 4.0)
            draw_text(screen, label, font(FONT_UI_CONDENSED, 26, bold=True), col,
                      (cx - 2, 84), anchor="midtop", shadow=(0, 0, 0), shadow_offset=2)
            bar = pygame.Rect(cx + 26, 94, 74, 4)
            pygame.draw.rect(screen, (30, 38, 38), bar, border_radius=2)
            frac = clamp(game.combo_timer / 3.6, 0.0, 1.0)
            if frac > 0:
                pygame.draw.rect(screen, col, (bar.x, bar.y, int(bar.w * frac), bar.h),
                                 border_radius=2)

        # ----- right: mode metric
        panel = pygame.Rect(SCREEN_W - 320, 20, 296, 84)
        self._pill(screen, panel, accent, 205)
        right_x = SCREEN_W - 44
        if game.mode == "trial":
            self._label(screen, "TIME LEFT", (right_x, 30), UI_COLORS["muted"], "topright", spacing=3)
            t = game.time_left
            urgent = t <= 10
            col = UI_COLORS["danger"] if urgent else UI_COLORS["ivory"]
            if urgent:
                pulse = 0.5 + 0.5 * math.sin(game.time * 9.0)
                col = color_lerp(UI_COLORS["danger"], (255, 220, 210), pulse * 0.5)
            draw_text(screen, format_time(t), self.f_hud_num, col,
                      (right_x, 47), anchor="topright", shadow=(0, 0, 0), shadow_offset=2)
            draw_text(screen, f"BEST {format_score(game.best_for_mode())}",
                      self.f_tiny, UI_COLORS["dim"], (right_x, 85), anchor="topright", shadow=None)
        elif game.mode == "levels":
            self._label(screen, "QUEST PROGRESS", (right_x, 30), UI_COLORS["muted"], "topright", spacing=3)
            draw_text(screen, f"LEVEL {game.level_number}", self.f_hud_num, UI_COLORS["ivory"],
                      (right_x, 47), anchor="topright", shadow=(0, 0, 0), shadow_offset=2)
            draw_text(screen, f"TIME {format_time(game.elapsed)}   ·   DIFF {game.difficulty_mode.upper()}",
                      self.f_tiny, UI_COLORS["dim"], (right_x, 85), anchor="topright", shadow=None)
        else:
            self._label(screen, "DISTANCE", (right_x, 30), UI_COLORS["muted"], "topright", spacing=3)
            draw_text(screen, f"{game.distance:,} m", self.f_hud_num, UI_COLORS["ivory"],
                      (right_x, 47), anchor="topright", shadow=(0, 0, 0), shadow_offset=2)
            draw_text(screen, f"LOOP {game.loop_number}   ·   BEST {format_score(game.best_for_mode())}",
                      self.f_tiny, UI_COLORS["dim"], (right_x, 85), anchor="topright", shadow=None)

        # ----- biome banner
        if game.banner_timer > 0:
            self._draw_banner(screen, game)

        # ----- controls hint at the start
        if game.state == "playing" and game.elapsed < 9.5 and game.hints:
            a = 1.0
            if game.elapsed < 1.0:
                a = game.elapsed
            elif game.elapsed > 7.5:
                a = clamp(9.5 - game.elapsed, 0.0, 1.0)
            hint = ("A D  move     SPACE  jump (hold = higher)     W S  climb     "
                    "SHIFT  dash     P  pause")
            self._faded_text(screen, hint, self.f_small, UI_COLORS["ivory"],
                             (SCREEN_W // 2, SCREEN_H - 34), int(210 * a), "center")

        if game.debug_fps:
            draw_text(screen, f"{game.clock.get_fps():5.1f} fps · gl {game.renderer.last_render_ms:4.1f} ms",
                      self.f_tiny, (180, 220, 180), (SCREEN_W - 20, SCREEN_H - 20),
                      anchor="bottomright", shadow=None)

    def _draw_banner(self, screen, game) -> None:
        pal = BIOMES[game.biome_index % len(BIOMES)]
        life = game.banner_timer
        total = game.banner_total
        t = 1.0 - clamp(life / total, 0.0, 1.0)
        if t < 0.15:
            a = t / 0.15
        elif t > 0.8:
            a = (1 - t) / 0.2
        else:
            a = 1.0
        a = clamp(a, 0.0, 1.0)
        cx = SCREEN_W // 2
        y = 138
        surf = pygame.Surface((720, 116), pygame.SRCALPHA)
        label = game.banner_title or pal["name"]
        draw_text_spaced(surf, label, self.f_banner, pal["accent"], (360, 8),
                         5, anchor="midtop", shadow=(0, 0, 0), shadow_offset=2)
        if game.banner_sub:
            draw_text(surf, game.banner_sub, self.f_banner_sub, UI_COLORS["muted"], (360, 48),
                      anchor="midtop", shadow=None)
        # decorative lines
        pygame.draw.line(surf, (*pal["accent"], 120), (90, 38), (250, 38), 1)
        pygame.draw.line(surf, (*pal["accent"], 120), (470, 38), (630, 38), 1)
        pygame.draw.circle(surf, pal["accent"], (360, 40), 2)
        surf.set_alpha(int(235 * a))
        screen.blit(surf, (cx - 360, y))

    def _faded_text(self, screen, value, f, color, pos, alpha, anchor="topleft"):
        if alpha <= 2:
            return
        img = f.render(value, True, color)
        img.set_alpha(alpha)
        rect = img.get_rect(**{anchor: pos})
        screen.blit(img, rect)

    # ------------------------------------------------------------------
    # dynamic colorful menu primitives (zero font-glyph arrows)
    # ------------------------------------------------------------------
    def _draw_aurora_backdrop(self, screen, t: float, alpha_dim: int = 120) -> None:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((10, 12, 28, alpha_dim))
        screen.blit(overlay, (0, 0))

        # Drifting multi-hue color nebulae so menus feel vibrant and alive
        nebulae = [
            (270 + math.sin(t * 0.55) * 85, 200 + math.cos(t * 0.42) * 40, 350, (255, 132, 78), 46),
            (1010 + math.cos(t * 0.48) * 85, 220 + math.sin(t * 0.52) * 45, 350, (196, 94, 255), 48),
            (640 + math.sin(t * 0.62 + 1.2) * 95, 520 + math.cos(t * 0.38) * 35, 340, (64, 242, 196), 42),
            (640 + math.cos(t * 0.45) * 65, 115 + math.sin(t * 0.35) * 25, 270, (98, 198, 255), 38),
        ]
        for nx, ny, nr, ncol, na in nebulae:
            draw_glow(screen, (int(nx), int(ny)), nr, ncol, na, 2.2)

        # Floating prism bokeh & 4-point star sparkles
        spark_cols = [
            (255, 196, 92),
            (92, 248, 202),
            (214, 122, 255),
            (255, 118, 168),
            (112, 214, 255),
        ]
        for i in range(24):
            col = spark_cols[i % len(spark_cols)]
            px = (i * 173 + t * (18 + (i % 4) * 7)) % (SCREEN_W + 80) - 40
            py = (i * 97 - t * (14 + (i % 3) * 6)) % (SCREEN_H + 80) - 40
            pulse = 0.55 + 0.45 * math.sin(t * 2.4 + i * 1.3)
            r = 2 + (i % 3)
            draw_glow(screen, (int(px), int(py)), r * 5, col, int(36 * pulse), 2.0)
            if i % 3 == 0:
                s = int(4 + 2 * pulse)
                pygame.draw.line(screen, col, (int(px - s), int(py)), (int(px + s), int(py)), 1)
                pygame.draw.line(screen, col, (int(px), int(py - s)), (int(px), int(py + s)), 1)
            else:
                pygame.draw.circle(screen, col, (int(px), int(py)), r)

    def _draw_vector_arrow(self, screen, center, size: float, direction: str, color) -> None:
        """100% vector-polygon arrows ('left', 'right', 'play') — never relies on fonts."""
        cx, cy = center
        s = float(size)
        if direction == "play":
            pts = [
                (cx - s * 0.42, cy - s * 0.72),
                (cx + s * 0.72, cy),
                (cx - s * 0.42, cy + s * 0.72),
            ]
            pygame.draw.polygon(screen, color, pts)
            return

        w = max(2.6, s * 0.38)
        if direction == "left":
            pts = [
                (cx + s * 0.25, cy - s * 0.82),
                (cx + s * 0.25 + w, cy - s * 0.82),
                (cx - s * 0.52 + w, cy),
                (cx + s * 0.25 + w, cy + s * 0.82),
                (cx + s * 0.25, cy + s * 0.82),
                (cx - s * 0.52, cy),
            ]
        else:  # "right"
            pts = [
                (cx - s * 0.25 - w, cy - s * 0.82),
                (cx - s * 0.25, cy - s * 0.82),
                (cx + s * 0.52, cy),
                (cx - s * 0.25, cy + s * 0.82),
                (cx - s * 0.25 - w, cy + s * 0.82),
                (cx + s * 0.52 - w, cy),
            ]
        pygame.draw.polygon(screen, color, pts)

    def _draw_arrow_btn(self, screen, center, radius: int, direction: str, color, active: bool = True) -> None:
        cx, cy = int(center[0]), int(center[1])
        if active:
            draw_glow(screen, (cx, cy), int(radius * 1.9), color, 68, 2.0)
        fill = (24, 30, 52) if active else (15, 19, 32)
        rim = color if active else (86, 102, 132)
        arrow_col = (255, 250, 242) if active else (158, 174, 198)
        pygame.draw.circle(screen, fill, (cx, cy), radius)
        pygame.draw.circle(screen, rim, (cx, cy), radius, 2)
        self._draw_vector_arrow(screen, (cx, cy), radius * 0.52, direction, arrow_col)

    def _draw_back_btn(self, screen, accent) -> None:
        self._draw_arrow_btn(screen, (56, 52), 21, "left", accent, active=True)
        draw_text_spaced(screen, "BACK", self.f_label, UI_COLORS["ivory"],
                         (86, 46), 2, shadow=(0, 0, 0), shadow_offset=1)

    def _draw_floating_orb(
        self,
        screen,
        center: tuple[int, int],
        base_r: int,
        selected: bool,
        col_a: tuple[int, int, int],
        col_b: tuple[int, int, int],
        t: float,
        phase: float = 0.0,
    ) -> tuple[int, int, int]:
        cx = int(center[0])
        cy = int(center[1] + math.sin(t * 2.15 + phase) * 9.0)
        r = int(base_r + (12 if selected else 0) + math.sin(t * 3.1 + phase) * (3.0 if selected else 1.5))

        # Multi-ring colorful glow
        draw_glow(screen, (cx, cy), int(r * 1.85), col_a, 92 if selected else 46, 2.1)
        draw_glow(screen, (cx, cy), int(r * 1.38), col_b, 74 if selected else 34, 2.0)

        # Revolving orbital satellites
        orbit_r = r + (17 if selected else 12)
        sat_count = 12 if selected else 8
        for k in range(sat_count):
            ang = t * (0.95 if k % 2 == 0 else -0.72) + phase + k * (math.tau / sat_count)
            ox = cx + math.cos(ang) * orbit_r
            oy = cy + math.sin(ang) * orbit_r
            scol = col_a if k % 2 == 0 else col_b
            sr = 4 if (selected and k % 3 == 0) else 2.5
            pygame.draw.circle(screen, scol, (int(ox), int(oy)), int(sr))

        # Thin outer orbital halo ring
        halo = pygame.Surface((orbit_r * 2 + 8, orbit_r * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(
            halo,
            (*col_b, 120 if selected else 52),
            (orbit_r + 4, orbit_r + 4),
            orbit_r,
            2 if selected else 1,
        )
        screen.blit(halo, (cx - orbit_r - 4, cy - orbit_r - 4))

        # Orb shadow & jewel-tinted core
        pygame.draw.circle(screen, (6, 8, 18), (cx, cy + 7), r)
        core_col = color_lerp((18, 22, 44), col_a, 0.25 if selected else 0.13)
        pygame.draw.circle(screen, core_col, (cx, cy), r)

        # Inner luminous gradient crown
        draw_glow(screen, (cx, cy - int(r * 0.28)), int(r * 0.82), col_b, 64 if selected else 32, 2.0)

        # Crisp concentric colored rims
        rim_outer = color_lerp(col_a, (255, 255, 255), 0.28) if selected else col_a
        pygame.draw.circle(screen, rim_outer, (cx, cy), r, 4 if selected else 2)
        pygame.draw.circle(screen, col_b, (cx, cy), r - 7, 2 if selected else 1)
        return cx, cy, r

    # ------------------------------------------------------------------
    # title — dynamic colorful menu with TWO floating circles
    # ------------------------------------------------------------------
    def draw_title(self, screen, game) -> None:
        t = game.time
        self._draw_aurora_backdrop(screen, t, alpha_dim=95)

        # Radiant centered logo
        cx_mid = SCREEN_W // 2
        spire_col = color_lerp((84, 250, 204), (118, 208, 255), 0.5 + 0.5 * math.sin(t * 1.4))
        gold_col = (255, 224, 146)
        draw_glow(screen, (cx_mid - 140, 104), 220, (255, 168, 84), 48, 2.3)
        draw_glow(screen, (cx_mid + 140, 104), 220, (186, 104, 255), 48, 2.3)

        w_thorn = sum(self.f_title.size(ch)[0] + 6 for ch in "THORN")
        w_spire = sum(self.f_title.size(ch)[0] + 6 for ch in "SPIRE") - 6
        logo_x = cx_mid - (w_thorn + 10 + w_spire) // 2
        logo_y = 40
        thorn_rect = draw_text_spaced(
            screen, "THORN", self.f_title, (255, 248, 232),
            (logo_x, logo_y), 6, shadow=(10, 12, 28), shadow_offset=4,
        )
        draw_text_spaced(
            screen, "SPIRE", self.f_title, spire_col,
            (logo_x + thorn_rect.w + 10, logo_y), 6, shadow=(10, 12, 28), shadow_offset=4,
        )

        # Colorful dual-wing divider & subtitle
        line_y = 148
        pygame.draw.line(screen, (255, 174, 88), (cx_mid - 290, line_y), (cx_mid - 18, line_y), 2)
        pygame.draw.line(screen, (198, 114, 255), (cx_mid + 18, line_y), (cx_mid + 290, line_y), 2)
        pygame.draw.polygon(
            screen, gold_col,
            [(cx_mid, line_y - 7), (cx_mid + 9, line_y), (cx_mid, line_y + 7), (cx_mid - 9, line_y)],
        )
        draw_text_spaced(
            screen, "CLIMB THE BRAMBLE  ·  CONQUER THE 10 REALMS",
            self.f_title_sub, (226, 236, 250), (cx_mid, 164), 3,
            anchor="midtop", shadow=(8, 10, 22), shadow_offset=2,
        )

        unlocked = min(TOTAL_LEVELS, int(game.save.get("unlocked_level", 1)))
        cloak_info = HERO_CLOAKS[game.custom_cloak % len(HERO_CLOAKS)]
        gear_info = HERO_HEADGEARS[game.custom_headgear % len(HERO_HEADGEARS)]

        # ---- FLOATING CIRCLE 1: PLAY GAME ----
        sel_play = game.title_index == 0
        px, py, pr = self._draw_floating_orb(
            screen, (440, 392), 126, sel_play,
            (255, 176, 68), (78, 246, 198), t, phase=0.0,
        )
        # Animated portal & play emblem inside top of PLAY GAME circle
        em_y = py - 42
        draw_glow(screen, (px, em_y), 46, (255, 196, 88), 80 if sel_play else 45, 2.0)
        pygame.draw.circle(screen, (255, 210, 104), (px, em_y), 30, 3)
        pygame.draw.circle(screen, (96, 250, 208), (px, em_y), 22, 1)
        self._draw_vector_arrow(screen, (px + 2, em_y), 19, "play", (255, 250, 236))

        draw_text(
            screen, "PLAY GAME", self.f_h2,
            (255, 252, 242) if sel_play else (220, 230, 242),
            (px, py + 4), anchor="midtop", shadow=(6, 10, 22), shadow_offset=2,
        )
        draw_text(
            screen, f"Level {unlocked}/{TOTAL_LEVELS} · Infinite · Trial", self.f_small,
            (255, 220, 138) if sel_play else (175, 192, 212),
            (px, py + 46), anchor="midtop", shadow=None,
        )
        draw_text(
            screen, "Easy · Medium · Hard", self.f_tiny,
            (116, 248, 208) if sel_play else (140, 160, 180),
            (px, py + 68), anchor="midtop", shadow=None,
        )
        pill_play = pygame.Rect(px - 64, py + pr - 16, 128, 30)
        rounded_panel(
            screen, pill_play,
            (46, 36, 18) if sel_play else (20, 26, 40), 245,
            (255, 196, 84) if sel_play else (110, 130, 155), 235 if sel_play else 110, 15, 2,
        )
        draw_text(
            screen, "PLAY", self.f_key,
            (255, 248, 230) if sel_play else (175, 190, 210),
            (pill_play.centerx - 8, pill_play.centery), anchor="center", shadow=None,
        )
        self._draw_vector_arrow(
            screen, (pill_play.centerx + 22, pill_play.centery), 6.5, "play",
            (255, 206, 92) if sel_play else (155, 172, 192),
        )

        # ---- FLOATING CIRCLE 2: CUSTOMIZE ----
        sel_cust = game.title_index == 1
        cx, cy, cr = self._draw_floating_orb(
            screen, (840, 392), 126, sel_cust,
            (204, 108, 255), (255, 108, 192), t, phase=2.1,
        )
        # Live animated running mini-hero inside top of CUSTOMIZE circle
        stage_y = cy - 18
        pygame.draw.ellipse(screen, (36, 24, 62), (cx - 46, stage_y - 6, 92, 16))
        pygame.draw.ellipse(screen, (216, 132, 255), (cx - 46, stage_y - 6, 92, 16), 1)
        if game.custom_preview_player is not None:
            pp = game.custom_preview_player
            pp.x = cx - pp.w / 2
            pp.y = stage_y - pp.h + 4
            pp.custom_cloak = game.custom_cloak
            pp.custom_scarf = game.custom_scarf
            pp.custom_headgear = game.custom_headgear
            pp.custom_trail = game.custom_trail
            pp.draw(screen, 0, 0)

        draw_text(
            screen, "CUSTOMIZE", self.f_h2,
            (255, 252, 246) if sel_cust else (220, 230, 242),
            (cx, cy + 4), anchor="midtop", shadow=(8, 8, 24), shadow_offset=2,
        )
        draw_text(
            screen, f"{cloak_info['name']}", self.f_small,
            (242, 168, 255) if sel_cust else (175, 192, 212),
            (cx, cy + 46), anchor="midtop", shadow=None,
        )
        draw_text(
            screen, f"{gear_info['name']} · Trails", self.f_tiny,
            (255, 152, 212) if sel_cust else (140, 160, 180),
            (cx, cy + 68), anchor="midtop", shadow=None,
        )
        pill_cust = pygame.Rect(cx - 64, cy + cr - 16, 128, 30)
        rounded_panel(
            screen, pill_cust,
            (42, 22, 58) if sel_cust else (20, 26, 40), 245,
            (218, 126, 255) if sel_cust else (110, 130, 155), 235 if sel_cust else 110, 15, 2,
        )
        draw_text(
            screen, "STUDIO", self.f_key,
            (255, 246, 255) if sel_cust else (175, 190, 210),
            (pill_cust.centerx - 8, pill_cust.centery), anchor="center", shadow=None,
        )
        self._draw_vector_arrow(
            screen, (pill_cust.centerx + 26, pill_cust.centery), 6.5, "right",
            (232, 146, 255) if sel_cust else (155, 172, 192),
        )

        # Sleek colorful glass footer bar
        foot = pygame.Rect(150, SCREEN_H - 64, SCREEN_W - 300, 44)
        rounded_panel(screen, foot, (14, 18, 36), 210, (124, 156, 214), 95, 22, 1)
        self._coin_icon(screen, (foot.x + 28, foot.centery), 8)
        c_rect = draw_text(
            screen, f"{game.save.get('total_coins', 0):,}", self.f_small,
            UI_COLORS["gold"], (foot.x + 42, foot.centery), anchor="midleft", shadow=None,
        )
        self._gem_icon(screen, (c_rect.right + 22, foot.centery), 8)
        draw_text(
            screen, f"{game.save.get('total_gems', 0):,}", self.f_small,
            (216, 176, 255), (c_rect.right + 36, foot.centery), anchor="midleft", shadow=None,
        )
        draw_text_spaced(
            screen, "A / D  or  MOUSE  CHOOSE     ENTER  OPEN     M  SOUND     F11  FULLSCREEN",
            self.f_label, (214, 226, 245), (foot.right - 26, foot.centery), 2,
            anchor="midright", shadow=None,
        )

    # ------------------------------------------------------------------
    # mode_select — 3 colorful floating circles inside PLAY GAME
    # ------------------------------------------------------------------
    def draw_mode_select(self, screen, game) -> None:
        t = game.time
        self._draw_aurora_backdrop(screen, t, alpha_dim=145)
        self._draw_back_btn(screen, (116, 224, 255))

        draw_text_spaced(
            screen, "CHOOSE YOUR GAME", self.f_h1, (255, 250, 240),
            (SCREEN_W // 2, 28), 5, anchor="midtop", shadow=(8, 10, 24), shadow_offset=3,
        )
        draw_text(
            screen, "pick your adventure  ·  next step: choose Easy, Medium or Hard",
            self.f_body, (214, 226, 246), (SCREEN_W // 2, 90), anchor="midtop", shadow=None,
        )

        unlocked = min(TOTAL_LEVELS, int(game.save.get("unlocked_level", 1)))
        records = game.save.get("level_records", {})
        total_stars = sum(int(v.get("stars", 0)) for v in records.values())
        best_loop = int(game.save.get("best_loop", 0))
        best_dist = int(game.save.get("best_distance_loop", 0))
        best_trial = int(game.save.get("best_trial", 0))

        orbs = [
            {
                "cx": 256,
                "title": "100 LEVELS",
                "sub1": "10 Worlds · Rift Quest",
                "sub2": f"Level {unlocked}/{TOTAL_LEVELS}",
                "stars": total_stars,
                "col_a": (255, 134, 76),
                "col_b": (255, 214, 92),
                "icon": "rift",
            },
            {
                "cx": 640,
                "title": "INFINITE RUN",
                "sub1": "Endless Ascent · 10 Worlds",
                "sub2": f"Best {format_score(best_loop)} · {best_dist:,} m",
                "col_a": (78, 245, 178),
                "col_b": (96, 214, 255),
                "icon": "loop",
            },
            {
                "cx": 1024,
                "title": "TIME TRIAL",
                "sub1": "90s Chrono Score Rush",
                "sub2": f"Best {format_score(best_trial)} PTS",
                "col_a": (106, 214, 255),
                "col_b": (224, 116, 255),
                "icon": "chrono",
            },
        ]

        for i, m in enumerate(orbs):
            sel = i == game.mode_select_index
            ox, oy, orad = self._draw_floating_orb(
                screen, (m["cx"], 392), 114, sel,
                m["col_a"], m["col_b"], t, phase=i * 1.6,
            )
            ey = oy - 40
            if m["icon"] == "rift":
                pygame.draw.circle(screen, m["col_a"], (ox, ey), 26, 3)
                pygame.draw.circle(screen, m["col_b"], (ox, ey), 16, 2)
                for k in range(4):
                    ang = t * 2.3 + k * (math.pi / 2)
                    pygame.draw.circle(
                        screen, m["col_b"],
                        (int(ox + math.cos(ang) * 33), int(ey + math.sin(ang) * 33)), 4,
                    )
            elif m["icon"] == "loop":
                pts = [(ox - 36 + k * 12, ey + math.sin(t * 2.2 + k * 0.85) * 14) for k in range(7)]
                pygame.draw.lines(screen, m["col_a"], False, pts, 3)
                pygame.draw.circle(screen, (255, 214, 96), (ox, ey - 16), 7)
            else:
                pygame.draw.circle(screen, m["col_a"], (ox, ey), 25, 2)
                ha = t * 2.5
                pygame.draw.line(screen, (255, 250, 240), (ox, ey),
                                 (ox + math.cos(ha) * 16, ey + math.sin(ha) * 16), 2)
                pygame.draw.line(screen, m["col_b"], (ox, ey), (ox, ey - 18), 2)

            draw_text(
                screen, m["title"], self.f_h2,
                (255, 252, 244) if sel else (218, 228, 242),
                (ox, oy + 2), anchor="midtop", shadow=(6, 8, 20), shadow_offset=2,
            )
            draw_text(
                screen, m["sub1"], self.f_small,
                m["col_b"] if sel else (168, 184, 204),
                (ox, oy + 42), anchor="midtop", shadow=None,
            )
            if "stars" in m:
                txt = f"{m['sub2']}  ·  "
                tw = self.f_tiny.size(txt)[0]
                sw = self.f_tiny.size(str(m["stars"]))[0]
                sx = ox - (tw + 15 + sw) // 2
                draw_text(screen, txt, self.f_tiny, (255, 220, 128), (sx, oy + 71), anchor="midleft", shadow=None)
                self._star_icon(screen, (sx + tw + 6, oy + 71), 6, True, (255, 214, 92))
                draw_text(screen, str(m["stars"]), self.f_tiny, (255, 220, 128),
                          (sx + tw + 15, oy + 71), anchor="midleft", shadow=None)
            else:
                draw_text(
                    screen, m["sub2"], self.f_tiny,
                    (226, 236, 250) if sel else (142, 158, 180),
                    (ox, oy + 65), anchor="midtop", shadow=None,
                )

            pill = pygame.Rect(ox - 60, oy + orad - 15, 120, 28)
            rounded_panel(
                screen, pill, (24, 30, 50), 245,
                m["col_a"] if sel else (100, 118, 144), 235 if sel else 110, 14, 2,
            )
            draw_text(
                screen, "SELECT", self.f_key,
                (255, 250, 240) if sel else (170, 186, 206),
                (pill.centerx - 8, pill.centery), anchor="center", shadow=None,
            )
            self._draw_vector_arrow(
                screen, (pill.centerx + 25, pill.centery), 6.0, "right",
                m["col_a"] if sel else (150, 168, 190),
            )

        draw_text_spaced(
            screen,
            "A / D  or  MOUSE  CHOOSE GAME     ENTER  NEXT     ESC  BACK",
            self.f_label, (214, 226, 246), (SCREEN_W // 2, SCREEN_H - 42), 2,
            anchor="midtop", shadow=None,
        )

    # ------------------------------------------------------------------
    # difficulty_select — 3 floating difficulty circles (ENTER starts run!)
    # ------------------------------------------------------------------
    def draw_difficulty_select(self, screen, game) -> None:
        t = game.time
        self._draw_aurora_backdrop(screen, t, alpha_dim=152)
        self._draw_back_btn(screen, (255, 198, 88))

        pmode = getattr(game, "pending_mode", "loop")
        if pmode == "levels":
            mode_tag = f"LEVEL {game.selected_level}"
        elif pmode == "trial":
            mode_tag = "TIME TRIAL"
        else:
            mode_tag = "INFINITE RUN"

        draw_text_spaced(
            screen, f"{mode_tag}  ·  DIFFICULTY", self.f_h1, (255, 250, 240),
            (SCREEN_W // 2, 28), 4, anchor="midtop", shadow=(8, 10, 24), shadow_offset=3,
        )
        draw_text(
            screen, "press ENTER or click a circle to start playing right away!",
            self.f_body, (218, 230, 248), (SCREEN_W // 2, 90), anchor="midtop", shadow=None,
        )

        centers_x = [256, 640, 1024]
        for i, dkey in enumerate(DIFFICULTY_MODES):
            dinfo = DIFFICULTIES[dkey]
            sel = i == game.diff_select_index
            col_a = dinfo["color"]
            col_b = dinfo["glow"]
            ox, oy, orad = self._draw_floating_orb(
                screen, (centers_x[i], 396), 122, sel,
                col_a, col_b, t, phase=i * 1.5,
            )

            # Visual hearts & shields row inside top of the difficulty orb
            hy = oy - 58
            hearts = dinfo["hearts"]
            h_step = 21
            hx0 = ox - ((hearts - 1) * h_step) // 2
            for hi in range(hearts):
                draw_heart(screen, (hx0 + hi * h_step, hy), 14, (255, 106, 142), glow=None)

            armor = dinfo["armor"]
            if armor > 0:
                ax0 = ox - ((armor - 1) * 20) // 2
                for ai in range(armor):
                    self._shield_icon(screen, (ax0 + ai * 20, hy + 23), 7.5, True)
            else:
                draw_text(
                    screen, "NO ARMOR SHIELD", self.f_tiny, (255, 148, 162),
                    (ox, hy + 16), anchor="midtop", shadow=None,
                )

            draw_text(
                screen, dinfo["name"], self.f_h2,
                (255, 252, 244) if sel else (222, 232, 244),
                (ox, oy - 8), anchor="midtop", shadow=(6, 8, 20), shadow_offset=2,
            )
            shield_txt = f"{armor} Shield{'s' if armor != 1 else ''}" if armor > 0 else "0 Shields"
            draw_text(
                screen, f"{hearts} Lives  ·  {shield_txt}", self.f_small,
                col_a if sel else (182, 196, 214),
                (ox, oy + 32), anchor="midtop", shadow=None,
            )
            draw_text(
                screen, dinfo["desc"], self.f_tiny,
                (230, 238, 250) if sel else (144, 160, 182),
                (ox, oy + 52), anchor="midtop", shadow=None,
            )

            pill = pygame.Rect(ox - 66, oy + orad - 15, 132, 30)
            rounded_panel(
                screen, pill, (26, 30, 52), 245,
                col_a if sel else (105, 122, 148), 235 if sel else 110, 15, 2,
            )
            draw_text(
                screen, "PLAY NOW", self.f_key,
                (255, 250, 240) if sel else (175, 190, 210),
                (pill.centerx - 8, pill.centery), anchor="center", shadow=None,
            )
            self._draw_vector_arrow(
                screen, (pill.centerx + 32, pill.centery), 6.5, "play",
                col_a if sel else (155, 172, 192),
            )

        draw_text_spaced(
            screen,
            "A / D  or  MOUSE  CHOOSE DIFFICULTY     ENTER  START GAME     ESC  BACK",
            self.f_label, (214, 226, 246), (SCREEN_W // 2, SCREEN_H - 42), 2,
            anchor="midtop", shadow=None,
        )

    # ------------------------------------------------------------------
    # pause / results
    # ------------------------------------------------------------------
    def _dim(self, screen, alpha=150):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((3, 7, 8, alpha))
        screen.blit(overlay, (0, 0))

    def draw_pause(self, screen, game) -> None:
        # Deliberately no HUD behind the pause card: a clean, high-contrast panel.
        self._dim(screen, 205)
        w, h = 570, 452
        rect = pygame.Rect((SCREEN_W - w) // 2, (SCREEN_H - h) // 2, w, h)
        accent = game.palette["accent"]
        rounded_panel(screen, rect, (6, 12, 14), 248, accent, 160, 16, 2)
        draw_text_spaced(screen, "RUN PAUSED", self.f_label, accent,
                         (rect.centerx, rect.y + 24), 4, anchor="midtop", shadow=None)
        draw_text_spaced(screen, "PAUSED", self.f_h1, UI_COLORS["ivory"],
                         (rect.centerx, rect.y + 44), 6, anchor="midtop",
                         shadow=(0, 0, 0), shadow_offset=2)
        draw_text(screen, "the bramble waits", self.f_small, UI_COLORS["muted"],
                  (rect.centerx, rect.y + 108), anchor="midtop", shadow=None)
        if game.mode == "levels":
            mode_name = f"LEVEL {game.level_number}  ({game.difficulty_mode.upper()})"
            metric = format_time(game.elapsed)
        elif game.mode == "loop":
            mode_name = "ENDLESS CLIMB"
            metric = f"{game.distance:,} m"
        else:
            mode_name = "TIME TRIAL"
            metric = format_time(game.time_left)
        draw_text(screen, f"{mode_name}   ·   {metric}   ·   {format_score(game.score)} PTS",
                  self.f_small, UI_COLORS["ivory"], (rect.centerx, rect.y + 132),
                  anchor="midtop", shadow=None)
        pygame.draw.line(screen, (*UI_COLORS["muted"], 60),
                         (rect.x + 58, rect.y + 158), (rect.right - 58, rect.y + 158), 1)
        items = game.pause_items()
        hints = {0: "ESC", 2: "M"}
        for i, label in enumerate(items):
            y = rect.y + 180 + i * 52
            selected = i == game.menu_index
            row = pygame.Rect(rect.x + 58, y, rect.w - 116, 44)
            if selected:
                rounded_panel(screen, row, (16, 30, 30), 235, accent, 165, 8, 1)
                pygame.draw.rect(screen, accent, (row.x, row.y + 8, 3, row.h - 16))
                pygame.draw.polygon(screen, accent,
                                    [(row.x + 16, row.centery - 6),
                                     (row.x + 24, row.centery),
                                     (row.x + 16, row.centery + 6)])
            else:
                rounded_panel(screen, row, (9, 17, 18), 130, None, 0, 8, 0)
            draw_text(screen, label, self.f_menu,
                      UI_COLORS["ivory"] if selected else UI_COLORS["muted"],
                      (rect.centerx, row.centery), anchor="center",
                      shadow=(0, 0, 0), shadow_offset=2)
            if i in hints:
                draw_text(screen, hints[i], self.f_key, UI_COLORS["muted"],
                          (row.right - 14, row.centery), anchor="midright", shadow=None)
        draw_text_spaced(screen, "ESC  RESUME     M  SOUND     F11  FULLSCREEN",
                         self.f_label, UI_COLORS["muted"],
                         (rect.centerx, rect.bottom - 34), 2,
                         anchor="midtop", shadow=None)

    def draw_gameover(self, screen, game) -> None:
        self._dim(screen, 190)
        w, h = 660, 520
        rect = pygame.Rect((SCREEN_W - w) // 2, (SCREEN_H - h) // 2, w, h)
        accent = game.palette["accent"]
        danger = UI_COLORS["danger"]
        rounded_panel(screen, rect, (7, 12, 14), 244, danger if game.end_reason == "death" else accent, 130, 16, 2)

        if game.end_reason == "time":
            heading = "TIME'S UP"
            sub = "the chronometer runs cold in the bramble"
        else:
            heading = "ALL LIVES LOST"
            if game.mode == "levels":
                sub = f"fallen on Level {game.level_number} · the bramble claims your climb"
            else:
                sub = f"all hearts depleted after {game.distance:,} m · the climb ends"

        draw_text_spaced(screen, heading, self.f_h2, UI_COLORS["ivory"],
                         (rect.centerx, rect.y + 24), 4, anchor="midtop",
                         shadow=(0, 0, 0), shadow_offset=2)
        draw_text(screen, sub, self.f_small, UI_COLORS["muted"],
                  (rect.centerx, rect.y + 66), anchor="midtop", shadow=None)

        # Trio Prominent Metric Cards: Time Taken, Coins, Gems
        cw, ch = 180, 80
        cy = rect.y + 104
        cards = [
            ("TIME TAKEN", format_time(game.elapsed), (240, 245, 250)),
            ("COINS", f"{game.coins}", UI_COLORS["gold"]),
            ("GEMS", f"{game.gems}", UI_COLORS["gem"]),
        ]
        for i, (label, val, col) in enumerate(cards):
            card_rect = pygame.Rect(rect.x + 36 + i * (cw + 24), cy, cw, ch)
            rounded_panel(screen, card_rect, (12, 18, 22), 220, col, 80, 8, 1)
            draw_text_spaced(screen, label, self.f_label, UI_COLORS["dim"],
                             (card_rect.centerx, card_rect.y + 12), 2, anchor="midtop", shadow=None)
            draw_text(screen, val, font(FONT_UI_CONDENSED, 32, bold=True), col,
                      (card_rect.centerx, card_rect.y + 36), anchor="midtop",
                      shadow=(0, 0, 0), shadow_offset=2)

        # Contextual summary row
        sy = rect.y + 204
        diff_str = game.difficulty_mode.upper()
        if game.mode == "levels":
            context_str = f"PROGRESS: LEVEL {game.level_number} OF {TOTAL_LEVELS}   ·   MODE: {diff_str}"
        else:
            context_str = f"DISTANCE: {game.distance:,} m   ·   LOOPS: {game.loop_number}   ·   MODE: {diff_str}"
        draw_text(screen, context_str, self.f_small, UI_COLORS["muted"],
                  (rect.centerx, sy), anchor="midtop", shadow=None)

        # Final Score
        draw_text_spaced(screen, "FINAL SCORE", self.f_label, UI_COLORS["dim"],
                         (rect.centerx, sy + 30), 3, anchor="midtop", shadow=None)
        draw_text(screen, format_score(game.final_score), font(FONT_UI_CONDENSED, 46, bold=True),
                  UI_COLORS["gold"], (rect.centerx, sy + 46), anchor="midtop",
                  shadow=(0, 0, 0), shadow_offset=2)

        if game.new_best:
            badge = pygame.Rect(rect.centerx + 120, sy + 58, 92, 22)
            rounded_panel(screen, badge, (40, 32, 10), 210, UI_COLORS["gold"], 200, 4, 1)
            draw_text(screen, "NEW BEST", self.f_tiny, UI_COLORS["gold"],
                      badge.center, anchor="center", shadow=None)

        pygame.draw.line(screen, (*UI_COLORS["muted"], 40),
                         (rect.x + 48, rect.y + 358), (rect.right - 48, rect.y + 358), 1)

        # Action Buttons
        items = game.over_items()
        for i, label in enumerate(items):
            y = rect.y + 376 + i * 42
            selected = i == game.menu_index
            row = pygame.Rect(rect.x + 100, y - 4, rect.w - 200, 36)
            if selected:
                rounded_panel(screen, row, (16, 26, 28), 220, accent, 140, 8, 1)
                pygame.draw.rect(screen, accent, (row.x, row.y + 6, 3, row.h - 12))
            draw_text(screen, label, self.f_menu,
                      UI_COLORS["ivory"] if selected else UI_COLORS["muted"],
                      (rect.centerx, row.centery), anchor="center",
                      shadow=(0, 0, 0), shadow_offset=1)

        draw_text(screen, "ENTER  select      ESC  title", self.f_tiny, UI_COLORS["dim"],
                  (rect.centerx, rect.bottom - 18), anchor="midtop", shadow=None)

    def draw_customize(self, screen, game) -> None:
        t = game.time
        self._draw_aurora_backdrop(screen, t, alpha_dim=155)
        studio_accent = (212, 118, 255)
        self._draw_back_btn(screen, studio_accent)

        draw_text_spaced(
            screen, "HERO CUSTOMIZATION STUDIO", self.f_h1, (255, 250, 244),
            (SCREEN_W // 2, 28), 4, anchor="midtop", shadow=(8, 10, 24), shadow_offset=3,
        )
        draw_text(
            screen, "tailor your cloaks, gear, trails and colors  ·  saved automatically",
            self.f_body, (218, 228, 246), (SCREEN_W // 2, 88), anchor="midtop", shadow=None,
        )

        cloak_info = HERO_CLOAKS[game.custom_cloak % len(HERO_CLOAKS)]
        scarf_info = HERO_SCARFS[game.custom_scarf % len(HERO_SCARFS)]
        stage_glow = scarf_info.get("color", studio_accent)

        # Left Panel: Vibrant Live Running Hero Stage
        prev_w, prev_h = 360, 424
        prev_x, prev_y = 110, 134
        prev_rect = pygame.Rect(prev_x, prev_y, prev_w, prev_h)
        rounded_panel(screen, prev_rect, (16, 20, 40), 240, studio_accent, 185, 16, 2)
        draw_text_spaced(
            screen, "LIVE RUNNER STAGE", self.f_label, (236, 172, 255),
            (prev_rect.centerx, prev_rect.y + 20), 3, anchor="midtop", shadow=None,
        )

        ped_y = prev_rect.bottom - 104
        draw_glow(screen, (prev_rect.centerx, ped_y - 24), 125, stage_glow, 68, 2.1)
        draw_glow(screen, (prev_rect.centerx, ped_y - 24), 85, cloak_info["cloak_light"], 55, 2.0)
        pygame.draw.ellipse(screen, (28, 34, 62), (prev_rect.centerx - 94, ped_y + 10, 188, 28))
        pygame.draw.ellipse(screen, stage_glow, (prev_rect.centerx - 94, ped_y + 10, 188, 28), 2)

        if game.custom_preview_player is not None:
            pp = game.custom_preview_player
            pp.x = prev_rect.centerx - pp.w / 2
            pp.y = ped_y - pp.h + 18
            pp.custom_cloak = game.custom_cloak
            pp.custom_scarf = game.custom_scarf
            pp.custom_headgear = game.custom_headgear
            pp.custom_trail = game.custom_trail
            pp.draw(screen, 0, 0)

        draw_text(
            screen, f"{cloak_info['name']}  ·  {scarf_info['name']}", self.f_small,
            (238, 224, 255), (prev_rect.centerx, prev_rect.bottom - 56), anchor="midtop", shadow=None,
        )
        draw_text(
            screen, "LIVE ANIMATION PREVIEW", self.f_tiny, (152, 168, 198),
            (prev_rect.centerx, prev_rect.bottom - 32), anchor="midtop", shadow=None,
        )

        # Right Panel: Colorful Category Selectors with Circular Vector Arrow Buttons
        opt_w, opt_h = 670, 424
        opt_x, opt_y = 500, 134
        opt_rect = pygame.Rect(opt_x, opt_y, opt_w, opt_h)
        rounded_panel(screen, opt_rect, (14, 18, 36), 236, (124, 148, 204), 115, 16, 1)

        row_accents = [
            (208, 122, 255),
            (255, 124, 176),
            (255, 202, 88),
            (84, 242, 198),
            (108, 224, 255),
        ]
        categories = [
            ("CLOAK STYLE", cloak_info["name"],
             f"{game.custom_cloak % len(HERO_CLOAKS) + 1} / {len(HERO_CLOAKS)} styles"),
            ("SCARF ACCENT", scarf_info["name"],
             f"{game.custom_scarf % len(HERO_SCARFS) + 1} / {len(HERO_SCARFS)} colors"),
            ("HEADGEAR", HERO_HEADGEARS[game.custom_headgear % len(HERO_HEADGEARS)]["name"],
             HERO_HEADGEARS[game.custom_headgear % len(HERO_HEADGEARS)]["desc"]),
            ("RUNNING TRAIL", HERO_TRAILS[game.custom_trail % len(HERO_TRAILS)]["name"],
             HERO_TRAILS[game.custom_trail % len(HERO_TRAILS)]["desc"]),
            ("SAVE & RETURN", "apply customized hero", "back to title menu"),
        ]

        f_val = font(FONT_UI, 22, bold=True)
        row_h = 74
        for i, (cat, val, sub) in enumerate(categories):
            selected = i == game.custom_index
            rcol = row_accents[i]
            row = pygame.Rect(opt_rect.x + 28, opt_rect.y + 24 + i * row_h, opt_rect.w - 56, 60)
            if selected:
                rounded_panel(screen, row, (26, 32, 58), 242, rcol, 220, 12, 2)
                pygame.draw.rect(screen, rcol, (row.x, row.y + 10, 4, row.h - 20), border_radius=2)
            else:
                rounded_panel(screen, row, (18, 22, 42), 185, (92, 110, 148), 75, 12, 1)

            draw_text_spaced(
                screen, cat, self.f_label, rcol if selected else (168, 184, 212),
                (row.x + 20, row.y + 11), 2, shadow=None,
            )
            draw_text(
                screen, sub, self.f_tiny, (198, 212, 236) if selected else (132, 148, 176),
                (row.x + 20, row.y + 34), shadow=None,
            )

            if i < 4:
                left_btn = (row.right - 266, row.centery)
                right_btn = (row.right - 28, row.centery)
                val_cx = (left_btn[0] + right_btn[0]) // 2
                self._draw_arrow_btn(screen, left_btn, 16, "left", rcol, active=selected)
                draw_text(
                    screen, val, f_val,
                    (255, 252, 246) if selected else (206, 218, 238),
                    (val_cx, row.centery), anchor="center",
                    shadow=(6, 8, 20), shadow_offset=1,
                )
                self._draw_arrow_btn(screen, right_btn, 16, "right", rcol, active=selected)
            else:
                pill = pygame.Rect(row.right - 166, row.centery - 16, 146, 32)
                rounded_panel(
                    screen, pill, (28, 44, 68), 240,
                    rcol if selected else (106, 126, 158), 225 if selected else 95, 16, 2 if selected else 1,
                )
                draw_text(
                    screen, "SAVE & BACK", self.f_key,
                    (255, 252, 246) if selected else (188, 204, 226),
                    (pill.centerx - 8, pill.centery), anchor="center", shadow=None,
                )
                self._draw_vector_arrow(
                    screen, (pill.right - 18, pill.centery), 6.5, "play",
                    rcol if selected else (160, 178, 204),
                )

        draw_text_spaced(
            screen,
            "W / S  SELECT ROW     A / D  or  CLICK ARROWS  CHANGE     ENTER / ESC  SAVE & BACK",
            self.f_label, (214, 226, 246), (SCREEN_W // 2, SCREEN_H - 42), 2,
            anchor="midtop", shadow=None,
        )

    def draw_level_select(self, screen, game) -> None:
        t = game.time
        self._draw_aurora_backdrop(screen, t, alpha_dim=158)
        self._draw_back_btn(screen, (255, 152, 88))

        draw_text_spaced(
            screen, "100 LEVELS  ·  SELECT STAGE", self.f_h1, (255, 250, 244),
            (SCREEN_W // 2, 24), 4, anchor="midtop", shadow=(8, 10, 24), shadow_offset=3,
        )

        page = game.level_page
        start_lvl = page * 20 + 1
        end_lvl = min(TOTAL_LEVELS, (page + 1) * 20)
        unlocked = game.save.get("unlocked_level", 1)

        sub = f"PAGE {page + 1} / 5   ·   LEVELS {start_lvl} TO {end_lvl}   ·   UNLOCKED {min(TOTAL_LEVELS, unlocked)} / {TOTAL_LEVELS}"
        draw_text(
            screen, sub, self.f_body, (216, 228, 248),
            (SCREEN_W // 2, 84), anchor="midtop", shadow=None,
        )

        # Big crisp circular vector Page-Turn Arrow Buttons flanking the grid
        self._draw_arrow_btn(screen, (56, 348), 23, "left", (255, 168, 92), active=True)
        self._draw_arrow_btn(screen, (SCREEN_W - 56, 348), 23, "right", (255, 168, 92), active=True)

        grid_w, grid_h = 1040, 440
        grid_x = (SCREEN_W - grid_w) // 2
        grid_y = 128

        cols = 5
        rows = 4
        card_w = 188
        card_h = 92
        gap_x = (grid_w - cols * card_w) // (cols - 1)
        gap_y = (grid_h - rows * card_h) // (rows - 1)

        level_records = game.save.get("level_records", {})

        for idx in range(20):
            lvl_num = page * 20 + idx + 1
            if lvl_num > TOTAL_LEVELS:
                break
            c = idx % cols
            r = idx // cols
            cx = grid_x + c * (card_w + gap_x)
            cy = grid_y + r * (card_h + gap_y)
            rect = pygame.Rect(cx, cy, card_w, card_h)

            is_unlocked = lvl_num <= unlocked
            selected = lvl_num == game.selected_level

            biome_idx = level_biome_index(lvl_num)
            biome_pal = BIOMES[biome_idx]
            tile_accent = biome_pal["accent"] if is_unlocked else (92, 106, 134)

            if selected:
                rounded_panel(screen, rect, (26, 34, 58), 246, tile_accent, 235, 12, 2)
                pygame.draw.rect(screen, tile_accent, (rect.x, rect.y + 8, 4, rect.h - 16), border_radius=2)
            else:
                rounded_panel(
                    screen, rect, (16, 22, 40) if is_unlocked else (12, 16, 28),
                    205 if is_unlocked else 155,
                    tile_accent if is_unlocked else (54, 66, 88),
                    135 if is_unlocked else 55, 12, 1,
                )

            if is_unlocked:
                draw_text(
                    screen, f"{lvl_num:02d}", self.f_h2,
                    (255, 252, 244) if selected else (218, 228, 244),
                    (rect.x + 16, rect.y + 10), shadow=(6, 8, 20), shadow_offset=1,
                )
                draw_text(
                    screen, biome_pal["name"].split()[0], self.f_tiny,
                    biome_pal["accent"], (rect.right - 14, rect.y + 14), anchor="topright", shadow=None,
                )

                rec = level_records.get(str(lvl_num), {})
                stars = rec.get("stars", 0)
                for si in range(3):
                    self._star_icon(screen, (rect.x + 23 + si * 20, rect.bottom - 20), 7, si < stars)

                best_t = rec.get("time", 0.0)
                if best_t > 0:
                    draw_text(
                        screen, format_time(best_t), self.f_tiny, (186, 202, 226),
                        (rect.right - 14, rect.bottom - 13), anchor="bottomright", shadow=None,
                    )
            else:
                draw_text(
                    screen, f"{lvl_num:02d}", self.f_h2, (98, 114, 142),
                    (rect.x + 16, rect.y + 10), shadow=None,
                )
                self._lock_icon(screen, (rect.x + 22, rect.bottom - 19), 6, (108, 124, 152))
                draw_text(
                    screen, "LOCKED", self.f_tiny, (108, 124, 152),
                    (rect.x + 34, rect.bottom - 19), anchor="midleft", shadow=None,
                )

        draw_text_spaced(
            screen,
            "ARROWS  SELECT LEVEL     A / D  or  SIDE ARROWS  PAGE     ENTER  CHOOSE DIFFICULTY     ESC  BACK",
            self.f_label, (214, 226, 246), (SCREEN_W // 2, SCREEN_H - 42), 2,
            anchor="midtop", shadow=None,
        )

    def draw_level_complete(self, screen, game) -> None:
        self._dim(screen, 205)
        w, h = 640, 520
        rect = pygame.Rect((SCREEN_W - w) // 2, (SCREEN_H - h) // 2, w, h)
        accent = game.palette["accent"]
        rounded_panel(screen, rect, (6, 12, 16), 245, accent, 160, 16, 2)

        draw_text_spaced(screen, f"LEVEL {game.level_number} CLEARED!", self.f_h2, UI_COLORS["ivory"],
                         (rect.centerx, rect.y + 26), 4, anchor="midtop",
                         shadow=(0, 0, 0), shadow_offset=2)
        draw_text(screen, "RIFT GATEWAY ACTIVATED · REALM CONQUERED", self.f_small, UI_COLORS["muted"],
                  (rect.centerx, rect.y + 68), anchor="midtop", shadow=None)

        stars = game.level_stars
        for si in range(3):
            self._star_icon(screen, (rect.centerx + (si - 1) * 52, rect.y + 118), 16, si < stars)

        cw, ch = 176, 76
        cy = rect.y + 160
        cards = [
            ("TIME TAKEN", format_time(game.elapsed), accent),
            ("COINS", f"+{game.coins}", UI_COLORS["gold"]),
            ("GEMS", f"+{game.gems}", UI_COLORS["gem"]),
        ]
        for i, (label, val, col) in enumerate(cards):
            card_rect = pygame.Rect(rect.x + 36 + i * (cw + 24), cy, cw, ch)
            rounded_panel(screen, card_rect, (12, 20, 24), 220, col, 80, 8, 1)
            draw_text_spaced(screen, label, self.f_label, UI_COLORS["dim"],
                             (card_rect.centerx, card_rect.y + 10), 2, anchor="midtop", shadow=None)
            draw_text(screen, val, font(FONT_UI_CONDENSED, 28, bold=True), col,
                      (card_rect.centerx, card_rect.y + 32), anchor="midtop",
                      shadow=(0, 0, 0), shadow_offset=1)

        next_biome_idx = level_biome_index(min(TOTAL_LEVELS, game.level_number + 1))
        draw_text(screen, f"LEVEL SCORE: {format_score(game.score)} PTS   ·   NEXT REALM: {BIOMES[next_biome_idx]['name']}",
                  self.f_small, UI_COLORS["ivory"], (rect.centerx, rect.y + 258),
                  anchor="midtop", shadow=None)

        pygame.draw.line(screen, (*UI_COLORS["muted"], 50),
                         (rect.x + 48, rect.y + 288), (rect.right - 48, rect.y + 288), 1)

        items = ["NEXT LEVEL", "RETRY LEVEL", "LEVEL SELECT", "MAIN MENU"]
        for i, label in enumerate(items):
            y = rect.y + 308 + i * 46
            selected = i == game.menu_index
            row = pygame.Rect(rect.x + 90, y, rect.w - 180, 38)
            if selected:
                rounded_panel(screen, row, (16, 28, 30), 220, accent, 150, 8, 1)
                pygame.draw.rect(screen, accent, (row.x, row.y + 6, 3, row.h - 12))
            draw_text(screen, label, self.f_menu,
                      UI_COLORS["ivory"] if selected else UI_COLORS["muted"],
                      (rect.centerx, row.centery), anchor="center",
                      shadow=(0, 0, 0), shadow_offset=1)

        draw_text(screen, "ENTER  select      ESC  level select", self.f_tiny, UI_COLORS["dim"],
                  (rect.centerx, rect.bottom - 18), anchor="midtop", shadow=None)

    def draw_dying(self, screen, game) -> None:
        a = clamp(game.death_timer / 1.25, 0.0, 1.0)
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((10, 2, 4, int(120 * a)))
        screen.blit(overlay, (0, 0))
        if a > 0.25:
            msg = "TIME'S UP" if game.end_reason == "time" else "THE BRAMBLE TAKES YOU"
            self._faded_text(screen, msg, self.f_h2, UI_COLORS["ivory"],
                             (SCREEN_W // 2, SCREEN_H // 2 - 20),
                             int(220 * clamp((a - 0.25) / 0.5, 0, 1)), "center")

    # ------------------------------------------------------------------
    # icons
    # ------------------------------------------------------------------
    def _shield_icon(self, screen, center, r, filled):
        cx, cy = center
        pts = [(cx, cy - r * 1.5), (cx + r * 1.15, cy - r * 0.7),
               (cx + r * 0.95, cy + r * 0.45), (cx, cy + r * 1.45),
               (cx - r * 0.95, cy + r * 0.45), (cx - r * 1.15, cy - r * 0.7)]
        if filled:
            draw_glow(screen, center, int(r * 1.8), (128, 238, 255), 45, 2.0)
            pygame.draw.polygon(screen, (38, 104, 124), pts)
            pygame.draw.polygon(screen, (140, 240, 255), pts, 1)
            pygame.draw.polygon(screen, (96, 196, 220),
                                [(cx, cy - r * 1.2), (cx + r * 0.6, cy - r * 0.55),
                                 (cx, cy + r * 0.9), (cx - r * 0.6, cy - r * 0.55)])
        else:
            pygame.draw.polygon(screen, (32, 42, 44), pts)
            pygame.draw.polygon(screen, (52, 66, 68), pts, 1)

    def _coin_icon(self, screen, center, r):
        cx, cy = center
        draw_glow(screen, center, r * 2, (255, 198, 96), 50, 2.0)
        pygame.draw.circle(screen, (255, 205, 104), (int(cx), int(cy)), int(r))
        pygame.draw.circle(screen, (196, 136, 52), (int(cx), int(cy)), int(r), 2)
        pygame.draw.circle(screen, (255, 244, 200), (int(cx - r * 0.3), int(cy - r * 0.3)),
                           max(1, int(r * 0.28)))

    def _gem_icon(self, screen, center, r):
        cx, cy = center
        draw_glow(screen, center, r * 2, (170, 132, 255), 50, 2.0)
        pts = [(cx, cy - r * 1.5), (cx + r, cy - r * 0.2), (cx, cy + r * 1.2),
               (cx - r, cy - r * 0.2)]
        pygame.draw.polygon(screen, (160, 124, 255), pts)
        pygame.draw.polygon(screen, (216, 196, 255),
                            [(cx, cy - r * 1.5), (cx + r * 0.5, cy - r * 0.2),
                             (cx, cy + r * 0.5)])
        pygame.draw.polygon(screen, (236, 226, 255), pts, 1)

    def _chrono_icon(self, screen, center, r):
        cx, cy = center
        draw_glow(screen, center, r * 2, (120, 240, 255), 45, 2.0)
        pygame.draw.circle(screen, (90, 190, 214), (int(cx), int(cy)), int(r))
        pygame.draw.circle(screen, (214, 255, 255), (int(cx), int(cy)), int(r), 1)
        pygame.draw.line(screen, (240, 255, 255), (cx, cy), (cx, cy - r * 0.7), 1)
        pygame.draw.line(screen, (240, 255, 255), (cx, cy), (cx + r * 0.55, cy), 1)

    def _star_icon(self, screen, center, r: float, filled: bool, color=None) -> None:
        cx, cy = center
        pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * (math.pi / 5)
            rad = r if k % 2 == 0 else r * 0.42
            pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad))
        if filled:
            col = color or UI_COLORS["gold"]
            draw_glow(screen, (int(cx), int(cy)), max(8, int(r * 2.1)), col, 52, 2.0)
            pygame.draw.polygon(screen, col, pts)
            pygame.draw.polygon(screen, (255, 244, 204), pts, 1)
        else:
            pygame.draw.polygon(screen, (24, 34, 38), pts)
            pygame.draw.polygon(screen, (68, 84, 90), pts, 1)

    def _lock_icon(self, screen, center, r: float, color=None) -> None:
        cx, cy = center
        col = color or UI_COLORS["dim"]
        pygame.draw.circle(screen, col, (int(cx), int(cy - r * 0.38)), max(3, int(r * 0.58)), 2)
        body = pygame.Rect(int(cx - r * 0.8), int(cy - r * 0.18), max(8, int(r * 1.6)), max(6, int(r * 1.2)))
        pygame.draw.rect(screen, (18, 26, 30), body, border_radius=2)
        pygame.draw.rect(screen, col, body, 1, border_radius=2)
        pygame.draw.circle(screen, col, body.center, 1)

    def _chevron(self, screen, center, size: float, direction: int, color) -> None:
        cx, cy = center
        if direction >= 0:
            pts = [(cx - size * 0.45, cy - size * 0.85),
                   (cx + size * 0.55, cy),
                   (cx - size * 0.45, cy + size * 0.85)]
        else:
            pts = [(cx + size * 0.45, cy - size * 0.85),
                   (cx - size * 0.55, cy),
                   (cx + size * 0.45, cy + size * 0.85)]
        pygame.draw.polygon(screen, color, pts)

    # ------------------------------------------------------------------
    def draw_loading(self, screen, value="GROWING THE BRAMBLE") -> None:
        screen.fill((5, 9, 11))
        draw_text_spaced(screen, TITLE, font(FONT_TITLE, 74, bold=True),
                         UI_COLORS["ivory"], (SCREEN_W // 2, SCREEN_H // 2 - 40), 8,
                         anchor="midbottom", shadow=(0, 0, 0), shadow_offset=2)
        draw_text(screen, value, self.f_small, UI_COLORS["muted"],
                  (SCREEN_W // 2, SCREEN_H // 2), anchor="midtop", shadow=None)
