# Rock-Paper-Scissors CLI Game in R

cat("==== ROCK - PAPER - SCISSORS ====\n")
cat("Type r, p, s to play or q to quit.\n\n")

choices <- c("r", "p", "s")
names(choices) <- c("Rock", "Paper", "Scissors")

player_score <- 0
computer_score <- 0
ties <- 0

repeat {
  player <- tolower(readline(prompt = "Your move (r/p/s or q to quit): "))

  # Quit condition
  if (player == "q") {
    cat("\nExiting game...\n")
    break
  }

  # Validate input
  if (!(player %in% choices)) {
    cat("Invalid choice! Try again.\n\n")
    next
  }

  # Computer randomly picks
  computer <- sample(choices, 1)

  # Convert letters to names for display
  player_name <- names(choices)[choices == player]
  computer_name <- names(choices)[choices == computer]

  cat("\nYou chose:     ", player_name)
  cat("\nComputer chose:", computer_name, "\n")

  # Decide winner
  if (player == computer) {
    result <- "It's a tie!"
    ties <- ties + 1
  } else if (
    (player == "r" && computer == "s") ||
    (player == "p" && computer == "r") ||
    (player == "s" && computer == "p")
  ) {
    result <- "You win!"
    player_score <- player_score + 1
  } else {
    result <- "Computer wins!"
    computer_score <- computer_score + 1
  }

  cat("Result:", result, "\n")
  cat("Score -> You:", player_score, " Computer:", computer_score, " Ties:", ties, "\n\n")
}

cat("\n==== FINAL SCORE ====\n")
cat("You:", player_score, "\n")
cat("Computer:", computer_score, "\n")
cat("Ties:", ties, "\n")
cat("Thanks for playing!\n")