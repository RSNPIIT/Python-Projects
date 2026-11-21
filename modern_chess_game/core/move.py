"""Modern Chess Game - Move representation"""
from typing import Optional
from core.constants import PieceType, square_name
from core.piece import Piece

class Move:
    def __init__(
        self,
        start_sq: tuple[int, int],
        target_sq: tuple[int, int],
        piece: Piece,
        captured: Optional[Piece] = None,
        promotion: Optional[PieceType] = None,
        is_en_passant: bool = False,
        is_castling: bool = False
    ):
        self.start_sq = start_sq
        self.target_sq = target_sq
        self.piece = piece
        self.captured = captured
        self.promotion = promotion
        self.is_en_passant = is_en_passant
        self.is_castling = is_castling

        # State tracking for undo
        self.prev_has_moved = piece.has_moved
        self.prev_en_passant_target = None
        self.prev_halfmove_clock = 0

    @property
    def is_capture(self) -> bool:
        return self.captured is not None

    def to_san(self) -> str:
        """Standard Algebraic Notation representation (basic)"""
        if self.is_castling:
            return "O-O" if self.target_sq[1] > self.start_sq[1] else "O-O-O"

        piece_prefix = "" if self.piece.piece_type == PieceType.PAWN else self.piece.piece_type.symbol
        capture_mark = ""
        start_file = square_name(*self.start_sq)[0]
        target_name = square_name(*self.target_sq)

        if self.is_capture:
            if self.piece.piece_type == PieceType.PAWN:
                piece_prefix = start_file
            capture_mark = "x"

        promo_mark = f"={self.promotion.symbol}" if self.promotion else ""
        return f"{piece_prefix}{capture_mark}{target_name}{promo_mark}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Move):
            return False
        return (
            self.start_sq == other.start_sq and
            self.target_sq == other.target_sq and
            self.promotion == other.promotion
        )

    def __hash__(self) -> int:
        return hash((self.start_sq, self.target_sq, self.promotion))

    def __repr__(self) -> str:
        return f"Move({square_name(*self.start_sq)} -> {square_name(*self.target_sq)}, {self.piece}, promo={self.promotion})"
