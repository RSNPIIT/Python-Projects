"""
hud.py - In-Game Heads-Up Display (Score, Score Pop Animation, Status Indicators).
"""

import pygame
from ..config import SCREEN_WIDTH, SCREEN_HEIGHT


class HUD:
    """Manages active gameplay telemetry, large arcade score counter, and indicators."""

    def __init__(self):
        pygame.font.init()
        # Large arcade score font
        self.font_score = pygame.font.SysFont("Impact, Arial Black, Helvetica", 68)
        self.font_hud = pygame.font.SysFont("Helvetica, Arial", 16, bold=True)
        self.font_pause = pygame.font.SysFont("Impact, Arial Black, Helvetica", 56)

        # Score bounce animation
        self.pop_scale = 1.0

    def trigger_score_pop(self):
        self.pop_scale = 1.35

    def update(self, dt: float):
        if self.pop_scale > 1.0:
            self.pop_scale = max(1.0, self.pop_scale - 2.2 * dt)

    def draw_score(self, surface: pygame.Surface, score: int):
        """Draws large centered arcade score with heavy dark outline."""
        text = str(score)
        # Render text
        base_surf = self.font_score.render(text, True, (255, 255, 255))

        # Apply pop scale if active
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

    def draw_status_badges(self, surface: pygame.Surface, diff_name: str, skin_name: str, muted: bool):
        """Draws subtle header badges for active difficulty, skin, and sound state."""
        # Top Left: Mode & Skin
        mode_text = f"DIFFICULTY: {diff_name.upper()}  |  SKIN: {skin_name.upper()}"
        mode_surf = self.font_hud.render(mode_text, True, (255, 255, 255))
        # Semi-transparent pill
        pill = pygame.Surface((mode_surf.get_width() + 18, mode_surf.get_height() + 8), pygame.SRCALPHA)
        pill.fill((10, 15, 25, 150))
        surface.blit(pill, (18, 14))
        surface.blit(mode_surf, (27, 18))

        # Top Right: Audio State
        sfx_text = "SFX: OFF (M)" if muted else "SFX: ON (M)"
        sfx_col = (255, 100, 100) if muted else (120, 240, 140)
        sfx_surf = self.font_hud.render(sfx_text, True, sfx_col)
        pill_r = pygame.Surface((sfx_surf.get_width() + 18, sfx_surf.get_height() + 8), pygame.SRCALPHA)
        pill_r.fill((10, 15, 25, 150))
        rx = SCREEN_WIDTH - sfx_surf.get_width() - 36
        surface.blit(pill_r, (rx, 14))
        surface.blit(sfx_surf, (rx + 9, 18))

    def draw_pause_overlay(self, surface: pygame.Surface):
        """Draws dark semi-transparent veil and PAUSED banner."""
        veil = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        veil.fill((10, 15, 25, 175))
        surface.blit(veil, (0, 0))

        # Title
        p_surf = self.font_pause.render("MATCH PAUSED", True, (255, 215, 0))
        # Outline
        p_rect = p_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
            sh = self.font_pause.render("MATCH PAUSED", True, (20, 20, 25))
            surface.blit(sh, (p_rect.x + dx, p_rect.y + dy))
        surface.blit(p_surf, p_rect)

        # Prompt
        sub_surf = self.font_hud.render("PRESS P OR ESC TO RESUME  |  R TO RESTART", True, (230, 240, 255))
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        surface.blit(sub_surf, sub_rect)
