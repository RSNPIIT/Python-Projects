"""Modern Chess Game - Hardware-Accelerated ModernGL Renderer with NumPy"""
from pathlib import Path
import math
import numpy as np
import moderngl
import pygame

from core.constants import (
    BOARD_SIZE, SQUARE_PIXELS, BOARD_PIXELS,
    SIDE_PANEL_WIDTH, WINDOW_WIDTH, WINDOW_HEIGHT,
    Color, PieceType, THEMES, DEFAULT_THEME, square_name
)
from core.piece import Piece
from core.board import Board
from core.move import Move
from graphics.shaders import (
    TEXTURED_QUAD_VS, TEXTURED_QUAD_FS,
    RECT_VS, RECT_FS,
    CIRCLE_VS, CIRCLE_FS
)
from graphics.texture import TextureManager

class PieceAnimation:
    def __init__(self, piece: Piece, start_px: tuple[float, float], target_px: tuple[float, float], duration: float = 0.16):
        self.piece = piece
        self.start_px = start_px
        self.target_px = target_px
        self.duration = duration
        self.elapsed = 0.0
        self.completed = False

    def update(self, dt: float) -> tuple[float, float]:
        self.elapsed += dt
        t = min(1.0, self.elapsed / self.duration)
        # Ease out cubic curve
        ease = 1.0 - (1.0 - t) ** 3
        curr_x = self.start_px[0] + (self.target_px[0] - self.start_px[0]) * ease
        curr_y = self.start_px[1] + (self.target_px[1] - self.start_px[1]) * ease
        if t >= 1.0:
            self.completed = True
        return (curr_x, curr_y)


class ModernRenderer:
    def __init__(self, ctx: moderngl.Context, assets_dir: Path):
        self.ctx = ctx
        self.assets_dir = assets_dir
        self.texture_mgr = TextureManager(ctx)
        self.current_theme = THEMES[DEFAULT_THEME]
        self.current_theme_name = DEFAULT_THEME
        
        # Enable Alpha Blending in OpenGL
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)

        # Initialize Pygame fonts
        pygame.font.init()
        self.font_main = pygame.font.SysFont("Helvetica Neue, Arial, sans-serif", 18, bold=True)
        self.font_title = pygame.font.SysFont("Helvetica Neue, Arial, sans-serif", 24, bold=True)
        self.font_small = pygame.font.SysFont("Helvetica Neue, Arial, sans-serif", 13)
        self.font_history = pygame.font.SysFont("Courier, Monaco, monospace", 14)

        # Compile ModernGL Shader Programs
        self.prog_tex = self.ctx.program(vertex_shader=TEXTURED_QUAD_VS, fragment_shader=TEXTURED_QUAD_FS)
        self.prog_rect = self.ctx.program(vertex_shader=RECT_VS, fragment_shader=RECT_FS)
        self.prog_circle = self.ctx.program(vertex_shader=CIRCLE_VS, fragment_shader=CIRCLE_FS)

        # Create Unit Quad NumPy Buffers (pos and uv)
        quad_pos = np.array([
            0.0, 0.0,
            1.0, 0.0,
            0.0, 1.0,
            1.0, 1.0
        ], dtype='f4')

        quad_uv = np.array([
            0.0, 0.0,
            1.0, 0.0,
            0.0, 1.0,
            1.0, 1.0
        ], dtype='f4')

        self.vbo_pos = self.ctx.buffer(quad_pos.tobytes())
        self.vbo_uv = self.ctx.buffer(quad_uv.tobytes())

        # VAOs for rendering
        self.vao_tex = self.ctx.vertex_array(
            self.prog_tex,
            [
                (self.vbo_pos, '2f', 'in_pos'),
                (self.vbo_uv, '2f', 'in_uv')
            ]
        )
        self.vao_rect = self.ctx.vertex_array(self.prog_rect, [(self.vbo_pos, '2f', 'in_pos')])
        self.vao_circle = self.ctx.vertex_array(self.prog_circle, [(self.vbo_pos, '2f', 'in_pos')])

        self.active_animations: list[PieceAnimation] = []
        self.load_piece_assets()

    def set_theme(self, theme_name: str):
        if theme_name in THEMES:
            self.current_theme = THEMES[theme_name]
            self.current_theme_name = theme_name

    def load_piece_assets(self):
        """Preload piece textures from assets folder."""
        pieces_dir = self.assets_dir / "pieces"
        mapping = {
            "w_pawn": "w_pawn_png_1024px.png",
            "w_knight": "w_knight_png_1024px.png",
            "w_bishop": "w_bishop_png_1024px.png",
            "w_rook": "w_rook_png_1024px.png",
            "w_queen": "w_queen_png_1024px.png",
            "w_king": "w_king_png_1024px.png",
            "b_pawn": "b_pawn_png_1024px.png",
            "b_knight": "b_knight_png_1024px.png",
            "b_bishop": "b_bishop_png_1024px.png",
            "b_rook": "b_rook_png_1024px.png",
            "b_queen": "b_queen_png_1024px.png",
            "b_king": "b_king_png_1024px.png",
        }
        for key, fname in mapping.items():
            fpath = pieces_dir / fname
            if fpath.exists():
                self.texture_mgr.load_piece_texture(key, fpath)

    def square_to_px(self, row: int, col: int, flipped: bool) -> tuple[float, float]:
        """Convert board (row, col) to pixel (x, y) on screen."""
        draw_col = 7 - col if flipped else col
        draw_row = 7 - row if flipped else row
        return (draw_col * SQUARE_PIXELS, draw_row * SQUARE_PIXELS)

    def px_to_square(self, px_x: float, px_y: float, flipped: bool) -> tuple[int, int] | None:
        """Convert pixel (x, y) to board (row, col)."""
        if px_x < 0 or px_x >= BOARD_PIXELS or px_y < 0 or px_y >= BOARD_PIXELS:
            return None
        col = int(px_x // SQUARE_PIXELS)
        row = int(px_y // SQUARE_PIXELS)
        if flipped:
            return (7 - row, 7 - col)
        return (row, col)

    def draw_rect(
        self,
        pos: tuple[float, float],
        size: tuple[float, float],
        color: tuple[float, float, float, float],
        radius: float = 0.0,
        border_color: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0),
        border_width: float = 0.0
    ):
        self.prog_rect['u_resolution'].value = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.prog_rect['u_position'].value = pos
        self.prog_rect['u_size'].value = size
        self.prog_rect['u_color'].value = color
        self.prog_rect['u_radius'].value = radius
        self.prog_rect['u_border_color'].value = border_color
        self.prog_rect['u_border_width'].value = border_width
        self.vao_rect.render(moderngl.TRIANGLE_STRIP)

    def draw_textured_quad(
        self,
        texture: moderngl.Texture,
        pos: tuple[float, float],
        size: tuple[float, float],
        tint: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        opacity: float = 1.0,
        is_shadow: bool = False
    ):
        texture.use(location=0)
        self.prog_tex['u_texture'].value = 0
        self.prog_tex['u_resolution'].value = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.prog_tex['u_position'].value = pos
        self.prog_tex['u_size'].value = size
        self.prog_tex['u_tint'].value = tint
        self.prog_tex['u_opacity'].value = opacity
        self.prog_tex['u_is_shadow'].value = is_shadow
        self.vao_tex.render(moderngl.TRIANGLE_STRIP)

    def draw_circle(
        self,
        pos: tuple[float, float],
        size: tuple[float, float],
        color: tuple[float, float, float, float],
        inner_radius: float = 0.0,
        outer_radius: float = 0.5,
        glow: float = 0.0
    ):
        self.prog_circle['u_resolution'].value = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.prog_circle['u_position'].value = pos
        self.prog_circle['u_size'].value = size
        self.prog_circle['u_color'].value = color
        self.prog_circle['u_inner_radius'].value = inner_radius
        self.prog_circle['u_outer_radius'].value = outer_radius
        self.prog_circle['u_glow'].value = glow
        self.vao_circle.render(moderngl.TRIANGLE_STRIP)

    def draw_text(self, text: str, pos: tuple[float, float], font: pygame.font.Font, color: tuple[int, int, int] = (240, 240, 240)):
        """Render text using Pygame font rendered into a dynamic ModernGL texture."""
        surf = font.render(text, True, color)
        w, h = surf.get_size()
        tex_key = f"txt_{text}_{font.get_height()}_{color}"
        tex = self.texture_mgr.texture_from_surface(tex_key, surf)
        self.draw_textured_quad(tex, pos, (w, h))

    def trigger_move_animation(self, piece: Piece, start_sq: tuple[int, int], target_sq: tuple[int, int], flipped: bool):
        start_px = self.square_to_px(start_sq[0], start_sq[1], flipped)
        target_px = self.square_to_px(target_sq[0], target_sq[1], flipped)
        anim = PieceAnimation(piece, start_px, target_px, duration=0.15)
        self.active_animations.append(anim)

    def update_animations(self, dt: float):
        for anim in self.active_animations:
            anim.update(dt)
        self.active_animations = [a for a in self.active_animations if not a.completed]

    def render_board(
        self,
        board: Board,
        selected_sq: tuple[int, int] | None,
        valid_moves: list[Move],
        hovered_sq: tuple[int, int] | None,
        flipped: bool,
        time_sec: float
    ):
        theme = self.current_theme

        # 1. Background Fill
        self.draw_rect((0, 0), (WINDOW_WIDTH, WINDOW_HEIGHT), theme["bg"])

        # 2. Board 64 Squares
        last_move = board.move_history[-1] if board.move_history else None

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                px, py = self.square_to_px(r, c, flipped)
                is_light = (r + c) % 2 == 0
                sq_color = theme["light_sq"] if is_light else theme["dark_sq"]

                # Base square
                self.draw_rect((px, py), (SQUARE_PIXELS, SQUARE_PIXELS), sq_color)

                # Last move highlight
                if last_move and ((r, c) == last_move.start_sq or (r, c) == last_move.target_sq):
                    self.draw_rect((px, py), (SQUARE_PIXELS, SQUARE_PIXELS), theme["last_move"])

                # Hover highlight
                if hovered_sq == (r, c) and selected_sq != (r, c):
                    self.draw_rect((px, py), (SQUARE_PIXELS, SQUARE_PIXELS), theme["hover"])

                # Selected square highlight
                if selected_sq == (r, c):
                    self.draw_rect(
                        (px + 3, py + 3),
                        (SQUARE_PIXELS - 6, SQUARE_PIXELS - 6),
                        theme["selected"],
                        radius=8.0
                    )

        # 3. King in Check Glow Effect
        for color in [Color.WHITE, Color.BLACK]:
            if board.is_in_check(color):
                k_pos = board.find_king(color)
                if k_pos:
                    kpx, kpy = self.square_to_px(k_pos[0], k_pos[1], flipped)
                    pulse = 0.75 + 0.25 * math.sin(time_sec * 8.0)
                    glow_color = (theme["check_glow"][0], theme["check_glow"][1], theme["check_glow"][2], theme["check_glow"][3] * pulse)
                    self.draw_circle((kpx, kpy), (SQUARE_PIXELS, SQUARE_PIXELS), glow_color, outer_radius=0.55, glow=1.0)

        # 4. Valid Move Indicators (Dots for empty, Rings for captures)
        valid_targets = {m.target_sq: m for m in valid_moves}
        for (tr, tc), move in valid_targets.items():
            tpx, tpy = self.square_to_px(tr, tc, flipped)
            dot_color = theme["move_dot"]
            if move.is_capture or move.is_en_passant:
                # Capture Ring
                self.draw_circle(
                    (tpx + 6, tpy + 6),
                    (SQUARE_PIXELS - 12, SQUARE_PIXELS - 12),
                    (dot_color[0], dot_color[1], dot_color[2], 0.8),
                    inner_radius=0.38,
                    outer_radius=0.48
                )
            else:
                # Move Dot
                dot_size = SQUARE_PIXELS * 0.32
                offset = (SQUARE_PIXELS - dot_size) / 2
                self.draw_circle(
                    (tpx + offset, tpy + offset),
                    (dot_size, dot_size),
                    (dot_color[0], dot_color[1], dot_color[2], 0.75),
                    inner_radius=0.0,
                    outer_radius=0.48
                )

        # 5. Coordinate Labels (ranks 1-8, files a-h)
        for i in range(BOARD_SIZE):
            file_char = chr(ord('h') - i if flipped else ord('a') + i)
            rank_char = str(1 + i if flipped else 8 - i)

            # Files at bottom of board
            label_col = (0.9, 0.9, 0.9) if (7 + i) % 2 != 0 else (0.2, 0.2, 0.2)
            self.draw_text(
                file_char,
                (i * SQUARE_PIXELS + SQUARE_PIXELS - 15, BOARD_PIXELS - 18),
                self.font_small,
                color=(int(label_col[0]*255), int(label_col[1]*255), int(label_col[2]*255))
            )
            # Ranks at left of board
            rank_col = (0.9, 0.9, 0.9) if i % 2 != 0 else (0.2, 0.2, 0.2)
            self.draw_text(
                rank_char,
                (4, i * SQUARE_PIXELS + 4),
                self.font_small,
                color=(int(rank_col[0]*255), int(rank_col[1]*255), int(rank_col[2]*255))
            )

    def render_pieces(
        self,
        board: Board,
        flipped: bool,
        dragged_piece: Piece | None,
        dragged_pos: tuple[float, float] | None,
        dragged_orig_sq: tuple[int, int] | None
    ):
        animating_pieces = {a.piece: a for a in self.active_animations}

        # 1. Render stationary pieces on board
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = board.get_piece(r, c)
                if piece is None:
                    continue
                if piece == dragged_piece and (r, c) == dragged_orig_sq:
                    continue
                if piece in animating_pieces:
                    continue

                px, py = self.square_to_px(r, c, flipped)
                tex = self.texture_mgr.get(piece.texture_key)
                if tex:
                    # Subtle drop shadow
                    self.draw_textured_quad(tex, (px + 4, py + 6), (SQUARE_PIXELS, SQUARE_PIXELS), is_shadow=True)
                    # Main piece
                    self.draw_textured_quad(tex, (px, py), (SQUARE_PIXELS, SQUARE_PIXELS))

        # 2. Render animating pieces (smooth interpolation)
        for anim in self.active_animations:
            cur_x, cur_y = anim.update(0.0)
            tex = self.texture_mgr.get(anim.piece.texture_key)
            if tex:
                self.draw_textured_quad(tex, (cur_x + 5, cur_y + 8), (SQUARE_PIXELS, SQUARE_PIXELS), is_shadow=True)
                self.draw_textured_quad(tex, (cur_x, cur_y), (SQUARE_PIXELS, SQUARE_PIXELS))

        # 3. Render dragged piece on top of everything
        if dragged_piece and dragged_pos:
            tex = self.texture_mgr.get(dragged_piece.texture_key)
            if tex:
                dsize = SQUARE_PIXELS * 1.12
                dpos = (dragged_pos[0] - dsize / 2, dragged_pos[1] - dsize / 2)
                # Elevated drop shadow
                self.draw_textured_quad(tex, (dpos[0] + 10, dpos[1] + 16), (dsize, dsize), opacity=0.8, is_shadow=True)
                self.draw_textured_quad(tex, dpos, (dsize, dsize), opacity=1.0)

    def render_side_panel(self, board: Board, flipped: bool):
        theme = self.current_theme
        panel_x = BOARD_PIXELS
        panel_w = SIDE_PANEL_WIDTH
        panel_h = WINDOW_HEIGHT

        # Panel Background with subtle border
        self.draw_rect((panel_x, 0), (panel_w, panel_h), theme["panel_bg"])
        self.draw_rect(
            (panel_x, 0), (panel_w, panel_h),
            (0.0, 0.0, 0.0, 0.0),
            border_color=(0.25, 0.30, 0.38, 0.4),
            border_width=1.5
        )

        # Title
        self.draw_text("MODERN CHESS", (panel_x + 20, 20), self.font_title, color=(245, 245, 250))
        self.draw_text(f"Theme: {self.current_theme_name}", (panel_x + 20, 52), self.font_small, color=(140, 160, 180))

        # Turn indicator card
        turn_color_str = board.turn.name_str
        card_y = 80
        self.draw_rect((panel_x + 16, card_y), (panel_w - 32, 54), (0.15, 0.18, 0.22, 0.8), radius=8.0)
        
        # Turn dot
        dot_col = (1.0, 1.0, 1.0, 1.0) if board.turn == Color.WHITE else (0.1, 0.1, 0.1, 1.0)
        self.draw_circle((panel_x + 28, card_y + 16), (22, 22), dot_col, outer_radius=0.48)
        self.draw_circle((panel_x + 28, card_y + 16), (22, 22), (0.5, 0.5, 0.5, 0.8), inner_radius=0.45, outer_radius=0.50)

        status_text = f"{turn_color_str} to move"
        if board.is_checkmate():
            status_text = f"Checkmate! {board.turn.opponent.name_str} wins!"
        elif board.is_stalemate():
            status_text = "Stalemate! Draw."
        elif board.is_in_check(board.turn):
            status_text = f"{turn_color_str} is in Check!"

        self.draw_text(status_text, (panel_x + 58, card_y + 16), self.font_main, color=(255, 215, 100) if board.is_in_check(board.turn) else (230, 235, 240))

        # Captured Pieces Section
        cap_y = 150
        self.draw_text("CAPTURED PIECES", (panel_x + 20, cap_y), self.font_small, color=(140, 150, 170))

        # Render captured by White (Black pieces)
        row1_y = cap_y + 22
        icon_size = 28
        for i, piece in enumerate(board.captured_black[:8]):
            tex = self.texture_mgr.get(piece.texture_key)
            if tex:
                self.draw_textured_quad(tex, (panel_x + 20 + i * 26, row1_y), (icon_size, icon_size))
        
        # Render captured by Black (White pieces)
        row2_y = row1_y + 32
        for i, piece in enumerate(board.captured_white[:8]):
            tex = self.texture_mgr.get(piece.texture_key)
            if tex:
                self.draw_textured_quad(tex, (panel_x + 20 + i * 26, row2_y), (icon_size, icon_size))

        # Move History Section
        hist_y = 250
        self.draw_text("MOVE LOG", (panel_x + 20, hist_y), self.font_small, color=(140, 150, 170))
        self.draw_rect((panel_x + 16, hist_y + 20), (panel_w - 32, 280), (0.07, 0.08, 0.10, 0.8), radius=6.0)

        # Show last 10 move pairs
        history = board.move_history
        moves_to_show = history[-14:]
        lines = []
        for i in range(0, len(moves_to_show), 2):
            w_move = moves_to_show[i]
            b_move = moves_to_show[i + 1] if i + 1 < len(moves_to_show) else None
            move_num = (history.index(w_move) // 2) + 1
            line = f"{move_num:2d}. {w_move.to_san():<7}"
            if b_move:
                line += f" {b_move.to_san()}"
            lines.append(line)

        for idx, line in enumerate(lines[-10:]):
            self.draw_text(line, (panel_x + 28, hist_y + 30 + idx * 24), self.font_history, color=(200, 210, 225))

        # Shortcuts Info Card at Bottom
        info_y = 560
        self.draw_rect((panel_x + 16, info_y), (panel_w - 32, 140), (0.12, 0.14, 0.18, 0.6), radius=8.0)
        self.draw_text("SHORTCUTS & CONTROLS", (panel_x + 28, info_y + 12), self.font_small, color=(130, 170, 220))
        self.draw_text("[F] Flip Board", (panel_x + 28, info_y + 36), self.font_small, color=(180, 190, 205))
        self.draw_text("[U] / [Ctrl+Z] Undo Move", (panel_x + 28, info_y + 58), self.font_small, color=(180, 190, 205))
        self.draw_text("[T] Switch Color Theme", (panel_x + 28, info_y + 80), self.font_small, color=(180, 190, 205))
        self.draw_text("[R] Reset / New Game", (panel_x + 28, info_y + 102), self.font_small, color=(180, 190, 205))

    def render_promotion_dialog(self, color: Color, col: int, flipped: bool):
        """Draw sleek promotion choice overlay when a pawn is promoted."""
        pieces = [PieceType.QUEEN, PieceType.KNIGHT, PieceType.ROOK, PieceType.BISHOP]
        prefix = "w" if color == Color.WHITE else "b"
        
        draw_col = 7 - col if flipped else col
        base_x = draw_col * SQUARE_PIXELS
        dialog_y = 0 if (color == Color.WHITE and not flipped) or (color == Color.BLACK and flipped) else (BOARD_SIZE - 4) * SQUARE_PIXELS

        # Dark frosted modal background
        self.draw_rect((base_x - 4, dialog_y - 4), (SQUARE_PIXELS + 8, SQUARE_PIXELS * 4 + 8), (0.05, 0.06, 0.09, 0.95), radius=10.0, border_color=(0.4, 0.7, 1.0, 0.6), border_width=2.0)

        for i, ptype in enumerate(pieces):
            py = dialog_y + i * SQUARE_PIXELS
            # Highlight item hover
            self.draw_rect((base_x + 2, py + 2), (SQUARE_PIXELS - 4, SQUARE_PIXELS - 4), (0.15, 0.18, 0.24, 0.9), radius=6.0)
            tex_key = f"{prefix}_{ptype.name.lower()}"
            tex = self.texture_mgr.get(tex_key)
            if tex:
                self.draw_textured_quad(tex, (base_x, py), (SQUARE_PIXELS, SQUARE_PIXELS))
