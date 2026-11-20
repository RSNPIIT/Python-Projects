from board import Board

## PIECE VALUES
## pawn(1) = 1
## knight(2) = 3
## bishop(3) = 3
## rook(4) = 5
## queen(5) = 9

class Evaluate:
    def __init__(self):
        pass

    def evaluate(self, board):
        score = 0

        for ri, r in enumerate(board.state):
            for ci, p in enumerate(r):

                if p > 0:
                    team = 1
                elif p < 0:
                    team = -1
                else:
                    continue

                if p == 1 or p == -1: ## PAWNS
                    score += 1 * team

                    ## DOUBLED PAWNS
                    if team == 1:
                        if ri + 1 <= 7:
                            if board.state[ri + 1][ci] == 1:
                                score -= 0.5
                    elif team == -1:
                        if ri - 1 >= 0:
                            if board.state[ri - 1][ci] == -1:
                                score += 0.5

                if p == 2 or p == -2: ## KNIGHTS
                    score += 3 * team

                    if (ri == 3 or ri == 4) and (ci == 3 or ci == 4): ## CENTER
                        score += 0.5 * team
                    if (ri == 2 or ri == 5) and (ci == 2 or ci == 5): ## SEMI-CENTER
                        score += 0.25 * team
                    if (ri == 1 or ri == 6) and (ci == 1 or ci == 6): ## OUTER
                        score -= 0.25 * team
                    if (ri == 0 or ri == 7) and (ci == 0 or ci == 7): ## CORNERS
                        score -= 0.5 * team

                if p == 3 or p == -3: ## BISHOPS
                    score += 3 * team

                    if (ri == 3 or ri == 4) and (ci == 3 or ci == 4): ## CENTER
                        score += 0.5 * team
                    if (ri == 2 or ri == 5) and (ci == 2 or ci == 5): ## SEMI-CENTER
                        score += 0.25 * team

                if p == 4 or p == -4: ## ROOKS
                    score += 5 * team

                if p == 5 or p == -5: ## QUEENS
                    score += 9 * team

                if p == 6 or p == -6: ## KINGS
                    if team == 1:
                        if (ri == 7 and ci == 2) or (ri == 7 and ci == 6): ## SAFE
                            score += 0.75
                        if (ri == 7 and ci == 1) or (ri == 7 and ci == 7): ## SEMI-SAFE
                            score += 0.25

                    if team == -1:
                        if (ri == 0 and ci == 2) or (ri == 0 and ci == 6): ## SAFE
                            score -= 0.75
                        if (ri == 0 and ci == 1) or (ri == 0 and ci == 7): ## SEMI-SAFE
                            score -= 0.25

        return score