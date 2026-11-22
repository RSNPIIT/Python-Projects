"""
hud.py - In-Game Heads-Up Display (Score, Score Pop Animation, Status Indicators & Biome Transition Banners).
"""

import math
import pygame
from ..config import SCREEN_WIDTH, SCREEN_HEIGHT


class HUD:
    """Manages active gameplay telemetry, large arcade score counter, and indicators."""

    def __init__(self):
        pygame.font.init()
        # Large arcade score font
        self.font_score = pygame.font.SysFont("Impact, Arial Black, Helvetica", 68)
        self.font_hud = pygame.font.SysFont("Helvetica, Arial", 15, bold=True)
        self.font_banner_title = pygame.font.SysFont("Impact, Arial Black, Helvetica", 32)
        self.font_banner_sub = pygame.font.SysFont("Helvetica, Arial", 16, bold=True)
        self.font_pause = pygame.font.SysFont("Impact, Arial Black, Helvetica", 56)

        # Score bounce animation
        self.pop_scale = 1.0

        # Biome Shift Notification Banner
        self.banner_timer = 0.0
        self.banner_duration = 3.2
        self.banner_title = ""
        self.banner_accent = (255, 215, 60)

    def trigger_score_pop(self):
        self.pop_scale = 1.35

    def trigger_biome_banner(self, title: str, accent: tuple = (255, 215, 60)):
        self.banner_title = title
        self.banner_accent = accent
        self.banner_timer = self.banner_duration

    def update(self, dt: float):
        if self.pop_scale > 1.0:
            self.pop_scale = max(1.0, self.pop_scale - 2.2 * dt)

        if self.banner_timer > 0:
            self.banner_timer = max(0.0, self.banner_timer - dt)

    def draw_score(self, surface: pygame.Surface, score: int):
        """Draws large centered arcade score with heavy dark outline."""
        text = str(score)
        base_surf = self.font_score.render(text, True, (255, 255, 255))

        if self.pop_scale > 1.01:
            w = int(base_surf.get_width() * self.pop_scale)
            h = int(base_surf.get_height() * self.pop_scale)
            render_surf = pygame.transform.smoothscale(base_surf, (w, h))
        else:
            render_surf = base_surf

        cx = SCREEN_WIDTH // 2
        cy = 55
        rect = render_surf.get_rect(center=(cx, cy))

        # Thick drop-shadow outline
        for dx, dy in [(-3, -3), (-3, 3), (3, -3), (3, 3), (0, 4), (-4, 0), (4, 0), (0, -4)]:
            shadow_surf = self.font_score.render(text, True, (20, 20, 25))
            if self.pop_scale > 1.01:
                shadow_surf = pygame.transform.smoothscale(shadow_surf, (rect.width, rect.height))
            surface.blit(shadow_surf, (rect.x + dx, rect.y + dy))

        surface.blit(render_surf, rect)

    def draw_status_badges(self, surface: pygame.Surface, diff_name: str, skin_name: str, biome_name: str, muted: bool):
        """Draws telemetry header badges for active difficulty, skin, current biome, and sound state."""
        # Top Left: Mode & Skin
        mode_text = f"DIFFICULTY: {diff_name.upper()}  |  SKIN: {skin_name.upper()}"
        mode_surf = self.font_hud.render(mode_text, True, (255, 255, 255))
        pill = pygame.Surface((mode_surf.get_width() + 18, mode_surf.get_height() + 8), pygame.SRCALPHA)
        pill.fill((10, 15, 25, 170))
        surface.blit(pill, (18, 14))
        surface.blit(mode_surf, (27, 18))

        # Biome / Sector Indicator
        b_text = f"SECTOR: {biome_name.upper()}"
        b_surf = self.font_hud.render(b_text, True, (255, 235, 120))
        pill_b = pygame.Surface((b_surf.get_width() + 18, b_surf.get_height() + 8), pygame.SRCALPHA)
        pill_b.fill((10, 15, 25, 170))
        surface.blit(pill_b, (18, 44))
        surface.blit(b_surf, (27, 48))

        # Top Right: Audio State
        sfx_text = "SFX: OFF (M)" if muted else "SFX: ON (M)"
        sfx_col = (255, 100, 100) if muted else (120, 240, 140)
        sfx_surf = self.font_hud.render(sfx_text, True, sfx_col)
        pill_r = pygame.Surface((sfx_surf.get_width() + 18, sfx_surf.get_height() + 8), pygame.SRCALPHA)
        pill_r.fill((10, 15, 25, 170))
        rx = SCREEN_WIDTH - sfx_surf.get_width() - 36
        surface.blit(pill_r, (rx, 14))
        surface.blit(sfx_surf, (rx + 9, 18))

    def draw_biome_transition_banner(self, surface: pygame.Surface):
        """Draws animated cinematic milestone banner when transitioning sectors."""
        if self.banner_timer <= 0:
            return

        cx = SCREEN_WIDTH // 2
        cy = 135

        # Alpha fade in / out
        progress = self.banner_timer / self.banner_duration
        if progress > 0.8:
            alpha = (1.0 - progress) / 0.2
        elif progress < 0.2:
            alpha = progress / 0.2
        else:
            alpha = 1.0

        int_alpha = max(0, min(255, int(alpha * 240)))
        banner_w = 680
        banner_h = 60
        bx = cx - banner_w // 2
        by = cy - banner_h // 2

        # Card surface
        card = pygame.Surface((banner_w, banner_h), pygame.SRCALPHA)
        card.fill((10, 15, 28, int_alpha))
        surface.blit(card, (bx, by))

        # Border
        b_col = (*self.banner_accent[:3], int_alpha)
        border_surf = pygame.Surface((banner_w, banner_h), pygame.SRCALPHA)
        pygame.draw.rect(border_surf, b_col, (0, 0, banner_w, banner_h), 3, border_radius=8)
        surface.blit(border_surf, (bx, by))

        # Text
        txt_surf = self.font_banner_title.render(self.banner_title, True, self.banner_accent)
        t_alpha = pygame.Surface(txt_surf.get_size(), pygame.SRCALPHA)
        t_alpha.blit(txt_surf, (0, 0))
        t_alpha.set_alpha(int_alpha)
        surface.blit(t_alpha, (cx - txt_surf.get_width() // 2, cy - txt_surf.get_height() // 2))

    def draw_pause_overlay(self, surface: pygame.Surface):
        """Draws dark semi-transparent veil and PAUSED banner."""
        veil = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        veil.fill((10, 15, 25, 175))
        surface.blit(veil, (0, 0))

        p_surf = self.font_pause.render("MATCH PAUSED", True, (255, 215, 0))
        p_rect = p_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
            sh = self.font_pause.render("MATCH PAUSED", True, (20, 20, 25))
            surface.blit(sh, (p_rect.x + dx, p_rect.y + dy))
        surface.blit(p_surf, p_rect)

        sub_surf = self.font_hud.render("PRESS P OR ESC TO RESUME  |  R TO RESTART", True, (230, 240, 255))
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        surface.blit(sub_surf, sub_rect)
