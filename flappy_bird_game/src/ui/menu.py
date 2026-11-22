"""
menu.py - Title Screen, Scoreboard Card, Medal Presentation & Game Over Modals.
"""

import math
import pygame
from ..config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SKINS, DIFFICULTIES, TIME_THEMES,
    SKIN_KEYS, THEME_KEYS
)
from .medals import draw_medal, get_medal_for_score


class Menu:
    """Renders the Title Screen, Game Over Scoreboard Card, and interactive prompts."""

    def __init__(self):
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Impact, Arial Black, Helvetica", 82)
        self.font_subtitle = pygame.font.SysFont("Helvetica, Arial", 22, bold=True)
        self.font_card_lbl = pygame.font.SysFont("Impact, Arial Black, Helvetica", 22)
        self.font_card_val = pygame.font.SysFont("Impact, Arial Black, Helvetica", 36)
        self.font_tips = pygame.font.SysFont("Helvetica, Arial", 16, bold=True)

        self.hover_timer = 0.0
        self.prompt_blink = 0.0

        # Game over slide-in animation
        self.card_y_offset = -400.0
        self.display_score = 0
        self.target_score = 0
        self.score_roll_timer = 0.0

    def reset_game_over(self, score: int):
        self.card_y_offset = -450.0
        self.display_score = 0
        self.target_score = score
        self.score_roll_timer = 0.0

    def update(self, dt: float):
        self.hover_timer += dt
        self.prompt_blink += dt

        # Slide-in animation for game over
        if self.card_y_offset < 0:
            self.card_y_offset = min(0.0, self.card_y_offset + 950.0 * dt)

        # Counting-up score effect
        if self.display_score < self.target_score:
            self.score_roll_timer += dt
            if self.score_roll_timer > 0.04:
                self.score_roll_timer = 0.0
                step = max(1, (self.target_score - self.display_score) // 4)
                self.display_score = min(self.target_score, self.display_score + step)

    def draw_title_screen(
        self,
        surface: pygame.Surface,
        bird,
        best_score: int,
        diff_key: str,
        skin_key: str,
        theme_key: str
    ):
        """Draws the main menu with 3D block logo, hovering bird, and controls."""
        cx = SCREEN_WIDTH // 2

        # 1. 3D Block Stylized Title "KFLAPPER"
        title_text = "KFLAPPER"
        cy_title = 160

        # Multi-layer extrude shadow for block retro 3D feel
        for d in range(8, 0, -1):
            sh_surf = self.font_title.render(title_text, True, (25, 40, 20))
            surface.blit(sh_surf, (cx - sh_surf.get_width() // 2 + d, cy_title - sh_surf.get_height() // 2 + d))

        # Main bright face
        t_surf = self.font_title.render(title_text, True, (255, 220, 40))
        surface.blit(t_surf, (cx - t_surf.get_width() // 2, cy_title - t_surf.get_height() // 2))
        # Inner specular highlight
        hi_surf = self.font_title.render(title_text, True, (255, 255, 220))
        surface.blit(hi_surf, (cx - hi_surf.get_width() // 2 - 2, cy_title - hi_surf.get_height() // 2 - 2))

        # Subtitle
        sub_text = "THE OG FLAPPY BIRD // HD ARCADE EDITION"
        sub_surf = self.font_subtitle.render(sub_text, True, (255, 255, 255))
        sub_rect = sub_surf.get_rect(center=(cx, cy_title + 60))
        # Drop shadow
        sh_sub = self.font_subtitle.render(sub_text, True, (15, 20, 30))
        surface.blit(sh_sub, (sub_rect.x + 2, sub_rect.y + 2))
        surface.blit(sub_surf, sub_rect)

        # 2. Hovering Animated Bird in Center
        hover_y = 310 + math.sin(self.hover_timer * 3.6) * 14.0
        bird.x = cx
        bird.y = hover_y
        bird.angle = math.sin(self.hover_timer * 2.0) * 10.0
        bird.draw(surface)

        # 3. Flashing Pulsing Action Prompt
        alpha = int(128 + 127 * math.sin(self.prompt_blink * 5.0))
        prompt_text = "PRESS SPACE OR CLICK TO FLAP"
        prompt_surf = self.font_subtitle.render(prompt_text, True, (255, 235, 80))
        p_surf_alpha = pygame.Surface(prompt_surf.get_size(), pygame.SRCALPHA)
        p_surf_alpha.blit(prompt_surf, (0, 0))
        p_surf_alpha.set_alpha(alpha)
        surface.blit(p_surf_alpha, (cx - prompt_surf.get_width() // 2, 400))

        # 4. Settings Dashboard Card
        card_w, card_h = 680, 100
        card_x = cx - card_w // 2
        card_y = 475

        # Background card
        card_bg = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_bg.fill((12, 18, 32, 210))
        surface.blit(card_bg, (card_x, card_y))
        pygame.draw.rect(surface, (255, 215, 60), (card_x, card_y, card_w, card_h), 2)

        # Dashboard Information Columns
        cols_info = [
            ("SKIN (C)", SKINS[skin_key]["name"].split()[0]),
            ("DIFFICULTY (D)", diff_key),
            ("TIME (T)", theme_key),
            ("BEST SCORE", str(best_score))
        ]
        col_w = card_w // len(cols_info)
        for idx, (label, val) in enumerate(cols_info):
            lx = card_x + idx * col_w + col_w // 2
            lbl_s = self.font_tips.render(label, True, (160, 185, 220))
            surface.blit(lbl_s, (lx - lbl_s.get_width() // 2, card_y + 18))

            val_s = self.font_subtitle.render(val, True, (255, 255, 255))
            surface.blit(val_s, (lx - val_s.get_width() // 2, card_y + 48))

        # 5. Bottom Controls Bar
        ctrl_text = "[SPACE/CLICK] Flap  •  [C] Skin  •  [D] Difficulty  •  [T] Theme  •  [M] Mute  •  [F11] Fullscreen"
        ctrl_s = self.font_tips.render(ctrl_text, True, (240, 245, 255))
        c_rect = ctrl_s.get_rect(center=(cx, 650))
        pill = pygame.Surface((c_rect.width + 24, c_rect.height + 10), pygame.SRCALPHA)
        pill.fill((10, 15, 25, 180))
        surface.blit(pill, (c_rect.x - 12, c_rect.y - 5))
        surface.blit(ctrl_s, c_rect)

    def draw_game_over(
        self,
        surface: pygame.Surface,
        score: int,
        best_score: int,
        is_new_best: bool
    ):
        """Draws the post-crash Game Over banner and metallic score card."""
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        # Apply slide-in vertical offset
        card_center_y = cy + int(self.card_y_offset)

        # 1. "GAME OVER" Title Banner
        go_text = "GAME OVER"
        go_y = card_center_y - 135
        # 3D Drop shadow
        for dx, dy in [(3, 3), (3, -3), (-3, 3), (-3, -3), (0, 5)]:
            sh = self.font_title.render(go_text, True, (20, 20, 25))
            surface.blit(sh, (cx - sh.get_width() // 2 + dx, go_y + dy))

        go_surf = self.font_title.render(go_text, True, (250, 70, 70))
        surface.blit(go_surf, (cx - go_surf.get_width() // 2, go_y))

        # 2. Scoreboard Metallic Card
        card_w, card_h = 460, 220
        card_x = cx - card_w // 2
        card_y = card_center_y - card_h // 2 + 10

        # Beveled metallic card frame
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((235, 215, 175))  # Nostalgic warm arcade paper/metal
        surface.blit(card_surf, (card_x, card_y))

        # Frame border
        pygame.draw.rect(surface, (120, 95, 60), (card_x, card_y, card_w, card_h), 5)
        pygame.draw.rect(surface, (255, 245, 220), (card_x + 5, card_y + 5, card_w - 10, card_h - 10), 2)

        # 3. Left: Medal Slot
        medal_slot_cx = card_x + 95
        medal_slot_cy = card_y + 110
        # Dark metallic recessed socket
        pygame.draw.circle(surface, (160, 135, 95), (medal_slot_cx, medal_slot_cy), 48)
        pygame.draw.circle(surface, (90, 70, 45), (medal_slot_cx, medal_slot_cy), 45)

        # Label above medal
        m_lbl = self.font_card_lbl.render("MEDAL", True, (160, 120, 70))
        surface.blit(m_lbl, (medal_slot_cx - m_lbl.get_width() // 2, card_y + 24))

        # Draw unlocked medal badge
        tier = get_medal_for_score(score)
        if tier:
            draw_medal(surface, medal_slot_cx, medal_slot_cy, tier, radius=36)
        else:
            # Empty socket silhouette
            none_lbl = self.font_tips.render("NO MEDAL", True, (130, 110, 80))
            surface.blit(none_lbl, (medal_slot_cx - none_lbl.get_width() // 2, medal_slot_cy - 8))

        # 4. Right: Score & Best Readouts
        right_x = card_x + 210

        # Current Score
        s_lbl = self.font_card_lbl.render("SCORE", True, (160, 120, 70))
        surface.blit(s_lbl, (right_x, card_y + 24))

        s_val = self.font_card_val.render(str(self.display_score), True, (30, 30, 35))
        surface.blit(s_val, (card_x + card_w - 45 - s_val.get_width(), card_y + 48))

        # Divider line
        pygame.draw.line(surface, (180, 155, 115), (right_x, card_y + 105), (card_x + card_w - 30, card_y + 105), 2)

        # Best Score
        b_lbl = self.font_card_lbl.render("BEST", True, (160, 120, 70))
        surface.blit(b_lbl, (right_x, card_y + 116))

        b_val = self.font_card_val.render(str(best_score), True, (30, 30, 35))
        surface.blit(b_val, (card_x + card_w - 45 - b_val.get_width(), card_y + 140))

        # New High Score Sparkle Badge
        if is_new_best:
            badge_x = right_x + 65
            badge_y = card_y + 120
            # Glowing badge
            pygame.draw.rect(surface, (230, 40, 50), (badge_x, badge_y, 48, 20), border_radius=4)
            badge_txt = self.font_tips.render("NEW!", True, (255, 255, 255))
            surface.blit(badge_txt, (badge_x + 5, badge_y + 2))

        # 5. Play Again / Restart Button Prompt
        if self.card_y_offset >= -10:
            prompt_y = card_y + card_h + 35
            p_text = "PRESS SPACE OR CLICK TO PLAY AGAIN"
            p_surf = self.font_subtitle.render(p_text, True, (255, 235, 80))
            p_rect = p_surf.get_rect(center=(cx, prompt_y))

            pill = pygame.Surface((p_rect.width + 36, p_rect.height + 16), pygame.SRCALPHA)
            pill.fill((10, 15, 25, 210))
            surface.blit(pill, (p_rect.x - 18, p_rect.y - 8))
            pygame.draw.rect(surface, (255, 215, 60), (p_rect.x - 18, p_rect.y - 8, p_rect.width + 36, p_rect.height + 16), 2, border_radius=6)
            surface.blit(p_surf, p_rect)

            sub_tip = self.font_tips.render("[C] Change Skin   •   [D] Difficulty   •   [R] Quick Reset", True, (240, 245, 255))
            st_rect = sub_tip.get_rect(center=(cx, prompt_y + 44))
            surface.blit(sub_tip, st_rect)
