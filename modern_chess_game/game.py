"""Modern Chess Game - Main Game Controller and Event Handler"""
import time
import threading
from pathlib import Path
from typing import Optional
import pygame

from core.constants import (
    BOARD_SIZE, SQUARE_PIXELS, BOARD_PIXELS, SIDE_PANEL_WIDTH,
    WINDOW_WIDTH, WINDOW_HEIGHT,
    Color, PieceType, THEMES, DEFAULT_THEME
)
from core.piece import Piece
from core.move import Move
from core.board import Board
from core.ai import ChessAI
from graphics.renderer import ModernRenderer
from audio.sound_manager import SoundManager

class ChessGame:
    def __init__(self, renderer: ModernRenderer, sound_mgr: SoundManager):
        self.renderer = renderer
        self.sound = sound_mgr
        self.board = Board()
        
        # Game State: "MENU" (Main Title Menu) or "GAME" (Active Chess Match)
        self.state = "MENU"

        # UI & Interaction State
        self.flipped = False
        self.auto_flip = False
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

        # Game Mode & AI Engine
        # Modes: "Human vs AI", "Human vs Human"
        self.game_mode = "Human vs AI"
        self.ai_difficulty_levels = ["Easy", "Medium", "Hard"]
        self.ai_difficulty_idx = 1  # Default "Medium"
        self.ai_difficulty = self.ai_difficulty_levels[self.ai_difficulty_idx]
        self.ai_color = Color.BLACK
        self.ai = ChessAI(difficulty=self.ai_difficulty)
        
        self.is_ai_thinking = False
        self.pending_ai_move: Optional[Move] = None

        # Main Menu Buttons (Centered in 560x560 container at x=210, y=80)
        self.menu_btn_pvp = pygame.Rect(260, 215, 460, 85)
        self.menu_btn_pve = pygame.Rect(260, 320, 460, 130)
        self.menu_diff_rects = {
            "Easy": pygame.Rect(440, 395, 70, 26),
            "Medium": pygame.Rect(520, 395, 86, 26),
            "Hard": pygame.Rect(616, 395, 70, 26),
        }
        self.menu_btn_quit = pygame.Rect(410, 470, 160, 34)

        # In-Game Side Panel Buttons
        self.btn_mode_rect = pygame.Rect(BOARD_PIXELS + 16, 46, SIDE_PANEL_WIDTH - 32, 28)
        self.btn_diff_rect = pygame.Rect(BOARD_PIXELS + 16, 78, SIDE_PANEL_WIDTH - 32, 24)

        # Themes list for cycling
        self.theme_keys = list(THEMES.keys())
        self.current_theme_idx = self.theme_keys.index(DEFAULT_THEME)

        # Quit Confirmation Dialog State
        self.show_quit_dialog = False
        card_w, card_h = 420, 220
        card_x = (WINDOW_WIDTH - card_w) // 2
        card_y = (WINDOW_HEIGHT - card_h) // 2
        btn_w, btn_h = 160, 44
        btn_y = card_y + card_h - 66
        self.btn_quit_rect = pygame.Rect(card_x + 32, btn_y, btn_w, btn_h)
        self.btn_cancel_rect = pygame.Rect(card_x + card_w - btn_w - 32, btn_y, btn_w, btn_h)

    def start_game(self, mode: str):
        self.game_mode = mode
        self.reset_game()
        self.state = "GAME"
        self.sound.play("move")

    def return_to_menu(self):
        self.state = "MENU"
        self.is_ai_thinking = False
        self.pending_ai_move = None
        self.sound.play("move")

    def toggle_game_mode(self):
        if self.game_mode == "Human vs AI":
            self.game_mode = "Human vs Human"
        else:
            self.game_mode = "Human vs AI"
        self.is_ai_thinking = False
        self.pending_ai_move = None

    def cycle_ai_difficulty(self):
        self.ai_difficulty_idx = (self.ai_difficulty_idx + 1) % len(self.ai_difficulty_levels)
        self.ai_difficulty = self.ai_difficulty_levels[self.ai_difficulty_idx]
        self.ai.set_difficulty(self.ai_difficulty)

    def request_quit(self):
        self.show_quit_dialog = True
        self.is_dragging = False

    def cancel_quit(self):
        self.show_quit_dialog = False

    def handle_quit_click(self, mouse_pos: tuple[int, int]) -> str | None:
        if not self.show_quit_dialog:
            return None
        if self.btn_quit_rect.collidepoint(mouse_pos):
            return "quit"
        if self.btn_cancel_rect.collidepoint(mouse_pos):
            self.cancel_quit()
            return "cancel"
        return None

    def reset_game(self):
        self.board.setup_initial_position()
        self.selected_sq = None
        self.valid_moves.clear()
        self.hovered_sq = None
        self.is_dragging = False
        self.dragged_piece = None
        self.pending_promotion_move = None
        self.is_ai_thinking = False
        self.pending_ai_move = None
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

        # Auto flip if enabled (in PvP mode)
        if self.auto_flip and self.game_mode == "Human vs Human":
            self.flipped = not self.flipped

    def try_execute_move(self, start_sq: tuple[int, int], target_sq: tuple[int, int]):
        matching_moves = [
            m for m in self.valid_moves
            if m.start_sq == start_sq and m.target_sq == target_sq
        ]
        if not matching_moves:
            return False

        if any(m.promotion is not None for m in matching_moves):
            self.pending_promotion_move = matching_moves[0]
            return True

        self.handle_move_execution(matching_moves[0])
        return True

    def handle_promotion_choice(self, chosen_promo: PieceType):
        if self.pending_promotion_move:
            m = self.pending_promotion_move
            matches = [
                legal_m for legal_m in self.valid_moves
                if legal_m.start_sq == m.start_sq and legal_m.target_sq == m.target_sq and legal_m.promotion == chosen_promo
            ]
            if matches:
                self.pending_promotion_move = None
                self.handle_move_execution(matches[0])

    def handle_mouse_down(self, pos: tuple[int, int], button: int):
        if button != 1:
            return

        mx, my = pos

        # =================================================================
        # MAIN MENU INTERACTION
        # =================================================================
        if self.state == "MENU":
            # 1. Human vs Human clicked
            if self.menu_btn_pvp.collidepoint(mx, my):
                self.start_game("Human vs Human")
                return

            # 2. Check Difficulty Chips inside Human vs Bot card
            for dname, drect in self.menu_diff_rects.items():
                if drect.collidepoint(mx, my):
                    self.ai_difficulty = dname
                    self.ai.set_difficulty(dname)
                    self.sound.play("move")
                    return

            # 3. Human vs Bot clicked
            if self.menu_btn_pve.collidepoint(mx, my):
                self.start_game("Human vs AI")
                return

            # 4. Quit Game Button clicked
            if self.menu_btn_quit.collidepoint(mx, my):
                self.request_quit()
                return

            return

        # =================================================================
        # IN-GAME INTERACTION
        # =================================================================
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

        # Check Side Panel Button clicks
        if self.btn_mode_rect.collidepoint(mx, my):
            # Return to Main Menu
            self.return_to_menu()
            return
        if self.game_mode == "Human vs AI" and self.btn_diff_rect.collidepoint(mx, my):
            self.cycle_ai_difficulty()
            return

        # If it's AI's turn, human cannot click/drag board pieces
        if self.game_mode == "Human vs AI" and self.board.turn == self.ai_color:
            return

        sq = self.renderer.px_to_square(mx, my, self.flipped)
        if sq is None:
            self.selected_sq = None
            self.valid_moves.clear()
            return

        row, col = sq
        piece = self.board.get_piece(row, col)

        # If square already selected and valid target clicked
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
        if self.state == "GAME":
            self.hovered_sq = self.renderer.px_to_square(mx, my, self.flipped)
            if self.is_dragging:
                self.drag_mouse_pos = (float(mx), float(my))

    def handle_mouse_up(self, pos: tuple[int, int], button: int):
        if button != 1:
            return

        if self.state == "GAME" and self.is_dragging and self.dragged_orig_sq:
            mx, my = pos
            target_sq = self.renderer.px_to_square(mx, my, self.flipped)
            dist_dragged = ((mx - self.drag_start_pos[0])**2 + (my - self.drag_start_pos[1])**2)**0.5

            if dist_dragged > 8.0 and target_sq is not None and target_sq != self.dragged_orig_sq:
                if not self.try_execute_move(self.dragged_orig_sq, target_sq):
                    pass
            self.is_dragging = False
            self.dragged_piece = None
            self.dragged_orig_sq = None

    def handle_key_down(self, event: pygame.event.Event):
        if self.state == "MENU":
            if event.key == pygame.K_1:
                self.start_game("Human vs Human")
            elif event.key == pygame.K_2:
                self.start_game("Human vs AI")
            elif event.key == pygame.K_d:
                self.cycle_ai_difficulty()
            elif event.key == pygame.K_ESCAPE:
                self.request_quit()
            return

        # In-game shortcuts
        if event.key == pygame.K_m:
            self.return_to_menu()
        elif event.key == pygame.K_d:
            self.cycle_ai_difficulty()
        elif event.key == pygame.K_f:
            self.flipped = not self.flipped
        elif event.key == pygame.K_a:
            self.auto_flip = not self.auto_flip
        elif event.key == pygame.K_t:
            self.cycle_theme()
        elif event.key == pygame.K_r:
            self.reset_game()
        elif event.key == pygame.K_u or (event.key == pygame.K_z and (event.mod & pygame.KMOD_META or event.mod & pygame.KMOD_CTRL)):
            if self.game_mode == "Human vs AI" and len(self.board.move_history) >= 2:
                self.board.undo_move()
                self.board.undo_move()
                self.selected_sq = None
                self.valid_moves.clear()
                self.sound.play("move")
            else:
                undone = self.board.undo_move()
                if undone:
                    self.selected_sq = None
                    self.valid_moves.clear()
                    self.sound.play("move")
                    if self.auto_flip:
                        self.flipped = not self.flipped

    def update(self, dt: float):
        if self.state != "GAME":
            return

        # AI Turn Handling in PvE mode
        if (self.game_mode == "Human vs AI" and
            self.board.turn == self.ai_color and
            not self.board.is_checkmate() and
            not self.board.is_stalemate() and
            not self.show_quit_dialog):

            if not self.is_ai_thinking and self.pending_ai_move is None:
                self.is_ai_thinking = True
                
                def ai_worker():
                    time.sleep(0.30)
                    best_move = self.ai.compute_best_move(self.board)
                    self.pending_ai_move = best_move
                    self.is_ai_thinking = False

                threading.Thread(target=ai_worker, daemon=True).start()

        # If AI move ready, execute it on main thread
        if self.pending_ai_move is not None:
            move = self.pending_ai_move
            self.pending_ai_move = None
            self.handle_move_execution(move)

    def render(self, time_sec: float, mouse_pos: tuple[int, int] = (0, 0)):
        # 1. Main Menu State
        if self.state == "MENU":
            self.renderer.render_main_menu(
                mouse_pos,
                self.menu_btn_pvp,
                self.menu_btn_pve,
                self.menu_diff_rects,
                self.ai_difficulty,
                self.menu_btn_quit,
                time_sec
            )
        else:
            # 2. In-Game Chess Playing State
            self.renderer.render_board(
                self.board,
                self.selected_sq,
                self.valid_moves,
                self.hovered_sq,
                self.flipped,
                time_sec
            )

            self.renderer.render_pieces(
                self.board,
                self.flipped,
                self.dragged_piece if self.is_dragging else None,
                self.drag_mouse_pos if self.is_dragging else None,
                self.dragged_orig_sq if self.is_dragging else None
            )

            self.renderer.render_side_panel(
                self.board,
                self.flipped,
                self.game_mode,
                self.ai_difficulty,
                self.is_ai_thinking,
                self.btn_mode_rect,
                self.btn_diff_rect,
                mouse_pos
            )

            if self.pending_promotion_move:
                self.renderer.render_promotion_dialog(
                    self.pending_promotion_move.piece.color,
                    self.pending_promotion_move.target_sq[1],
                    self.flipped
                )

        # 3. Quit Confirmation Dialog Overlay (Active across all states)
        if self.show_quit_dialog:
            self.renderer.render_quit_dialog(mouse_pos, self.btn_quit_rect, self.btn_cancel_rect)
