"""Modern Chess Game - Board State and Rules Engine"""
from typing import Optional
from core.constants import Color, PieceType, BOARD_SIZE
from core.piece import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from core.move import Move

class Board:
    def __init__(self):
        self.grid: list[list[Optional[Piece]]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn: Color = Color.WHITE
        self.en_passant_target: Optional[tuple[int, int]] = None
        self.halfmove_clock: int = 0
        self.fullmove_number: int = 1
        
        self.move_history: list[Move] = []
        self.captured_white: list[Piece] = []
        self.captured_black: list[Piece] = []
        
        self.setup_initial_position()

    def setup_initial_position(self):
        """Set up standard starting chess position."""
        self.grid = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = Color.WHITE
        self.en_passant_target = None
        self.move_history.clear()
        self.captured_white.clear()
        self.captured_black.clear()
        self.halfmove_clock = 0
        self.fullmove_number = 1

        # Black Major Pieces (Row 0)
        self.grid[0][0] = Rook(Color.BLACK)
        self.grid[0][1] = Knight(Color.BLACK)
        self.grid[0][2] = Bishop(Color.BLACK)
        self.grid[0][3] = Queen(Color.BLACK)
        self.grid[0][4] = King(Color.BLACK)
        self.grid[0][5] = Bishop(Color.BLACK)
        self.grid[0][6] = Knight(Color.BLACK)
        self.grid[0][7] = Rook(Color.BLACK)

        # Black Pawns (Row 1)
        for col in range(BOARD_SIZE):
            self.grid[1][col] = Pawn(Color.BLACK)

        # White Pawns (Row 6)
        for col in range(BOARD_SIZE):
            self.grid[6][col] = Pawn(Color.WHITE)

        # White Major Pieces (Row 7)
        self.grid[7][0] = Rook(Color.WHITE)
        self.grid[7][1] = Knight(Color.WHITE)
        self.grid[7][2] = Bishop(Color.WHITE)
        self.grid[7][3] = Queen(Color.WHITE)
        self.grid[7][4] = King(Color.WHITE)
        self.grid[7][5] = Bishop(Color.WHITE)
        self.grid[7][6] = Knight(Color.WHITE)
        self.grid[7][7] = Rook(Color.WHITE)

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return self.grid[row][col]
        return None

    def set_piece(self, row: int, col: int, piece: Optional[Piece]):
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            self.grid[row][col] = piece

    def find_king(self, color: Color) -> Optional[tuple[int, int]]:
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.grid[r][c]
                if p is not None and p.piece_type == PieceType.KING and p.color == color:
                    return (r, c)
        return None

    def is_square_attacked(self, target_row: int, target_col: int, by_color: Color) -> bool:
        """Check if target square is attacked by any piece of by_color."""
        # 1. Pawns
        pawn_dir = 1 if by_color == Color.BLACK else -1
        # If by_color attacks target_row, the attacking pawn must be at target_row - pawn_dir
        pawn_row = target_row - pawn_dir
        for dc in [-1, 1]:
            pc = target_col + dc
            if 0 <= pawn_row < BOARD_SIZE and 0 <= pc < BOARD_SIZE:
                piece = self.grid[pawn_row][pc]
                if piece and piece.color == by_color and piece.piece_type == PieceType.PAWN:
                    return True

        # 2. Knights
        knight_offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for dr, dc in knight_offsets:
            nr, nc = target_row + dr, target_col + dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                piece = self.grid[nr][nc]
                if piece and piece.color == by_color and piece.piece_type == PieceType.KNIGHT:
                    return True

        # 3. Kings
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = target_row + dr, target_col + dc
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    piece = self.grid[nr][nc]
                    if piece and piece.color == by_color and piece.piece_type == PieceType.KING:
                        return True

        # 4. Diagonal Rays (Bishops & Queens)
        diag_dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in diag_dirs:
            nr, nc = target_row + dr, target_col + dc
            while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                piece = self.grid[nr][nc]
                if piece is not None:
                    if piece.color == by_color and piece.piece_type in (PieceType.BISHOP, PieceType.QUEEN):
                        return True
                    break
                nr += dr
                nc += dc

        # 5. Orthogonal Rays (Rooks & Queens)
        ortho_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in ortho_dirs:
            nr, nc = target_row + dr, target_col + dc
            while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                piece = self.grid[nr][nc]
                if piece is not None:
                    if piece.color == by_color and piece.piece_type in (PieceType.ROOK, PieceType.QUEEN):
                        return True
                    break
                nr += dr
                nc += dc

        return False

    def is_in_check(self, color: Color) -> bool:
        king_pos = self.find_king(color)
        if king_pos is None:
            return False
        return self.is_square_attacked(king_pos[0], king_pos[1], color.opponent)

    def can_castle_kingside(self, color: Color) -> bool:
        row = 7 if color == Color.WHITE else 0
        king = self.get_piece(row, 4)
        rook = self.get_piece(row, 7)
        if not king or king.piece_type != PieceType.KING or king.has_moved:
            return False
        if not rook or rook.piece_type != PieceType.ROOK or rook.has_moved:
            return False
        # Squares between must be empty
        if self.grid[row][5] is not None or self.grid[row][6] is not None:
            return False
        # King cannot castle out of check, through check, or into check
        opponent = color.opponent
        if (self.is_square_attacked(row, 4, opponent) or
            self.is_square_attacked(row, 5, opponent) or
            self.is_square_attacked(row, 6, opponent)):
            return False
        return True

    def can_castle_queenside(self, color: Color) -> bool:
        row = 7 if color == Color.WHITE else 0
        king = self.get_piece(row, 4)
        rook = self.get_piece(row, 0)
        if not king or king.piece_type != PieceType.KING or king.has_moved:
            return False
        if not rook or rook.piece_type != PieceType.ROOK or rook.has_moved:
            return False
        # Squares between must be empty
        if self.grid[row][1] is not None or self.grid[row][2] is not None or self.grid[row][3] is not None:
            return False
        # King cannot castle out of check, through check, or into check
        opponent = color.opponent
        if (self.is_square_attacked(row, 4, opponent) or
            self.is_square_attacked(row, 3, opponent) or
            self.is_square_attacked(row, 2, opponent)):
            return False
        return True

    def generate_legal_moves(self, color: Optional[Color] = None) -> list[Move]:
        if color is None:
            color = self.turn

        legal_moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = self.grid[r][c]
                if piece and piece.color == color:
                    pseudo_moves = piece.get_pseudo_legal_moves(self, r, c)
                    for move in pseudo_moves:
                        if self._is_move_safe(move, color):
                            legal_moves.append(move)
        return legal_moves

    def get_valid_moves_for_piece(self, row: int, col: int) -> list[Move]:
        piece = self.get_piece(row, col)
        if piece is None or piece.color != self.turn:
            return []
        pseudo = piece.get_pseudo_legal_moves(self, row, col)
        return [m for m in pseudo if self._is_move_safe(m, self.turn)]

    def _is_move_safe(self, move: Move, color: Color) -> bool:
        """Simulate move and check if own king is in check afterwards."""
        sr, sc = move.start_sq
        tr, tc = move.target_sq
        piece = self.grid[sr][sc]
        target_orig = self.grid[tr][tc]

        # Handle En Passant simulation
        ep_captured_pos = None
        ep_captured_piece = None
        if move.is_en_passant:
            ep_captured_pos = (sr, tc)
            ep_captured_piece = self.grid[sr][tc]
            self.grid[sr][tc] = None

        # Execute temporary move
        self.grid[tr][tc] = piece
        self.grid[sr][sc] = None

        safe = not self.is_in_check(color)

        # Rollback
        self.grid[sr][sc] = piece
        self.grid[tr][tc] = target_orig
        if move.is_en_passant and ep_captured_pos is not None:
            self.grid[ep_captured_pos[0]][ep_captured_pos[1]] = ep_captured_piece

        return safe

    def make_move(self, move: Move):
        """Execute a move on the board."""
        sr, sc = move.start_sq
        tr, tc = move.target_sq
        piece = self.grid[sr][sc]

        move.prev_has_moved = piece.has_moved
        move.prev_en_passant_target = self.en_passant_target
        move.prev_halfmove_clock = self.halfmove_clock

        # Handle Capture
        if move.captured:
            if move.captured.color == Color.WHITE:
                self.captured_white.append(move.captured)
            else:
                self.captured_black.append(move.captured)

        # Handle En Passant
        if move.is_en_passant:
            self.grid[sr][tc] = None

        # Handle Castling Rook Movement
        if move.is_castling:
            if tc > sc:  # Kingside
                rook = self.grid[sr][7]
                self.grid[sr][5] = rook
                self.grid[sr][7] = None
                if rook: rook.has_moved = True
            else:  # Queenside
                rook = self.grid[sr][0]
                self.grid[sr][3] = rook
                self.grid[sr][0] = None
                if rook: rook.has_moved = True

        # Handle Pawn Promotion
        if move.promotion:
            promo_cls = {
                PieceType.QUEEN: Queen,
                PieceType.ROOK: Rook,
                PieceType.BISHOP: Bishop,
                PieceType.KNIGHT: Knight
            }[move.promotion]
            piece = promo_cls(piece.color)
            piece.has_moved = True

        # Move Piece
        self.grid[tr][tc] = piece
        self.grid[sr][sc] = None
        piece.has_moved = True

        # Update En Passant Target
        if piece.piece_type == PieceType.PAWN and abs(tr - sr) == 2:
            self.en_passant_target = ((sr + tr) // 2, sc)
        else:
            self.en_passant_target = None

        # Halfmove clock
        if piece.piece_type == PieceType.PAWN or move.is_capture:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if self.turn == Color.BLACK:
            self.fullmove_number += 1

        self.turn = self.turn.opponent
        self.move_history.append(move)

    def undo_move(self) -> Optional[Move]:
        """Undo the last played move."""
        if not self.move_history:
            return None

        move = self.move_history.pop()
        sr, sc = move.start_sq
        tr, tc = move.target_sq

        piece = self.grid[tr][tc]
        if move.promotion:
            piece = Pawn(move.piece.color)

        piece.has_moved = move.prev_has_moved
        self.grid[sr][sc] = piece
        self.grid[tr][tc] = move.captured if not move.is_en_passant else None

        if move.is_en_passant:
            self.grid[sr][tc] = move.captured

        if move.is_castling:
            if tc > sc:  # Kingside
                rook = self.grid[sr][5]
                self.grid[sr][7] = rook
                self.grid[sr][5] = None
                if rook: rook.has_moved = False
            else:  # Queenside
                rook = self.grid[sr][3]
                self.grid[sr][0] = rook
                self.grid[sr][3] = None
                if rook: rook.has_moved = False

        if move.captured:
            if move.captured.color == Color.WHITE:
                self.captured_white.pop()
            else:
                self.captured_black.pop()

        self.en_passant_target = move.prev_en_passant_target
        self.halfmove_clock = move.prev_halfmove_clock
        self.turn = self.turn.opponent
        if self.turn == Color.BLACK:
            self.fullmove_number -= 1

        return move

    def is_checkmate(self) -> bool:
        return self.is_in_check(self.turn) and len(self.generate_legal_moves(self.turn)) == 0

    def is_stalemate(self) -> bool:
        return (not self.is_in_check(self.turn)) and len(self.generate_legal_moves(self.turn)) == 0
