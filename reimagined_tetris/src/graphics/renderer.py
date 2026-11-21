"""
renderer.py - High-Fidelity 2D Graphics, Block Shading, Grid & HUD Layout Renderer.
"""

import math
import pygame
from config import (
    COLOR_BG_DEEP, COLOR_MATRIX_BG, COLOR_MATRIX_BORDER, COLOR_GRID_LINE,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED, COLOR_ACCENT_CYAN, COLOR_ACCENT_GOLD,
    COLOR_ACCENT_MAGENTA, TETROMINO_COLORS
)
from src.engine.tetromino import SHAPES
from src.graphics.ui_components import draw_glass_panel, draw_meter_bar


class GameRenderer:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height

        # Fonts
        self.font_title = pygame.font.SysFont('Arial', 32, bold=True)
        self.font_sub = pygame.font.SysFont('Arial', 20, bold=True)
        self.font_body = pygame.font.SysFont('Arial', 16, bold=True)
        self.font_digits = pygame.font.SysFont('Arial', 26, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 13)

        # Ambient background particles
        self.stars = [
            [
                (i * 97) % width,
                (i * 131) % height,
                (i % 3) + 1,
                0.2 + (i % 5) * 0.15
            ]
            for i in range(75)
        ]

    def render_background(self, surface, time_sec):
        # Deep space dark gradient
        surface.fill(COLOR_BG_DEEP)

        # Drift ambient stars
        for star in self.stars:
            star[1] = (star[1] + star[3] * 0.4) % self.height
            alpha = int(120 + 80 * math.sin(time_sec * 2.0 + star[0]))
            pygame.draw.circle(surface, (120, 180, 255, alpha), (int(star[0]), int(star[1])), star[2])

        # Futuristic horizon perspective lines at bottom
        horizon_y = self.height * 0.82
        for i in range(-12, 13):
            sx = self.width * 0.5 + i * 140
            pygame.draw.line(surface, (20, 35, 55, 45), (self.width * 0.5, horizon_y - 80), (sx, self.height), 1)

    def draw_block(self, surface, x, y, size, color, is_ghost=False, lock_glow=0.0):
        rect = pygame.Rect(x, y, size, size)

        if is_ghost:
            ghost_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.rect(ghost_surf, (*color[:3], 32), (0, 0, size, size), border_radius=4)
            pygame.draw.rect(ghost_surf, (*color[:3], 140), (0, 0, size, size), width=1, border_radius=4)
            surface.blit(ghost_surf, (x, y))
            return

        # Base colored block
        r, g, b = color[:3]
        if lock_glow > 0.0:
            glow_add = int(lock_glow * 65)
            r = min(255, r + glow_add)
            g = min(255, g + glow_add)
            b = min(255, b + glow_add)

        # Main fill with slight corner radius
        pygame.draw.rect(surface, (r, g, b), rect, border_radius=4)

        # Top & Left bevel highlight
        highlight_col = (min(255, int(r * 1.35) + 30), min(255, int(g * 1.35) + 30), min(255, int(b * 1.35) + 30))
        pygame.draw.line(surface, highlight_col, (x + 2, y + 2), (x + size - 3, y + 2), 2)
        pygame.draw.line(surface, highlight_col, (x + 2, y + 2), (x + 2, y + size - 3), 2)

        # Bottom & Right shadow
        shadow_col = (max(0, int(r * 0.55)), max(0, int(g * 0.55)), max(0, int(b * 0.55)))
        pygame.draw.line(surface, shadow_col, (x + 2, y + size - 2), (x + size - 2, y + size - 2), 2)
        pygame.draw.line(surface, shadow_col, (x + size - 2, y + 2), (x + size - 2, y + size - 2), 2)

        # Inner crystal core
        inset = max(3, size // 5)
        core_col = (min(255, r + 20), min(255, g + 20), min(255, b + 20))
        pygame.draw.rect(surface, core_col, (x + inset, y + inset, size - inset * 2, size - inset * 2), border_radius=2)

        # Dark outer perimeter border
        pygame.draw.rect(surface, (10, 14, 20), rect, width=1, border_radius=4)

    def draw_mini_piece(self, surface, kind, center_x, center_y, cell_size=20):
        if not kind or kind not in SHAPES:
            return
        shape_mat = SHAPES[kind][0]
        color = TETROMINO_COLORS[kind]
        rows = len(shape_mat)
        cols = len(shape_mat[0])

        # Bounding box bounds of occupied cells for precise centering
        min_r, max_r = rows, 0
        min_c, max_c = cols, 0
        for r_idx, row in enumerate(shape_mat):
            for c_idx, val in enumerate(row):
                if val:
                    min_r = min(min_r, r_idx)
                    max_r = max(max_r, r_idx)
                    min_c = min(min_c, c_idx)
                    max_c = max(max_c, c_idx)

        w = (max_c - min_c + 1) * cell_size
        h = (max_r - min_r + 1) * cell_size
        start_x = center_x - w * 0.5
        start_y = center_y - h * 0.5

        for r_idx in range(min_r, max_r + 1):
            for c_idx in range(min_c, max_c + 1):
                if shape_mat[r_idx][c_idx]:
                    px = start_x + (c_idx - min_c) * cell_size
                    py = start_y + (r_idx - min_r) * cell_size
                    self.draw_block(surface, px, py, cell_size, color)

    def render_game_scene(self, surface, game_state, time_sec):
        self.render_background(surface, time_sec)

        board = game_state.board
        cell_size = game_state.cell_size
        matrix_w = board.cols * cell_size
        matrix_h = board.visible_rows * cell_size

        # Board container centering
        board_x = (self.width - matrix_w) // 2
        board_y = (self.height - matrix_h) // 2 + 20

        # 1. Central Matrix Glass Container
        matrix_rect = pygame.Rect(board_x - 6, board_y - 6, matrix_w + 12, matrix_h + 12)
        draw_glass_panel(surface, matrix_rect, border_color=COLOR_MATRIX_BORDER, bg_color=COLOR_MATRIX_BG, corner_radius=12, glow=True)

        # Grid lines inside visible matrix
        for c in range(1, board.cols):
            gx = board_x + c * cell_size
            pygame.draw.line(surface, COLOR_GRID_LINE, (gx, board_y), (gx, board_y + matrix_h), 1)
        for r in range(1, board.visible_rows):
            gy = board_y + r * cell_size
            pygame.draw.line(surface, COLOR_GRID_LINE, (board_x, gy), (board_x + matrix_w, gy), 1)

        # 2. Render Locked Blocks
        for r in range(board.buffer_rows, board.total_rows):
            disp_r = r - board.buffer_rows
            by = board_y + disp_r * cell_size
            for c in range(board.cols):
                bx = board_x + c * cell_size
                cell_color = board.grid[r][c]
                if cell_color is not None:
                    self.draw_block(surface, bx, by, cell_size, cell_color)

        # 3. Render Ghost Piece (if enabled)
        active_piece = game_state.active_piece
        if active_piece and game_state.show_ghost:
            ghost_y = board.get_ghost_y(active_piece)
            ghost_blocks = active_piece.get_blocks(offset_x=active_piece.x, offset_y=ghost_y)
            for gx, gy in ghost_blocks:
                if gy >= board.buffer_rows:
                    disp_gy = gy - board.buffer_rows
                    self.draw_block(surface, board_x + gx * cell_size, board_y + disp_gy * cell_size, cell_size, active_piece.color, is_ghost=True)

        # 4. Render Active Falling Piece
        if active_piece:
            lock_glow_val = game_state.lock_timer / game_state.lock_delay if game_state.touching_surface else 0.0
            blocks = active_piece.get_blocks()
            for bx, by in blocks:
                if by >= board.buffer_rows:
                    disp_by = by - board.buffer_rows
                    self.draw_block(surface, board_x + bx * cell_size, board_y + disp_by * cell_size, cell_size, active_piece.color, lock_glow=lock_glow_val)

        # 5. Render Particles, Lasers, Floating Text
        game_state.particle_mgr.draw(surface)

        # 6. LEFT SIDEBAR: HOLD & STATS PANELS
        left_w = 210
        left_x = board_x - left_w - 24

        # Hold Card
        hold_rect = pygame.Rect(left_x, board_y, left_w, 140)
        draw_glass_panel(surface, hold_rect, corner_radius=12)
        lbl_hold = self.font_sub.render("HOLD", True, COLOR_TEXT_MUTED)
        surface.blit(lbl_hold, (left_x + 18, board_y + 14))

        if game_state.held_kind:
            center_x = left_x + left_w // 2
            center_y = board_y + 80
            self.draw_mini_piece(surface, game_state.held_kind, center_x, center_y, cell_size=22)
            if game_state.swapped_this_drop:
                lock_lbl = self.font_small.render("[LOCKED]", True, (255, 100, 100))
                surface.blit(lock_lbl, (left_x + left_w - lock_lbl.get_width() - 16, board_y + 18))

        # Stats Breakdown Card
        stats_h = 290
        stats_rect = pygame.Rect(left_x, board_y + 160, left_w, stats_h)
        draw_glass_panel(surface, stats_rect, corner_radius=12)
        lbl_stats = self.font_sub.render("STATISTICS", True, COLOR_TEXT_MUTED)
        surface.blit(lbl_stats, (left_x + 18, board_y + 174))

        stats_entries = [
            ("SINGLES", game_state.score_mgr.singles),
            ("DOUBLES", game_state.score_mgr.doubles),
            ("TRIPLES", game_state.score_mgr.triples),
            ("TETRISES", game_state.score_mgr.tetrises),
            ("T-SPINS", game_state.score_mgr.tspins),
            ("MAX COMBO", f"x{game_state.score_mgr.max_combo}" if game_state.score_mgr.max_combo > 0 else "-"),
        ]
        for idx, (label, val) in enumerate(stats_entries):
            row_y = board_y + 210 + idx * 36
            lbl = self.font_body.render(label, True, COLOR_TEXT_MUTED)
            val_col = COLOR_ACCENT_GOLD if "TETRIS" in label or "T-SPIN" in label else COLOR_TEXT_PRIMARY
            v = self.font_body.render(str(val), True, val_col)
            surface.blit(lbl, (left_x + 18, row_y))
            surface.blit(v, (left_x + left_w - v.get_width() - 18, row_y))

        # Controls Pill at bottom-left
        ctrl_rect = pygame.Rect(left_x, board_y + 470, left_w, 175)
        draw_glass_panel(surface, ctrl_rect, corner_radius=12)
        lbl_ctrl = self.font_small.render("CONTROLS", True, COLOR_TEXT_MUTED)
        surface.blit(lbl_ctrl, (left_x + 16, board_y + 482))
        ctrl_tips = [
            ("MOVE", "← → / A D"),
            ("ROTATE", "↑ / W / X"),
            ("SOFT DROP", "↓ / S"),
            ("HARD DROP", "SPACE"),
            ("HOLD", "C / SHIFT"),
            ("PAUSE", "ESC / P"),
        ]
        for idx, (action, bind) in enumerate(ctrl_tips):
            cy = board_y + 504 + idx * 22
            surface.blit(self.font_small.render(action, True, COLOR_TEXT_MUTED), (left_x + 16, cy))
            b_surf = self.font_small.render(bind, True, COLOR_ACCENT_CYAN)
            surface.blit(b_surf, (left_x + left_w - b_surf.get_width() - 16, cy))

        # 7. RIGHT SIDEBAR: NEXT QUEUE & SCORE / LEVEL METERS
        right_w = 220
        right_x = board_x + matrix_w + 24

        # Next Queue Card (displays 5 upcoming pieces)
        next_h = 320
        next_rect = pygame.Rect(right_x, board_y, right_w, next_h)
        draw_glass_panel(surface, next_rect, corner_radius=12)
        lbl_next = self.font_sub.render("NEXT", True, COLOR_TEXT_MUTED)
        surface.blit(lbl_next, (right_x + 18, board_y + 14))

        upcoming_pieces = game_state.randomizer.peek_next(5)
        for idx, kind in enumerate(upcoming_pieces):
            cx = right_x + right_w // 2
            cy = board_y + 60 + idx * 52
            scale_cell = 20 if idx == 0 else 16  # Highlight first piece larger
            self.draw_mini_piece(surface, kind, cx, cy, cell_size=scale_cell)

        # Score & High Score Card
        score_y = board_y + 340
        score_rect = pygame.Rect(right_x, score_y, right_w, 140)
        draw_glass_panel(surface, score_rect, corner_radius=12)

        lbl_sc = self.font_sub.render("SCORE", True, COLOR_TEXT_MUTED)
        val_sc = self.font_digits.render(f"{game_state.score_mgr.score:,}", True, COLOR_TEXT_PRIMARY)
        surface.blit(lbl_sc, (right_x + 18, score_y + 14))
        surface.blit(val_sc, (right_x + 18, score_y + 40))

        lbl_hs = self.font_small.render("BEST", True, COLOR_TEXT_MUTED)
        val_hs = self.font_body.render(f"{game_state.score_mgr.high_score:,}", True, COLOR_ACCENT_GOLD)
        surface.blit(lbl_hs, (right_x + 18, score_y + 88))
        surface.blit(val_hs, (right_x + 18, score_y + 104))

        # Level, Lines & Combo Card
        level_y = score_y + 160
        level_rect = pygame.Rect(right_x, level_y, right_w, 145)
        draw_glass_panel(surface, level_rect, corner_radius=12)

        lbl_lvl = self.font_sub.render("LEVEL", True, COLOR_TEXT_MUTED)
        val_lvl = self.font_digits.render(f"{game_state.score_mgr.level:02d}", True, COLOR_ACCENT_CYAN)
        surface.blit(lbl_lvl, (right_x + 18, level_y + 14))
        surface.blit(val_lvl, (right_x + 18, level_y + 38))

        lbl_ln = self.font_sub.render("LINES", True, COLOR_TEXT_MUTED)
        val_ln = self.font_digits.render(f"{game_state.score_mgr.lines:03d}", True, COLOR_TEXT_PRIMARY)
        surface.blit(lbl_ln, (right_x + 115, level_y + 14))
        surface.blit(val_ln, (right_x + 115, level_y + 38))

        # Lines to next level progress bar
        lines_in_level = game_state.score_mgr.lines % 10
        draw_meter_bar(surface, right_x + 18, level_y + 82, right_w - 36, 8, lines_in_level / 10.0, fill_color=COLOR_ACCENT_CYAN)

        if game_state.score_mgr.combo > 0:
            combo_str = f"COMBO x{game_state.score_mgr.combo}"
            combo_surf = self.font_body.render(combo_str, True, COLOR_ACCENT_MAGENTA)
            surface.blit(combo_surf, (right_x + 18, level_y + 106))
        elif game_state.score_mgr.b2b:
            b2b_surf = self.font_body.render("BACK-TO-BACK", True, COLOR_ACCENT_GOLD)
            surface.blit(b2b_surf, (right_x + 18, level_y + 106))

        # 8. TOP HEADER BAR: Mode, Timer, Pause Button
        header_y = 12
        mode_name = game_state.mode.upper()
        mode_surf = self.font_sub.render(f"// {mode_name} MODE", True, COLOR_ACCENT_CYAN)
        surface.blit(mode_surf, (board_x, header_y))

        # Timer format: MM:SS.ss
        mins = int(game_state.elapsed_time // 60)
        secs = game_state.elapsed_time % 60
        timer_str = f"{mins:02d}:{secs:05.2f}"
        timer_surf = self.font_sub.render(timer_str, True, COLOR_TEXT_PRIMARY)
        surface.blit(timer_surf, (board_x + matrix_w - timer_surf.get_width(), header_y))
