"""
board.py - Matrix Board State, Collision Checking, Ghost Calculation & T-Spin Rules.
"""

from config import DEFAULT_COLS, DEFAULT_ROWS, BUFFER_ROWS


class Board:
    def __init__(self, cols=DEFAULT_COLS, rows=DEFAULT_ROWS, buffer_rows=BUFFER_ROWS):
        self.cols = cols
        self.visible_rows = rows
        self.buffer_rows = buffer_rows
        self.total_rows = rows + buffer_rows

        # Grid is index 0 at top of buffer, index (buffer_rows) at top of visible board
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.total_rows)]
        self.clearing_rows = []
        self.clear_anim_timer = 0.0

    def is_inside(self, x, y):
        return 0 <= x < self.cols and 0 <= y < self.total_rows

    def is_occupied(self, x, y):
        if x < 0 or x >= self.cols or y >= self.total_rows:
            return True
        if y < 0:
            return False  # Above the buffer ceiling is open
        return self.grid[y][x] is not None

    def is_valid_position(self, piece, offset_x=None, offset_y=None, rotation=None):
        blocks = piece.get_blocks(offset_x, offset_y, rotation)
        for bx, by in blocks:
            if bx < 0 or bx >= self.cols:
                return False
            if by >= self.total_rows:
                return False
            if by >= 0 and self.grid[by][bx] is not None:
                return False
        return True

    def get_ghost_y(self, piece):
        ghost_y = piece.y
        while self.is_valid_position(piece, offset_x=piece.x, offset_y=ghost_y + 1, rotation=piece.rotation):
            ghost_y += 1
        return ghost_y

    def lock_piece(self, piece):
        blocks = piece.get_blocks()
        game_over = False
        for bx, by in blocks:
            if by < self.buffer_rows:
                game_over = True
            if 0 <= by < self.total_rows and 0 <= bx < self.cols:
                self.grid[by][bx] = piece.color
        return game_over

    def find_completed_lines(self):
        full_rows = []
        for r in range(self.total_rows):
            if all(cell is not None for cell in self.grid[r]):
                full_rows.append(r)
        return full_rows

    def remove_lines(self, row_indices):
        if not row_indices:
            return 0
        sorted_rows = sorted(row_indices, reverse=True)
        for r in sorted_rows:
            del self.grid[r]
            # Insert empty row at top
            self.grid.insert(0, [None for _ in range(self.cols)])
        return len(sorted_rows)

    def is_perfect_clear(self):
        for r in range(self.total_rows):
            if any(cell is not None for cell in self.grid[r]):
                return False
        return True

    def check_t_spin(self, piece):
        """
        Official Tetris Guideline 3-Corner T-Spin Rule.
        Returns: ('none' | 'mini' | 'regular')
        """
        if piece.kind != 'T' or not piece.last_move_was_rotation:
            return 'none'

        cx, cy = piece.x + 1, piece.y + 1
        # Diagonal corners around T center
        corners = [
            (cx - 1, cy - 1),  # Top-Left
            (cx + 1, cy - 1),  # Top-Right
            (cx + 1, cy + 1),  # Bottom-Right
            (cx - 1, cy + 1),  # Bottom-Left
        ]

        occupied = [self.is_occupied(x, y) for x, y in corners]
        if sum(occupied) < 3:
            return 'none'

        # Front corners according to rotation
        # 0: Top-Left & Top-Right (0, 1)
        # 1: Top-Right & Bottom-Right (1, 2)
        # 2: Bottom-Right & Bottom-Left (2, 3)
        # 3: Bottom-Left & Top-Left (3, 0)
        front_indices = {
            0: (0, 1),
            1: (1, 2),
            2: (2, 3),
            3: (3, 0),
        }[piece.rotation]

        front_occupied = occupied[front_indices[0]] and occupied[front_indices[1]]

        # If front 2 corners occupied or 5th wall kick was used -> full T-Spin
        if front_occupied or piece.last_kick_index == 4:
            return 'regular'
        return 'mini'

    def clear(self):
        self.grid = [[None for _ in range(self.cols)] for _ in range(self.total_rows)]
        self.clearing_rows.clear()
        self.clear_anim_timer = 0.0
