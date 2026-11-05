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
)
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
        draw_text(screen, "ARMOR", self.f_tiny, UI_COLORS["dim"], (196, 29), shadow=None)
        for i in range(MAX_ARMOR):
            self._shield_icon(screen, (202 + i * 22, 53), 9, i < player.armor)
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
    # title
    # ------------------------------------------------------------------
    def draw_title(self, screen, game) -> None:
        screen.blit(self._left_shade, (0, 0))
        t = game.time
        pal = BIOMES[0]
        # logo
        glow_alpha = int(30 + 14 * math.sin(t * 1.2))
        draw_glow(screen, (360, 205), 250, pal["accent"], glow_alpha, 2.4)
        x = 92
        y = 138
        thorn = draw_text_spaced(screen, "THORN", self.f_title, UI_COLORS["ivory"], (x, y),
                                 6, shadow=(2, 9, 10), shadow_offset=3)
        draw_text_spaced(screen, "SPIRE", self.f_title, pal["accent"],
                         (x + thorn.w + 8, y), 6, shadow=(2, 9, 10), shadow_offset=3)
        pygame.draw.line(screen, (*pal["accent"], 110),
                         (x + 4, y + 125), (x + 560, y + 125), 1)
        draw_text_spaced(screen, "CLIMB THE BRAMBLE · OUTRUN THE DARK",
                         self.f_title_sub, UI_COLORS["muted"], (x + 6, y + 138), 3)
        # small thorn ornament
        for i, ox in enumerate((525, 545, 565)):
            pygame.draw.lines(screen, pal["moss"], False,
                              [(x + ox, y + 125), (x + ox + 8, y + 112),
                               (x + ox + 16, y + 125)], 1)

        # menu
        menu_x = 96
        menu_y = 360
        row_h = 84
        draw_text_spaced(screen, "CHOOSE YOUR CLIMB", self.f_label, pal["accent"],
                         (menu_x - 10, menu_y - 34), 4, shadow=None)
        options = game.title_options
        for i, (title, sub) in enumerate(options):
            selected = i == game.title_index
            row = pygame.Rect(menu_x - 14, menu_y + i * row_h - 8, 600, 70)
            rounded_panel(screen, row, (6, 13, 14), 225 if selected else 160,
                          pal["accent"] if selected else UI_COLORS["dim"],
                          175 if selected else 70, 10, 1 if not selected else 2)
            if selected:
                pygame.draw.rect(screen, pal["accent"],
                                 (row.x, row.y + 8, 4, row.h - 16), border_radius=2)
                pygame.draw.polygon(screen, pal["accent"],
                                    [(row.x + 19, row.centery - 8),
                                     (row.x + 28, row.centery),
                                     (row.x + 19, row.centery + 8)])
            draw_text(screen, f"0{i + 1}", self.f_menu_num,
                      pal["accent"] if selected else UI_COLORS["dim"],
                      (row.x + 48, row.centery), anchor="midleft", shadow=None)
            draw_text(screen, title, self.f_menu,
                      UI_COLORS["ivory"] if selected else UI_COLORS["muted"],
                      (row.x + 84, row.y + 10), shadow=(0, 0, 0), shadow_offset=2)
            draw_text(screen, sub, self.f_menu_small,
                      UI_COLORS["muted"] if selected else UI_COLORS["dim"],
                      (row.x + 86, row.y + 45), shadow=None)
            best = game.save.get("best_loop" if i == 0 else "best_trial", 0)
            if best:
                draw_text(screen, format_score(best), self.f_menu_num,
                          UI_COLORS["gold"] if selected else UI_COLORS["dim"],
                          (row.right - 20, row.y + 20), anchor="midright", shadow=None)
                draw_text(screen, "BEST", self.f_tiny, UI_COLORS["dim"],
                          (row.right - 20, row.y + 40), anchor="midright", shadow=None)

        # field notes / controls
        px = SCREEN_W - 356
        py = 338
        panel = pygame.Rect(px, py, 312, 292)
        rounded_panel(screen, panel, UI_COLORS["panel"], 210, UI_COLORS["muted"], 85, 12, 1)
        draw_text_spaced(screen, "FIELD NOTES", self.f_label, pal["accent"],
                         (px + 22, py + 18), 3, shadow=None)
        rows = [
            ("A D", "move  ·  arrows too"),
            ("SPACE", "jump · hold for height"),
            ("W S", "climb vines"),
            ("SHIFT", "dash"),
            ("P / ESC", "pause"),
            ("M", "sound"),
        ]
        for i, (key, desc) in enumerate(rows):
            yy = py + 46 + i * 32
            kw = self._keycap(screen, px + 22, yy, key)
            draw_text(screen, desc, self.f_small, UI_COLORS["muted"],
                      (px + 22 + kw + 14, yy + 4), shadow=None)
        pygame.draw.line(screen, (*UI_COLORS["muted"], 44),
                         (px + 22, py + 246), (px + 290, py + 246), 1)
        draw_text(screen, "pygame · moderngl · numpy", self.f_tiny, UI_COLORS["dim"],
                  (px + 22, py + 260), shadow=None)

        # footer
        draw_text(screen, "UP / DOWN", self.f_small, UI_COLORS["muted"],
                  (96, SCREEN_H - 55), shadow=None)
        draw_text(screen, "SELECT", self.f_small, UI_COLORS["ivory"],
                  (210, SCREEN_H - 55), shadow=None)
        draw_text(screen, "ENTER", self.f_small, UI_COLORS["muted"],
                  (320, SCREEN_H - 55), shadow=None)
        draw_text(screen, "BEGIN", self.f_small, UI_COLORS["ivory"],
                  (390, SCREEN_H - 55), shadow=None)
        draw_text(screen, "F11   FULLSCREEN", self.f_small, UI_COLORS["muted"],
                  (510, SCREEN_H - 55), shadow=None)
        draw_text(screen, "M   SOUND", self.f_small, UI_COLORS["muted"],
                  (690, SCREEN_H - 55), shadow=None)
        draw_text(screen, f"TOTAL COINS {game.save.get('total_coins', 0):,}   ·   "
                          f"GEMS {game.save.get('total_gems', 0):,}",
                  self.f_tiny, UI_COLORS["dim"], (96, SCREEN_H - 30), shadow=None)
        draw_text(screen, "v1.0", self.f_tiny, UI_COLORS["dim"],
                  (SCREEN_W - 40, SCREEN_H - 30), anchor="topright", shadow=None)

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
        mode_name = "ENDLESS LOOP" if game.mode == "loop" else "TIME TRIAL"
        metric = (f"{game.distance:,} m" if game.mode == "loop"
                  else format_time(game.time_left))
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
        self._dim(screen, 175)
        w, h = 640, 500
        rect = pygame.Rect((SCREEN_W - w) // 2, (SCREEN_H - h) // 2, w, h)
        accent = game.palette["accent"]
        rounded_panel(screen, rect, (7, 12, 14), 238, accent, 100, 16, 1)
        if game.end_reason == "time":
            heading = "TIME'S UP"
            sub = "the bramble keeps its secrets"
        else:
            heading = "THE BRAMBLE REMEMBERS"
            sub = "another climb ends in the dark"
        draw_text_spaced(screen, heading, self.f_h2, UI_COLORS["ivory"],
                         (rect.centerx, rect.y + 28), 4, anchor="midtop",
                         shadow=(0, 0, 0), shadow_offset=2)
        draw_text(screen, sub, self.f_small, UI_COLORS["muted"],
                  (rect.centerx, rect.y + 74), anchor="midtop", shadow=None)
        draw_text_spaced(screen, "FINAL SCORE", self.f_label, UI_COLORS["dim"],
                         (rect.centerx, rect.y + 108), 4, anchor="midtop", shadow=None)
        draw_text(screen, format_score(game.final_score), font(FONT_UI_CONDENSED, 62, bold=True),
                  UI_COLORS["gold"], (rect.centerx, rect.y + 124), anchor="midtop",
                  shadow=(0, 0, 0), shadow_offset=3)
        if game.new_best:
            badge = pygame.Rect(rect.centerx + 96, rect.y + 138, 106, 26)
            rounded_panel(screen, badge, (40, 32, 10), 210, UI_COLORS["gold"], 200, 5, 1)
            draw_text(screen, "NEW BEST", self.f_tiny, UI_COLORS["gold"],
                      badge.center, anchor="center", shadow=None)
        # stats
        sx = rect.x + 70
        sy = rect.y + 218
        rows = [
            ("DISTANCE", f"{game.distance:,} m"),
            ("COINS", f"{game.coins}"),
            ("GEMS", f"{game.gems}"),
        ]
        if game.mode == "trial":
            rows.append(("CHRONO SHARDS", str(game.chronos)))
        else:
            rows.append(("LOOPS", str(game.loop_number)))
        rows.append(("BEST " + game.mode.upper(), format_score(game.best_for_mode())))
        for i, (label, value) in enumerate(rows):
            yy = sy + i * 30
            draw_text_spaced(screen, label, self.f_label, UI_COLORS["dim"],
                             (sx, yy + 3), 2, shadow=None)
            draw_text(screen, value, self.f_small, UI_COLORS["ivory"], (rect.right - 70, yy),
                      anchor="topright", shadow=None)
            pygame.draw.line(screen, (*UI_COLORS["muted"], 26),
                             (sx, yy + 24), (rect.right - 70, yy + 24), 1)
        items = game.over_items()
        for i, label in enumerate(items):
            y = rect.y + 392 + i * 42
            selected = i == game.menu_index
            row = pygame.Rect(rect.x + 110, y - 6, rect.w - 220, 36)
            if selected:
                rounded_panel(screen, row, (14, 26, 26), 200, accent, 130, 8, 1)
            draw_text(screen, label, self.f_menu,
                      UI_COLORS["ivory"] if selected else UI_COLORS["muted"],
                      (rect.centerx, y + 10), anchor="midtop",
                      shadow=(0, 0, 0), shadow_offset=1)
        draw_text(screen, "ENTER  select      ESC  title", self.f_tiny, UI_COLORS["dim"],
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

    # ------------------------------------------------------------------
    def draw_loading(self, screen, value="GROWING THE BRAMBLE") -> None:
        screen.fill((5, 9, 11))
        draw_text_spaced(screen, TITLE, font(FONT_TITLE, 74, bold=True),
                         UI_COLORS["ivory"], (SCREEN_W // 2, SCREEN_H // 2 - 40), 8,
                         anchor="midbottom", shadow=(0, 0, 0), shadow_offset=2)
        draw_text(screen, value, self.f_small, UI_COLORS["muted"],
                  (SCREEN_W // 2, SCREEN_H // 2), anchor="midtop", shadow=None)
