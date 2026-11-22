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
    PLAYABLE_HEIGHT, DIFFICULTIES, BIOMES, DIFF_KEYS,
    SKINS, SKIN_KEYS
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
        self.current_diff_key = "Classic"
        self.diff_cfg = DIFFICULTIES[self.current_diff_key]

        # 0 = Dynamic Progressive Biomes (0-29 Earth, 30-59 Mars, 60-89 Cyber, 90+ Cosmic)
        # 1..4 = Fixed Biome Lock
        self.theme_mode_index = 0
        self.last_biome_id = None

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
        """
        Determines active environment theme:
        - Mode 0 (Default): Dynamic Progressive Evolution based on score!
          0 - 29 bars: Earth Meadow
          30 - 59 bars: Martian Red Wasteland
          60 - 89 bars: Cyber Neon City
          90+ bars: Cosmic Midnight Aurora
        - Mode 1..4: Locked to specific biome.
        """
        if self.theme_mode_index == 0:
            if self.score < 30:
                return BIOMES[0]
            elif self.score < 60:
                return BIOMES[1]
            elif self.score < 90:
                return BIOMES[2]
            else:
                return BIOMES[3]
        else:
            idx = (self.theme_mode_index - 1) % len(BIOMES)
            return BIOMES[idx]

    @property
    def theme_display_name(self) -> str:
        if self.theme_mode_index == 0:
            curr = self.get_current_theme()
            return f"Dynamic ({curr['name'].split()[0]})"
        else:
            idx = (self.theme_mode_index - 1) % len(BIOMES)
            return BIOMES[idx]["name"].split()[0]

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)

    def set_difficulty(self, diff_key: str):
        if diff_key in DIFFICULTIES:
            self.current_diff_key = diff_key
            self.diff_cfg = DIFFICULTIES[diff_key]
            self.pipes.reset(gap_size=self.diff_cfg["gap"], speed=self.diff_cfg["speed"])
            self.sound.play_swoosh()

    def cycle_difficulty(self):
        idx = DIFF_KEYS.index(self.current_diff_key) if self.current_diff_key in DIFF_KEYS else 0
        next_key = DIFF_KEYS[(idx + 1) % len(DIFF_KEYS)]
        self.set_difficulty(next_key)

    def cycle_skin(self, step: int = 1):
        self.skin_index = (self.skin_index + step) % len(SKIN_KEYS)
        self.bird.set_skin(SKIN_KEYS[self.skin_index])
        self.sound.play_swoosh()

    def cycle_theme(self):
        # 0: Dynamic, 1: Earth, 2: Mars, 3: Cyber, 4: Cosmic
        self.theme_mode_index = (self.theme_mode_index + 1) % (len(BIOMES) + 1)
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

        # Set initial biome
        curr_b = self.get_current_theme()
        self.last_biome_id = curr_b["id"]

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

            elif event.type == pygame.MOUSEMOTION:
                if self.state in (GameState.MENU, GameState.GAME_OVER):
                    self.menu.update_hover(event.pos)

            elif event.type in (pygame.MOUSEBUTTONDOWN, getattr(pygame, 'FINGERDOWN', -1)):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button not in (1, 2, 3):
                    continue

                mouse_pos = pygame.mouse.get_pos()

                if self.state == GameState.MENU:
                    action, payload = self.menu.handle_click(mouse_pos, "MENU")
                    if action == "set_diff":
                        self.set_difficulty(payload)
                    elif action == "cycle_skin":
                        self.cycle_skin(payload)
                    elif action == "cycle_theme":
                        self.cycle_theme()
                    elif action == "start_game":
                        self.start_game()
                    elif action == "toggle_sound":
                        self.sound.toggle_mute()
                    elif action == "toggle_fullscreen":
                        self.toggle_fullscreen()
                    else:
                        # Click on background starts game
                        self.start_game()

                elif self.state == GameState.GAME_OVER:
                    action, payload = self.menu.handle_click(mouse_pos, "GAME_OVER")
                    if action == "start_game":
                        self.start_game()
                    elif action == "go_to_menu":
                        self.state = GameState.MENU
                        self.sound.play_swoosh()
                    else:
                        self.trigger_flap()

                elif self.state == GameState.PLAYING:
                    self.trigger_flap()

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
                    self.cycle_skin(1)

                elif event.key == pygame.K_d:
                    if self.state != GameState.PLAYING:
                        self.cycle_difficulty()

                elif event.key == pygame.K_t:
                    self.cycle_theme()

                elif event.key == pygame.K_m:
                    self.sound.toggle_mute()

                elif event.key in (pygame.K_F11, pygame.K_f):
                    self.toggle_fullscreen()

    def update(self, dt: float):
        theme = self.get_current_theme()
        scroll_speed = self.diff_cfg["speed"]

        # Update Background Parallax
        if self.state in (GameState.MENU, GameState.PLAYING):
            self.background.update(scroll_speed)

        # Ambient Biome VFX
        self.particles.update_ambient(dt, theme.get("ambient_fx", "feathers"), SCREEN_WIDTH, SCREEN_HEIGHT)

        # Update Particles, HUD & Menu
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

                # Check Dynamic Biome Shift (at 30, 60, 90 bars)
                new_theme = self.get_current_theme()
                if new_theme["id"] != self.last_biome_id:
                    self.last_biome_id = new_theme["id"]
                    self.hud.trigger_biome_banner(new_theme["banner"], new_theme["accent"])
                    self.sound.play_medal()
                    self.particles.emit_biome_transition(new_theme["accent"])

            # Check pipe collision
            if self.pipes.check_collision(self.bird):
                self.trigger_game_over()
                return

        elif self.state == GameState.GAME_OVER:
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

        # 4. Particles (Ambient, Feathers, Sparkles)
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
                theme_display_name=self.theme_display_name,
                sound_muted=self.sound.muted
            )

        elif self.state == GameState.PLAYING:
            self.hud.draw_score(canvas, self.score)
            self.hud.draw_status_badges(
                canvas,
                self.current_diff_key,
                SKINS[SKIN_KEYS[self.skin_index]]["name"],
                theme["name"],
                self.sound.muted
            )
            self.hud.draw_biome_transition_banner(canvas)

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
            if dt > 0.05:
                dt = 0.05

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
