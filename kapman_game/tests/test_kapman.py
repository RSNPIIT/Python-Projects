"""Kapman Game - Comprehensive Test Suite"""
import os
import pytest
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from core.constants import (
    DIR_NONE, DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    GHOST_CHASE, GHOST_SCATTER, GHOST_FRIGHTENED, GHOST_EATEN,
    GHOST_ENTERING, GHOST_EXITING,
    THEME_EGYPTIAN, THEME_CLASSIC
)
from core.maze import Maze
from core.kapman import Kapman
from core.ghost import Ghost, GHOST_RED, GHOST_PINK, GHOST_CYAN, GHOST_ORANGE
from game import KapmanGame

@pytest.fixture
def game():
    g = KapmanGame()
    g.start_new_game()
    g.state = "PLAYING"
    return g

def test_maze_structure(game):
    """Verifies grid dimensions, pill counts and gate positioning."""
    assert game.maze.rows == 31
    assert game.maze.cols == 28
    assert game.maze.pills_remaining > 0
    # Gate at row 12, cols 13 and 14
    assert game.maze.is_gate(12, 13)
    assert game.maze.is_gate(12, 14)
    assert not game.maze.is_passable(12, 13, allow_gate=False)
    assert game.maze.is_passable(12, 13, allow_gate=True)

def test_ghost_initial_release(game):
    """Verifies that all 3 ghosts inside the house smoothly emerge through the gate."""
    # Place Kapman safely away so he doesn't take damage during wait
    game.kapman.direction = DIR_NONE
    game.kapman.x = 20.0
    game.kapman.y = 20.0

    # Simulate 10 seconds of updates (600 frames)
    for _ in range(600):
        game.update(1.0 / 60.0)

    for idx, g in enumerate(game.ghosts):
        assert not g.in_house, f"Ghost {idx} is still inside house!"
        assert g.state in (GHOST_CHASE, GHOST_SCATTER), f"Ghost {idx} has invalid state: {g.state}"

def test_energizer_and_frightened_lifecycle(game):
    """Verifies that energizers frighten ghosts, speed slows down, and restores when timer expires."""
    game.kapman.direction = DIR_NONE
    game.kapman.x = 20.0
    game.kapman.y = 20.0

    # Ensure all ghosts have emerged
    for _ in range(600):
        game.update(1.0 / 60.0)

    # Trigger energizer
    game.fright_timer = 2.0
    for g in game.ghosts:
        g.become_frightened()

    for g in game.ghosts:
        assert g.state == GHOST_FRIGHTENED
        assert g.speed < g.base_speed

    # Run for 2.2 seconds to expire timer
    for _ in range(132):
        game.update(1.0 / 60.0)

    assert game.fright_timer == 0.0
    for g in game.ghosts:
        assert g.state in (GHOST_CHASE, GHOST_SCATTER)
        assert g.speed == g.base_speed

def test_ghost_consumption_revival_and_exit(game):
    """Verifies that when a ghost is eaten, its eyes return home, revive, and exit out of the gate."""
    game.kapman.direction = DIR_NONE
    game.kapman.x = 20.0
    game.kapman.y = 20.0

    for _ in range(600):
        game.update(1.0 / 60.0)

    g1 = game.ghosts[1]
    g1.become_eaten()
    assert g1.state == GHOST_EATEN

    entered = False
    revived = False
    exited = False

    for _ in range(600):
        game.update(1.0 / 60.0)
        if g1.state == GHOST_ENTERING:
            entered = True
        elif g1.state == GHOST_EXITING:
            revived = True
        elif revived and g1.state in (GHOST_CHASE, GHOST_SCATTER):
            exited = True
            break

    assert entered, "Eaten ghost failed to enter through gate!"
    assert revived, "Eaten ghost failed to revive at house center!"
    assert exited, "Revived ghost failed to exit out through the gate!"
    assert g1.row <= 11, f"Ghost ended up at row {g1.row}, expected <= 11 outside gate!"

def test_theme_toggle(game):
    """Verifies switching between Egyptian and Classic arcade themes."""
    assert game.renderer.theme == THEME_EGYPTIAN
    game.renderer.toggle_theme()
    assert game.renderer.theme == THEME_CLASSIC
    game.renderer.toggle_theme()
    assert game.renderer.theme == THEME_EGYPTIAN
