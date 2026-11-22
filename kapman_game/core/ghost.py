"""Kapman Game - Ghost / Mummy AI & State Machine"""
import math
import random
from core.constants import (
    TILE_SIZE,
    GHOST_CHASE, GHOST_SCATTER, GHOST_FRIGHTENED, GHOST_EATEN,
    GHOST_NORMAL_SPEED, GHOST_FRIGHT_SPEED, GHOST_EATEN_SPEED, GHOST_TUNNEL_SPEED,
    DIR_NONE, DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    OPPOSITE_DIR
)
from core.character import Character
from core.maze import Maze

GHOST_RED = 0     # Akhenaten / Blinky
GHOST_PINK = 1    # Nefertiti / Pinky
GHOST_CYAN = 2    # Anubis / Inky
GHOST_ORANGE = 3  # Horus / Clyde

GHOST_NAMES = {
    GHOST_RED: "Akhenaten",
    GHOST_PINK: "Nefertiti",
    GHOST_CYAN: "Anubis",
    GHOST_ORANGE: "Horus"
}

GHOST_BASE_COLORS = {
    GHOST_RED: (240, 50, 60),      # Crimson
    GHOST_PINK: (255, 130, 180),   # Rose
    GHOST_CYAN: (45, 215, 240),    # Turquoise
    GHOST_ORANGE: (255, 160, 40)   # Amber
}

class Ghost(Character):
    def __init__(self, ghost_id: int, start_col: float, start_row: float, scatter_col: int, scatter_row: int):
        super().__init__(start_col, start_row, GHOST_NORMAL_SPEED)
        self.ghost_id = ghost_id
        self.scatter_target = (scatter_col, scatter_row)
        self.state = GHOST_SCATTER
        self.base_color = GHOST_BASE_COLORS[ghost_id]

        # House & release state
        self.in_house = (ghost_id != GHOST_RED)
        self.house_exit_timer = {
            GHOST_RED: 0.0,
            GHOST_PINK: 2.0,
            GHOST_CYAN: 6.0,
            GHOST_ORANGE: 10.0
        }[ghost_id]

        self.last_tile = (self.row, self.col)

    def reset(self):
        self.reset_position()
        self.state = GHOST_SCATTER
        self.in_house = (self.ghost_id != GHOST_RED)
        self.speed = GHOST_NORMAL_SPEED
        self.house_exit_timer = {
            GHOST_RED: 0.0,
            GHOST_PINK: 2.0,
            GHOST_CYAN: 6.0,
            GHOST_ORANGE: 10.0
        }[self.ghost_id]
        self.last_tile = (self.row, self.col)

    def become_frightened(self):
        if self.state != GHOST_EATEN and not self.in_house:
            self.state = GHOST_FRIGHTENED
            self.speed = GHOST_FRIGHT_SPEED
            # Reverse direction on fright
            self.desired_direction = OPPOSITE_DIR.get(self.direction, DIR_NONE)

    def become_eaten(self):
        self.state = GHOST_EATEN
        self.speed = GHOST_EATEN_SPEED

    def update(
        self,
        dt: float,
        maze: Maze,
        kapman_pos: tuple[float, float],
        kapman_dir: tuple[int, int],
        red_ghost_pos: tuple[float, float] = (0, 0),
        global_mode: str = GHOST_SCATTER
    ):
        # 1. Update in-house timer
        if self.in_house:
            self.house_exit_timer -= dt
            # Bob up and down inside house
            self.y += math.sin(self.house_exit_timer * 6.0) * 0.4
            if self.house_exit_timer <= 0:
                # Emerge through door at (row 12, col 13.5)
                self.x = (13.5 + 0.5) * TILE_SIZE
                self.y = (11.0 + 0.5) * TILE_SIZE
                self.in_house = False
                self.direction = DIR_LEFT
            return

        # 2. Adjust state based on global cycle
        if self.state not in (GHOST_FRIGHTENED, GHOST_EATEN):
            self.state = global_mode
            self.speed = GHOST_NORMAL_SPEED

        # 3. Slow down in side warp tunnels
        if self.row == 14 and (self.col <= 5 or self.col >= 22):
            self.speed = min(self.speed, GHOST_TUNNEL_SPEED)

        # 4. Determine AI target tile
        target_tile = self._calculate_target_tile(kapman_pos, kapman_dir, red_ghost_pos)

        # 5. At intersection / new tile, choose optimal turn
        curr_tile = (self.row, self.col)
        dist_to_center = abs(self.x - self.center_tile_x) + abs(self.y - self.center_tile_y)

        if curr_tile != self.last_tile or (dist_to_center < 3.0 and self.desired_direction == DIR_NONE):
            self._decide_next_turn(maze, target_tile)
            self.last_tile = curr_tile

        # Allow gate passage only when returning home after being eaten
        allow_gate = (self.state == GHOST_EATEN)
        self.update_movement(dt, maze, allow_gate=allow_gate)

        # 6. Eaten ghost reaches home -> revives!
        if self.state == GHOST_EATEN:
            gate_x = (13.5 + 0.5) * TILE_SIZE
            gate_y = (14.0 + 0.5) * TILE_SIZE
            if abs(self.x - gate_x) < 8.0 and abs(self.y - gate_y) < 8.0:
                self.state = global_mode
                self.speed = GHOST_NORMAL_SPEED
                self.direction = DIR_UP

    def _calculate_target_tile(
        self,
        kapman_pos: tuple[float, float],
        kapman_dir: tuple[int, int],
        red_ghost_pos: tuple[float, float]
    ) -> tuple[int, int]:
        # Eaten -> target ghost house door at (12, 13)
        if self.state == GHOST_EATEN:
            return (12, 13)

        # Scatter -> target designated corner
        if self.state == GHOST_SCATTER:
            return self.scatter_target

        # Frightened -> pseudo-random
        if self.state == GHOST_FRIGHTENED:
            return (random.randint(0, 30), random.randint(0, 27))

        # Chase mode: personality-specific targeting
        k_col = int(kapman_pos[0] // TILE_SIZE)
        k_row = int(kapman_pos[1] // TILE_SIZE)

        if self.ghost_id == GHOST_RED:
            # Akhenaten: Direct Chase
            return (k_row, k_col)

        elif self.ghost_id == GHOST_PINK:
            # Nefertiti: Ambush 4 tiles ahead of Kapman
            target_r = k_row + kapman_dir[1] * 4
            target_c = k_col + kapman_dir[0] * 4
            return (target_r, target_c)

        elif self.ghost_id == GHOST_CYAN:
            # Anubis: Flanking vector
            pivot_r = k_row + kapman_dir[1] * 2
            pivot_c = k_col + kapman_dir[0] * 2
            red_r = int(red_ghost_pos[1] // TILE_SIZE)
            red_c = int(red_ghost_pos[0] // TILE_SIZE)
            target_r = pivot_r + (pivot_r - red_r)
            target_c = pivot_c + (pivot_c - red_c)
            return (target_r, target_c)

        elif self.ghost_id == GHOST_ORANGE:
            # Horus: Shy - chase if > 8 tiles away, else scatter
            dist_sq = (self.row - k_row) ** 2 + (self.col - k_col) ** 2
            if dist_sq > 64:  # > 8 tiles
                return (k_row, k_col)
            else:
                return self.scatter_target

        return (k_row, k_col)

    def _decide_next_turn(self, maze: Maze, target_tile: tuple[int, int]):
        """Evaluates adjacent tiles and picks direction minimizing distance to target."""
        candidates = [DIR_UP, DIR_LEFT, DIR_DOWN, DIR_RIGHT]
        opposite = OPPOSITE_DIR.get(self.direction, DIR_NONE)

        best_dir = DIR_NONE
        min_dist_sq = float("inf")

        for d in candidates:
            # Cannot do immediate 180 reverse at intersection
            if d == opposite and self.direction != DIR_NONE:
                continue

            nr = self.row + d[1]
            nc = self.col + d[0]

            allow_gate = (self.state == GHOST_EATEN)
            if maze.is_passable(nr, nc, allow_gate=allow_gate):
                dist_sq = (nr - target_tile[0]) ** 2 + (nc - target_tile[1]) ** 2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    best_dir = d

        if best_dir != DIR_NONE:
            self.set_desired_direction(best_dir)
