"""
test_kflapper.py - Automated Unit Tests for KFlapper.
Verifies physics, collision detection, animation, audio, and game state.
"""

import os
import sys
import tempfile
import pygame

# Set headless dummy video driver for automated testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import (
    BIRD_X, BIRD_RADIUS, GRAVITY, FLAP_STRENGTH, PLAYABLE_HEIGHT,
    SKIN_KEYS, DIFFICULTIES
)
from src.entities.bird import Bird
from src.entities.pipe import PipeManager, PipePair
from src.entities.background import Background
from src.entities.particles import ParticleManager
from src.audio import SoundManager
from src.game import KFlapperGame, GameState


def test_bird_physics_and_skins():
    pygame.init()
    b = Bird(start_x=BIRD_X, start_y=300.0, skin_key="KFlapper")
    assert b.x == BIRD_X
    assert b.y == 300.0
    assert b.alive

    # Test Flap
    b.flap()
    assert b.vy == FLAP_STRENGTH
    assert b.angle > 0

    # Test Physics Step
    b.update(dt=1.0 / 60.0, ground_y=PLAYABLE_HEIGHT)
    assert b.y < 300.0  # Moved upwards due to flap

    # Test all 5 skins build frames cleanly
    for s_key in SKIN_KEYS:
        b.set_skin(s_key)
        assert len(b.frames) == 3, f"Skin {s_key} should have 3 frames"
    print("[PASS] Bird physics & 5-skin animation tests passed.")


def test_pipe_manager_and_collisions():
    pm = PipeManager(gap_size=195, speed=3.8)
    assert len(pm.pipes) == 0

    # Spawn first pipe
    pm.spawn_pipe(500.0)
    assert len(pm.pipes) == 1
    pipe = pm.pipes[0]

    # Test scoring: bird passing through gap safely
    bird = Bird(start_x=500.0 + pipe.width / 2 + 10, start_y=pipe.gap_y + pipe.gap_height / 2)
    assert pm.check_score(bird.x), "Bird should trigger score increment"
    assert not pm.check_collision(bird), "Bird in middle of gap should NOT collide"

    # Test collision: bird hitting top pipe
    bird_crash = Bird(start_x=500.0 + 10, start_y=pipe.gap_y - 20)
    assert pm.check_collision(bird_crash), "Bird inside top pipe should trigger collision"

    # Test update scrolls pipes
    pm.update()
    assert pm.pipes[0].x < 500.0
    print("[PASS] Pipe spawning, gap scoring, and collision detection tests passed.")


def test_audio_synthesis():
    with tempfile.TemporaryDirectory() as td:
        sm = SoundManager(td)
        assert len(sm.sounds) >= 5, "At least 5 sounds should be synthesized"
        # Test non-blocking playback calls
        sm.play_flap()
        sm.play_point()
        sm.play_hit()
        sm.play_die()
        sm.play_swoosh()
        sm.play_medal()
        assert not sm.muted
        sm.toggle_mute()
        assert sm.muted
    print("[PASS] Procedural sound synthesis and manager tests passed.")


def test_game_state_machine():
    game = KFlapperGame()
    assert game.state == GameState.MENU

    # Test drawing in MENU
    game.draw()

    # Start game via flap (simulate mouse click or tap)
    game.trigger_flap()
    assert game.state == GameState.PLAYING
    assert game.score == 0

    # Test drawing in PLAYING (verifies SKINS and badge rendering)
    game.draw()

    # Step game
    game.update(1.0 / 60.0)
    assert game.state == GameState.PLAYING

    # Test another flap during PLAYING
    game.trigger_flap()

    # Trigger game over
    game.trigger_game_over()
    assert game.state == GameState.GAME_OVER
    assert not game.bird.alive

    # Test drawing in GAME_OVER
    game.draw()
    print("[PASS] Game state machine and lifecycle tests passed.")


def test_dynamic_biomes_and_menu_gui():
    game = KFlapperGame()
    assert game.state == GameState.MENU

    # 1. Test Menu GUI Difficulty Button Click
    game.draw()
    assert "diff_Chill" in game.menu.buttons
    assert "diff_Hardcore" in game.menu.buttons
    assert "btn_play" in game.menu.buttons

    # Simulate click on Chill card
    chill_rect = game.menu.buttons["diff_Chill"]
    action, payload = game.menu.handle_click((chill_rect.centerx, chill_rect.centery), "MENU")
    assert action == "set_diff" and payload == "Chill"
    game.set_difficulty("Chill")
    assert game.current_diff_key == "Chill"
    assert game.diff_cfg["gap"] == 240

    # Simulate click on Hardcore card
    hardcore_rect = game.menu.buttons["diff_Hardcore"]
    action, payload = game.menu.handle_click((hardcore_rect.centerx, hardcore_rect.centery), "MENU")
    assert action == "set_diff" and payload == "Hardcore"
    game.set_difficulty("Hardcore")
    assert game.current_diff_key == "Hardcore"
    assert game.diff_cfg["gap"] == 165

    # 2. Test Dynamic Biome Evolution (0-29 Earth, 30-59 Mars, 60-89 Cyber, 90+ Cosmic)
    game.theme_mode_index = 0  # Dynamic Progressive Biomes
    game.score = 15
    assert game.get_current_theme()["id"] == "earth"

    game.score = 30
    assert game.get_current_theme()["id"] == "martian", "Score 30 must transition to Martian Reds"

    game.score = 65
    assert game.get_current_theme()["id"] == "cyber", "Score 60+ must transition to Cyber Neon"

    game.score = 95
    assert game.get_current_theme()["id"] == "night", "Score 90+ must transition to Cosmic Night"

    print("[PASS] Interactive Menu GUI & Dynamic Progressive Biomes tests passed.")


if __name__ == "__main__":
    test_bird_physics_and_skins()
    test_pipe_manager_and_collisions()
    test_audio_synthesis()
    test_game_state_machine()
    test_dynamic_biomes_and_menu_gui()
    print("\nALL KFLAPPER AUTOMATED TESTS PASSED!")
