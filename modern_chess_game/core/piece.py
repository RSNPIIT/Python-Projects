"""Modern Chess Game - Piece Hierarchy (OOP)"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from core.constants import Color, PieceType, BOARD_SIZE

if TYPE_CHECKING:
    from core.board import Board
    from core.move import Move

class Piece(ABC):
    """Abstract Base Class for all chess pieces."""

    def __init__(self, color: Color, piece_type: PieceType):
        self.color = color
        self.piece_type = piece_type
        self.has_moved = False

    @property
    def texture_key(self) -> str:
        color_prefix = "w" if self.color == Color.WHITE else "b"
        return f"{color_prefix}_{self.piece_type.name.lower()}"

    @abstractmethod
    def get_pseudo_legal_moves(self, board: "Board", row: int, col: int) -> list["Move"]:
        """Generate pseudo-legal moves for this piece without verifying king safety."""
        pass

    def clone(self) -> "Piece":
        """Create a deep copy of the piece."""
        new_piece = self.__class__(self.color)
        new_piece.has_moved = self.has_moved
        return new_piece

    def __repr__(self) -> str:
        symbol = self.piece_type.symbol
        return symbol if self.color == Color.WHITE else symbol.lower()


class Pawn(Piece):
    def __init__(self, color: Color):
        super().__init__(color, PieceType.PAWN)

    def get_pseudo_legal_moves(self, board: "Board", row: int, col: int) -> list["Move"]:
        from core.move import Move
        moves = []
        direction = -1 if self.color == Color.WHITE else 1
        start_row = 6 if self.color == Color.WHITE else 1
        promotion_row = 0 if self.color == Color.WHITE else 7

        # 1-square forward
        next_row = row + direction
        if 0 <= next_row < BOARD_SIZE and board.get_piece(next_row, col) is None:
            if next_row == promotion_row:
                for promo in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                    moves.append(Move((row, col), (next_row, col), self, promotion=promo))
            else:
                moves.append(Move((row, col), (next_row, col), self))

            # 2-square initial jump
            double_row = row + 2 * direction
            if row == start_row and board.get_piece(double_row, col) is None:
                moves.append(Move((row, col), (double_row, col), self))

        # Diagonal captures
        for dc in [-1, 1]:
            target_col = col + dc
            if 0 <= target_col < BOARD_SIZE and 0 <= next_row < BOARD_SIZE:
                target_piece = board.get_piece(next_row, target_col)
                # Standard capture
                if target_piece is not None and target_piece.color != self.color:
                    if next_row == promotion_row:
                        for promo in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                            moves.append(Move((row, col), (next_row, target_col), self, captured=target_piece, promotion=promo))
                    else:
                        moves.append(Move((row, col), (next_row, target_col), self, captured=target_piece))
                # En passant capture
                elif (next_row, target_col) == board.en_passant_target:
                    captured_pawn = board.get_piece(row, target_col)
                    moves.append(Move((row, col), (next_row, target_col), self, captured=captured_pawn, is_en_passant=True))

        return moves


class Knight(Piece):
    def __init__(self, color: Color):
        super().__init__(color, PieceType.KNIGHT)

    def get_pseudo_legal_moves(self, board: "Board", row: int, col: int) -> list["Move"]:
        from core.move import Move
        moves = []
        offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for dr, dc in offsets:
            nr, nc = row + dr, col + dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                target = board.get_piece(nr, nc)
                if target is None:
                    moves.append(Move((row, col), (nr, nc), self))
                elif target.color != self.color:
                    moves.append(Move((row, col), (nr, nc), self, captured=target))
        return moves


class Bishop(Piece):
    def __init__(self, color: Color):
        super().__init__(color, PieceType.BISHOP)

    def get_pseudo_legal_moves(self, board: "Board", row: int, col: int) -> list["Move"]:
        from core.move import Move
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                target = board.get_piece(nr, nc)
                if target is None:
                    moves.append(Move((row, col), (nr, nc), self))
                else:
                    if target.color != self.color:
                        moves.append(Move((row, col), (nr, nc), self, captured=target))
                    break
                nr += dr
                nc += dc
        return moves


class Rook(Piece):
    def __init__(self, color: Color):
        super().__init__(color, PieceType.ROOK)

    def get_pseudo_legal_moves(self, board: "Board", row: int, col: int) -> list["Move"]:
        from core.move import Move
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                target = board.get_piece(nr, nc)
                if target is None:
                    moves.append(Move((row, col), (nr, nc), self))
                else:
                    if target.color != self.color:
                        moves.append(Move((row, col), (nr, nc), self, captured=target))
                    break
                nr += dr
                nc += dc
        return moves


class Queen(Piece):
    def __init__(self, color: Color):
        super().__init__(color, PieceType.QUEEN)

    def get_pseudo_legal_moves(self, board: "Board", row: int, col: int) -> list["Move"]:
        from core.move import Move
        moves = []
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                target = board.get_piece(nr, nc)
                if target is None:
                    moves.append(Move((row, col), (nr, nc), self))
                else:
                    if target.color != self.color:
                        moves.append(Move((row, col), (nr, nc), self, captured=target))
                    break
                nr += dr
                nc += dc
        return moves


class King(Piece):
    def __init__(self, color: Color):
        super().__init__(color, PieceType.KING)

    def get_pseudo_legal_moves(self, board: "Board", row: int, col: int) -> list["Move"]:
        from core.move import Move
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    target = board.get_piece(nr, nc)
                    if target is None:
                        moves.append(Move((row, col), (nr, nc), self))
                    elif target.color != self.color:
                        moves.append(Move((row, col), (nr, nc), self, captured=target))

        # Castling pseudo-moves (full check safety verified in board.generate_legal_moves)
        if not self.has_moved:
            # Kingside castling
            if board.can_castle_kingside(self.color):
                moves.append(Move((row, col), (row, col + 2), self, is_castling=True))
            # Queenside castling
            if board.can_castle_queenside(self.color):
                moves.append(Move((row, col), (row, col - 2), self, is_castling=True))

        return moves
