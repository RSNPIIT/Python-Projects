"""Kapman Game - Ghost / Mummy AI & State Machine"""
import math
import random
from collections import deque
from core.constants import (
    TILE_SIZE, MAZE_COLS, MAZE_ROWS,
    GHOST_CHASE, GHOST_SCATTER, GHOST_FRIGHTENED, GHOST_EATEN,
    GHOST_ENTERING, GHOST_EXITING,
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

# Key navigation coordinates for Ghost House
DOOR_CENTER_X = (13.5 + 0.5) * TILE_SIZE  # 280.0 px (horizontal center)
DOOR_CENTER_Y = (11.0 + 0.5) * TILE_SIZE  # 230.0 px (row 11 corridor outside gate)
HOUSE_CENTER_Y = (14.0 + 0.5) * TILE_SIZE # 290.0 px (row 14 altar inside house)

class Ghost(Character):
    _HOME_FLOW_FIELD: dict[tuple[int, int], tuple[int, int]] | None = None

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
            GHOST_CYAN: 5.0,
            GHOST_ORANGE: 8.0
        }[ghost_id]

        self.last_tile = (self.row, self.col)

    @classmethod
    def _build_home_flow_field(cls, maze: Maze) -> dict[tuple[int, int], tuple[int, int]]:
        """Precomputes BFS shortest path directions from every tile to the ghost house entrance."""
        doors = [(11, 13), (11, 14)]
        queue = deque(doors)
        visited = set(doors)
        dist = {d: 0 for d in doors}

        while queue:
            r, c = queue.popleft()
            for dc, dr in [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]:
                nr = r + dr
                nc = c + dc
                if nr == 14:
                    if nc < 0:
                        nc = MAZE_COLS - 1
                    elif nc >= MAZE_COLS:
                        nc = 0
                if 0 <= nr < MAZE_ROWS and 0 <= nc < MAZE_COLS:
                    if maze.is_passable(nr, nc, allow_gate=False) and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        dist[(nr, nc)] = dist[(r, c)] + 1
                        queue.append((nr, nc))

        flow_field = {}
        for (r, c) in visited:
            if (r, c) in doors:
                continue
            best_dir = DIR_NONE
            min_d = float("inf")
            for d in [DIR_UP, DIR_LEFT, DIR_DOWN, DIR_RIGHT]:
                dc, dr = d
                nr = r + dr
                nc = c + dc
                if nr == 14:
                    if nc < 0:
                        nc = MAZE_COLS - 1
                    elif nc >= MAZE_COLS:
                        nc = 0
                if (nr, nc) in dist and dist[(nr, nc)] < min_d:
                    min_d = dist[(nr, nc)]
                    best_dir = d
            flow_field[(r, c)] = best_dir

        return flow_field

    def reset(self):
        self.reset_position()
        self.state = GHOST_SCATTER
        self.in_house = (self.ghost_id != GHOST_RED)
        self.speed = GHOST_NORMAL_SPEED
        self.house_exit_timer = {
            GHOST_RED: 0.0,
            GHOST_PINK: 2.0,
            GHOST_CYAN: 5.0,
            GHOST_ORANGE: 8.0
        }[self.ghost_id]
        self.last_tile = (self.row, self.col)

        if not self.in_house:
            self.direction = DIR_LEFT

    def become_frightened(self):
        # Only ghosts actively roaming the maze can become frightened
        if self.state in (GHOST_CHASE, GHOST_SCATTER) and not self.in_house:
            self.state = GHOST_FRIGHTENED
            self.speed = GHOST_FRIGHT_SPEED
            # Immediate 180 reverse direction on fright
            self.desired_direction = OPPOSITE_DIR.get(self.direction, DIR_NONE)

    def become_eaten(self):
        self.state = GHOST_EATEN
        self.speed = GHOST_EATEN_SPEED
        self.last_tile = (-1, -1)
        if Ghost._HOME_FLOW_FIELD:
            flow_dir = Ghost._HOME_FLOW_FIELD.get((self.row, self.col))
            if flow_dir:
                self.set_desired_direction(flow_dir)
                self.direction = flow_dir
            else:
                self.direction = DIR_NONE
                self.desired_direction = DIR_NONE
        else:
            self.direction = DIR_NONE
            self.desired_direction = DIR_NONE

    def update(
        self,
        dt: float,
        maze: Maze,
        kapman_pos: tuple[float, float],
        kapman_dir: tuple[int, int],
        red_ghost_pos: tuple[float, float] = (0, 0),
        global_mode: str = GHOST_SCATTER,
        is_frightened: bool = False
    ):
        if Ghost._HOME_FLOW_FIELD is None:
            Ghost._HOME_FLOW_FIELD = Ghost._build_home_flow_field(maze)

        # 1. Update in-house ghosts waiting to emerge
        if self.in_house:
            if self.house_exit_timer > 0:
                self.house_exit_timer -= dt
                # Gentle vertical bobbing at spawn location
                self.y = self.start_y + math.sin(self.house_exit_timer * 6.0) * 3.0
                return
            else:
                # Timer expired: align horizontally to door center (280 px), then step out
                if abs(self.x - DOOR_CENTER_X) > 1.5:
                    step = min(abs(DOOR_CENTER_X - self.x), GHOST_NORMAL_SPEED * dt)
                    self.x += step if DOOR_CENTER_X > self.x else -step
                    self.direction = DIR_RIGHT if DOOR_CENTER_X > self.x else DIR_LEFT
                    return
                else:
                    self.x = DOOR_CENTER_X
                    self.in_house = False
                    self.state = GHOST_EXITING
                    self.direction = DIR_UP
                    self.speed = GHOST_NORMAL_SPEED
                    return

        # 2. Exiting the Ghost House through the gate
        if self.state == GHOST_EXITING:
            self.x = DOOR_CENTER_X
            self.direction = DIR_UP
            self.speed = GHOST_NORMAL_SPEED
            self.y -= self.speed * dt
            if self.y <= DOOR_CENTER_Y:
                self.y = DOOR_CENTER_Y
                self.state = global_mode
                self.direction = DIR_LEFT
                self.desired_direction = DIR_NONE
                self.last_tile = (11, 13)
            return

        # 3. Entering the Ghost House through the gate (eyes descending to altar)
        if self.state == GHOST_ENTERING:
            self.x = DOOR_CENTER_X
            self.direction = DIR_DOWN
            self.speed = GHOST_EATEN_SPEED
            self.y += self.speed * dt
            if self.y >= HOUSE_CENTER_Y:
                self.y = HOUSE_CENTER_Y
                # Regenerate mummy/ghost body and immediately exit!
                self.state = GHOST_EXITING
                self.direction = DIR_UP
                self.speed = GHOST_NORMAL_SPEED
            return

        # 4. Eaten eyes navigating back to the ghost house entrance
        if self.state == GHOST_EATEN:
            # Check if arrived at doorway entrance
            if self.row == 11 and self.col in (13, 14) and abs(self.x - DOOR_CENTER_X) <= 6.0:
                self.x = DOOR_CENTER_X
                self.y = DOOR_CENTER_Y
                self.state = GHOST_ENTERING
                self.direction = DIR_DOWN
                return

            curr_tile = (self.row, self.col)
            dist_to_center = abs(self.x - self.center_tile_x) + abs(self.y - self.center_tile_y)
            if curr_tile != self.last_tile or dist_to_center < 6.0 or self.direction == DIR_NONE:
                flow_dir = Ghost._HOME_FLOW_FIELD.get(curr_tile)
                if flow_dir:
                    self.set_desired_direction(flow_dir)
                    if self.direction == DIR_NONE:
                        self.direction = flow_dir
                self.last_tile = curr_tile

            self.update_movement(dt, maze, allow_gate=False)
            return

        # 5. Handle frightened mode expiration and state synchronization
        if self.state == GHOST_FRIGHTENED:
            if not is_frightened:
                self.state = global_mode
                self.speed = GHOST_NORMAL_SPEED
        elif self.state not in (GHOST_EATEN, GHOST_ENTERING, GHOST_EXITING):
            self.state = global_mode
            self.speed = GHOST_NORMAL_SPEED

        # 6. Slow down in side warp tunnels
        if self.row == 14 and (self.col <= 5 or self.col >= 22):
            self.speed = min(self.speed, GHOST_TUNNEL_SPEED)

        # 7. Navigation & intersection turn decisions
        curr_tile = (self.row, self.col)
        dist_to_center = abs(self.x - self.center_tile_x) + abs(self.y - self.center_tile_y)

        if curr_tile != self.last_tile or (dist_to_center < 3.0 and self.desired_direction == DIR_NONE):
            if self.state == GHOST_FRIGHTENED:
                self._decide_frightened_turn(maze)
            else:
                target_tile = self._calculate_target_tile(kapman_pos, kapman_dir, red_ghost_pos)
                self._decide_next_turn(maze, target_tile)
            self.last_tile = curr_tile

        self.update_movement(dt, maze, allow_gate=False)

    def _decide_frightened_turn(self, maze: Maze):
        """Randomized turn at intersections while in frightened panic."""
        candidates = [DIR_UP, DIR_LEFT, DIR_DOWN, DIR_RIGHT]
        opposite = OPPOSITE_DIR.get(self.direction, DIR_NONE)
        valid = []

        for d in candidates:
            if d == opposite and self.direction != DIR_NONE:
                continue
            nr = self.row + d[1]
            nc = self.col + d[0]
            if maze.is_passable(nr, nc, allow_gate=False):
                valid.append(d)

        if valid:
            self.set_desired_direction(random.choice(valid))
        elif opposite != DIR_NONE and maze.is_passable(self.row + opposite[1], self.col + opposite[0], allow_gate=False):
            self.set_desired_direction(opposite)

    def _calculate_target_tile(
        self,
        kapman_pos: tuple[float, float],
        kapman_dir: tuple[int, int],
        red_ghost_pos: tuple[float, float]
    ) -> tuple[int, int]:
        # Scatter -> target designated corner
        if self.state == GHOST_SCATTER:
            return self.scatter_target

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

            if maze.is_passable(nr, nc, allow_gate=False):
                dist_sq = (nr - target_tile[0]) ** 2 + (nc - target_tile[1]) ** 2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    best_dir = d

        if best_dir != DIR_NONE:
            self.set_desired_direction(best_dir)
