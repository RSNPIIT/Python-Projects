"""2048 Game - Board Matrix State, Slide & Merge Logic, and Undo History"""
import copy
import random
from core.constants import GRID_SIZE, DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
from core.tile import AnimatedTile

class MoveResult:
    def __init__(self, moved: bool, score_earned: int, merged_values: list[int]):
        self.moved = moved
        self.score_earned = score_earned
        self.merged_values = merged_values

class Board:
    def __init__(self):
        self.size = GRID_SIZE
        # Pure numeric grid (0 = empty)
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        # Visual animated tile references: grid of AnimatedTile | None
        self.tiles: list[list[AnimatedTile | None]] = [[None for _ in range(self.size)] for _ in range(self.size)]
        # Sliding transient tiles that are dying after merge
        self.dying_tiles: list[AnimatedTile] = []

        self.score = 0
        self.best_score = 0
        self.has_won = False
        self.keep_playing = False
        self.game_over = False

        # Undo stack: stores snapshots of (grid, score, has_won, game_over)
        self.undo_stack: list[dict] = []
        self.max_undo = 15

    def reset(self):
        """Resets the board and spawns 2 initial tiles."""
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.tiles = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.dying_tiles.clear()
        self.score = 0
        self.has_won = False
        self.keep_playing = False
        self.game_over = False
        self.undo_stack.clear()

        # Spawn initial 2 tiles
        self.spawn_random_tile()
        self.spawn_random_tile()

    def get_empty_cells(self) -> list[tuple[int, int]]:
        """Returns list of (row, col) for all empty cells."""
        cells = []
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == 0:
                    cells.append((r, c))
        return cells

    def spawn_random_tile(self) -> AnimatedTile | None:
        """Spawns a new tile (90% chance of 2, 10% chance of 4) in an empty cell."""
        empty_cells = self.get_empty_cells()
        if not empty_cells:
            return None

        r, c = random.choice(empty_cells)
        value = 2 if random.random() < 0.9 else 4
        self.grid[r][c] = value

        tile = AnimatedTile(r, c, value, is_spawn=True)
        self.tiles[r][c] = tile
        return tile

    def save_undo_snapshot(self):
        """Saves current state snapshot into undo stack."""
        snapshot = {
            "grid": copy.deepcopy(self.grid),
            "score": self.score,
            "has_won": self.has_won,
            "keep_playing": self.keep_playing,
            "game_over": self.game_over
        }
        self.undo_stack.append(snapshot)
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)

    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0

    def undo(self) -> bool:
        """Restores the last state from the undo stack."""
        if not self.can_undo():
            return False

        snapshot = self.undo_stack.pop()
        self.grid = snapshot["grid"]
        self.score = snapshot["score"]
        self.has_won = snapshot["has_won"]
        self.keep_playing = snapshot["keep_playing"]
        self.game_over = snapshot["game_over"]

        # Reconstruct animated tile representations
        self.dying_tiles.clear()
        self.tiles = [[None for _ in range(self.size)] for _ in range(self.size)]
        for r in range(self.size):
            for c in range(self.size):
                val = self.grid[r][c]
                if val > 0:
                    self.tiles[r][c] = AnimatedTile(r, c, val, is_spawn=False)

        return True

    def is_animating(self) -> bool:
        """Returns True if any tile is currently sliding, spawning or popping."""
        if self.dying_tiles:
            return True
        for r in range(self.size):
            for c in range(self.size):
                t = self.tiles[r][c]
                if t and (t.is_sliding or t.is_spawning or t.is_merging):
                    return True
        return False

    def update_animations(self, dt: float):
        """Advances animation state for all active and dying tiles."""
        # Update dying sliding tiles
        surviving_dying = []
        for dtile in self.dying_tiles:
            if dtile.update(dt):
                surviving_dying.append(dtile)
        self.dying_tiles = surviving_dying

        # Update active board tiles
        for r in range(self.size):
            for c in range(self.size):
                tile = self.tiles[r][c]
                if tile:
                    tile.update(dt)

    def can_move(self) -> bool:
        """Returns True if there is at least one valid slide or merge move available."""
        # 1. Any empty cell?
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] == 0:
                    return True

        # 2. Any adjacent horizontal merges?
        for r in range(self.size):
            for c in range(self.size - 1):
                if self.grid[r][c] == self.grid[r][c + 1]:
                    return True

        # 3. Any adjacent vertical merges?
        for r in range(self.size - 1):
            for c in range(self.size):
                if self.grid[r][c] == self.grid[r + 1][c]:
                    return True

        return False

    def move(self, direction: tuple[int, int]) -> MoveResult:
        """
        Executes a slide move in DIR_UP, DIR_DOWN, DIR_LEFT, or DIR_RIGHT.
        Updates board grid, triggers tile slide & merge animations, tracks score.
        """
        if direction not in (DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT):
            return MoveResult(False, 0, [])

        # Save snapshot for undo BEFORE modifying state
        self.save_undo_snapshot()

        dx, dy = direction
        moved = False
        score_earned = 0
        merged_values = []

        # Determine iteration order based on direction so outer tiles move first
        if direction == DIR_LEFT:
            row_indices = list(range(self.size))
            col_indices = list(range(self.size))
        elif direction == DIR_RIGHT:
            row_indices = list(range(self.size))
            col_indices = list(reversed(range(self.size)))
        elif direction == DIR_UP:
            row_indices = list(range(self.size))
            col_indices = list(range(self.size))
        else:  # DIR_DOWN
            row_indices = list(reversed(range(self.size)))
            col_indices = list(range(self.size))

        # Track which target cells already merged in this single move
        merged_cells = [[False for _ in range(self.size)] for _ in range(self.size)]

        # New visual tile placements for post-move board
        new_tiles = [[None for _ in range(self.size)] for _ in range(self.size)]

        for r in row_indices:
            for c in col_indices:
                val = self.grid[r][c]
                tile = self.tiles[r][c]
                if val == 0 or tile is None:
                    continue

                curr_r, curr_c = r, c
                next_r, next_c = curr_r + dy, curr_c + dx

                # Find furthest empty cell in direction
                while 0 <= next_r < self.size and 0 <= next_c < self.size and self.grid[next_r][next_c] == 0:
                    curr_r, curr_c = next_r, next_c
                    next_r, next_c = curr_r + dy, curr_c + dx

                # Check if we can merge with neighbor at (next_r, next_c)
                can_merge = False
                if 0 <= next_r < self.size and 0 <= next_c < self.size:
                    if self.grid[next_r][next_c] == val and not merged_cells[next_r][next_c]:
                        can_merge = True

                if can_merge:
                    # Move to merge target cell
                    target_r, target_c = next_r, next_c
                    merged_val = val * 2
                    self.grid[r][c] = 0
                    self.grid[target_r][target_c] = merged_val
                    merged_cells[target_r][target_c] = True

                    score_earned += merged_val
                    merged_values.append(merged_val)

                    # Existing tile at target cell becomes the merged tile
                    target_tile = new_tiles[target_r][target_c]
                    if target_tile is None:
                        target_tile = self.tiles[target_r][target_c]

                    # This moving tile slides into target cell and dies
                    tile.move_to(target_r, target_c)
                    tile.is_dying = True
                    self.dying_tiles.append(tile)

                    # Target tile receives merge pulse and new value
                    if target_tile:
                        target_tile.trigger_merge(merged_val)
                        new_tiles[target_r][target_c] = target_tile

                    moved = True

                elif curr_r != r or curr_c != c:
                    # Slide to furthest empty cell
                    self.grid[r][c] = 0
                    self.grid[curr_r][curr_c] = val
                    tile.move_to(curr_r, curr_c)
                    new_tiles[curr_r][curr_c] = tile
                    moved = True
                else:
                    # Remained stationary
                    new_tiles[r][c] = tile

        if not moved:
            # Revert the unused undo snapshot
            self.undo_stack.pop()
            return MoveResult(False, 0, [])

        self.tiles = new_tiles
        self.score += score_earned
        if self.score > self.best_score:
            self.best_score = self.score

        # Check win condition (reaching 2048)
        if not self.has_won and not self.keep_playing:
            for r in range(self.size):
                for c in range(self.size):
                    if self.grid[r][c] >= 2048:
                        self.has_won = True
                        break

        # Spawn a new random tile after successful move
        self.spawn_random_tile()

        # Check game over condition
        if not self.can_move():
            self.game_over = True

        return MoveResult(True, score_earned, merged_values)
