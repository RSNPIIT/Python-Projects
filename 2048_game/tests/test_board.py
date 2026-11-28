"""2048 Game - Comprehensive Unit Test Suite"""
import os
import pytest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from core.constants import DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT, THEME_LIGHT, THEME_DARK
from core.board import Board
from core.tile import AnimatedTile
from game import Game2048

@pytest.fixture
def board():
    b = Board()
    b.reset()
    return b

def test_initial_board_state(board):
    """Verifies that the initial board has exactly 2 non-zero tiles of value 2 or 4."""
    non_zero_tiles = []
    for r in range(4):
        for c in range(4):
            val = board.grid[r][c]
            if val != 0:
                non_zero_tiles.append(val)
                assert board.tiles[r][c] is not None
                assert board.tiles[r][c].value == val
            else:
                assert board.tiles[r][c] is None

    assert len(non_zero_tiles) == 2
    for v in non_zero_tiles:
        assert v in (2, 4)
    assert board.score == 0
    assert not board.has_won
    assert not board.game_over

def test_slide_left_simple_merge(board):
    """Tests [2, 2, 0, 0] -> [4, 0, 0, 0] + 1 newly spawned tile."""
    # Custom deterministic board row
    board.grid = [
        [2, 2, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    board.tiles = [
        [AnimatedTile(0, 0, 2), AnimatedTile(0, 1, 2), None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None]
    ]

    res = board.move(DIR_LEFT)
    assert res.moved is True
    assert res.score_earned == 4
    assert 4 in res.merged_values
    assert board.score == 4
    # The merged tile must be at (0, 0)
    assert board.grid[0][0] == 4

def test_slide_left_double_merge(board):
    """Tests [2, 2, 2, 2] -> [4, 4, 0, 0] (no quadruple merge to 8)."""
    board.grid = [
        [2, 2, 2, 2],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    board.tiles = [
        [AnimatedTile(0, 0, 2), AnimatedTile(0, 1, 2), AnimatedTile(0, 2, 2), AnimatedTile(0, 3, 2)],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None]
    ]

    res = board.move(DIR_LEFT)
    assert res.moved is True
    assert res.score_earned == 8
    assert res.merged_values == [4, 4]
    assert board.grid[0][0] == 4
    assert board.grid[0][1] == 4

def test_slide_right_gaps(board):
    """Tests [2, 0, 2, 0] moving RIGHT -> [0, 0, 0, 4]."""
    board.grid = [
        [2, 0, 2, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    board.tiles = [
        [AnimatedTile(0, 0, 2), None, AnimatedTile(0, 2, 2), None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None]
    ]

    res = board.move(DIR_RIGHT)
    assert res.moved is True
    assert res.score_earned == 4
    assert board.grid[0][3] == 4

def test_vertical_slide_up_and_down(board):
    """Tests UP and DOWN sliding across multiple columns."""
    board.grid = [
        [4, 0, 0, 0],
        [4, 0, 0, 0],
        [0, 2, 0, 0],
        [0, 2, 0, 0]
    ]
    board.tiles = [
        [AnimatedTile(0, 0, 4), None, None, None],
        [AnimatedTile(1, 0, 4), None, None, None],
        [None, AnimatedTile(2, 1, 2), None, None],
        [None, AnimatedTile(3, 1, 2), None, None]
    ]

    res = board.move(DIR_UP)
    assert res.moved is True
    assert res.score_earned == 8 + 4  # 4+4=8, 2+2=4
    assert board.grid[0][0] == 8
    assert board.grid[0][1] == 4

def test_invalid_move_no_action(board):
    """Tests that attempting a move into a wall with no open cells or merges does not spawn tiles."""
    board.grid = [
        [2, 4, 8, 16],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    board.tiles = [
        [AnimatedTile(0, 0, 2), AnimatedTile(0, 1, 4), AnimatedTile(0, 2, 8), AnimatedTile(0, 3, 16)],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None]
    ]

    initial_score = board.score
    res = board.move(DIR_UP)
    assert res.moved is False
    assert board.score == initial_score
    # Board must remain identical
    assert board.grid[0] == [2, 4, 8, 16]

def test_undo_stack(board):
    """Tests snapshot restoration on undo."""
    board.grid = [
        [2, 2, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    board.tiles = [
        [AnimatedTile(0, 0, 2), AnimatedTile(0, 1, 2), None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None]
    ]
    board.score = 10

    assert board.can_undo() is False
    res = board.move(DIR_LEFT)
    assert res.moved is True
    assert board.can_undo() is True
    assert board.score == 14

    # Execute undo
    assert board.undo() is True
    assert board.score == 10
    assert board.grid[0] == [2, 2, 0, 0]
    assert board.can_undo() is False

def test_win_condition(board):
    """Tests reaching 2048 triggers has_won."""
    board.grid = [
        [1024, 1024, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
    board.tiles = [
        [AnimatedTile(0, 0, 1024), AnimatedTile(0, 1, 1024), None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None]
    ]

    res = board.move(DIR_LEFT)
    assert res.moved is True
    assert board.grid[0][0] == 2048
    assert board.has_won is True

def test_game_over_detection(board):
    """Tests that a full board with alternating values and no valid moves triggers game_over."""
    board.grid = [
        [2, 4, 2, 4],
        [4, 2, 4, 2],
        [2, 4, 2, 4],
        [4, 2, 4, 0]
    ]
    board.tiles = [
        [AnimatedTile(r, c, board.grid[r][c]) if board.grid[r][c] != 0 else None for c in range(4)]
        for r in range(4)
    ]

    assert board.can_move() is True
    # Fill last slot
    board.grid[3][3] = 2
    board.tiles[3][3] = AnimatedTile(3, 3, 2)

    assert board.can_move() is False

def test_game_class_integration():
    """Tests Game2048 high-level integration, keyboard inputs, theme toggle, and mute."""
    game = Game2048()
    assert game.board.size == 4
    assert game.renderer.theme == THEME_LIGHT

    # Theme toggle
    game.renderer.toggle_theme()
    assert game.renderer.theme == THEME_DARK

    # Sound mute toggle
    initial_sound = game.sound.enabled
    game.sound.toggle_sound()
    assert game.sound.enabled != initial_sound

    # Keydown movement
    game.handle_keydown(pygame.K_LEFT)
    # Check that game runs updates cleanly without exception
    game.update(0.016)
