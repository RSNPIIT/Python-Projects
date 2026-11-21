"""
solver.py - Logical Deduction & Smart Hint Engine for Minesweeper.
Analyzes revealed constraints to find mathematically guaranteed safe moves and mines.
"""

from typing import List, Optional, Set, Tuple
from .board import Board
from .cell import Cell


class HintResult:
    def __init__(self, row: int, col: int, is_safe: bool, explanation: str):
        self.row = row
        self.col = col
        self.is_safe = is_safe
        self.explanation = explanation

    def __repr__(self) -> str:
        action = "CLICK" if self.is_safe else "FLAG"
        return f"Hint({action} at ({self.row}, {self.col}): {self.explanation})"


class Solver:
    """Performs constraint propagation to identify 100% deduction moves without guessing."""

    @staticmethod
    def get_hint(board: Board) -> Optional[HintResult]:
        """
        Scans the board and returns the first logically proven safe move or guaranteed mine.
        Returns None if board is fresh or requires probabilistic guessing.
        """
        if not board.first_click_made:
            # First click is always safe
            center_r, center_c = board.rows // 2, board.cols // 2
            return HintResult(center_r, center_c, True, "First move is guaranteed safe with an opening cascade!")

        # Step 1: Single-cell direct deductions
        for r in range(board.rows):
            for c in range(board.cols):
                cell = board.grid[r][c]
                if not cell.is_revealed or cell.neighbor_mines == 0:
                    continue

                neighbors = board.get_neighbors(r, c)
                hidden_unflagged = [n for n in neighbors if not n.is_revealed and not n.is_flagged]
                flagged = [n for n in neighbors if n.is_flagged]

                # Case A: All required mines are already flagged -> remaining hidden are SAFE!
                if len(flagged) == cell.neighbor_mines and hidden_unflagged:
                    target = hidden_unflagged[0]
                    return HintResult(
                        target.row,
                        target.col,
                        True,
                        f"Numbered cell '{cell.neighbor_mines}' at ({r+1}, {c+1}) already has all {cell.neighbor_mines} mines flagged."
                    )

                # Case B: Remaining hidden tiles exactly equal remaining mines needed -> all are MINES!
                mines_needed = cell.neighbor_mines - len(flagged)
                if len(hidden_unflagged) == mines_needed and hidden_unflagged:
                    target = hidden_unflagged[0]
                    return HintResult(
                        target.row,
                        target.col,
                        False,
                        f"Numbered cell '{cell.neighbor_mines}' at ({r+1}, {c+1}) needs {mines_needed} more mine(s), exactly matching the {len(hidden_unflagged)} available tile(s)."
                    )

        # Step 2: Subset reduction logic (2-cell interactions, e.g. 1-2-1 / 1-2-2-1 patterns)
        frontier_constraints = []
        for r in range(board.rows):
            for c in range(board.cols):
                cell = board.grid[r][c]
                if cell.is_revealed and cell.neighbor_mines > 0:
                    neighbors = board.get_neighbors(r, c)
                    hidden_set = {n for n in neighbors if not n.is_revealed and not n.is_flagged}
                    flagged_count = sum(1 for n in neighbors if n.is_flagged)
                    remaining = cell.neighbor_mines - flagged_count
                    if hidden_set and remaining > 0:
                        frontier_constraints.append((hidden_set, remaining, cell))

        # Check pairs of constraints (A is subset of B)
        for i in range(len(frontier_constraints)):
            set_a, count_a, cell_a = frontier_constraints[i]
            for j in range(len(frontier_constraints)):
                if i == j:
                    continue
                set_b, count_b, cell_b = frontier_constraints[j]

                if set_a.issubset(set_b) and set_a != set_b:
                    diff_set = set_b - set_a
                    diff_count = count_b - count_a

                    # If difference has 0 mines, all cells in diff_set are SAFE!
                    if diff_count == 0 and diff_set:
                        target = next(iter(diff_set))
                        return HintResult(
                            target.row,
                            target.col,
                            True,
                            f"Subset deduction between ({cell_a.row+1}, {cell_a.col+1}) and ({cell_b.row+1}, {cell_b.col+1}) proves this tile is safe."
                        )

                    # If difference tiles equal difference count, all are MINES!
                    if diff_count == len(diff_set) and diff_set:
                        target = next(iter(diff_set))
                        return HintResult(
                            target.row,
                            target.col,
                            False,
                            f"Subset deduction between ({cell_a.row+1}, {cell_a.col+1}) and ({cell_b.row+1}, {cell_b.col+1}) proves this tile is a mine."
                        )

        # If no 100% deterministic deduction is found, suggest a low-risk edge cell
        all_hidden = [
            board.grid[r][c]
            for r in range(board.rows)
            for c in range(board.cols)
            if not board.grid[r][c].is_revealed and not board.grid[r][c].is_flagged
        ]
        if all_hidden:
            target = all_hidden[0]
            return HintResult(
                target.row,
                target.col,
                True,
                "No pure deduction available. Recommended least-constrained tile to probe."
            )

        return None
