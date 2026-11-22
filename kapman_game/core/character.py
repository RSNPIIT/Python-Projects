"""Kapman Game - Base Character with Corner Buffering & Grid Alignment"""
import math
from core.constants import (
    TILE_SIZE, MAZE_WIDTH, MAZE_HEIGHT,
    DIR_NONE, DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    OPPOSITE_DIR
)
from core.maze import Maze

class Character:
    def __init__(self, start_col: float, start_row: float, speed: float):
        self.start_x = (start_col + 0.5) * TILE_SIZE
        self.start_y = (start_row + 0.5) * TILE_SIZE
        self.x = self.start_x
        self.y = self.start_y
        self.speed = speed
        self.base_speed = speed

        self.direction = DIR_NONE
        self.desired_direction = DIR_NONE

    def reset_position(self):
        self.x = self.start_x
        self.y = self.start_y
        self.direction = DIR_NONE
        self.desired_direction = DIR_NONE

    @property
    def col(self) -> int:
        return int(self.x // TILE_SIZE)

    @property
    def row(self) -> int:
        return int(self.y // TILE_SIZE)

    @property
    def center_tile_x(self) -> float:
        return (self.col + 0.5) * TILE_SIZE

    @property
    def center_tile_y(self) -> float:
        return (self.row + 0.5) * TILE_SIZE

    def set_desired_direction(self, new_dir: tuple[int, int]):
        self.desired_direction = new_dir

    def update_movement(self, dt: float, maze: Maze, allow_gate: bool = False):
        """
        Executes movement with pre-turn corner buffering and wall collision.
        """
        if self.direction == DIR_NONE and self.desired_direction == DIR_NONE:
            return

        # 1. Immediate 180-degree reversal check
        if self.desired_direction == OPPOSITE_DIR.get(self.direction):
            self.direction = self.desired_direction

        # 2. Check if we can turn in desired direction
        dist_to_cx = self.x - self.center_tile_x
        dist_to_cy = self.y - self.center_tile_y
        corner_tolerance = 5.0  # px snap threshold for cornering

        if self.desired_direction != DIR_NONE and self.desired_direction != self.direction:
            target_col = self.col + self.desired_direction[0]
            target_row = self.row + self.desired_direction[1]

            if maze.is_passable(target_row, target_col, allow_gate=allow_gate):
                # Check perpendicular alignment to snap cleanly
                can_turn = False
                if self.desired_direction in (DIR_UP, DIR_DOWN):
                    if abs(dist_to_cx) <= corner_tolerance:
                        self.x = self.center_tile_x
                        can_turn = True
                elif self.desired_direction in (DIR_LEFT, DIR_RIGHT):
                    if abs(dist_to_cy) <= corner_tolerance:
                        self.y = self.center_tile_y
                        can_turn = True

                if can_turn:
                    self.direction = self.desired_direction

        # 3. Advance in current direction if path ahead is clear
        if self.direction != DIR_NONE:
            move_dist = self.speed * dt
            next_x = self.x + self.direction[0] * move_dist
            next_y = self.y + self.direction[1] * move_dist

            # Check next tile
            ahead_col = int((next_x + self.direction[0] * (TILE_SIZE * 0.45)) // TILE_SIZE)
            ahead_row = int((next_y + self.direction[1] * (TILE_SIZE * 0.45)) // TILE_SIZE)

            # Special case: Warp tunnel row 14
            if self.row == 14 and (next_x < -TILE_SIZE / 2 or next_x > MAZE_WIDTH + TILE_SIZE / 2):
                if next_x < -TILE_SIZE / 2:
                    next_x = MAZE_WIDTH + TILE_SIZE / 2
                elif next_x > MAZE_WIDTH + TILE_SIZE / 2:
                    next_x = -TILE_SIZE / 2
                self.x = next_x
                self.y = next_y
                return

            if maze.is_passable(ahead_row, ahead_col, allow_gate=allow_gate):
                self.x = next_x
                self.y = next_y
            else:
                # Wall hit: snap flush to center of current tile and halt
                if self.direction in (DIR_LEFT, DIR_RIGHT):
                    self.x = self.center_tile_x
                else:
                    self.y = self.center_tile_y
                self.direction = DIR_NONE
