"""Modern Chess Game - Intelligent Chess AI Engine (Minimax with Alpha-Beta & PST)"""
import random
from typing import Optional
from core.constants import Color, PieceType, BOARD_SIZE
from core.piece import Piece
from core.board import Board
from core.move import Move

# Piece-Square Tables (PST) for mid-game positional evaluation (from White's perspective)
# Higher values = better squares
PAWN_TABLE = [
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [ 5,  5, 10, 25, 25, 10,  5,  5],
    [ 0,  0,  0, 20, 20,  0,  0,  0],
    [ 5, -5,-10,  0,  0,-10, -5,  5],
    [ 5, 10, 10,-20,-20, 10, 10,  5],
    [ 0,  0,  0,  0,  0,  0,  0,  0]
]

KNIGHT_TABLE = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

BISHOP_TABLE = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]

ROOK_TABLE = [
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [ 0,  0,  0,  5,  5,  0,  0,  0]
]

QUEEN_TABLE = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [ -5,  0,  5,  5,  5,  5,  0, -5],
    [  0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
]

KING_TABLE = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [ 20, 20,  0,  0,  0,  0, 20, 20],
    [ 20, 30, 10,  0,  0, 10, 30, 20]
]

PST_MAP = {
    PieceType.PAWN: PAWN_TABLE,
    PieceType.KNIGHT: KNIGHT_TABLE,
    PieceType.BISHOP: BISHOP_TABLE,
    PieceType.ROOK: ROOK_TABLE,
    PieceType.QUEEN: QUEEN_TABLE,
    PieceType.KING: KING_TABLE,
}

class ChessAI:
    def __init__(self, difficulty: str = "Medium"):
        self.difficulty = difficulty

    def set_difficulty(self, difficulty: str):
        self.difficulty = difficulty

    def evaluate_board(self, board: Board) -> int:
        """
        Evaluate board state from White's perspective.
        Positive = White advantage, Negative = Black advantage.
        """
        if board.is_checkmate():
            return -99999 if board.turn == Color.WHITE else 99999
        if board.is_stalemate():
            return 0

        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = board.grid[r][c]
                if piece is None:
                    continue

                val = piece.piece_type.value
                table = PST_MAP.get(piece.piece_type)
                
                # Flip table row for Black
                pst_val = table[r][c] if piece.color == Color.WHITE else table[7 - r][c]
                total_val = val + pst_val

                if piece.color == Color.WHITE:
                    score += total_val
                else:
                    score -= total_val

        return score

    def move_priority(self, move: Move) -> int:
        """Move ordering heuristic: search captures and promotions first."""
        priority = 0
        if move.captured:
            priority += move.captured.piece_type.value * 10 - move.piece.piece_type.value
        if move.promotion:
            priority += 800
        if move.is_castling:
            priority += 60
        return priority

    def minimax(
        self,
        board: Board,
        depth: int,
        alpha: int,
        beta: int,
        is_maximizing: bool
    ) -> tuple[int, Optional[Move]]:
        legal_moves = board.generate_legal_moves()
        if not legal_moves:
            if board.is_in_check(board.turn):
                return (-99999 + (3 - depth) * 100 if is_maximizing else 99999 - (3 - depth) * 100), None
            return 0, None

        if depth == 0:
            return self.evaluate_board(board), None

        # Sort moves to maximize alpha-beta cutoffs
        legal_moves.sort(key=self.move_priority, reverse=True)

        best_move = None
        if is_maximizing:
            max_eval = -999999
            for move in legal_moves:
                board.make_move(move)
                eval_score, _ = self.minimax(board, depth - 1, alpha, beta, False)
                board.undo_move()

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = 999999
            for move in legal_moves:
                board.make_move(move)
                eval_score, _ = self.minimax(board, depth - 1, alpha, beta, True)
                board.undo_move()

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def compute_best_move(self, board: Board) -> Optional[Move]:
        # Work on an isolated clone of the board so live game state is never mutated in the background thread!
        board_copy = board.clone()
        legal_moves = board_copy.generate_legal_moves()
        if not legal_moves:
            return None

        # Depth based on difficulty
        if self.difficulty == "Easy":
            if random.random() < 0.35:
                chosen = random.choice(legal_moves)
                return self._find_matching_move(board, chosen)
            depth = 1
        elif self.difficulty == "Hard":
            depth = 3
        else:  # Medium
            depth = 2

        is_maximizing = (board_copy.turn == Color.WHITE)
        _, best_move = self.minimax(board_copy, depth, -999999, 999999, is_maximizing)
        if best_move is None:
            best_move = random.choice(legal_moves)

        return self._find_matching_move(board, best_move)

    def _find_matching_move(self, live_board: Board, ai_move: Move) -> Optional[Move]:
        live_legal = live_board.generate_legal_moves()
        for m in live_legal:
            if m.start_sq == ai_move.start_sq and m.target_sq == ai_move.target_sq and m.promotion == ai_move.promotion:
                return m
        return live_legal[0] if live_legal else None
