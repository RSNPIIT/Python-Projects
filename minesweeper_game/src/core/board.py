"""
board.py - Minesweeper Board Logic with Fair Generation & Cascade Mechanics.
Encapsulates 2D grid, guaranteed safe opening, BFS cascade, chording, and 3BV calculation.
"""

import random
from collections import deque
from typing import Generator, List, Optional, Set, Tuple
from .cell import Cell, CellState


class Board:
    """Manages 2D grid of Cells and game-rule evaluations."""

    def __init__(self, rows: int = 9, cols: int = 9, mines: int = 10, safe_opening: bool = True):
        self.rows = max(4, min(rows, 60))
        self.cols = max(4, min(cols, 60))
        # Ensure mine count is within playable bounds
        max_possible_mines = (self.rows * self.cols) - 1
        self.total_mines = max(1, min(mines, max_possible_mines))
        self.safe_opening = safe_opening

        self.grid: List[List[Cell]] = [
            [Cell(r, c) for c in range(self.cols)] for r in range(self.rows)
        ]
        self.first_click_made = False
        self.mines_placed = False

    def reset(self, rows: Optional[int] = None, cols: Optional[int] = None, mines: Optional[int] = None) -> None:
        """Resets the board, optionally reconfiguring dimensions."""
        if rows is not None:
            self.rows = max(4, min(rows, 60))
        if cols is not None:
            self.cols = max(4, min(cols, 60))
        if mines is not None:
            max_possible_mines = (self.rows * self.cols) - 1
            self.total_mines = max(1, min(mines, max_possible_mines))

        self.grid = [[Cell(r, c) for c in range(self.cols)] for r in range(self.rows)]
        self.first_click_made = False
        self.mines_placed = False

    def get_cell(self, row: int, col: int) -> Optional[Cell]:
        """Safely gets cell if within bounds."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None

    def get_neighbors(self, row: int, col: int) -> List[Cell]:
        """Returns adjacent orthogonal and diagonal neighbor cells (up to 8)."""
        neighbors = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    neighbors.append(self.grid[nr][nc])
        return neighbors

    def place_mines(self, safe_r: int, safe_c: int) -> None:
        """
        Distributes mines randomly across the board.
        If safe_opening is True, guarantees an opening cascade by keeping (safe_r, safe_c)
        and all its immediate neighbors free of mines (unless board density is too extreme).
        """
        all_coords = [(r, c) for r in range(self.rows) for c in range(self.cols)]

        # Protected zone for first click
        protected: Set[Tuple[int, int]] = {(safe_r, safe_c)}
        if self.safe_opening and (self.rows * self.cols - 9 >= self.total_mines):
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr, nc = safe_r + dr, safe_c + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        protected.add((nr, nc))

        candidate_coords = [coord for coord in all_coords if coord not in protected]

        # If not enough room outside protected zone, relax protected to just the clicked cell
        if len(candidate_coords) < self.total_mines:
            candidate_coords = [coord for coord in all_coords if coord != (safe_r, safe_c)]

        chosen_mine_coords = set(random.sample(candidate_coords, self.total_mines))

        # Assign mines and compute adjacent numbers
        for r, c in chosen_mine_coords:
            self.grid[r][c].is_mine = True

        for r in range(self.rows):
            for c in range(self.cols):
                if not self.grid[r][c].is_mine:
                    self.grid[r][c].neighbor_mines = sum(
                        1 for n in self.get_neighbors(r, c) if n.is_mine
                    )

        self.mines_placed = True

    def reveal_cell(self, row: int, col: int) -> Tuple[bool, List[Cell]]:
        """
        Reveals cell at (row, col).
        Returns:
            (hit_mine: bool, newly_revealed_cells: List[Cell])
        """
        cell = self.get_cell(row, col)
        if not cell or cell.is_revealed or cell.is_flagged:
            return False, []

        # Handle first-click safety
        if not self.first_click_made:
            self.first_click_made = True
            if not self.mines_placed:
                self.place_mines(row, col)

        # Triggered mine
        if cell.is_mine:
            cell.exploded = True
            cell.reveal()
            return True, [cell]

        # Non-mine cell revealed
        revealed_cells: List[Cell] = []
        queue = deque([cell])
        visited: Set[Tuple[int, int]] = {(row, col)}

        while queue:
            curr = queue.popleft()
            if curr.is_flagged:
                continue

            if curr.reveal():
                revealed_cells.append(curr)

            # If empty (0 neighbors), cascade flood-fill adjacent hidden cells
            if curr.neighbor_mines == 0 and not curr.is_mine:
                for neighbor in self.get_neighbors(curr.row, curr.col):
                    coord = (neighbor.row, neighbor.col)
                    if coord not in visited and not neighbor.is_revealed and not neighbor.is_flagged:
                        visited.add(coord)
                        queue.append(neighbor)

        return False, revealed_cells

    def chord(self, row: int, col: int) -> Tuple[bool, List[Cell]]:
        """
        Chords a revealed numbered tile:
        If number of flagged adjacent cells equals neighbor_mines, reveals all other neighbors!
        Returns:
            (hit_mine: bool, newly_revealed_cells: List[Cell])
        """
        cell = self.get_cell(row, col)
        if not cell or not cell.is_revealed or cell.neighbor_mines == 0:
            return False, []

        neighbors = self.get_neighbors(row, col)
        flagged_count = sum(1 for n in neighbors if n.is_flagged)

        if flagged_count != cell.neighbor_mines:
            return False, []

        hit_mine = False
        all_revealed: List[Cell] = []

        for n in neighbors:
            if not n.is_revealed and not n.is_flagged:
                mine_hit, rev = self.reveal_cell(n.row, n.col)
                all_revealed.extend(rev)
                if mine_hit:
                    hit_mine = True

        return hit_mine, all_revealed

    @property
    def flags_placed(self) -> int:
        """Count of currently active flags."""
        return sum(
            1 for row in self.grid for cell in row if cell.is_flagged
        )

    @property
    def remaining_mines(self) -> int:
        """Mines minus flags placed (can be negative if overflagged)."""
        return self.total_mines - self.flags_placed

    @property
    def revealed_count(self) -> int:
        """Total revealed non-mine cells."""
        return sum(
            1 for row in self.grid for cell in row if cell.is_revealed and not cell.is_mine
        )

    @property
    def target_revealed_count(self) -> int:
        """Total safe non-mine cells required to win."""
        return (self.rows * self.cols) - self.total_mines

    def check_win(self) -> bool:
        """Returns True if all non-mine cells are revealed."""
        return self.revealed_count == self.target_revealed_count

    def auto_flag_all_mines(self) -> None:
        """Automatically flags all unflagged mines upon victory."""
        for row in self.grid:
            for cell in row:
                if cell.is_mine and not cell.is_flagged:
                    cell.state = CellState.FLAGGED

    def reveal_all_on_loss(self) -> None:
        """Reveals all remaining mines and flags false positives on defeat."""
        for row in self.grid:
            for cell in row:
                if cell.is_mine:
                    if not cell.is_flagged:
                        cell.reveal()
                else:
                    if cell.is_flagged:
                        cell.wrong_flag = True

    def calculate_3bv(self) -> int:
        """
        Calculates Bechtel's Board Benchmark Value (3BV).
        Standard competitive benchmark: minimum clicks needed to clear the board without flags.
        """
        if not self.mines_placed:
            return 0

        visited = set()
        openings = 0

        # Count 0 openings
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if not cell.is_mine and cell.neighbor_mines == 0 and (r, c) not in visited:
                    openings += 1
                    # Flood fill this opening
                    q = deque([(r, c)])
                    visited.add((r, c))
                    while q:
                        cr, cc = q.popleft()
                        for n in self.get_neighbors(cr, cc):
                            if not n.is_mine:
                                visited.add((n.row, n.col))
                                if n.neighbor_mines == 0 and (n.row, n.col) not in visited:
                                    q.append((n.row, n.col))

        # Count remaining non-mine cells not covered by any opening
        isolated = 0
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if not cell.is_mine and (r, c) not in visited:
                    isolated += 1

        return openings + isolated
