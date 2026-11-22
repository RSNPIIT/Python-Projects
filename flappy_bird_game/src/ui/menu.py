"""
menu.py - Interactive GUI Menu, Difficulty Selector, Live Skin Switcher & Scoreboard.
Features responsive clickable buttons, hover glow effects, and arcade layout.
"""

import math
import pygame
from ..config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SKINS, DIFFICULTIES, BIOMES,
    DIFF_KEYS, SKIN_KEYS
)
from .medals import draw_medal, get_medal_for_score


class Menu:
    """Manages GUI buttons, title screen, difficulty selection, and post-game scoreboard."""

    def __init__(self):
        pygame.font.init()
        self.font_title = pygame.font.SysFont("Impact, Arial Black, Helvetica", 72)
        self.font_subtitle = pygame.font.SysFont("Helvetica, Arial", 18, bold=True)
        self.font_btn = pygame.font.SysFont("Impact, Arial Black, Helvetica", 24)
        self.font_btn_sm = pygame.font.SysFont("Impact, Arial Black, Helvetica", 18)
        self.font_desc = pygame.font.SysFont("Helvetica, Arial", 12, bold=True)
        self.font_tag = pygame.font.SysFont("Helvetica, Arial", 10, bold=True)
        self.font_card_lbl = pygame.font.SysFont("Impact, Arial Black, Helvetica", 22)
        self.font_card_val = pygame.font.SysFont("Impact, Arial Black, Helvetica", 36)
        self.font_tips = pygame.font.SysFont("Helvetica, Arial", 14, bold=True)

        self.hover_timer = 0.0
        self.pulse_timer = 0.0
        self.hovered_btn = None

        # Game over slide-in animation
        self.card_y_offset = -450.0
        self.display_score = 0
        self.target_score = 0
        self.score_roll_timer = 0.0

        # Interactive Button Hitboxes (Calculated in draw / initialized here)
        self.buttons = {}

    def reset_game_over(self, score: int):
        self.card_y_offset = -450.0
        self.display_score = 0
        self.target_score = score
        self.score_roll_timer = 0.0

    def update(self, dt: float):
        self.hover_timer += dt
        self.pulse_timer += dt

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

    def update_hover(self, mouse_pos: tuple):
        self.hovered_btn = None
        for btn_id, rect in self.buttons.items():
            if rect and rect.collidepoint(mouse_pos):
                self.hovered_btn = btn_id
                break

    def handle_click(self, mouse_pos: tuple, current_state_name: str) -> tuple:
        """
        Translates a mouse click coordinate into a menu event action.
        Returns: (action_name: str, payload: any) or (None, None)
        """
        if current_state_name == "MENU":
            # 1. Difficulty Buttons
            for diff_key in DIFF_KEYS:
                rect = self.buttons.get(f"diff_{diff_key}")
                if rect and rect.collidepoint(mouse_pos):
                    return ("set_diff", diff_key)

            # 2. Skin Selector Arrows & Card
            if self.buttons.get("skin_prev") and self.buttons["skin_prev"].collidepoint(mouse_pos):
                return ("cycle_skin", -1)
            if self.buttons.get("skin_next") and self.buttons["skin_next"].collidepoint(mouse_pos):
                return ("cycle_skin", 1)
            if self.buttons.get("skin_card") and self.buttons["skin_card"].collidepoint(mouse_pos):
                return ("cycle_skin", 1)

            # 3. Play Button
            if self.buttons.get("btn_play") and self.buttons["btn_play"].collidepoint(mouse_pos):
                return ("start_game", None)

            # 4. Toolbar Buttons
            if self.buttons.get("btn_theme") and self.buttons["btn_theme"].collidepoint(mouse_pos):
                return ("cycle_theme", None)
            if self.buttons.get("btn_sound") and self.buttons["btn_sound"].collidepoint(mouse_pos):
                return ("toggle_sound", None)
            if self.buttons.get("btn_fs") and self.buttons["btn_fs"].collidepoint(mouse_pos):
                return ("toggle_fullscreen", None)

        elif current_state_name == "GAME_OVER":
            if self.card_y_offset >= -20:
                if self.buttons.get("go_replay") and self.buttons["go_replay"].collidepoint(mouse_pos):
                    return ("start_game", None)
                if self.buttons.get("go_menu") and self.buttons["go_menu"].collidepoint(mouse_pos):
                    return ("go_to_menu", None)

        return (None, None)

    def draw_title_screen(
        self,
        surface: pygame.Surface,
        bird,
        best_score: int,
        diff_key: str,
        skin_key: str,
        theme_display_name: str,
        sound_muted: bool
    ):
        """Renders rich, intuitive GUI menu with difficulty selector cards and live bird preview."""
        cx = SCREEN_WIDTH // 2
        self.buttons.clear()

        # -------------------------------------------------------------
        # 1. HEADER LOGO & SUBTITLE
        # -------------------------------------------------------------
        cy_title = 85
        title_text = "KFLAPPER"

        # 3D Extrude effect
        for d in range(7, 0, -1):
            sh_surf = self.font_title.render(title_text, True, (25, 35, 20))
            surface.blit(sh_surf, (cx - sh_surf.get_width() // 2 + d, cy_title - sh_surf.get_height() // 2 + d))

        # Main glowing title face
        t_surf = self.font_title.render(title_text, True, (255, 220, 40))
        surface.blit(t_surf, (cx - t_surf.get_width() // 2, cy_title - t_surf.get_height() // 2))
        hi_surf = self.font_title.render(title_text, True, (255, 255, 220))
        surface.blit(hi_surf, (cx - hi_surf.get_width() // 2 - 2, cy_title - hi_surf.get_height() // 2 - 2))

        # Subtitle
        sub_text = "THE OG FLAPPY BIRD // HD ARCADE EDITION"
        sub_surf = self.font_subtitle.render(sub_text, True, (255, 255, 255))
        sub_rect = sub_surf.get_rect(center=(cx, cy_title + 44))
        sh_sub = self.font_subtitle.render(sub_text, True, (15, 20, 30))
        surface.blit(sh_sub, (sub_rect.x + 2, sub_rect.y + 2))
        surface.blit(sub_surf, sub_rect)

        # -------------------------------------------------------------
        # 2. CENTER: ANIMATED BIRD & SKIN SELECTOR GUI
        # -------------------------------------------------------------
        hover_y = 205 + math.sin(self.hover_timer * 3.6) * 12.0
        bird.x = cx
        bird.y = hover_y
        bird.angle = math.sin(self.hover_timer * 2.0) * 10.0
        bird.draw(surface)

        # Skin Selector Bar below Bird (y=255)
        skin_cfg = SKINS.get(skin_key, SKINS["KFlapper"])
        skin_bar_w = 340
        skin_bar_h = 42
        skin_bar_x = cx - skin_bar_w // 2
        skin_bar_y = 255

        # Left Arrow Button [ ◀ ]
        btn_prev_rect = pygame.Rect(skin_bar_x, skin_bar_y, 44, skin_bar_h)
        self.buttons["skin_prev"] = btn_prev_rect
        is_prev_hov = (self.hovered_btn == "skin_prev")
        prev_bg = (45, 60, 95) if is_prev_hov else (18, 25, 42)
        pygame.draw.rect(surface, prev_bg, btn_prev_rect, border_radius=6)
        pygame.draw.rect(surface, (255, 215, 60) if is_prev_hov else (70, 90, 130), btn_prev_rect, 2, border_radius=6)
        arr_l = self.font_btn_sm.render("<", True, (255, 255, 255))
        surface.blit(arr_l, (btn_prev_rect.centerx - arr_l.get_width() // 2, btn_prev_rect.centery - arr_l.get_height() // 2))

        # Skin Card Center [ 🐤 Skin Name ]
        card_rect = pygame.Rect(skin_bar_x + 50, skin_bar_y, skin_bar_w - 100, skin_bar_h)
        self.buttons["skin_card"] = card_rect
        is_card_hov = (self.hovered_btn == "skin_card")
        card_bg = (30, 42, 70) if is_card_hov else (14, 20, 36)
        pygame.draw.rect(surface, card_bg, card_rect, border_radius=6)
        pygame.draw.rect(surface, (255, 215, 60) if is_card_hov else (60, 80, 120), card_rect, 2, border_radius=6)

        skin_title = f"SKIN: {skin_cfg['short_name'].upper()}"
        skin_surf = self.font_desc.render(skin_title, True, skin_cfg["wing_color"])
        surface.blit(skin_surf, (card_rect.centerx - skin_surf.get_width() // 2, card_rect.centery - skin_surf.get_height() // 2))

        # Right Arrow Button [ ▶ ]
        btn_next_rect = pygame.Rect(skin_bar_x + skin_bar_w - 44, skin_bar_y, 44, skin_bar_h)
        self.buttons["skin_next"] = btn_next_rect
        is_next_hov = (self.hovered_btn == "skin_next")
        next_bg = (45, 60, 95) if is_next_hov else (18, 25, 42)
        pygame.draw.rect(surface, next_bg, btn_next_rect, border_radius=6)
        pygame.draw.rect(surface, (255, 215, 60) if is_next_hov else (70, 90, 130), btn_next_rect, 2, border_radius=6)
        arr_r = self.font_btn_sm.render(">", True, (255, 255, 255))
        surface.blit(arr_r, (btn_next_rect.centerx - arr_r.get_width() // 2, btn_next_rect.centery - arr_r.get_height() // 2))

        # -------------------------------------------------------------
        # 3. INTERACTIVE GUI DIFFICULTY SELECTOR SECTION
        # -------------------------------------------------------------
        diff_section_y = 315

        # Section Header with styling lines
        sec_title = "CHOOSE DIFFICULTY"
        sec_surf = self.font_subtitle.render(sec_title, True, (255, 240, 180))
        surface.blit(sec_surf, (cx - sec_surf.get_width() // 2, diff_section_y))

        # Left / Right ornamental horizontal rules
        line_w = 160
        line_y = diff_section_y + sec_surf.get_height() // 2
        pygame.draw.line(surface, (255, 215, 60, 120), (cx - sec_surf.get_width() // 2 - line_w - 15, line_y), (cx - sec_surf.get_width() // 2 - 15, line_y), 2)
        pygame.draw.line(surface, (255, 215, 60, 120), (cx + sec_surf.get_width() // 2 + 15, line_y), (cx + sec_surf.get_width() // 2 + line_w + 15, line_y), 2)

        # 3 Dedicated Clickable Difficulty Cards
        card_w = 300
        card_h = 86
        gap_between = 24
        total_w = card_w * 3 + gap_between * 2
        start_x = cx - total_w // 2
        cards_y = diff_section_y + 32

        for idx, k in enumerate(DIFF_KEYS):
            d_cfg = DIFFICULTIES[k]
            bx = start_x + idx * (card_w + gap_between)
            rect = pygame.Rect(bx, cards_y, card_w, card_h)
            self.buttons[f"diff_{k}"] = rect

            is_active = (k == diff_key)
            is_hovered = (self.hovered_btn == f"diff_{k}")
            badge_col = d_cfg["badge_color"]

            # Background fill
            if is_active:
                bg_col = (20, 36, 56)
                border_col = badge_col
                border_thick = 3
            elif is_hovered:
                bg_col = (28, 38, 54)
                border_col = (255, 255, 255)
                border_thick = 2
            else:
                bg_col = (12, 18, 30, 220)
                border_col = (50, 70, 95)
                border_thick = 1

            # Draw card surface
            s = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            s.fill(bg_col)
            surface.blit(s, (bx, cards_y))
            pygame.draw.rect(surface, border_col, rect, border_thick, border_radius=8)

            # Top Tag Badge (e.g., EASY / OG / PRO)
            tag_text = d_cfg["tag"]
            tag_surf = self.font_tag.render(tag_text, True, (15, 20, 30))
            tag_pill_w = tag_surf.get_width() + 14
            tag_pill_h = 16
            tag_rx = bx + card_w - tag_pill_w - 10
            tag_ry = cards_y + 10
            pygame.draw.rect(surface, badge_col, (tag_rx, tag_ry, tag_pill_w, tag_pill_h), border_radius=4)
            surface.blit(tag_surf, (tag_rx + 7, tag_ry + 2))

            # Difficulty Title
            title_col = badge_col if is_active else (235, 240, 250)
            d_title_s = self.font_btn.render(d_cfg["name"].upper(), True, title_col)
            surface.blit(d_title_s, (bx + 14, cards_y + 10))

            # Active Checkmark Indicator
            if is_active:
                chk_s = self.font_desc.render("ACTIVE", True, badge_col)
                surface.blit(chk_s, (bx + 16 + d_title_s.get_width(), cards_y + 16))

            # Description Subtitle
            desc_s = self.font_desc.render(d_cfg["desc"], True, (160, 180, 210))
            surface.blit(desc_s, (bx + 14, cards_y + 48))

        # -------------------------------------------------------------
        # 4. PRIMARY PLAY BUTTON GUI (Large & Inviting)
        # -------------------------------------------------------------
        play_w = 460
        play_h = 62
        play_x = cx - play_w // 2
        play_y = 475
        play_rect = pygame.Rect(play_x, play_y, play_w, play_h)
        self.buttons["btn_play"] = play_rect

        is_play_hov = (self.hovered_btn == "btn_play")
        pulse = 0.5 + 0.5 * math.sin(self.pulse_timer * 6.0)

        # Glowing button fill
        play_bg = (245, 180, 20) if is_play_hov else (225, 155, 10)
        pygame.draw.rect(surface, play_bg, play_rect, border_radius=10)
        # Glowing border
        border_glow = (255, 245, 180) if is_play_hov else (255, 215, 60)
        pygame.draw.rect(surface, border_glow, play_rect, 3 + int(pulse * 1.5), border_radius=10)

        play_label = "PLAY GAME  [ SPACE / TAP ]"
        play_s = self.font_btn.render(play_label, True, (20, 25, 10))
        surface.blit(play_s, (cx - play_s.get_width() // 2, play_y + (play_h - play_s.get_height()) // 2))

        # -------------------------------------------------------------
        # 5. BOTTOM GUI TOOLBAR & BEST SCORE CARD
        # -------------------------------------------------------------
        toolbar_y = 560
        tb_btn_h = 38

        # A. Theme / Biome Shift Button
        theme_label = f"BIOMES: {theme_display_name.upper()}"
        t_text = f"MAP: {theme_display_name.upper()} (T)"
        t_surf = self.font_tips.render(t_text, True, (240, 245, 255))
        tb1_w = t_surf.get_width() + 28
        tb1_x = cx - 280
        btn_theme_rect = pygame.Rect(tb1_x, toolbar_y, tb1_w, tb_btn_h)
        self.buttons["btn_theme"] = btn_theme_rect
        is_t_hov = (self.hovered_btn == "btn_theme")
        pygame.draw.rect(surface, (35, 48, 75) if is_t_hov else (16, 22, 38, 220), btn_theme_rect, border_radius=6)
        pygame.draw.rect(surface, (255, 215, 60) if is_t_hov else (60, 80, 115), btn_theme_rect, 2, border_radius=6)
        surface.blit(t_surf, (btn_theme_rect.centerx - t_surf.get_width() // 2, btn_theme_rect.centery - t_surf.get_height() // 2))

        # B. Sound Toggle Button
        s_text = "SFX: OFF (M)" if sound_muted else "SFX: ON (M)"
        s_col = (255, 100, 100) if sound_muted else (120, 240, 140)
        s_surf = self.font_tips.render(s_text, True, s_col)
        tb2_w = s_surf.get_width() + 28
        tb2_x = cx - 280 + tb1_w + 14
        btn_sound_rect = pygame.Rect(tb2_x, toolbar_y, tb2_w, tb_btn_h)
        self.buttons["btn_sound"] = btn_sound_rect
        is_s_hov = (self.hovered_btn == "btn_sound")
        pygame.draw.rect(surface, (35, 48, 75) if is_s_hov else (16, 22, 38, 220), btn_sound_rect, border_radius=6)
        pygame.draw.rect(surface, (255, 215, 60) if is_s_hov else (60, 80, 115), btn_sound_rect, 2, border_radius=6)
        surface.blit(s_surf, (btn_sound_rect.centerx - s_surf.get_width() // 2, btn_sound_rect.centery - s_surf.get_height() // 2))

        # C. Best Score Display Pill
        best_text = f"BEST SCORE: {best_score}"
        best_surf = self.font_tips.render(best_text, True, (255, 215, 60))
        tb3_w = best_surf.get_width() + 28
        tb3_x = tb2_x + tb2_w + 14
        pygame.draw.rect(surface, (14, 20, 36, 230), (tb3_x, toolbar_y, tb3_w, tb_btn_h), border_radius=6)
        pygame.draw.rect(surface, (255, 215, 60), (tb3_x, toolbar_y, tb3_w, tb_btn_h), 2, border_radius=6)
        surface.blit(best_surf, (tb3_x + 14, toolbar_y + (tb_btn_h - best_surf.get_height()) // 2))

        # D. Bottom Shortcut Info Bar
        ctrl_text = "CLICK BUTTONS OR USE HOTKEYS: [SPACE/CLICK] Flap  •  [C] Skin  •  [D] Difficulty  •  [T] Biomes  •  [F11] Fullscreen"
        ctrl_s = self.font_desc.render(ctrl_text, True, (240, 245, 255))
        c_rect = ctrl_s.get_rect(center=(cx, 660))
        pill = pygame.Surface((c_rect.width + 24, c_rect.height + 8), pygame.SRCALPHA)
        pill.fill((10, 15, 25, 180))
        surface.blit(pill, (c_rect.x - 12, c_rect.y - 4))
        surface.blit(ctrl_s, c_rect)

    def draw_game_over(
        self,
        surface: pygame.Surface,
        score: int,
        best_score: int,
        is_new_best: bool
    ):
        """Draws the post-crash Game Over banner and metallic score card with GUI action buttons."""
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        self.buttons.clear()

        # Apply slide-in vertical offset
        card_center_y = cy + int(self.card_y_offset)

        # 1. "GAME OVER" Title Banner
        go_text = "GAME OVER"
        go_y = card_center_y - 145
        for dx, dy in [(3, 3), (3, -3), (-3, 3), (-3, -3), (0, 5)]:
            sh = self.font_title.render(go_text, True, (20, 20, 25))
            surface.blit(sh, (cx - sh.get_width() // 2 + dx, go_y + dy))

        go_surf = self.font_title.render(go_text, True, (250, 70, 70))
        surface.blit(go_surf, (cx - go_surf.get_width() // 2, go_y))

        # 2. Scoreboard Metallic Card
        card_w, card_h = 480, 220
        card_x = cx - card_w // 2
        card_y = card_center_y - card_h // 2 + 5

        # Beveled metallic card frame
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((235, 215, 175))
        surface.blit(card_surf, (card_x, card_y))

        pygame.draw.rect(surface, (120, 95, 60), (card_x, card_y, card_w, card_h), 5)
        pygame.draw.rect(surface, (255, 245, 220), (card_x + 5, card_y + 5, card_w - 10, card_h - 10), 2)

        # 3. Left: Medal Slot
        medal_slot_cx = card_x + 105
        medal_slot_cy = card_y + 110
        pygame.draw.circle(surface, (160, 135, 95), (medal_slot_cx, medal_slot_cy), 48)
        pygame.draw.circle(surface, (90, 70, 45), (medal_slot_cx, medal_slot_cy), 45)

        m_lbl = self.font_card_lbl.render("MEDAL", True, (160, 120, 70))
        surface.blit(m_lbl, (medal_slot_cx - m_lbl.get_width() // 2, card_y + 24))

        tier = get_medal_for_score(score)
        if tier:
            draw_medal(surface, medal_slot_cx, medal_slot_cy, tier, radius=36)
        else:
            none_lbl = self.font_tips.render("NO MEDAL", True, (130, 110, 80))
            surface.blit(none_lbl, (medal_slot_cx - none_lbl.get_width() // 2, medal_slot_cy - 8))

        # 4. Right: Score & Best Readouts
        right_x = card_x + 225

        s_lbl = self.font_card_lbl.render("SCORE", True, (160, 120, 70))
        surface.blit(s_lbl, (right_x, card_y + 24))

        s_val = self.font_card_val.render(str(self.display_score), True, (30, 30, 35))
        surface.blit(s_val, (card_x + card_w - 45 - s_val.get_width(), card_y + 48))

        # Divider line
        pygame.draw.line(surface, (180, 155, 115), (right_x, card_y + 105), (card_x + card_w - 30, card_y + 105), 2)

        b_lbl = self.font_card_lbl.render("BEST", True, (160, 120, 70))
        surface.blit(b_lbl, (right_x, card_y + 116))

        b_val = self.font_card_val.render(str(best_score), True, (30, 30, 35))
        surface.blit(b_val, (card_x + card_w - 45 - b_val.get_width(), card_y + 140))

        if is_new_best:
            badge_x = right_x + 65
            badge_y = card_y + 120
            pygame.draw.rect(surface, (230, 40, 50), (badge_x, badge_y, 48, 20), border_radius=4)
            badge_txt = self.font_tag.render("NEW!", True, (255, 255, 255))
            surface.blit(badge_txt, (badge_x + 7, badge_y + 3))

        # 5. Interactive GUI Action Buttons below card
        if self.card_y_offset >= -10:
            btn_w = 210
            btn_h = 50
            btn_y = card_y + card_h + 24

            # [ PLAY AGAIN ]
            r_replay = pygame.Rect(cx - btn_w - 12, btn_y, btn_w, btn_h)
            self.buttons["go_replay"] = r_replay
            is_rep_hov = (self.hovered_btn == "go_replay")
            pygame.draw.rect(surface, (245, 180, 20) if is_rep_hov else (225, 150, 10), r_replay, border_radius=8)
            pygame.draw.rect(surface, (255, 245, 180) if is_rep_hov else (140, 80, 10), r_replay, 2, border_radius=8)
            rep_s = self.font_btn_sm.render("PLAY AGAIN (SPACE)", True, (20, 25, 10))
            surface.blit(rep_s, (r_replay.centerx - rep_s.get_width() // 2, r_replay.centery - rep_s.get_height() // 2))

            # [ MAIN MENU ]
            r_menu = pygame.Rect(cx + 12, btn_y, btn_w, btn_h)
            self.buttons["go_menu"] = r_menu
            is_men_hov = (self.hovered_btn == "go_menu")
            pygame.draw.rect(surface, (45, 60, 95) if is_men_hov else (20, 28, 48), r_menu, border_radius=8)
            pygame.draw.rect(surface, (255, 215, 60) if is_men_hov else (70, 95, 135), r_menu, 2, border_radius=8)
            men_s = self.font_btn_sm.render("MAIN MENU (ESC)", True, (240, 245, 255))
            surface.blit(men_s, (r_menu.centerx - men_s.get_width() // 2, r_menu.centery - men_s.get_height() // 2))
