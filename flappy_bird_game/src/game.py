"""
game.py - Core Application Coordinator & State Machine for KFlapper.
Integrates physics simulation, input dispatch, audio, HUD, persistent scores, and renderer.
"""

import json
import os
import signal
import pygame
from enum import Enum, auto

from .config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, BIRD_X,
    PLAYABLE_HEIGHT, DIFFICULTIES, TIME_THEMES,
    SKINS, SKIN_KEYS, THEME_KEYS
)
from .audio import SoundManager
from .entities.bird import Bird
from .entities.pipe import PipeManager
from .entities.background import Background
from .entities.particles import ParticleManager
from .ui.hud import HUD
from .ui.menu import Menu
from .ui.medals import get_medal_for_score


def _trap_terminal_signals():
    """Ignores Ctrl+C, Ctrl+Z, Ctrl+\\ in terminal while game is running."""
    for sig_name in ("SIGINT", "SIGQUIT", "SIGTSTP"):
        if hasattr(signal, sig_name):
            try:
                signal.signal(getattr(signal, sig_name), signal.SIG_IGN)
            except Exception:
                pass


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class KFlapperGame:
    """Main Game Engine and Controller."""

    SAVE_FILE = os.path.expanduser("~/.kflapper_save.json")

    def __init__(self):
        _trap_terminal_signals()
        pygame.init()
        pygame.display.set_caption(TITLE)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.fullscreen = False

        # Asset Directories & Subsystems
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        asset_dir = os.path.join(base_dir, "assets")

        self.sound = SoundManager(asset_dir)
        self.particles = ParticleManager()
        self.hud = HUD()
        self.menu = Menu()
        self.background = Background()

        # Configurable Settings
        self.skin_index = 0
        self.diff_index = 0
        self.theme_index = 0  # 0: Day, 1: Sunset, 2: Night, 3: Dynamic

        self.diff_keys = list(DIFFICULTIES.keys())
        self.current_diff_key = self.diff_keys[self.diff_index]
        self.diff_cfg = DIFFICULTIES[self.current_diff_key]

        # Entities
        self.bird = Bird(start_x=BIRD_X, start_y=340.0, skin_key=SKIN_KEYS[self.skin_index])
        self.pipes = PipeManager(gap_size=self.diff_cfg["gap"], speed=self.diff_cfg["speed"])

        # High Scores Persistence
        self.high_scores = self._load_high_scores()

        # State Variables
        self.state = GameState.MENU
        self.score = 0
        self.is_new_best = False

    def _load_high_scores(self) -> dict:
        defaults = {k: 0 for k in DIFFICULTIES.keys()}
        if os.path.exists(self.SAVE_FILE):
            try:
                with open(self.SAVE_FILE, "r") as f:
                    data = json.load(f)
                    for k in defaults:
                        if k not in data:
                            data[k] = 0
                    return data
            except Exception:
                pass
        return defaults

    def _save_high_scores(self):
        try:
            with open(self.SAVE_FILE, "w") as f:
                json.dump(self.high_scores, f, indent=2)
        except Exception:
            pass

    @property
    def best_score(self) -> int:
        return self.high_scores.get(self.current_diff_key, 0)

    def get_current_theme(self) -> dict:
        if self.theme_index < len(THEME_KEYS):
            key = THEME_KEYS[self.theme_index]
            return TIME_THEMES[key]
        else:
            # Dynamic time of day: shifts every 10 points
            cycle = (self.score // 10) % 3
            key = THEME_KEYS[cycle]
            return TIME_THEMES[key]

    @property
    def theme_display_name(self) -> str:
        if self.theme_index < len(THEME_KEYS):
            return THEME_KEYS[self.theme_index]
        return "Dynamic"

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)

    def cycle_skin(self):
        self.skin_index = (self.skin_index + 1) % len(SKIN_KEYS)
        self.bird.set_skin(SKIN_KEYS[self.skin_index])
        self.sound.play_swoosh()

    def cycle_difficulty(self):
        self.diff_index = (self.diff_index + 1) % len(self.diff_keys)
        self.current_diff_key = self.diff_keys[self.diff_index]
        self.diff_cfg = DIFFICULTIES[self.current_diff_key]
        self.pipes.reset(gap_size=self.diff_cfg["gap"], speed=self.diff_cfg["speed"])
        self.sound.play_swoosh()

    def cycle_theme(self):
        # 0: Day, 1: Sunset, 2: Night, 3: Dynamic
        self.theme_index = (self.theme_index + 1) % (len(THEME_KEYS) + 1)
        self.sound.play_swoosh()

    def start_game(self):
        self.state = GameState.PLAYING
        self.score = 0
        self.is_new_best = False
        self.bird.reset(start_x=BIRD_X, start_y=340.0)
        self.bird.flap()
        self.pipes.reset(gap_size=self.diff_cfg["gap"], speed=self.diff_cfg["speed"])
        self.particles.clear()
        self.sound.play_flap()

    def trigger_flap(self):
        if self.state == GameState.MENU:
            self.start_game()
        elif self.state == GameState.PLAYING:
            self.bird.flap()
            self.sound.play_flap()
            self.particles.emit_flap_feathers(
                self.bird.x,
                self.bird.y,
                self.bird.skin_config["body_color"]
            )
        elif self.state == GameState.GAME_OVER:
            if self.menu.card_y_offset >= -20:
                self.start_game()

    def trigger_game_over(self):
        self.state = GameState.GAME_OVER
        self.bird.alive = False
        self.sound.play_hit()
        self.sound.play_die()

        # Burst feathers and impact dust
        self.particles.emit_crash_burst(
            self.bird.x,
            self.bird.y,
            self.bird.skin_config["body_color"]
        )

        # Check high score
        if self.score > self.best_score:
            self.high_scores[self.current_diff_key] = self.score
            self.is_new_best = True
            self._save_high_scores()
            if self.score >= 10:
                self.sound.play_medal()

        self.menu.reset_game_over(self.score)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    self.trigger_flap()

                elif event.key in (pygame.K_ESCAPE, pygame.K_p):
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING

                elif event.key == pygame.K_q:
                    self.running = False

                elif event.key in (pygame.K_r, pygame.K_RETURN):
                    if self.state in (GameState.GAME_OVER, GameState.PAUSED):
                        self.start_game()

                elif event.key == pygame.K_c:
                    self.cycle_skin()

                elif event.key == pygame.K_d:
                    if self.state != GameState.PLAYING:
                        self.cycle_difficulty()

                elif event.key == pygame.K_t:
                    self.cycle_theme()

                elif event.key == pygame.K_m:
                    self.sound.toggle_mute()

                elif event.key in (pygame.K_F11, pygame.K_f):
                    self.toggle_fullscreen()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (1, 2, 3):  # Left click, middle, or right click
                    self.trigger_flap()

            elif event.type == getattr(pygame, 'FINGERDOWN', -1):
                # Touchpad / Touchscreen direct finger tap
                self.trigger_flap()

    def update(self, dt: float):
        theme = self.get_current_theme()
        scroll_speed = self.diff_cfg["speed"]

        # Update Background Parallax
        if self.state in (GameState.MENU, GameState.PLAYING):
            self.background.update(scroll_speed)

        # Update Particles
        self.particles.update(dt)
        self.hud.update(dt)
        self.menu.update(dt)

        if self.state == GameState.PLAYING:
            # Bird Physics
            self.bird.update(dt, ground_y=PLAYABLE_HEIGHT)

            # Check ground collision
            if self.bird.collided:
                self.trigger_game_over()
                return

            # Pipes Update
            self.pipes.update()

            # Check pipe scoring
            if self.pipes.check_score(self.bird.x):
                self.score += 1
                self.sound.play_point()
                self.hud.trigger_score_pop()
                self.particles.emit_score_sparkles(self.bird.x, self.bird.y)

            # Check pipe collision
            if self.pipes.check_collision(self.bird):
                self.trigger_game_over()
                return

        elif self.state == GameState.GAME_OVER:
            # Let bird tumble to the ground if not there yet
            if not self.bird.collided:
                self.bird.update(dt, ground_y=PLAYABLE_HEIGHT)

    def draw(self):
        theme = self.get_current_theme()

        # Canvas surface for screen shake
        canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # 1. Background Layers (Sky, Clouds, City, Hills)
        self.background.draw(canvas, theme)

        # 2. Pipe Obstacles
        if self.state in (GameState.PLAYING, GameState.GAME_OVER, GameState.PAUSED):
            self.pipes.draw(canvas, theme)

        # 3. Foreground Ground (Drawn on top of pipes)
        self.background.draw_foreground(canvas, theme)

        # 4. Particles (Behind bird)
        self.particles.draw(canvas)

        # 5. Bird Entity
        if self.state in (GameState.PLAYING, GameState.GAME_OVER, GameState.PAUSED):
            self.bird.draw(canvas)

        # 6. UI Overlays
        if self.state == GameState.MENU:
            self.menu.draw_title_screen(
                canvas,
                self.bird,
                best_score=self.best_score,
                diff_key=self.current_diff_key,
                skin_key=SKIN_KEYS[self.skin_index],
                theme_key=self.theme_display_name
            )

        elif self.state == GameState.PLAYING:
            self.hud.draw_score(canvas, self.score)
            self.hud.draw_status_badges(
                canvas,
                self.current_diff_key,
                SKINS[SKIN_KEYS[self.skin_index]]["name"],
                self.sound.muted
            )

        elif self.state == GameState.PAUSED:
            self.hud.draw_score(canvas, self.score)
            self.hud.draw_pause_overlay(canvas)

        elif self.state == GameState.GAME_OVER:
            self.menu.draw_game_over(
                canvas,
                score=self.score,
                best_score=self.best_score,
                is_new_best=self.is_new_best
            )

        # Blit canvas to screen with screen shake offset
        shake_x, shake_y = self.particles.get_shake_offset()
        self.screen.blit(canvas, (int(shake_x), int(shake_y)))

        pygame.display.flip()

    def run(self):
        """Main game loop executing at 60 FPS."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            # Clamp dt to prevent physics leaps on lag spikes
            if dt > 0.05:
                dt = 0.05

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
