"""2048 Game - Master Controller, Input Handling, Swipes & High Score Persistence"""
import json
import os
import pygame
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BOARD_OFFSET_X, BOARD_OFFSET_Y, BOARD_WIDTH, BOARD_HEIGHT,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
)
from core.board import Board
from systems.renderer import GameRenderer
from systems.sound import SoundManager

BEST_SCORE_FILE = os.path.join(os.path.dirname(__file__), "best_score.json")

class Game2048:
    def __init__(self):
        self.board = Board()
        self.renderer = GameRenderer()
        self.sound = SoundManager()

        self.anim_time = 0.0
        self.show_quit_dialog = False
        self.should_exit = False

        # Mouse drag / swipe detection
        self.drag_start_pos: tuple[int, int] | None = None
        self.min_swipe_dist = 28  # px threshold for swipe

        # Load persisted best score
        self._load_best_score()

        # Start initial game
        self.board.reset()
        self.board.best_score = self.best_score

    def _load_best_score(self):
        self.best_score = 0
        if os.path.exists(BEST_SCORE_FILE):
            try:
                with open(BEST_SCORE_FILE, "r") as f:
                    data = json.load(f)
                    self.best_score = int(data.get("best_score", 0))
            except Exception:
                self.best_score = 0

    def _save_best_score(self):
        try:
            with open(BEST_SCORE_FILE, "w") as f:
                json.dump({"best_score": self.best_score}, f)
        except Exception:
            pass

    def start_new_game(self):
        """Starts a clean new game session."""
        self.sound.play("click")
        self.board.reset()
        self.board.best_score = self.best_score

    def execute_move(self, direction: tuple[int, int]):
        """Executes a move in the chosen direction and triggers appropriate audio."""
        if self.show_quit_dialog:
            return
        if self.board.has_won and not self.board.keep_playing:
            return
        if self.board.game_over:
            return

        res = self.board.move(direction)
        if res.moved:
            # Play slide sound
            self.sound.play("slide")

            # Play musical chime for merges
            if res.merged_values:
                highest_merge = max(res.merged_values)
                self.sound.play_merge(highest_merge)

            # Update best score
            if self.board.score > self.best_score:
                self.best_score = self.board.score
                self.board.best_score = self.best_score
                self._save_best_score()

            # Check special end-game states
            if self.board.has_won and not self.board.keep_playing:
                self.sound.play("victory")
            elif self.board.game_over:
                self.sound.play("game_over")

    def handle_keydown(self, key):
        """Processes keyboard input."""
        # Quit dialog modal shortcuts
        if self.show_quit_dialog:
            if key in (pygame.K_y, pygame.K_RETURN):
                self.should_exit = True
            elif key in (pygame.K_n, pygame.K_ESCAPE):
                self.show_quit_dialog = False
            return

        # Game controls
        if key in (pygame.K_UP, pygame.K_w):
            self.execute_move(DIR_UP)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.execute_move(DIR_DOWN)
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.execute_move(DIR_LEFT)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.execute_move(DIR_RIGHT)

        elif key == pygame.K_u:
            # Undo move
            if self.board.undo():
                self.sound.play("undo")

        elif key == pygame.K_r:
            # Restart game
            self.start_new_game()

        elif key == pygame.K_t:
            # Toggle Theme
            self.sound.play("click")
            self.renderer.toggle_theme()

        elif key == pygame.K_m:
            # Toggle Mute
            self.sound.toggle_sound()

        elif key == pygame.K_ESCAPE:
            self.show_quit_dialog = True

    def handle_mouse_down(self, pos: tuple[int, int]):
        """Records initial drag position for swipe detection."""
        self.drag_start_pos = pos

    def handle_mouse_up(self, pos: tuple[int, int]):
        """Detects clicks on buttons or swipe gestures."""
        start = self.drag_start_pos
        self.drag_start_pos = None

        if start is None:
            return

        dx = pos[0] - start[0]
        dy = pos[1] - start[1]
        dist_sq = dx * dx + dy * dy

        # If drag distance is significant, treat as a swipe!
        if dist_sq >= self.min_swipe_dist * self.min_swipe_dist:
            if abs(dx) > abs(dy):
                # Horizontal swipe
                direction = DIR_RIGHT if dx > 0 else DIR_LEFT
            else:
                # Vertical swipe
                direction = DIR_DOWN if dy > 0 else DIR_UP
            self.execute_move(direction)
            return

        # Otherwise treat as a click at pos!
        self._handle_click(pos)

    def _handle_click(self, pos: tuple[int, int]):
        # 1. Quit modal buttons
        if self.show_quit_dialog:
            modal_w, modal_h = 360, 180
            mx = (SCREEN_WIDTH - modal_w) // 2
            my = (SCREEN_HEIGHT - modal_h) // 2
            btn_yes = pygame.Rect(mx + 35, my + 110, 135, 42)
            btn_cancel = pygame.Rect(mx + 190, my + 110, 135, 42)

            if btn_yes.collidepoint(pos):
                self.should_exit = True
            elif btn_cancel.collidepoint(pos):
                self.show_quit_dialog = False
            return

        # 2. Victory overlay buttons
        if self.board.has_won and not self.board.keep_playing:
            board_cx = BOARD_OFFSET_X + BOARD_WIDTH // 2
            board_cy = BOARD_OFFSET_Y + BOARD_HEIGHT // 2
            btn_keep = pygame.Rect(board_cx - 145, board_cy + 35, 135, 42)
            btn_new = pygame.Rect(board_cx + 10, board_cy + 35, 135, 42)

            if btn_keep.collidepoint(pos):
                self.sound.play("click")
                self.board.keep_playing = True
            elif btn_new.collidepoint(pos):
                self.start_new_game()
            return

        # 3. Game over overlay buttons
        if self.board.game_over:
            board_cx = BOARD_OFFSET_X + BOARD_WIDTH // 2
            board_cy = BOARD_OFFSET_Y + BOARD_HEIGHT // 2
            btn_retry = pygame.Rect(board_cx - 70, board_cy + 25, 140, 44)
            if btn_retry.collidepoint(pos):
                self.start_new_game()
            return

        # 4. Header buttons
        if self.renderer.rect_btn_new.collidepoint(pos):
            self.start_new_game()
        elif self.renderer.rect_btn_undo.collidepoint(pos):
            if self.board.undo():
                self.sound.play("undo")
        elif self.renderer.rect_btn_theme.collidepoint(pos):
            self.sound.play("click")
            self.renderer.toggle_theme()
        elif self.renderer.rect_btn_sound.collidepoint(pos):
            self.sound.toggle_sound()

    def update(self, dt: float):
        """Advances animation clocks."""
        self.anim_time += dt
        self.board.update_animations(dt)

    def draw(self, surface: pygame.Surface):
        """Renders the game frame."""
        self.renderer.render(
            surface,
            self.board,
            self.anim_time,
            self.sound.enabled,
            self.show_quit_dialog
        )
