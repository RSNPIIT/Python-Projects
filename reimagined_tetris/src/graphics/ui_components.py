"""
ui_components.py - Glassmorphic Panels, Gauges, Next Queue Cards & Buttons.
"""

import pygame
from config import (
    COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_PANEL_BORDER_GLOW,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED, COLOR_ACCENT_CYAN, COLOR_ACCENT_GOLD
)


def draw_glass_panel(surface, rect, border_color=COLOR_PANEL_BORDER, bg_color=COLOR_PANEL_BG, corner_radius=12, glow=False):
    x, y, w, h = rect
    panel_surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # Base translucent body
    pygame.draw.rect(panel_surf, bg_color, (0, 0, w, h), border_radius=corner_radius)

    # Subtle inner gradient shine on top half
    shine_surf = pygame.Surface((w, h // 2), pygame.SRCALPHA)
    pygame.draw.rect(shine_surf, (255, 255, 255, 12), (0, 0, w, h // 2), border_top_left_radius=corner_radius, border_top_right_radius=corner_radius)
    panel_surf.blit(shine_surf, (0, 0))

    # Outer border
    pygame.draw.rect(panel_surf, border_color, (0, 0, w, h), width=2, border_radius=corner_radius)

    if glow:
        glow_surf = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*border_color[:3], 35), (0, 0, w + 8, h + 8), width=3, border_radius=corner_radius + 2)
        surface.blit(glow_surf, (x - 4, y - 4), special_flags=pygame.BLEND_ADD)

    surface.blit(panel_surf, (x, y))


def draw_meter_bar(surface, x, y, width, height, progress, fill_color=COLOR_ACCENT_CYAN, bg_color=(20, 28, 40)):
    # Background rail
    rail_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, bg_color, rail_rect, border_radius=height // 2)

    # Filled progress
    fill_w = int(max(0.0, min(1.0, progress)) * width)
    if fill_w > 0:
        fill_rect = pygame.Rect(x, y, fill_w, height)
        pygame.draw.rect(surface, fill_color, fill_rect, border_radius=height // 2)


class UIButton:
    def __init__(self, rect, text, command=None, font_size=20, primary=False):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.command = command
        self.font = pygame.font.SysFont('Arial', font_size, bold=True)
        self.primary = primary
        self.is_hovered = False
        self.hover_progress = 0.0

    def update(self, mouse_pos, dt):
        hovered = self.rect.collidepoint(mouse_pos)
        self.is_hovered = hovered
        target = 1.0 if hovered else 0.0
        self.hover_progress += (target - self.hover_progress) * min(1.0, dt * 14.0)

    def draw(self, surface):
        x, y, w, h = self.rect
        mix = self.hover_progress

        if self.primary:
            base_bg = (15, 140, 180, 220)
            hover_bg = (0, 200, 240, 245)
            border_col = (0, 240, 255)
        else:
            base_bg = (20, 28, 42, 200)
            hover_bg = (35, 55, 80, 230)
            border_col = (70, 100, 140)

        # Interpolate color
        r = int(base_bg[0] + (hover_bg[0] - base_bg[0]) * mix)
        g = int(base_bg[1] + (hover_bg[1] - base_bg[1]) * mix)
        b = int(base_bg[2] + (hover_bg[2] - base_bg[2]) * mix)
        a = int(base_bg[3] + (hover_bg[3] - base_bg[3]) * mix)

        draw_glass_panel(surface, self.rect, border_color=border_col, bg_color=(r, g, b, a), corner_radius=10, glow=self.is_hovered)

        text_col = (255, 255, 255) if self.is_hovered else COLOR_TEXT_PRIMARY
        text_surf = self.font.render(self.text, True, text_col)
        tx = x + (w - text_surf.get_width()) // 2
        ty = y + (h - text_surf.get_height()) // 2
        surface.blit(text_surf, (tx, ty))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.command:
                self.command()
                return True
        return False
