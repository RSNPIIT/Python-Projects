# ===============================
# Minimax Algorithm in R
# Tic-Tac-Toe Example
# ===============================

# Represent board as a vector of 9 cells:
# "X", "O", or "" (empty)

print_board <- function(board) {
  cat(board[1], board[2], board[3], "\n")
  cat(board[4], board[5], board[6], "\n")
  cat(board[7], board[8], board[9], "\n\n")
}

# Winning combinations
wins <- list(
  c(1,2,3), c(4,5,6), c(7,8,9), # rows
  c(1,4,7), c(2,5,8), c(3,6,9), # columns
  c(1,5,9), c(3,5,7)            # diagonals
)

# Check if a player has won
check_win <- function(board, player) {
  for (line in wins) {
    if (all(board[line] == player)) return(TRUE)
  }
  return(FALSE)
}

# Check terminal state
is_terminal <- function(board) {
  check_win(board, "X") || check_win(board, "O") || all(board != "")
}

# Evaluate board score
# X = maximizing player, O = minimizing player
score <- function(board) {
  if (check_win(board, "X")) return(+1)
  if (check_win(board, "O")) return(-1)
  return(0)
}

# Minimax function
minimax <- function(board, depth, isMaximizing) {
  if (is_terminal(board)) {
    return(score(board))
  }

  if (isMaximizing) {
    bestScore <- -Inf

    for (i in which(board == "")) {
      board_copy <- board
      board_copy[i] <- "X"

      result <- minimax(board_copy, depth + 1, FALSE)
      bestScore <- max(bestScore, result)
    }

    return(bestScore)

  } else {
    bestScore <- +Inf

    for (i in which(board == "")) {
      board_copy <- board
      board_copy[i] <- "O"

      result <- minimax(board_copy, depth + 1, TRUE)
      bestScore <- min(bestScore, result)
    }

    return(bestScore)
  }
}

# Best move function for X (AI / maximizing player)
best_move <- function(board) {
  bestScore <- -Inf
  move <- NULL

  for (i in which(board == "")) {
    board_copy <- board
    board_copy[i] <- "X"

    result <- minimax(board_copy, 0, FALSE)

    if (result > bestScore) {
      bestScore <- result
      move <- i
    }
  }

  return(move)
}

# ===============================
# Example Usage
# ===============================

board <- c("", "", "",
           "", "", "",
           "", "", "")

cat("Initial board:\n")
print_board(board)

next_move <- best_move(board)
cat("Best move for X is position:", next_move, "\n")