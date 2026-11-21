"""
menu_state.py - Cyberpunk Main Menu, Mode Selector & Interactive Settings Panel.
"""

import math
import pygame
from config import (
    COLOR_BG_DEEP, COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED, COLOR_ACCENT_CYAN, COLOR_ACCENT_GOLD, COLOR_ACCENT_MAGENTA
)
from src.graphics.ui_components import draw_glass_panel, UIButton


class MenuState:
    def __init__(self, sound_manager, shader_manager, start_game_callback):
        self.sound_mgr = sound_manager
        self.shader_mgr = shader_manager
        self.start_game_cb = start_game_callback

        self.sub_view = 'main'  # 'main', 'modes', 'settings', 'highscores'
        self.selected_mode = 'marathon'

        # Fonts
        self.font_logo = pygame.font.SysFont('Arial', 46, bold=True)
        self.font_sub = pygame.font.SysFont('Arial', 18, bold=True)
        self.font_title = pygame.font.SysFont('Arial', 26, bold=True)
        self.font_body = pygame.font.SysFont('Arial', 18)
        self.font_small = pygame.font.SysFont('Arial', 14)

        # Buttons
        self.buttons = []
        self._build_main_buttons()

    def _build_main_buttons(self):
        self.buttons.clear()
        bx = 475
        bw = 250
        bh = 50

        self.buttons.append(UIButton((bx, 340, bw, bh), "START GAME", command=lambda: self._set_sub_view('modes'), primary=True))
        self.buttons.append(UIButton((bx, 405, bw, bh), "HIGH SCORES", command=lambda: self._set_sub_view('highscores')))
        self.buttons.append(UIButton((bx, 470, bw, bh), "SETTINGS", command=lambda: self._set_sub_view('settings')))
        self.buttons.append(UIButton((bx, 535, bw, bh), "QUIT", command=self._quit))

    def _build_mode_buttons(self):
        self.buttons.clear()
        bx = 450
        bw = 300
        bh = 65

        modes = [
            ("MARATHON (150 LINES)", 'marathon', 280),
            ("SPRINT (40 LINES RUSH)", 'sprint', 360),
            ("ULTRA (3-MIN SCORE ATTACK)", 'ultra', 440),
            ("WIDE MATRIX (16 COLUMNS)", 'wide', 520),
        ]
        for title, mode_key, y in modes:
            self.buttons.append(UIButton((bx, y, bw, bh), title, command=lambda m=mode_key: self._launch_mode(m), primary=(mode_key == 'marathon')))

        self.buttons.append(UIButton((bx, 610, bw, 45), "← BACK TO MENU", command=lambda: self._set_sub_view('main')))

    def _build_settings_buttons(self):
        self.buttons.clear()
        bx = 450
        bw = 300
        bh = 48

        bloom_text = f"BLOOM SHADER: {'ON' if self.shader_mgr.enable_bloom else 'OFF'}"
        scanline_text = f"CRT SCANLINES: {'ON' if self.shader_mgr.enable_scanlines else 'OFF'}"

        self.buttons.append(UIButton((bx, 310, bw, bh), bloom_text, command=self._toggle_bloom))
        self.buttons.append(UIButton((bx, 370, bw, bh), scanline_text, command=self._toggle_scanlines))
        self.buttons.append(UIButton((bx, 430, bw, bh), f"SOUND SFX: {'ON' if self.sound_mgr.enabled else 'OFF'}", command=self._toggle_sound))
        self.buttons.append(UIButton((bx, 520, bw, 48), "← BACK TO MENU", command=lambda: self._set_sub_view('main'), primary=True))

    def _build_highscores_buttons(self):
        self.buttons.clear()
        bx = 475
        bw = 250
        self.buttons.append(UIButton((bx, 580, bw, 48), "← BACK TO MENU", command=lambda: self._set_sub_view('main'), primary=True))

    def _set_sub_view(self, view):
        self.sub_view = view
        self.sound_mgr.play('ui_click')
        if view == 'main':
            self._build_main_buttons()
        elif view == 'modes':
            self._build_mode_buttons()
        elif view == 'settings':
            self._build_settings_buttons()
        elif view == 'highscores':
            self._build_highscores_buttons()

    def _launch_mode(self, mode):
        self.sound_mgr.play('ui_click')
        self.start_game_cb(mode)

    def _toggle_bloom(self):
        self.shader_mgr.enable_bloom = not self.shader_mgr.enable_bloom
        self.sound_mgr.play('ui_click')
        self._build_settings_buttons()

    def _toggle_scanlines(self):
        self.shader_mgr.enable_scanlines = not self.shader_mgr.enable_scanlines
        self.sound_mgr.play('ui_click')
        self._build_settings_buttons()

    def _toggle_sound(self):
        self.sound_mgr.enabled = not self.sound_mgr.enabled
        self.sound_mgr.apply_volume()
        self.sound_mgr.play('ui_click')
        self._build_settings_buttons()

    def _quit(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_event(self, event):
        for btn in self.buttons:
            if btn.handle_event(event):
                return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.sub_view != 'main':
                self._set_sub_view('main')

    def update(self, mouse_pos, dt):
        for btn in self.buttons:
            was_hovered = btn.is_hovered
            btn.update(mouse_pos, dt)
            if not was_hovered and btn.is_hovered:
                self.sound_mgr.play('ui_hover')

    def draw(self, surface, time_sec):
        # Background space aesthetic
        surface.fill(COLOR_BG_DEEP)

        # Animated Grid background
        grid_col = (20, 32, 48, 60)
        offset = int((time_sec * 30) % 40)
        for x in range(0, 1200, 40):
            pygame.draw.line(surface, grid_col, (x, 0), (x, 800), 1)
        for y in range(0, 800, 40):
            pygame.draw.line(surface, grid_col, (0, y + offset), (1200, y + offset), 1)

        # Center Card Panel
        card_rect = pygame.Rect(380, 100, 440, 600)
        draw_glass_panel(surface, card_rect, border_color=COLOR_PANEL_BORDER, corner_radius=16, glow=True)

        # Logo Title with neon pulse
        pulse = (math.sin(time_sec * 3.0) + 1.0) * 0.5
        logo_col = (
            int(0 + pulse * 40),
            int(220 + pulse * 35),
            255
        )
        logo_surf = self.font_logo.render("TETRIS", True, logo_col)
        sub_surf = self.font_sub.render("REIMAGINED // CYBER MATRIX", True, COLOR_TEXT_MUTED)

        surface.blit(logo_surf, (600 - logo_surf.get_width() // 2, 140))
        surface.blit(sub_surf, (600 - sub_surf.get_width() // 2, 200))

        # Divider line
        pygame.draw.line(surface, (45, 65, 95), (420, 240), (780, 240), 1)

        # Views
        if self.sub_view == 'main':
            desc_surf = self.font_body.render("SELECT AN OPTION", True, COLOR_TEXT_PRIMARY)
            surface.blit(desc_surf, (600 - desc_surf.get_width() // 2, 275))

        elif self.sub_view == 'modes':
            desc_surf = self.font_title.render("CHOOSE GAME MODE", True, COLOR_ACCENT_CYAN)
            surface.blit(desc_surf, (600 - desc_surf.get_width() // 2, 250))

        elif self.sub_view == 'settings':
            desc_surf = self.font_title.render("SYSTEM SETTINGS", True, COLOR_ACCENT_CYAN)
            surface.blit(desc_surf, (600 - desc_surf.get_width() // 2, 255))

        elif self.sub_view == 'highscores':
            desc_surf = self.font_title.render("HALL OF FAME", True, COLOR_ACCENT_GOLD)
            surface.blit(desc_surf, (600 - desc_surf.get_width() // 2, 255))

            from src.engine.score_manager import ScoreManager
            modes = [('marathon', 'MARATHON'), ('sprint', 'SPRINT 40L'), ('ultra', 'ULTRA 3M'), ('wide', 'WIDE MATRIX')]
            for idx, (m_key, m_name) in enumerate(modes):
                sm = ScoreManager(mode=m_key)
                hs = sm.load_high_score()
                y = 320 + idx * 55
                surface.blit(self.font_body.render(m_name, True, COLOR_TEXT_PRIMARY), (440, y))
                hs_surf = self.font_body.render(f"{hs:,} PTS", True, COLOR_ACCENT_GOLD)
                surface.blit(hs_surf, (760 - hs_surf.get_width(), y))

        for btn in self.buttons:
            btn.draw(surface)

        # Footer Version
        v_surf = self.font_small.render("SRS ROTATION • 7-BAG RANDOMIZER • SHADERS ENABLED", True, COLOR_TEXT_MUTED)
        surface.blit(v_surf, (600 - v_surf.get_width() // 2, 730))
