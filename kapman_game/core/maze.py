"""Kapman Game - Maze Map, Geometry & State"""
from core.constants import (
    MAZE_COLS, MAZE_ROWS, TILE_SIZE,
    TILE_EMPTY, TILE_WALL, TILE_PILL, TILE_ENERGIZER,
    TILE_GATE, TILE_GHOST_HOUSE, TILE_WARP,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
)

DEFAULT_MAZE_LAYOUT = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #.##          ##.#     ",
    "     #.## ###__### ##.#     ",
    "######.## #HHHHHH# ##.######",
    "W     .   #HHHHHH#   .     W",
    "######.## #HHHHHH# ##.######",
    "     #.## ######## ##.#     ",
    "     #.##          ##.#     ",
    "     #.## ######## ##.#     ",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#o..##................##..o#",
    "###.##.##.########.##.##.###",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################"
]

class Maze:
    def __init__(self):
        self.cols = MAZE_COLS
        self.rows = MAZE_ROWS
        self.tiles = [[TILE_EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
        self.pills_remaining = 0
        self.total_pills = 0
        self.reset()

    def reset(self):
        """Re-initializes all tiles and pellets from layout."""
        self.pills_remaining = 0
        self.total_pills = 0

        for r in range(self.rows):
            line = DEFAULT_MAZE_LAYOUT[r]
            for c in range(self.cols):
                char = line[c]
                if char == "#":
                    self.tiles[r][c] = TILE_WALL
                elif char == ".":
                    self.tiles[r][c] = TILE_PILL
                    self.pills_remaining += 1
                    self.total_pills += 1
                elif char == "o":
                    self.tiles[r][c] = TILE_ENERGIZER
                    self.pills_remaining += 1
                    self.total_pills += 1
                elif char == "_":
                    self.tiles[r][c] = TILE_GATE
                elif char == "H":
                    self.tiles[r][c] = TILE_GHOST_HOUSE
                elif char == "W":
                    self.tiles[r][c] = TILE_WARP
                else:
                    self.tiles[r][c] = TILE_EMPTY

    def get_tile(self, row: int, col: int) -> int:
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.tiles[row][col]
        return TILE_WALL

    def is_wall(self, row: int, col: int) -> bool:
        return self.get_tile(row, col) == TILE_WALL

    def is_gate(self, row: int, col: int) -> bool:
        return self.get_tile(row, col) == TILE_GATE

    def is_passable(self, row: int, col: int, allow_gate: bool = False) -> bool:
        if not (0 <= row < self.rows):
            return False
        # Warp tunnels on row 14 allow horizontal wrap-around
        if row == 14 and (col < 0 or col >= self.cols):
            return True

        tile = self.get_tile(row, col)
        if tile == TILE_WALL:
            return False
        if tile == TILE_GATE:
            return allow_gate
        return True

    def eat_pellet(self, row: int, col: int) -> tuple[int, bool]:
        """
        Attempts to eat a pill/energizer at (row, col).
        Returns (score_earned, is_energizer).
        """
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return 0, False

        tile = self.tiles[row][col]
        if tile == TILE_PILL:
            self.tiles[row][col] = TILE_EMPTY
            self.pills_remaining -= 1
            return 10, False
        elif tile == TILE_ENERGIZER:
            self.tiles[row][col] = TILE_EMPTY
            self.pills_remaining -= 1
            return 50, True

        return 0, False

    def is_cleared(self) -> bool:
        return self.pills_remaining <= 0
