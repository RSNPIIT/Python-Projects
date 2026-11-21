"""Bubble Blast - Main Game Engine, Modes & UI Flow"""
import math
import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_BG, COLOR_CARD_BG, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED, COLOR_TEXT_GOLD,
    STAGE_RED, STAGE_GREEN, STAGE_YELLOW, STAGE_BLUE, BUBBLE_COLORS
)
from core.grid import BubbleGrid
from core.levels import LEVELS, generate_arcade_wave
from systems.particles import ParticleSystem
from systems.sound import SoundManager

class BubbleBlastGame:
    def __init__(self):
        self.particles = ParticleSystem()
        self.sound = SoundManager()
        self.grid = BubbleGrid(self.particles, self.sound)

        # Cross-Platform Fonts
        pygame.font.init()
        font_names = ["Arial", "Trebuchet MS", "Helvetica", "DejaVu Sans", "sans-serif"]
        self.font_hero = pygame.font.SysFont(font_names, 40, bold=True)
        self.font_title = pygame.font.SysFont(font_names, 28, bold=True)
        self.font_subtitle = pygame.font.SysFont(font_names, 16)
        self.font_main = pygame.font.SysFont(font_names, 20, bold=True)
        self.font_small = pygame.font.SysFont(font_names, 13, bold=True)
        self.font_tiny = pygame.font.SysFont(font_names, 11, bold=True)

        # States: "MENU", "PLAYING", "VICTORY", "DEFEAT"
        self.state = "MENU"
        self.mode = "PUZZLE"  # "PUZZLE" or "ARCADE"

        # Game Progress
        self.current_level_idx = 0
        self.arcade_wave = 1
        self.touches_left = 1
        self.max_touches = 1
        self.score = 0
        self.high_score = 0
        self.settling_delay = 0.0

        # Main Menu Buttons (540 x 860)
        self.btn_menu_puzzle = pygame.Rect(50, 240, 440, 110)
        self.btn_menu_arcade = pygame.Rect(50, 375, 440, 110)
        self.btn_menu_quit = pygame.Rect(180, 520, 180, 42)

        # In-Game Top Bar Buttons
        self.btn_ingame_menu = pygame.Rect(20, 20, 95, 34)
        self.btn_ingame_retry = pygame.Rect(SCREEN_WIDTH - 115, 20, 95, 34)

        # Modal Dialog Buttons
        self.btn_modal_next = pygame.Rect(SCREEN_WIDTH // 2 - 90, 520, 180, 46)
        self.btn_modal_retry = pygame.Rect(SCREEN_WIDTH // 2 - 90, 520, 180, 46)

        # Quit Confirmation Dialog State
        self.show_quit_dialog = False
        card_w, card_h = 390, 220
        card_x = (SCREEN_WIDTH - card_w) // 2
        card_y = (SCREEN_HEIGHT - card_h) // 2
        btn_w, btn_h = 145, 44
        btn_y = card_y + card_h - 66
        self.btn_quit_yes = pygame.Rect(card_x + 30, btn_y, btn_w, btn_h)
        self.btn_quit_cancel = pygame.Rect(card_x + card_w - btn_w - 30, btn_y, btn_w, btn_h)

    def start_puzzle_level(self, level_idx: int):
        self.mode = "PUZZLE"
        self.current_level_idx = max(0, min(len(LEVELS) - 1, level_idx))
        level_data = LEVELS[self.current_level_idx]
        self.max_touches = level_data["touches"]
        self.touches_left = self.max_touches
        self.grid.load_level_layout(level_data["layout"])
        self.state = "PLAYING"
        self.settling_delay = 0.0

    def start_arcade_game(self):
        self.mode = "ARCADE"
        self.arcade_wave = 1
        self.score = 0
        layout, touches = generate_arcade_wave(self.arcade_wave)
        self.max_touches = touches
        self.touches_left = touches
        self.grid.load_level_layout(layout)
        self.state = "PLAYING"
        self.settling_delay = 0.0

    def next_arcade_wave(self):
        self.arcade_wave += 1
        layout, touches = generate_arcade_wave(self.arcade_wave)
        self.max_touches = touches
        self.touches_left = touches
        self.grid.load_level_layout(layout)
        self.state = "PLAYING"
        self.settling_delay = 0.0

    def retry_current_level(self):
        if self.mode == "PUZZLE":
            self.start_puzzle_level(self.current_level_idx)
        else:
            self.start_arcade_game()

    def request_quit(self):
        self.show_quit_dialog = True

    def cancel_quit(self):
        self.show_quit_dialog = False

    def handle_quit_click(self, mouse_pos: tuple[int, int]) -> str | None:
        if not self.show_quit_dialog:
            return None
        if self.btn_quit_yes.collidepoint(mouse_pos):
            return "quit"
        if self.btn_quit_cancel.collidepoint(mouse_pos):
            self.cancel_quit()
            return "cancel"
        return None

    def handle_mouse_down(self, mouse_pos: tuple[int, int], button: int):
        if button != 1:
            return

        mx, my = mouse_pos

        # Quit Dialog Check
        if self.show_quit_dialog:
            return

        # 1. State MENU
        if self.state == "MENU":
            if self.btn_menu_puzzle.collidepoint(mx, my):
                self.sound.play("tap")
                self.start_puzzle_level(0)
                return
            if self.btn_menu_arcade.collidepoint(mx, my):
                self.sound.play("tap")
                self.start_arcade_game()
                return
            if self.btn_menu_quit.collidepoint(mx, my):
                self.request_quit()
                return
            return

        # 2. State VICTORY
        if self.state == "VICTORY":
            if self.btn_modal_next.collidepoint(mx, my):
                self.sound.play("tap")
                if self.mode == "PUZZLE":
                    next_idx = (self.current_level_idx + 1) % len(LEVELS)
                    self.start_puzzle_level(next_idx)
                else:
                    self.next_arcade_wave()
            return

        # 3. State DEFEAT
        if self.state == "DEFEAT":
            if self.btn_modal_retry.collidepoint(mx, my):
                self.sound.play("tap")
                self.retry_current_level()
            return

        # 4. State PLAYING
        # Check Top Bar Buttons
        if self.btn_ingame_menu.collidepoint(mx, my):
            self.sound.play("tap")
            self.state = "MENU"
            return
        if self.btn_ingame_retry.collidepoint(mx, my):
            self.sound.play("tap")
            self.retry_current_level()
            return

        # Bubble Tap Handling (Only when board is quiescent & touches remaining)
        if self.grid.is_quiescent() and self.touches_left > 0:
            target_bubble = self.grid.get_bubble_at_pos(mx, my)
            if target_bubble is not None and target_bubble.is_alive:
                tapped = self.grid.tap_bubble(target_bubble)
                if tapped:
                    self.touches_left -= 1
                    self.settling_delay = 0.35

    def update(self, dt: float):
        if self.show_quit_dialog:
            return

        self.particles.update(dt)

        if self.state == "PLAYING":
            self.grid.update(dt)

            if self.settling_delay > 0:
                self.settling_delay -= dt
                return

            # Check outcome once all projectiles have dissipated
            if self.grid.is_quiescent():
                if self.grid.is_cleared():
                    self.state = "VICTORY"
                    self.sound.play("victory")
                    if self.mode == "ARCADE":
                        self.score += 500 * self.arcade_wave
                        if self.score > self.high_score:
                            self.high_score = self.score
                elif self.touches_left <= 0:
                    self.state = "DEFEAT"
                    self.sound.play("game_over")

    def draw(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        surface.fill(COLOR_BG)

        # 1. State MENU
        if self.state == "MENU":
            self._draw_main_menu(surface, mouse_pos)

        # 2. In-Game & Modal States
        elif self.state in ("PLAYING", "VICTORY", "DEFEAT"):
            self._draw_hud(surface, mouse_pos)
            self.grid.draw(surface)
            self.particles.draw(surface)

            if self.state == "VICTORY":
                self._draw_victory_modal(surface, mouse_pos)
            elif self.state == "DEFEAT":
                self._draw_defeat_modal(surface, mouse_pos)

        # 3. Quit Confirmation Dialog (Top layer)
        if self.show_quit_dialog:
            self._draw_quit_dialog(surface, mouse_pos)

    def _draw_main_menu(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        mx, my = mouse_pos

        # Header Title
        title_text = self.font_hero.render("BUBBLE BLAST", True, COLOR_TEXT_WHITE)
        surface.blit(title_text, ((SCREEN_WIDTH - title_text.get_width()) // 2, 90))

        subtitle_text = self.font_subtitle.render("The Classic Chain Reaction Puzzle", True, (130, 180, 240))
        surface.blit(subtitle_text, ((SCREEN_WIDTH - subtitle_text.get_width()) // 2, 145))

        # Decorative Preview Row of Glossy Bubbles
        stages = [STAGE_RED, STAGE_GREEN, STAGE_YELLOW, STAGE_BLUE]
        spacing = 54
        start_x = (SCREEN_WIDTH - (len(stages) - 1) * spacing) // 2
        for i, st in enumerate(stages):
            col = BUBBLE_COLORS[st]
            bx = start_x + i * spacing
            by = 195
            pygame.draw.circle(surface, col, (bx, by), 16)
            pygame.draw.circle(surface, (255, 255, 255), (bx - 5, by - 6), 3)

        # 1. PUZZLE MODE Button Card
        is_puz_hover = self.btn_menu_puzzle.collidepoint(mx, my)
        puz_bg = (32, 42, 64) if is_puz_hover else (22, 28, 44)
        puz_border = (60, 190, 255) if is_puz_hover else (35, 48, 75)
        pygame.draw.rect(surface, puz_bg, self.btn_menu_puzzle, border_radius=16)
        pygame.draw.rect(surface, puz_border, self.btn_menu_puzzle, width=2, border_radius=16)

        # Icon circle
        pygame.draw.circle(surface, BUBBLE_COLORS[STAGE_RED], (self.btn_menu_puzzle.x + 55, self.btn_menu_puzzle.y + 55), 32)
        pygame.draw.circle(surface, (255, 255, 255), (self.btn_menu_puzzle.x + 46, self.btn_menu_puzzle.y + 44), 6)

        surface.blit(self.font_title.render("PUZZLE MODE", True, COLOR_TEXT_WHITE), (self.btn_menu_puzzle.x + 110, self.btn_menu_puzzle.y + 24))
        surface.blit(self.font_subtitle.render(f"Levels 1-{len(LEVELS)} • Limited Touch Puzzles", True, COLOR_TEXT_MUTED), (self.btn_menu_puzzle.x + 110, self.btn_menu_puzzle.y + 60))

        # 2. ARCADE / ENDLESS MODE Button Card
        is_arc_hover = self.btn_menu_arcade.collidepoint(mx, my)
        arc_bg = (32, 42, 64) if is_arc_hover else (22, 28, 44)
        arc_border = (255, 180, 50) if is_arc_hover else (35, 48, 75)
        pygame.draw.rect(surface, arc_bg, self.btn_menu_arcade, border_radius=16)
        pygame.draw.rect(surface, arc_border, self.btn_menu_arcade, width=2, border_radius=16)

        # Icon circle
        pygame.draw.circle(surface, BUBBLE_COLORS[STAGE_GREEN], (self.btn_menu_arcade.x + 55, self.btn_menu_arcade.y + 55), 32)
        pygame.draw.circle(surface, (255, 255, 255), (self.btn_menu_arcade.x + 46, self.btn_menu_arcade.y + 44), 6)

        surface.blit(self.font_title.render("ARCADE MODE", True, COLOR_TEXT_WHITE), (self.btn_menu_arcade.x + 110, self.btn_menu_arcade.y + 24))
        surface.blit(self.font_subtitle.render("Endless Waves • High Score Challenge", True, COLOR_TEXT_MUTED), (self.btn_menu_arcade.x + 110, self.btn_menu_arcade.y + 60))

        # 3. QUIT Button
        is_quit_hover = self.btn_menu_quit.collidepoint(mx, my)
        q_bg = (55, 24, 34) if is_quit_hover else (32, 18, 26)
        q_border = (255, 75, 95) if is_quit_hover else (120, 35, 48)
        pygame.draw.rect(surface, q_bg, self.btn_menu_quit, border_radius=10)
        pygame.draw.rect(surface, q_border, self.btn_menu_quit, width=1, border_radius=10)
        q_lbl = self.font_small.render("QUIT GAME [Esc]", True, (255, 200, 210))
        surface.blit(q_lbl, q_lbl.get_rect(center=self.btn_menu_quit.center))

        # Footer
        footer = self.font_tiny.render("Red bubbles burst into 4 darts • Chain reactions pop the rest!", True, (100, 120, 150))
        surface.blit(footer, ((SCREEN_WIDTH - footer.get_width()) // 2, SCREEN_HEIGHT - 45))

    def _draw_hud(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        mx, my = mouse_pos

        # Header Plate
        pygame.draw.rect(surface, COLOR_CARD_BG, (0, 0, SCREEN_WIDTH, 140))
        pygame.draw.line(surface, (36, 44, 64), (0, 140), (SCREEN_WIDTH, 140), 1)

        # Top Bar: Menu Button
        is_menu_hover = self.btn_ingame_menu.collidepoint(mx, my)
        m_bg = (38, 48, 72) if is_menu_hover else (26, 33, 50)
        pygame.draw.rect(surface, m_bg, self.btn_ingame_menu, border_radius=8)
        pygame.draw.rect(surface, (50, 65, 95), self.btn_ingame_menu, width=1, border_radius=8)
        m_lbl = self.font_small.render("< MENU", True, (230, 235, 245))
        surface.blit(m_lbl, m_lbl.get_rect(center=self.btn_ingame_menu.center))

        # Top Bar: Retry Button
        is_retry_hover = self.btn_ingame_retry.collidepoint(mx, my)
        r_bg = (38, 48, 72) if is_retry_hover else (26, 33, 50)
        pygame.draw.rect(surface, r_bg, self.btn_ingame_retry, border_radius=8)
        pygame.draw.rect(surface, (50, 65, 95), self.btn_ingame_retry, width=1, border_radius=8)
        r_lbl = self.font_small.render("RETRY [R]", True, (230, 235, 245))
        surface.blit(r_lbl, r_lbl.get_rect(center=self.btn_ingame_retry.center))

        # Level / Mode Title in Center
        if self.mode == "PUZZLE":
            lvl_name = LEVELS[self.current_level_idx]["name"]
            title_str = f"LEVEL {self.current_level_idx + 1}: {lvl_name}"
        else:
            title_str = f"ARCADE WAVE {self.arcade_wave}"

        t_surf = self.font_main.render(title_str, True, COLOR_TEXT_WHITE)
        surface.blit(t_surf, t_surf.get_rect(center=(SCREEN_WIDTH // 2, 37)))

        # Touches Left Card
        card_w = 220
        card_rect = pygame.Rect((SCREEN_WIDTH - card_w) // 2, 68, card_w, 56)
        pygame.draw.rect(surface, (14, 18, 28), card_rect, border_radius=12)
        pygame.draw.rect(surface, (45, 60, 90), card_rect, width=1, border_radius=12)

        lbl = self.font_tiny.render("TOUCHES LEFT", True, COLOR_TEXT_MUTED)
        surface.blit(lbl, lbl.get_rect(center=(SCREEN_WIDTH // 2, 84)))

        # Large Touch Number
        touch_col = (255, 75, 95) if self.touches_left == 1 else (50, 220, 130)
        num_surf = self.font_title.render(f"{self.touches_left}", True, touch_col)
        surface.blit(num_surf, num_surf.get_rect(center=(SCREEN_WIDTH // 2, 107)))

        # Score in Arcade Mode
        if self.mode == "ARCADE":
            score_txt = self.font_small.render(f"SCORE: {self.score:,}", True, COLOR_TEXT_GOLD)
            surface.blit(score_txt, (SCREEN_WIDTH - score_txt.get_width() - 25, 95))

    def _draw_victory_modal(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 16, 215))
        surface.blit(overlay, (0, 0))

        card_w, card_h = 390, 260
        card_rect = pygame.Rect((SCREEN_WIDTH - card_w) // 2, (SCREEN_HEIGHT - card_h) // 2 - 20, card_w, card_h)
        pygame.draw.rect(surface, COLOR_CARD_BG, card_rect, border_radius=20)
        pygame.draw.rect(surface, (50, 220, 130), card_rect, width=2, border_radius=20)

        # Star / Trophy Icon
        pygame.draw.circle(surface, COLOR_TEXT_GOLD, (SCREEN_WIDTH // 2, card_rect.top + 45), 24)
        pygame.draw.circle(surface, (255, 255, 255), (SCREEN_WIDTH // 2, card_rect.top + 45), 18)

        t = self.font_title.render("LEVEL CLEARED!", True, (50, 220, 130))
        surface.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, card_rect.top + 95)))

        sub = self.font_subtitle.render("Outstanding Chain Reaction!", True, COLOR_TEXT_WHITE)
        surface.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, card_rect.top + 130)))

        # Next Level Button
        self.btn_modal_next.top = card_rect.bottom - 65
        is_hover = self.btn_modal_next.collidepoint(mouse_pos)
        btn_bg = (40, 195, 110) if is_hover else (30, 155, 85)
        pygame.draw.rect(surface, btn_bg, self.btn_modal_next, border_radius=12)
        btn_lbl = self.font_main.render("NEXT LEVEL >", True, (255, 255, 255))
        surface.blit(btn_lbl, btn_lbl.get_rect(center=self.btn_modal_next.center))

    def _draw_defeat_modal(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 16, 215))
        surface.blit(overlay, (0, 0))

        card_w, card_h = 390, 260
        card_rect = pygame.Rect((SCREEN_WIDTH - card_w) // 2, (SCREEN_HEIGHT - card_h) // 2 - 20, card_w, card_h)
        pygame.draw.rect(surface, COLOR_CARD_BG, card_rect, border_radius=20)
        pygame.draw.rect(surface, (255, 65, 85), card_rect, width=2, border_radius=20)

        t = self.font_title.render("OUT OF TOUCHES!", True, (255, 65, 85))
        surface.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, card_rect.top + 55)))

        sub = self.font_subtitle.render("Find the right bubble to start the chain!", True, COLOR_TEXT_MUTED)
        surface.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, card_rect.top + 105)))

        # Retry Button
        self.btn_modal_retry.top = card_rect.bottom - 65
        is_hover = self.btn_modal_retry.collidepoint(mouse_pos)
        btn_bg = (235, 55, 80) if is_hover else (175, 38, 56)
        pygame.draw.rect(surface, btn_bg, self.btn_modal_retry, border_radius=12)
        btn_lbl = self.font_main.render("TRY AGAIN [R]", True, (255, 255, 255))
        surface.blit(btn_lbl, btn_lbl.get_rect(center=self.btn_modal_retry.center))

    def _draw_quit_dialog(self, surface: pygame.Surface, mouse_pos: tuple[int, int]):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 16, 225))
        surface.blit(overlay, (0, 0))

        card_w, card_h = 390, 220
        card_x = (SCREEN_WIDTH - card_w) // 2
        card_y = (SCREEN_HEIGHT - card_h) // 2
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        pygame.draw.rect(surface, COLOR_CARD_BG, card_rect, border_radius=18)
        pygame.draw.rect(surface, (255, 65, 95), card_rect, width=2, border_radius=18)

        title = self.font_title.render("QUIT GAME?", True, (255, 75, 105))
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, card_y + 45)))

        msg = self.font_subtitle.render("Are you sure you want to quit?", True, (230, 235, 245))
        surface.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2, card_y + 92)))

        # Buttons
        is_quit_hover = self.btn_quit_yes.collidepoint(mouse_pos)
        q_bg = (235, 55, 80) if is_quit_hover else (175, 38, 56)
        pygame.draw.rect(surface, q_bg, self.btn_quit_yes, border_radius=10)
        q_lbl = self.font_subtitle.render("YES, QUIT [Y]", True, (255, 255, 255))
        surface.blit(q_lbl, q_lbl.get_rect(center=self.btn_quit_yes.center))

        is_cancel_hover = self.btn_quit_cancel.collidepoint(mouse_pos)
        c_bg = (55, 68, 95) if is_cancel_hover else (35, 44, 62)
        pygame.draw.rect(surface, c_bg, self.btn_quit_cancel, border_radius=10)
        c_lbl = self.font_subtitle.render("CANCEL [Esc]", True, (255, 255, 255))
        surface.blit(c_lbl, c_lbl.get_rect(center=self.btn_quit_cancel.center))
