"""Modern Chess Game - Main Game Controller and Event Handler"""
import time
from pathlib import Path
from typing import Optional
import pygame

from core.constants import (
    BOARD_SIZE, SQUARE_PIXELS, BOARD_PIXELS,
    Color, PieceType, THEMES, DEFAULT_THEME
)
from core.piece import Piece
from core.move import Move
from core.board import Board
from graphics.renderer import ModernRenderer
from audio.sound_manager import SoundManager

class ChessGame:
    def __init__(self, renderer: ModernRenderer, sound_mgr: SoundManager):
        self.renderer = renderer
        self.sound = sound_mgr
        self.board = Board()
        
        # UI & Interaction State
        self.flipped = False
        self.auto_flip = False  # Toggleable: matches original turtle behavior when True
        self.selected_sq: Optional[tuple[int, int]] = None
        self.valid_moves: list[Move] = []
        self.hovered_sq: Optional[tuple[int, int]] = None
        
        # Drag and Drop State
        self.is_dragging = False
        self.dragged_piece: Optional[Piece] = None
        self.dragged_orig_sq: Optional[tuple[int, int]] = None
        self.drag_mouse_pos: tuple[float, float] = (0.0, 0.0)
        self.drag_start_pos: tuple[float, float] = (0.0, 0.0)

        # Promotion State
        self.pending_promotion_move: Optional[Move] = None

        # Themes list for cycling
        self.theme_keys = list(THEMES.keys())
        self.current_theme_idx = self.theme_keys.index(DEFAULT_THEME)

    def reset_game(self):
        self.board.setup_initial_position()
        self.selected_sq = None
        self.valid_moves.clear()
        self.hovered_sq = None
        self.is_dragging = False
        self.dragged_piece = None
        self.pending_promotion_move = None
        self.flipped = False

    def cycle_theme(self):
        self.current_theme_idx = (self.current_theme_idx + 1) % len(self.theme_keys)
        theme_name = self.theme_keys[self.current_theme_idx]
        self.renderer.set_theme(theme_name)

    def select_square(self, row: int, col: int):
        piece = self.board.get_piece(row, col)
        if piece is not None and piece.color == self.board.turn:
            self.selected_sq = (row, col)
            self.valid_moves = self.board.get_valid_moves_for_piece(row, col)
        else:
            self.selected_sq = None
            self.valid_moves.clear()

    def handle_move_execution(self, move: Move):
        """Execute move, trigger sound and visual effects."""
        piece = move.piece
        is_capture = move.is_capture or move.is_en_passant
        is_castle = move.is_castling

        # Trigger animation
        self.renderer.trigger_move_animation(piece, move.start_sq, move.target_sq, self.flipped)

        # Execute move on board
        self.board.make_move(move)

        # Sound effects
        if self.board.is_checkmate():
            self.sound.play("game_over")
        elif self.board.is_in_check(self.board.turn):
            self.sound.play("check")
        elif is_castle:
            self.sound.play("castle")
        elif is_capture:
            self.sound.play("capture")
        else:
            self.sound.play("move")

        # Clear selection
        self.selected_sq = None
        self.valid_moves.clear()
        self.is_dragging = False
        self.dragged_piece = None
        self.dragged_orig_sq = None

        # Auto flip if enabled
        if self.auto_flip:
            self.flipped = not self.flipped

    def try_execute_move(self, start_sq: tuple[int, int], target_sq: tuple[int, int]):
        matching_moves = [
            m for m in self.valid_moves
            if m.start_sq == start_sq and m.target_sq == target_sq
        ]
        if not matching_moves:
            return False

        # Check if move is pawn promotion
        if any(m.promotion is not None for m in matching_moves):
            # Prompt for promotion choice
            self.pending_promotion_move = matching_moves[0]
            return True

        # Normal move
        self.handle_move_execution(matching_moves[0])
        return True

    def handle_promotion_choice(self, chosen_promo: PieceType):
        if self.pending_promotion_move:
            m = self.pending_promotion_move
            # Find the legal move with chosen promotion
            matches = [
                legal_m for legal_m in self.valid_moves
                if legal_m.start_sq == m.start_sq and legal_m.target_sq == m.target_sq and legal_m.promotion == chosen_promo
            ]
            if matches:
                self.pending_promotion_move = None
                self.handle_move_execution(matches[0])

    def handle_mouse_down(self, pos: tuple[int, int], button: int):
        if button != 1:  # Left click only
            return

        mx, my = pos

        # If promotion popup is active
        if self.pending_promotion_move is not None:
            col = self.pending_promotion_move.target_sq[1]
            draw_col = 7 - col if self.flipped else col
            base_x = draw_col * SQUARE_PIXELS
            color = self.pending_promotion_move.piece.color
            dialog_y = 0 if (color == Color.WHITE and not self.flipped) or (color == Color.BLACK and self.flipped) else (BOARD_SIZE - 4) * SQUARE_PIXELS

            if base_x <= mx <= base_x + SQUARE_PIXELS:
                promo_options = [PieceType.QUEEN, PieceType.KNIGHT, PieceType.ROOK, PieceType.BISHOP]
                item_idx = int((my - dialog_y) // SQUARE_PIXELS)
                if 0 <= item_idx < len(promo_options):
                    self.handle_promotion_choice(promo_options[item_idx])
            return

        sq = self.renderer.px_to_square(mx, my, self.flipped)
        if sq is None:
            self.selected_sq = None
            self.valid_moves.clear()
            return

        row, col = sq
        piece = self.board.get_piece(row, col)

        # If a square was already selected and user clicked a valid destination
        if self.selected_sq is not None and sq != self.selected_sq:
            if self.try_execute_move(self.selected_sq, sq):
                return

        # Start selecting / dragging piece
        if piece is not None and piece.color == self.board.turn:
            self.select_square(row, col)
            self.is_dragging = True
            self.dragged_piece = piece
            self.dragged_orig_sq = sq
            self.drag_start_pos = (float(mx), float(my))
            self.drag_mouse_pos = (float(mx), float(my))
        else:
            self.selected_sq = None
            self.valid_moves.clear()

    def handle_mouse_move(self, pos: tuple[int, int]):
        mx, my = pos
        self.hovered_sq = self.renderer.px_to_square(mx, my, self.flipped)
        if self.is_dragging:
            self.drag_mouse_pos = (float(mx), float(my))

    def handle_mouse_up(self, pos: tuple[int, int], button: int):
        if button != 1:
            return

        if self.is_dragging and self.dragged_orig_sq:
            mx, my = pos
            target_sq = self.renderer.px_to_square(mx, my, self.flipped)
            dist_dragged = ((mx - self.drag_start_pos[0])**2 + (my - self.drag_start_pos[1])**2)**0.5

            # If user dragged more than 8 pixels, treat as drag-and-drop
            if dist_dragged > 8.0 and target_sq is not None and target_sq != self.dragged_orig_sq:
                if not self.try_execute_move(self.dragged_orig_sq, target_sq):
                    # Invalid drop, snap back
                    pass
            self.is_dragging = False
            self.dragged_piece = None
            self.dragged_orig_sq = None

    def handle_key_down(self, event: pygame.event.Event):
        if event.key == pygame.K_f:
            self.flipped = not self.flipped
        elif event.key == pygame.K_a:
            self.auto_flip = not self.auto_flip
        elif event.key == pygame.K_t:
            self.cycle_theme()
        elif event.key == pygame.K_r:
            self.reset_game()
        elif event.key == pygame.K_u or (event.key == pygame.K_z and (event.mod & pygame.KMOD_META or event.mod & pygame.KMOD_CTRL)):
            undone = self.board.undo_move()
            if undone:
                self.selected_sq = None
                self.valid_moves.clear()
                self.sound.play("move")
                if self.auto_flip:
                    self.flipped = not self.flipped

    def render(self, time_sec: float):
        # 1. Render Board & Squares
        self.renderer.render_board(
            self.board,
            self.selected_sq,
            self.valid_moves,
            self.hovered_sq,
            self.flipped,
            time_sec
        )

        # 2. Render Pieces & Active Animations
        self.renderer.render_pieces(
            self.board,
            self.flipped,
            self.dragged_piece if self.is_dragging else None,
            self.drag_mouse_pos if self.is_dragging else None,
            self.dragged_orig_sq if self.is_dragging else None
        )

        # 3. Render Side Panel UI
        self.renderer.render_side_panel(self.board, self.flipped)

        # 4. Render Promotion Dialog if pending
        if self.pending_promotion_move:
            self.renderer.render_promotion_dialog(
                self.pending_promotion_move.piece.color,
                self.pending_promotion_move.target_sq[1],
                self.flipped
            )
