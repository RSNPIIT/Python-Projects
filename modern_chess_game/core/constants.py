"""Modern Chess Game - Constants and Enums"""
from enum import Enum, auto
import numpy as np

class Color(Enum):
    WHITE = 0
    BLACK = 1

    @property
    def opponent(self):
        return Color.BLACK if self == Color.WHITE else Color.WHITE

    @property
    def name_str(self):
        return "White" if self == Color.WHITE else "Black"

class PieceType(Enum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

    @property
    def symbol(self):
        return {
            PieceType.PAWN: "P",
            PieceType.KNIGHT: "N",
            PieceType.BISHOP: "B",
            PieceType.ROOK: "R",
            PieceType.QUEEN: "Q",
            PieceType.KING: "K"
        }[self]

    @property
    def value(self):
        return {
            PieceType.PAWN: 100,
            PieceType.KNIGHT: 320,
            PieceType.BISHOP: 330,
            PieceType.ROOK: 500,
            PieceType.QUEEN: 900,
            PieceType.KING: 20000
        }[self]

# Board dimensions
BOARD_SIZE = 8
SQUARE_PIXELS = 90
BOARD_PIXELS = BOARD_SIZE * SQUARE_PIXELS  # 720 px
SIDE_PANEL_WIDTH = 260
WINDOW_WIDTH = BOARD_PIXELS + SIDE_PANEL_WIDTH  # 980 px
WINDOW_HEIGHT = BOARD_PIXELS  # 720 px

# Color Palettes (Normalized RGBA for ModernGL [0.0 - 1.0])
THEMES = {
    "Cyber Blue": {
        "bg": (0.12, 0.13, 0.16, 1.0),
        "panel_bg": (0.09, 0.10, 0.13, 1.0),
        "light_sq": (0.52, 0.79, 0.98, 1.0),       # #84c9fb from user's original turtle
        "dark_sq": (0.094, 0.141, 0.169, 1.0),     # #18242b from user's original turtle
        "selected": (0.91, 0.40, 0.47, 0.65),      # #CF6679 soft crimson
        "last_move": (0.95, 0.85, 0.35, 0.35),     # warm golden highlight
        "hover": (1.0, 1.0, 1.0, 0.15),
        "move_dot": (0.15, 0.80, 0.65, 0.65),      # teal accent dot
        "check_glow": (0.95, 0.20, 0.25, 0.85),    # red king check glow
    },
    "Neo Emerald": {
        "bg": (0.10, 0.12, 0.11, 1.0),
        "panel_bg": (0.07, 0.09, 0.08, 1.0),
        "light_sq": (0.93, 0.93, 0.82, 1.0),
        "dark_sq": (0.46, 0.59, 0.34, 1.0),
        "selected": (0.95, 0.75, 0.20, 0.65),
        "last_move": (0.85, 0.80, 0.25, 0.35),
        "hover": (1.0, 1.0, 1.0, 0.15),
        "move_dot": (0.25, 0.70, 0.40, 0.65),
        "check_glow": (0.95, 0.20, 0.25, 0.85),
    },
    "Midnight Slate": {
        "bg": (0.14, 0.15, 0.18, 1.0),
        "panel_bg": (0.10, 0.11, 0.13, 1.0),
        "light_sq": (0.85, 0.86, 0.88, 1.0),
        "dark_sq": (0.35, 0.40, 0.46, 1.0),
        "selected": (0.30, 0.65, 0.95, 0.65),
        "last_move": (0.40, 0.75, 0.90, 0.35),
        "hover": (1.0, 1.0, 1.0, 0.15),
        "move_dot": (0.30, 0.65, 0.95, 0.65),
        "check_glow": (0.95, 0.20, 0.25, 0.85),
    }
}
DEFAULT_THEME = "Cyber Blue"

def square_name(row: int, col: int) -> str:
    """Convert (row, col) [0..7, 0..7] with row 0 = rank 8 to algebraic 'a8'..'h1'"""
    file_char = chr(ord('a') + col)
    rank_num = 8 - row
    return f"{file_char}{rank_num}"

def name_to_square(name: str) -> tuple[int, int]:
    """Convert algebraic 'e4' to (row, col)"""
    col = ord(name[0].lower()) - ord('a')
    row = 8 - int(name[1])
    return (row, col)
