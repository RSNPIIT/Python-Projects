"""Kapman Game - State Machine, Rules, Collision & Scoring"""
import math
import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TOP_BAR_HEIGHT, BOTTOM_BAR_HEIGHT,
    MAZE_WIDTH, MAZE_HEIGHT, TILE_SIZE,
    DIR_NONE, DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    GHOST_CHASE, GHOST_SCATTER, GHOST_FRIGHTENED, GHOST_EATEN,
    GHOST_SCORES, FRIGHTENED_DURATION, EXTRA_LIFE_THRESHOLD,
    THEME_EGYPTIAN, THEME_CLASSIC,
    COLOR_BG_DARK, COLOR_TEXT_GOLD, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED
)
from core.maze import Maze
from core.kapman import Kapman
from core.ghost import Ghost, GHOST_RED, GHOST_PINK, GHOST_CYAN, GHOST_ORANGE
from core.items import BonusItem, FloatingScore
from systems.renderer import GameRenderer
from systems.sound import SoundManager
from systems.particles import ParticleSystem

class KapmanGame:
    def __init__(self):
        self.maze = Maze()
        self.kapman = Kapman(start_col=13.5, start_row=23.0)
        self.ghosts = [
            Ghost(GHOST_RED, start_col=13.5, start_row=11.0, scatter_col=27, scatter_row=0),
            Ghost(GHOST_PINK, start_col=13.5, start_row=14.0, scatter_col=0, scatter_row=0),
            Ghost(GHOST_CYAN, start_col=11.5, start_row=14.0, scatter_col=27, scatter_row=30),
            Ghost(GHOST_ORANGE, start_col=15.5, start_row=14.0, scatter_col=0, scatter_row=30)
        ]

        self.renderer = GameRenderer()
        self.sound = SoundManager()
        self.particles = ParticleSystem()
        self.floating_scores: list[FloatingScore] = []

        # Cross-Platform Safe Fonts
        pygame.font.init()
        font_names = ["Arial", "Trebuchet MS", "Helvetica", "DejaVu Sans", "sans-serif"]
        self.font_hero = pygame.font.SysFont(font_names, 36, bold=True)
        self.font_title = pygame.font.SysFont(font_names, 24, bold=True)
        self.font_sub = pygame.font.SysFont(font_names, 16, bold=True)
        self.font_hud = pygame.font.SysFont(font_names, 14, bold=True)
        self.font_small = pygame.font.SysFont(font_names, 12, bold=True)

        # Game State: "MENU", "READY", "PLAYING", "PAUSED", "GAME_OVER"
        self.state = "MENU"
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.next_extra_life = EXTRA_LIFE_THRESHOLD

        # Timers & Cycles
        self.anim_time = 0.0
        self.fright_timer = 0.0
        self.ghosts_eaten_in_fright = 0
        self.scatter_cycle_timer = 0.0
        self.global_ghost_mode = GHOST_SCATTER

        # Bonus item
        self.bonus_item: BonusItem | None = None
        self.spawned_bonus_70 = False
        self.spawned_bonus_170 = False

        # Modals
        self.show_quit_dialog = False
        self.should_exit = False

        # UI Buttons (560 x 700)
        self.btn_menu_play = pygame.Rect(SCREEN_WIDTH // 2 - 140, 320, 280, 52)
        self.btn_menu_theme = pygame.Rect(SCREEN_WIDTH // 2 - 140, 385, 280, 52)
        self.btn_menu_quit = pygame.Rect(SCREEN_WIDTH // 2 - 90, 455, 180, 42)

    def start_new_game(self):
        self.score = 0
        self.level = 1
        self.kapman.lives = 3
        self.next_extra_life = EXTRA_LIFE_THRESHOLD
        self._setup_level(self.level)
        self.state = "READY"

    def _setup_level(self, level: int):
        self.maze.reset()
        self.kapman.reset()
        for g in self.ghosts:
            g.reset()

        self.fright_timer = 0.0
        self.ghosts_eaten_in_fright = 0
        self.scatter_cycle_timer = 0.0
        self.global_ghost_mode = GHOST_SCATTER
        self.bonus_item = None
        self.spawned_bonus_70 = False
        self.spawned_bonus_170 = False
        self.floating_scores.clear()

    def reset_round_positions(self):
        self.kapman.reset()
        for g in self.ghosts:
            g.reset()
        self.fright_timer = 0.0
        self.ghosts_eaten_in_fright = 0
        self.state = "READY"

    def handle_keydown(self, key):
        if self.show_quit_dialog:
            if key in (pygame.K_y, pygame.K_RETURN):
                self.should_exit = True
            elif key in (pygame.K_n, pygame.K_ESCAPE):
                self.show_quit_dialog = False
            return

        if key == pygame.K_ESCAPE:
            if self.state == "PLAYING":
                self.state = "PAUSED"
            elif self.state == "PAUSED":
                self.state = "PLAYING"
            else:
                self.show_quit_dialog = True
            return

        if key in (pygame.K_t,):
            self.renderer.toggle_theme()
            return

        if self.state == "MENU":
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                self.start_new_game()
            return

        if self.state == "READY":
            # Any direction key starts game movement!
            if key in (pygame.K_UP, pygame.K_w):
                self.kapman.set_desired_direction(DIR_UP)
                self.state = "PLAYING"
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.kapman.set_desired_direction(DIR_DOWN)
                self.state = "PLAYING"
            elif key in (pygame.K_LEFT, pygame.K_a):
                self.kapman.set_desired_direction(DIR_LEFT)
                self.state = "PLAYING"
            elif key in (pygame.K_RIGHT, pygame.K_d):
                self.kapman.set_desired_direction(DIR_RIGHT)
                self.state = "PLAYING"
            elif key in (pygame.K_SPACE, pygame.K_RETURN):
                self.kapman.set_desired_direction(DIR_LEFT)
                self.state = "PLAYING"
            return

        if self.state == "PLAYING":
            if key in (pygame.K_UP, pygame.K_w):
                self.kapman.set_desired_direction(DIR_UP)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.kapman.set_desired_direction(DIR_DOWN)
            elif key in (pygame.K_LEFT, pygame.K_a):
                self.kapman.set_desired_direction(DIR_LEFT)
            elif key in (pygame.K_RIGHT, pygame.K_d):
                self.kapman.set_desired_direction(DIR_RIGHT)
            elif key == pygame.K_p:
                self.state = "PAUSED"
            return

        if self.state == "PAUSED":
            if key in (pygame.K_p, pygame.K_SPACE, pygame.K_RETURN):
                self.state = "PLAYING"
            elif key == pygame.K_m:
                self.state = "MENU"
            return

        if self.state == "GAME_OVER":
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                self.start_new_game()
            elif key == pygame.K_m:
                self.state = "MENU"
            return

    def handle_click(self, pos: tuple[int, int]):
        if self.show_quit_dialog:
            dialog_w, dialog_h = 360, 200
            dx = (SCREEN_WIDTH - dialog_w) // 2
            dy = (SCREEN_HEIGHT - dialog_h) // 2
            btn_confirm = pygame.Rect(dx + 30, dy + 125, 140, 44)
            btn_cancel = pygame.Rect(dx + 190, dy + 125, 140, 44)

            if btn_confirm.collidepoint(pos):
                self.should_exit = True
            elif btn_cancel.collidepoint(pos):
                self.show_quit_dialog = False
            return

        if self.state == "MENU":
            if self.btn_menu_play.collidepoint(pos):
                self.start_new_game()
            elif self.btn_menu_theme.collidepoint(pos):
                self.renderer.toggle_theme()
            elif self.btn_menu_quit.collidepoint(pos):
                self.show_quit_dialog = True
            return

        if self.state in ("GAME_OVER", "PAUSED"):
            btn_action = pygame.Rect(SCREEN_WIDTH // 2 - 130, 400, 260, 50)
            btn_menu = pygame.Rect(SCREEN_WIDTH // 2 - 90, 465, 180, 40)
            if btn_action.collidepoint(pos):
                if self.state == "GAME_OVER":
                    self.start_new_game()
                else:
                    self.state = "PLAYING"
            elif btn_menu.collidepoint(pos):
                self.state = "MENU"

    def update(self, dt: float):
        if self.show_quit_dialog:
            return

        self.anim_time += dt
        self.particles.update(dt)
        self.floating_scores = [fs for fs in self.floating_scores if fs.update(dt)]

        if self.state != "PLAYING":
            if self.state == "PLAYING" and self.kapman.dying:
                self.kapman.update(dt, self.maze)
            return

        # 1. Update Scatter / Chase cycle
        self.scatter_cycle_timer += dt
        if self.scatter_cycle_timer < 7.0:
            self.global_ghost_mode = GHOST_SCATTER
        elif self.scatter_cycle_timer < 27.0:
            self.global_ghost_mode = GHOST_CHASE
        else:
            self.scatter_cycle_timer = 0.0

        # 2. Update Frightened Timer
        is_energized = (self.fright_timer > 0)
        if is_energized:
            self.fright_timer -= dt
            if self.fright_timer <= 0:
                self.fright_timer = 0.0

        # 3. Update Kapman Movement
        self.kapman.update(dt, self.maze, is_energized=is_energized)

        # If dying, pause ghost movements until death animation completes
        if self.kapman.dying:
            return

        if not self.kapman.alive:
            self.kapman.lives -= 1
            if self.kapman.lives > 0:
                self.reset_round_positions()
            else:
                self.state = "GAME_OVER"
                self.sound.play("death")
            return

        # 4. Check Pill / Energizer Consumption
        k_col = self.kapman.col
        k_row = self.kapman.row
        dist_to_center = abs(self.kapman.x - self.kapman.center_tile_x) + abs(self.kapman.y - self.kapman.center_tile_y)

        if dist_to_center < 7.0:
            pts, is_energizer = self.maze.eat_pellet(k_row, k_col)
            if pts > 0:
                self.score += pts
                if self.score > self.high_score:
                    self.high_score = self.score

                # Extra life check
                if self.score >= self.next_extra_life:
                    self.kapman.lives = min(self.kapman.lives + 1, 5)
                    self.next_extra_life += EXTRA_LIFE_THRESHOLD
                    self.sound.play("bonus")

                if is_energizer:
                    self.fright_timer = FRIGHTENED_DURATION
                    self.ghosts_eaten_in_fright = 0
                    self.sound.play("energizer")
                    for g in self.ghosts:
                        g.become_frightened()
                    self.particles.emit_sparks(self.kapman.x, self.kapman.y, (255, 230, 90), count=16)
                else:
                    self.sound.play_chomp()
                    self.particles.emit_sparks(self.kapman.x, self.kapman.y, (245, 240, 200), count=4)

                # Bonus item spawn thresholds (70 and 170 pellets eaten)
                eaten_count = self.maze.total_pills - self.maze.pills_remaining
                if eaten_count >= 70 and not self.spawned_bonus_70:
                    self.spawned_bonus_70 = True
                    self.bonus_item = BonusItem(self.level)
                elif eaten_count >= 170 and not self.spawned_bonus_170:
                    self.spawned_bonus_170 = True
                    self.bonus_item = BonusItem(self.level)

        # 5. Update Bonus Item
        if self.bonus_item:
            if not self.bonus_item.update(dt):
                self.bonus_item = None
            else:
                dx = abs(self.kapman.x - self.bonus_item.x)
                dy = abs(self.kapman.y - self.bonus_item.y)
                if dx < 12.0 and dy < 12.0:
                    self.score += self.bonus_item.points
                    self.sound.play("bonus")
                    self.floating_scores.append(FloatingScore(self.bonus_item.x, self.bonus_item.y, self.bonus_item.points))
                    self.bonus_item = None

        # 6. Update Ghosts
        red_ghost_pos = (self.ghosts[GHOST_RED].x, self.ghosts[GHOST_RED].y)
        kapman_pos = (self.kapman.x, self.kapman.y)
        kapman_dir = self.kapman.direction

        for g in self.ghosts:
            g.update(
                dt, self.maze,
                kapman_pos=kapman_pos,
                kapman_dir=kapman_dir,
                red_ghost_pos=red_ghost_pos,
                global_mode=self.global_ghost_mode
            )

        # 7. Ghost vs Kapman Collisions
        for g in self.ghosts:
            dx = abs(self.kapman.x - g.x)
            dy = abs(self.kapman.y - g.y)
            if dx < 11.0 and dy < 11.0:
                if g.state == GHOST_FRIGHTENED:
                    # Eat Ghost!
                    g.become_eaten()
                    combo_idx = min(self.ghosts_eaten_in_fright, len(GHOST_SCORES) - 1)
                    ghost_pts = GHOST_SCORES[combo_idx]
                    self.ghosts_eaten_in_fright += 1

                    self.score += ghost_pts
                    if self.score > self.high_score:
                        self.high_score = self.score

                    self.sound.play("eat_ghost")
                    self.floating_scores.append(FloatingScore(g.x, g.y, ghost_pts, color=(80, 220, 255)))
                    self.particles.emit_sparks(g.x, g.y, (80, 220, 255), count=16)

                elif g.state in (GHOST_CHASE, GHOST_SCATTER):
                    # Kapman takes fatal hit!
                    self.kapman.dying = True
                    self.sound.play("death")
                    break

        # 8. Check Level Complete
        if self.maze.is_cleared():
            self.sound.play("victory")
            self.level += 1
            self._setup_level(self.level)
            self.state = "READY"

    def draw(self, surface: pygame.Surface):
        surface.fill(COLOR_BG_DARK)

        # 1. Top HUD Bar
        self._draw_hud(surface)

        # 2. Main Maze
        offset_y = TOP_BAR_HEIGHT
        self.renderer.draw_maze(surface, self.maze, offset_y, self.anim_time, self.fright_timer)

        # 3. Bonus Collectible
        if self.bonus_item:
            self.renderer.draw_bonus_item(surface, self.bonus_item, offset_y)

        # 4. Characters
        self.renderer.draw_kapman(surface, self.kapman, offset_y)
        for g in self.ghosts:
            self.renderer.draw_ghost(surface, g, offset_y, self.fright_timer, self.anim_time)

        # 5. Particles & Floating Scores
        self.particles.draw(surface, offset_y=offset_y)
        for fs in self.floating_scores:
            fs.draw(surface, self.font_hud, offset_y=offset_y)

        # 6. Bottom Status Bar (Lives & Theme pill)
        self._draw_bottom_bar(surface)

        # 7. State Overlays
        if self.state == "MENU":
            self._draw_menu(surface)
        elif self.state == "READY":
            self._draw_ready_message(surface)
        elif self.state == "PAUSED":
            self._draw_pause_card(surface)
        elif self.state == "GAME_OVER":
            self._draw_game_over_card(surface)

        # 8. Quit Dialog
        if self.show_quit_dialog:
            self._draw_quit_dialog(surface)

    def _draw_hud(self, surface: pygame.Surface):
        bar = pygame.Rect(0, 0, SCREEN_WIDTH, TOP_BAR_HEIGHT)
        pygame.draw.rect(surface, (18, 22, 34), bar)
        pygame.draw.line(surface, (40, 52, 78), (0, TOP_BAR_HEIGHT - 1), (SCREEN_WIDTH, TOP_BAR_HEIGHT - 1), 1)

        # Score
        lbl_score = self.font_small.render("SCORE", True, COLOR_TEXT_MUTED)
        val_score = self.font_hud.render(f"{self.score:,}", True, COLOR_TEXT_WHITE)
        surface.blit(lbl_score, (20, 10))
        surface.blit(val_score, (20, 26))

        # High Score
        lbl_hi = self.font_small.render("HIGH SCORE", True, COLOR_TEXT_MUTED)
        val_hi = self.font_hud.render(f"{self.high_score:,}", True, COLOR_TEXT_GOLD)
        surface.blit(lbl_hi, (SCREEN_WIDTH // 2 - 40, 10))
        surface.blit(val_hi, (SCREEN_WIDTH // 2 - 40, 26))

        # Level Badge
        lvl_rect = pygame.Rect(SCREEN_WIDTH - 110, 10, 95, 30)
        pygame.draw.rect(surface, (28, 36, 56), lvl_rect, border_radius=6)
        pygame.draw.rect(surface, (60, 80, 120), lvl_rect, width=1, border_radius=6)
        lvl_txt = self.font_hud.render(f"LEVEL {self.level}", True, (80, 215, 255))
        surface.blit(lvl_txt, lvl_txt.get_rect(center=lvl_rect.center))

    def _draw_bottom_bar(self, surface: pygame.Surface):
        by = SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT
        bar = pygame.Rect(0, by, SCREEN_WIDTH, BOTTOM_BAR_HEIGHT)
        pygame.draw.rect(surface, (18, 22, 34), bar)
        pygame.draw.line(surface, (40, 52, 78), (0, by), (SCREEN_WIDTH, by), 1)

        # Lives Indicator Icons
        lbl_lives = self.font_small.render("LIVES:", True, COLOR_TEXT_MUTED)
        surface.blit(lbl_lives, (16, by + 8))

        for i in range(self.kapman.lives):
            lx = 75 + i * 22
            ly = by + 15
            if self.renderer.theme == THEME_EGYPTIAN:
                # Explorer Fedora Icon
                pygame.draw.ellipse(surface, (125, 80, 40), (lx - 7, ly - 3, 14, 5))
                pygame.draw.rect(surface, (140, 90, 45), (lx - 4, ly - 7, 8, 5), border_radius=2)
            else:
                # Classic Yellow Wedge Icon
                pygame.draw.circle(surface, (255, 220, 30), (lx, ly), 7)

        # Theme Shortcut Pill
        t_name = "EGYPTIAN TOMB" if self.renderer.theme == THEME_EGYPTIAN else "CLASSIC ARCADE"
        theme_txt = self.font_small.render(f"[T] THEME: {t_name}", True, COLOR_TEXT_MUTED)
        surface.blit(theme_txt, (SCREEN_WIDTH - theme_txt.get_width() - 16, by + 8))

    def _draw_ready_message(self, surface: pygame.Surface):
        """Displays 'Level X' and 'Press any arrow key to start' in maze center (matching Image 1)."""
        cy = TOP_BAR_HEIGHT + (17.5 * TILE_SIZE)

        # Level Title
        lvl_text = self.font_hero.render(f"Level {self.level}", True, COLOR_TEXT_GOLD)
        surface.blit(lvl_text, lvl_text.get_rect(center=(SCREEN_WIDTH // 2, cy - 20)))

        # Subtitle
        pulse = 0.5 + 0.5 * math.sin(self.anim_time * 6.0)
        col = (255, int(215 * pulse + 40), 50)
        start_text = self.font_sub.render("Press any arrow key to start", True, col)
        surface.blit(start_text, start_text.get_rect(center=(SCREEN_WIDTH // 2, cy + 20)))

    def _draw_menu(self, surface: pygame.Surface):
        # Translucent backdrop
        scrim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(scrim, (10, 12, 20, 220), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.blit(scrim, (0, 0))

        # Hero Title
        title = self.font_hero.render("KAPMAN", True, COLOR_TEXT_GOLD)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 170)))

        subtitle = self.font_sub.render("THE CLASSIC RETRO MAZE CHASE", True, (130, 180, 255))
        surface.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 215)))

        # Preview Characters
        preview_y = 265
        # Draw Explorer in center
        pygame.draw.circle(surface, (255, 215, 180), (SCREEN_WIDTH // 2, preview_y - 2), 7)
        pygame.draw.rect(surface, (200, 45, 55), (SCREEN_WIDTH // 2 - 6, preview_y + 1, 12, 9), border_radius=2)
        pygame.draw.ellipse(surface, (125, 80, 40), (SCREEN_WIDTH // 2 - 10, preview_y - 8, 20, 6))

        # 4 Mummies on sides
        m_colors = [(240, 50, 60), (255, 130, 180), (45, 215, 240), (255, 160, 40)]
        for idx, col in enumerate(m_colors):
            mx = SCREEN_WIDTH // 2 - 90 + idx * 60
            if idx >= 2:
                mx += 20
            pygame.draw.ellipse(surface, (235, 225, 200), (mx - 7, preview_y - 6, 14, 18))
            pygame.draw.rect(surface, col, (mx - 7, preview_y + 1, 14, 3))

        mouse_pos = pygame.mouse.get_pos()
        theme_str = "THEME: EGYPTIAN" if self.renderer.theme == THEME_EGYPTIAN else "THEME: CLASSIC"
        buttons = [
            (self.btn_menu_play, "START GAME", (45, 130, 240)),
            (self.btn_menu_theme, theme_str, (180, 130, 45)),
            (self.btn_menu_quit, "QUIT", (200, 50, 70))
        ]

        for rect, label, accent in buttons:
            is_hover = rect.collidepoint(mouse_pos)
            bg = (34, 45, 70) if is_hover else (22, 28, 46)
            border = accent if is_hover else (45, 60, 95)
            pygame.draw.rect(surface, bg, rect, border_radius=12)
            pygame.draw.rect(surface, border, rect, width=2 if is_hover else 1, border_radius=12)
            txt = self.font_title.render(label, True, COLOR_TEXT_WHITE)
            surface.blit(txt, txt.get_rect(center=rect.center))

    def _draw_pause_card(self, surface: pygame.Surface):
        scrim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(scrim, (10, 12, 20, 200), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.blit(scrim, (0, 0))

        card = pygame.Rect(SCREEN_WIDTH // 2 - 160, 280, 320, 220)
        pygame.draw.rect(surface, (22, 28, 46), card, border_radius=16)
        pygame.draw.rect(surface, (60, 85, 140), card, width=2, border_radius=16)

        t = self.font_title.render("GAME PAUSED", True, COLOR_TEXT_GOLD)
        surface.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 330)))

        btn_action = pygame.Rect(SCREEN_WIDTH // 2 - 120, 375, 240, 46)
        pygame.draw.rect(surface, (35, 120, 210), btn_action, border_radius=10)
        res_txt = self.font_hud.render("RESUME [P]", True, COLOR_TEXT_WHITE)
        surface.blit(res_txt, res_txt.get_rect(center=btn_action.center))

        btn_menu = pygame.Rect(SCREEN_WIDTH // 2 - 90, 435, 180, 38)
        pygame.draw.rect(surface, (40, 52, 78), btn_menu, border_radius=8)
        m_txt = self.font_small.render("MAIN MENU [M]", True, COLOR_TEXT_MUTED)
        surface.blit(m_txt, m_txt.get_rect(center=btn_menu.center))

    def _draw_game_over_card(self, surface: pygame.Surface):
        scrim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(scrim, (10, 12, 20, 220), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.blit(scrim, (0, 0))

        card = pygame.Rect(SCREEN_WIDTH // 2 - 170, 250, 340, 270)
        pygame.draw.rect(surface, (28, 18, 26), card, border_radius=16)
        pygame.draw.rect(surface, (255, 60, 90), card, width=2, border_radius=16)

        t = self.font_title.render("GAME OVER", True, (255, 70, 95))
        surface.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 300)))

        sub = self.font_sub.render(f"Final Score: {self.score:,}", True, COLOR_TEXT_WHITE)
        surface.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, 345)))

        hi = self.font_small.render(f"High Score: {self.high_score:,}", True, COLOR_TEXT_GOLD)
        surface.blit(hi, hi.get_rect(center=(SCREEN_WIDTH // 2, 375)))

        btn_retry = pygame.Rect(SCREEN_WIDTH // 2 - 120, 410, 240, 46)
        pygame.draw.rect(surface, (180, 50, 75), btn_retry, border_radius=10)
        r_txt = self.font_hud.render("PLAY AGAIN [SPACE]", True, COLOR_TEXT_WHITE)
        surface.blit(r_txt, r_txt.get_rect(center=btn_retry.center))

        btn_menu = pygame.Rect(SCREEN_WIDTH // 2 - 90, 470, 180, 38)
        pygame.draw.rect(surface, (40, 52, 78), btn_menu, border_radius=8)
        m_txt = self.font_small.render("MAIN MENU [M]", True, COLOR_TEXT_MUTED)
        surface.blit(m_txt, m_txt.get_rect(center=btn_menu.center))

    def _draw_quit_dialog(self, surface: pygame.Surface):
        scrim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(scrim, (8, 10, 16, 215), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.blit(scrim, (0, 0))

        dialog_w, dialog_h = 360, 200
        dx = (SCREEN_WIDTH - dialog_w) // 2
        dy = (SCREEN_HEIGHT - dialog_h) // 2
        d_rect = pygame.Rect(dx, dy, dialog_w, dialog_h)

        pygame.draw.rect(surface, (20, 26, 42), d_rect, border_radius=16)
        pygame.draw.rect(surface, (255, 80, 100), d_rect, width=2, border_radius=16)

        t = self.font_title.render("QUIT GAME?", True, COLOR_TEXT_WHITE)
        surface.blit(t, t.get_rect(center=(dx + dialog_w // 2, dy + 45)))

        msg = self.font_small.render("Are you sure you want to exit?", True, COLOR_TEXT_MUTED)
        surface.blit(msg, msg.get_rect(center=(dx + dialog_w // 2, dy + 85)))

        mouse_pos = pygame.mouse.get_pos()
        btn_confirm = pygame.Rect(dx + 30, dy + 125, 140, 44)
        btn_cancel = pygame.Rect(dx + 190, dy + 125, 140, 44)

        h_conf = btn_confirm.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (200, 50, 70) if h_conf else (150, 35, 50), btn_confirm, border_radius=10)
        c_lbl = self.font_hud.render("QUIT [Y]", True, COLOR_TEXT_WHITE)
        surface.blit(c_lbl, c_lbl.get_rect(center=btn_confirm.center))

        h_canc = btn_cancel.collidepoint(mouse_pos)
        pygame.draw.rect(surface, (45, 60, 90) if h_canc else (30, 42, 65), btn_cancel, border_radius=10)
        can_lbl = self.font_hud.render("CANCEL [N]", True, COLOR_TEXT_WHITE)
        surface.blit(can_lbl, can_lbl.get_rect(center=btn_cancel.center))
