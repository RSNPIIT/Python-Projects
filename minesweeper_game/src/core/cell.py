"""
cell.py - Object-Oriented Cell Abstraction for Minesweeper.
Encapsulates individual tile state, flag cycles, mine presence, and neighbor count.
"""

from enum import Enum, auto


class CellState(Enum):
    HIDDEN = auto()
    REVEALED = auto()
    FLAGGED = auto()
    QUESTION = auto()


class Cell:
    """Represents a single square cell on the Minesweeper grid."""

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.is_mine = False
        self.neighbor_mines = 0
        self.state = CellState.HIDDEN

        # Game Over / Telemetry flags
        self.exploded = False       # True if this specific mine was triggered
        self.wrong_flag = False      # True if marked with flag but was not a mine
        self.shield_saved = False    # True if life/shield saved player from this mine
        self.highlighted = False     # Visual highlight for hint or keyboard navigation

    @property
    def is_revealed(self) -> bool:
        return self.state == CellState.REVEALED

    @property
    def is_flagged(self) -> bool:
        return self.state == CellState.FLAGGED

    @property
    def is_question(self) -> bool:
        return self.state == CellState.QUESTION

    @property
    def is_hidden(self) -> bool:
        return self.state == CellState.HIDDEN

    @property
    def is_empty(self) -> bool:
        """True if revealed, not a mine, and has 0 adjacent neighbor mines."""
        return self.is_revealed and not self.is_mine and self.neighbor_mines == 0

    def toggle_flag(self, allow_question: bool = True) -> CellState:
        """Cycles state: HIDDEN -> FLAGGED -> (QUESTION) -> HIDDEN."""
        if self.is_revealed:
            return self.state

        if self.state == CellState.HIDDEN:
            self.state = CellState.FLAGGED
        elif self.state == CellState.FLAGGED:
            self.state = CellState.QUESTION if allow_question else CellState.HIDDEN
        elif self.state == CellState.QUESTION:
            self.state = CellState.HIDDEN

        return self.state

    def set_flag(self, flag: bool) -> None:
        """Explicitly set or clear flag."""
        if self.is_revealed:
            return
        self.state = CellState.FLAGGED if flag else CellState.HIDDEN

    def reveal(self) -> bool:
        """Reveals cell. Returns True if successfully revealed, False if already revealed or flagged."""
        if self.state in (CellState.REVEALED, CellState.FLAGGED):
            return False
        self.state = CellState.REVEALED
        return True

    def reset(self) -> None:
        """Resets cell to default initial hidden state."""
        self.is_mine = False
        self.neighbor_mines = 0
        self.state = CellState.HIDDEN
        self.exploded = False
        self.wrong_flag = False
        self.shield_saved = False
        self.highlighted = False

    def __repr__(self) -> str:
        tag = "M" if self.is_mine else str(self.neighbor_mines)
        return f"Cell({self.row}, {self.col}, {self.state.name}, {tag})"
