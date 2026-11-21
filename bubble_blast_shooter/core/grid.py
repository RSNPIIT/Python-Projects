"""Bubble Blast Shooter - Hexagonal Honeycomb Bubble Grid"""
import collections
import pygame
from core.constants import (
    EVEN_COLS, ODD_COLS, MAX_ROWS,
    BUBBLE_RADIUS, BUBBLE_DIAMETER, HEX_ROW_HEIGHT,
    MARGIN_LEFT, GRID_TOP_MARGIN, DEADLINE_ROW,
    DEADLINE_Y, SCREEN_WIDTH
)
from core.bubble import Bubble

class BubbleGrid:
    def __init__(self):
        # 2D Grid: row -> list of Bubble or None
        self.grid: list[list[Bubble | None]] = []
        for r in range(MAX_ROWS):
            cols = EVEN_COLS if (r % 2 == 0) else ODD_COLS
            self.grid.append([None] * cols)

    def clear(self):
        for r in range(MAX_ROWS):
            cols = EVEN_COLS if (r % 2 == 0) else ODD_COLS
            self.grid[r] = [None] * cols

    @staticmethod
    def get_cols_for_row(r: int) -> int:
        return EVEN_COLS if (r % 2 == 0) else ODD_COLS

    @staticmethod
    def get_slot_center(r: int, c: int) -> tuple[float, float]:
        """Calculates pixel coordinates (cx, cy) of a slot (r, c)."""
        is_even = (r % 2 == 0)
        offset_x = MARGIN_LEFT + BUBBLE_RADIUS if is_even else MARGIN_LEFT + BUBBLE_DIAMETER
        cx = offset_x + c * BUBBLE_DIAMETER
        cy = GRID_TOP_MARGIN + BUBBLE_RADIUS + r * HEX_ROW_HEIGHT
        return float(cx), float(cy)

    def is_in_bounds(self, r: int, c: int) -> bool:
        if r < 0 or r >= MAX_ROWS:
            return False
        cols = self.get_cols_for_row(r)
        return 0 <= c < cols

    def get_bubble(self, r: int, c: int) -> Bubble | None:
        if not self.is_in_bounds(r, c):
            return None
        return self.grid[r][c]

    def set_bubble(self, r: int, c: int, bubble: Bubble | None):
        if self.is_in_bounds(r, c):
            self.grid[r][c] = bubble

    def get_neighbors(self, r: int, c: int) -> list[tuple[int, int]]:
        """Returns valid adjacent hexagonal coordinate pairs for (r, c)."""
        is_even = (r % 2 == 0)
        if is_even:
            candidates = [
                (r, c - 1), (r, c + 1),         # Left, Right
                (r - 1, c - 1), (r - 1, c),     # Up-Left, Up-Right
                (r + 1, c - 1), (r + 1, c)      # Down-Left, Down-Right
            ]
        else:
            candidates = [
                (r, c - 1), (r, c + 1),         # Left, Right
                (r - 1, c), (r - 1, c + 1),     # Up-Left, Up-Right
                (r + 1, c), (r + 1, c + 1)      # Down-Left, Down-Right
            ]
        return [(nr, nc) for (nr, nc) in candidates if self.is_in_bounds(nr, nc)]

    def find_matching_cluster(self, start_r: int, start_c: int) -> list[tuple[int, int]]:
        """Breadth-first search finding connected bubbles of the same color."""
        start_bubble = self.get_bubble(start_r, start_c)
        if not start_bubble:
            return []

        target_color = start_bubble.color_id
        cluster = []
        visited = set()
        queue = collections.deque([(start_r, start_c)])
        visited.add((start_r, start_c))

        while queue:
            r, c = queue.popleft()
            cluster.append((r, c))

            for nr, nc in self.get_neighbors(r, c):
                if (nr, nc) not in visited:
                    nb = self.get_bubble(nr, nc)
                    if nb and nb.color_id == target_color:
                        visited.add((nr, nc))
                        queue.append((nr, nc))

        return cluster

    def find_floating_bubbles(self) -> list[tuple[int, int, Bubble]]:
        """
        BFS from row 0 (the ceiling) to identify anchored bubbles.
        Any bubbles on the grid not reachable from row 0 are floating/orphaned.
        Detaches and returns them.
        """
        anchored = set()
        queue = collections.deque()

        # Row 0 bubbles are directly anchored to the ceiling
        for c in range(self.get_cols_for_row(0)):
            if self.grid[0][c] is not None:
                anchored.add((0, c))
                queue.append((0, c))

        # Propagate anchor connectivity
        while queue:
            r, c = queue.popleft()
            for nr, nc in self.get_neighbors(r, c):
                if (nr, nc) not in anchored:
                    if self.grid[nr][nc] is not None:
                        anchored.add((nr, nc))
                        queue.append((nr, nc))

        # Any bubble not in anchored is floating!
        floating = []
        for r in range(MAX_ROWS):
            cols = self.get_cols_for_row(r)
            for c in range(cols):
                b = self.grid[r][c]
                if b is not None and (r, c) not in anchored:
                    floating.append((r, c, b))
                    self.grid[r][c] = None

        return floating

    def snap_to_nearest_slot(self, px: float, py: float) -> tuple[int, int]:
        """Finds the closest empty valid slot in the grid to a projectile hit position."""
        best_slot = (0, 0)
        min_dist_sq = float("inf")

        for r in range(MAX_ROWS):
            cols = self.get_cols_for_row(r)
            for c in range(cols):
                if self.grid[r][c] is None:
                    # Check if this empty slot is valid (adjacent to an existing bubble or row 0)
                    is_valid_attachment = (r == 0)
                    if not is_valid_attachment:
                        for nr, nc in self.get_neighbors(r, c):
                            if self.grid[nr][nc] is not None:
                                is_valid_attachment = True
                                break

                    if is_valid_attachment:
                        cx, cy = self.get_slot_center(r, c)
                        dist_sq = (px - cx) ** 2 + (py - cy) ** 2
                        if dist_sq < min_dist_sq:
                            min_dist_sq = dist_sq
                            best_slot = (r, c)

        return best_slot

    def check_collision_with_bubble(self, px: float, py: float, radius: float = BUBBLE_RADIUS) -> bool:
        """Returns True if projectile circle overlaps any occupied bubble in the grid."""
        threshold_sq = (radius * 1.85) ** 2
        for r in range(MAX_ROWS):
            cols = self.get_cols_for_row(r)
            for c in range(cols):
                if self.grid[r][c] is not None:
                    cx, cy = self.get_slot_center(r, c)
                    dist_sq = (px - cx) ** 2 + (py - cy) ** 2
                    if dist_sq < threshold_sq:
                        return True
        return False

    def is_empty(self) -> bool:
        """Checks if all bubbles on the board have been cleared."""
        for r in range(MAX_ROWS):
            cols = self.get_cols_for_row(r)
            for c in range(cols):
                if self.grid[r][c] is not None:
                    return False
        return True

    def reached_deadline(self) -> bool:
        """Checks if any bubble has reached or crossed the danger deadline."""
        for r in range(DEADLINE_ROW, MAX_ROWS):
            cols = self.get_cols_for_row(r)
            for c in range(cols):
                if self.grid[r][c] is not None:
                    return True
        return False

    def get_remaining_colors(self) -> list[int]:
        """Returns the list of unique bubble color IDs currently on the grid."""
        colors = set()
        for r in range(MAX_ROWS):
            cols = self.get_cols_for_row(r)
            for c in range(cols):
                b = self.grid[r][c]
                if b is not None:
                    colors.add(b.color_id)
        return list(colors)

    def draw(self, surface: pygame.Surface):
        # 1. Subtle honeycomb slot background markers
        for r in range(DEADLINE_ROW + 1):
            cols = self.get_cols_for_row(r)
            for c in range(cols):
                cx, cy = self.get_slot_center(r, c)
                pygame.draw.circle(surface, (20, 26, 44), (int(cx), int(cy)), 3)

        # 2. Draw active bubbles
        for r in range(MAX_ROWS):
            cols = self.get_cols_for_row(r)
            for c in range(cols):
                b = self.grid[r][c]
                if b is not None:
                    cx, cy = self.get_slot_center(r, c)
                    b.draw(surface, cx, cy)
