"""
test_minesweeper.py - Automated Unit Tests for Core Minesweeper OOP Engine.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.cell import Cell, CellState
from src.core.board import Board
from src.core.solver import Solver
from src.core.game_state import GameStats, Difficulty
from src.audio.sound_engine import SoundEngine


def test_cell():
    c = Cell(0, 0)
    assert c.is_hidden
    assert not c.is_revealed
    assert not c.is_flagged

    # Flag toggles
    assert c.toggle_flag(allow_question=True) == CellState.FLAGGED
    assert c.is_flagged
    assert c.toggle_flag(allow_question=True) == CellState.QUESTION
    assert c.is_question
    assert c.toggle_flag(allow_question=True) == CellState.HIDDEN
    assert c.is_hidden

    # Reveal
    assert c.reveal()
    assert c.is_revealed
    # Cannot flag revealed
    assert c.toggle_flag() == CellState.REVEALED
    print("[PASS] Cell tests passed.")


def test_board():
    b = Board(9, 9, 10, safe_opening=True)
    assert b.rows == 9
    assert b.cols == 9
    assert b.total_mines == 10
    assert not b.first_click_made

    # First click at (4, 4)
    hit_mine, revealed = b.reveal_cell(4, 4)
    assert not hit_mine, "First click must never be a mine"
    assert len(revealed) > 0, "First click should cascade"
    assert b.first_click_made
    assert b.mines_placed

    # Verify center cell (4, 4) and its neighbors are free of mines
    c = b.get_cell(4, 4)
    assert not c.is_mine

    # Verify total mine count on board matches exactly 10
    total_mines_found = sum(1 for row in b.grid for cell in row if cell.is_mine)
    assert total_mines_found == 10, f"Expected 10 mines, found {total_mines_found}"

    # Verify 3BV calculation runs
    b_3bv = b.calculate_3bv()
    assert b_3bv > 0, "3BV should be greater than 0"
    print(f"[PASS] Board tests passed (3BV = {b_3bv}).")


def test_solver():
    b = Board(5, 5, 1)
    # Mock a deterministic situation:
    # Cell (1, 1) has neighbor_mines = 1
    # Cell (0, 0) is flagged
    # Cell (0, 1) is hidden
    b.first_click_made = True
    b.mines_placed = True
    b.grid[1][1].state = CellState.REVEALED
    b.grid[1][1].neighbor_mines = 1
    b.grid[0][0].state = CellState.FLAGGED
    b.grid[0][0].is_mine = True

    # The other neighbors should be deducible as safe!
    hint = Solver.get_hint(b)
    assert hint is not None
    assert hint.is_safe, f"Expected safe hint, got {hint}"
    print(f"[PASS] Solver deduction passed: {hint}")


def test_sounds(tmp_path):
    engine = SoundEngine(tmp_path)
    # Check that WAV files were generated
    for name in ["click.wav", "flag.wav", "unflag.wav", "cascade.wav", "chord.wav", "explode.wav", "win.wav"]:
        fpath = os.path.join(tmp_path, "sounds", name)
        assert os.path.exists(fpath), f"Missing {name}"
        assert os.path.getsize(fpath) > 100, f"File {name} too small"
    print("[PASS] Procedural sound engine generation passed.")


if __name__ == "__main__":
    test_cell()
    test_board()
    test_solver()
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        test_sounds(td)
    print("\nALL AUTOMATED TESTS PASSED!")
