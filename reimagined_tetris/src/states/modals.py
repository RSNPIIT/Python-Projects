"""
modals.py - Pause Menu & Game Over Summary Modal Dialogs.
"""

import pygame
from config import COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED, COLOR_ACCENT_CYAN, COLOR_ACCENT_GOLD
from src.graphics.ui_components import draw_glass_panel, UIButton


class PauseModal:
    def __init__(self, resume_cb, restart_cb, menu_cb):
        self.resume_cb = resume_cb
        self.restart_cb = restart_cb
        self.menu_cb = menu_cb

        self.font_title = pygame.font.SysFont('Arial', 32, bold=True)
        self.font_sub = pygame.font.SysFont('Arial', 18)

        bx = 475
        bw = 250
        bh = 48
        self.buttons = [
            UIButton((bx, 340, bw, bh), "RESUME", command=self.resume_cb, primary=True),
            UIButton((bx, 400, bw, bh), "RESTART", command=self.restart_cb),
            UIButton((bx, 460, bw, bh), "MAIN MENU", command=self.menu_cb),
        ]

    def handle_event(self, event):
        for btn in self.buttons:
            if btn.handle_event(event):
                return True
        return False

    def update(self, mouse_pos, dt):
        for btn in self.buttons:
            btn.update(mouse_pos, dt)

    def draw(self, surface):
        # Translucent dark backdrop
        scrim = pygame.Surface((1200, 800), pygame.SRCALPHA)
        scrim.fill((5, 8, 12, 185))
        surface.blit(scrim, (0, 0))

        # Center Dialog Card
        card_rect = pygame.Rect(430, 220, 340, 320)
        draw_glass_panel(surface, card_rect, border_color=COLOR_ACCENT_CYAN, corner_radius=16, glow=True)

        t_surf = self.font_title.render("PAUSED", True, COLOR_TEXT_PRIMARY)
        sub_surf = self.font_sub.render("TACTICAL MATRIX HOLD", True, COLOR_TEXT_MUTED)
        surface.blit(t_surf, (600 - t_surf.get_width() // 2, 250))
        surface.blit(sub_surf, (600 - sub_surf.get_width() // 2, 290))

        for btn in self.buttons:
            btn.draw(surface)


class GameOverModal:
    def __init__(self, is_victory, score_mgr, elapsed_time, restart_cb, menu_cb):
        self.is_victory = is_victory
        self.score_mgr = score_mgr
        self.elapsed_time = elapsed_time
        self.restart_cb = restart_cb
        self.menu_cb = menu_cb

        self.font_title = pygame.font.SysFont('Arial', 34, bold=True)
        self.font_sub = pygame.font.SysFont('Arial', 18, bold=True)
        self.font_body = pygame.font.SysFont('Arial', 16)
        self.font_digits = pygame.font.SysFont('Arial', 24, bold=True)

        bx = 475
        bw = 250
        bh = 48
        self.buttons = [
            UIButton((bx, 550, bw, bh), "PLAY AGAIN", command=self.restart_cb, primary=True),
            UIButton((bx, 610, bw, bh), "MAIN MENU", command=self.menu_cb),
        ]

    def handle_event(self, event):
        for btn in self.buttons:
            if btn.handle_event(event):
                return True
        return False

    def update(self, mouse_pos, dt):
        for btn in self.buttons:
            btn.update(mouse_pos, dt)

    def draw(self, surface):
        scrim = pygame.Surface((1200, 800), pygame.SRCALPHA)
        scrim.fill((6, 8, 12, 205))
        surface.blit(scrim, (0, 0))

        # Center Card
        card_rect = pygame.Rect(390, 110, 420, 580)
        border_col = COLOR_ACCENT_GOLD if self.is_victory else (255, 60, 80)
        draw_glass_panel(surface, card_rect, border_color=border_col, corner_radius=16, glow=True)

        header_str = "OPERATION COMPLETE!" if self.is_victory else "GAME OVER"
        header_col = COLOR_ACCENT_GOLD if self.is_victory else (255, 80, 95)
        t_surf = self.font_title.render(header_str, True, header_col)
        surface.blit(t_surf, (600 - t_surf.get_width() // 2, 140))

        # Final Score Callout
        sc_lbl = self.font_sub.render("FINAL SCORE", True, COLOR_TEXT_MUTED)
        sc_val = self.font_digits.render(f"{self.score_mgr.score:,}", True, COLOR_TEXT_PRIMARY)
        surface.blit(sc_lbl, (600 - sc_lbl.get_width() // 2, 195))
        surface.blit(sc_val, (600 - sc_val.get_width() // 2, 222))

        if self.score_mgr.score >= self.score_mgr.high_score and self.score_mgr.score > 0:
            rec_surf = self.font_sub.render("★ NEW RECORD HIGH SCORE! ★", True, COLOR_ACCENT_GOLD)
            surface.blit(rec_surf, (600 - rec_surf.get_width() // 2, 260))

        # Metrics Table
        mins = int(self.elapsed_time // 60)
        secs = self.elapsed_time % 60
        timer_str = f"{mins:02d}:{secs:05.2f}"

        stats = [
            ("Lines Cleared", f"{self.score_mgr.lines}"),
            ("Final Level", f"{self.score_mgr.level}"),
            ("Time Elapsed", timer_str),
            ("Tetrises (Quads)", f"{self.score_mgr.tetrises}"),
            ("T-Spins Executed", f"{self.score_mgr.tspins}"),
            ("Max Combo", f"x{self.score_mgr.max_combo}"),
        ]

        table_y = 300
        for idx, (label, val) in enumerate(stats):
            y = table_y + idx * 36
            surface.blit(self.font_body.render(label, True, COLOR_TEXT_MUTED), (430, y))
            v_surf = self.font_body.render(val, True, COLOR_TEXT_PRIMARY)
            surface.blit(v_surf, (770 - v_surf.get_width(), y))

        for btn in self.buttons:
            btn.draw(surface)
