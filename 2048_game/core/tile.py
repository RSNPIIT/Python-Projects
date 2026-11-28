"""2048 Game - Animated Tile Entity with Interpolation and Scale Transitions"""
import math
from core.constants import (
    TILE_SIZE, GRID_GAP, BOARD_OFFSET_X, BOARD_OFFSET_Y,
    ANIM_SLIDE_DURATION, ANIM_SPAWN_DURATION, ANIM_MERGE_DURATION
)

def get_cell_pixel_pos(row: int, col: int) -> tuple[float, float]:
    """Returns top-left pixel coordinate (x, y) for a tile cell."""
    x = BOARD_OFFSET_X + GRID_GAP + col * (TILE_SIZE + GRID_GAP)
    y = BOARD_OFFSET_Y + GRID_GAP + row * (TILE_SIZE + GRID_GAP)
    return float(x), float(y)

class AnimatedTile:
    """Represents a visual tile instance tracking position and pop/spawn animations."""
    _next_id = 1

    def __init__(self, row: int, col: int, value: int, is_spawn: bool = True):
        self.tile_id = AnimatedTile._next_id
        AnimatedTile._next_id += 1

        self.row = row
        self.col = col
        self.value = value

        self.target_x, self.target_y = get_cell_pixel_pos(row, col)
        self.current_x = self.target_x
        self.current_y = self.target_y

        # Slide animation
        self.is_sliding = False
        self.slide_start_x = self.target_x
        self.slide_start_y = self.target_y
        self.slide_timer = 0.0

        # Scale animation (Spawn or Merge)
        self.scale = 0.0 if is_spawn else 1.0
        self.is_spawning = is_spawn
        self.spawn_timer = 0.0

        self.is_merging = False
        self.merge_timer = 0.0

        # Mark tile for deletion once slide into merged destination completes
        self.is_dying = False

    def move_to(self, target_row: int, target_col: int):
        """Starts a slide animation toward destination cell."""
        self.row = target_row
        self.col = target_col
        self.slide_start_x = self.current_x
        self.slide_start_y = self.current_y
        self.target_x, self.target_y = get_cell_pixel_pos(target_row, target_col)
        self.slide_timer = 0.0
        self.is_sliding = True

    def trigger_merge(self, new_value: int):
        """Triggers the pop bounce animation when two tiles merge."""
        self.value = new_value
        self.is_merging = True
        self.merge_timer = 0.0

    def update(self, dt: float) -> bool:
        """
        Updates animation transitions.
        Returns False if the tile is dying and finished sliding.
        """
        # 1. Slide interpolation (Cubic ease-out)
        if self.is_sliding:
            self.slide_timer += dt
            t = min(1.0, self.slide_timer / ANIM_SLIDE_DURATION)
            # Cubic ease-out: 1 - (1 - t)^3
            ease = 1.0 - math.pow(1.0 - t, 3)
            self.current_x = self.slide_start_x + (self.target_x - self.slide_start_x) * ease
            self.current_y = self.slide_start_y + (self.target_y - self.slide_start_y) * ease

            if t >= 1.0:
                self.current_x = self.target_x
                self.current_y = self.target_y
                self.is_sliding = False
                if self.is_dying:
                    return False  # Finished sliding into merged partner; ready to be removed

        # 2. Spawn scale-up (Elastic ease-out)
        if self.is_spawning:
            self.spawn_timer += dt
            t = min(1.0, self.spawn_timer / ANIM_SPAWN_DURATION)
            # Smooth scale from 0.0 to 1.0
            self.scale = math.sin(t * (math.pi / 2.0))
            if t >= 1.0:
                self.scale = 1.0
                self.is_spawning = False

        # 3. Merge pop bounce (Scale 1.0 -> 1.18 -> 1.0)
        if self.is_merging:
            self.merge_timer += dt
            t = min(1.0, self.merge_timer / ANIM_MERGE_DURATION)
            # Pulse up to 1.18 then return to 1.0
            self.scale = 1.0 + 0.18 * math.sin(t * math.pi)
            if t >= 1.0:
                self.scale = 1.0
                self.is_merging = False

        return True
