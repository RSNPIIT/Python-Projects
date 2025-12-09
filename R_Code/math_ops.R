You said:
# math_ops.R
# Looping interactive calculator in R
# Exit only when user types 'q' or 'Q'

repeat {
  # Prompt for numbers
  num1 <- as.numeric(readline(prompt = "Enter first number (or q to quit): "))
  if (is.na(num1)) {
    input <- readline(prompt = "Did you mean to quit? (q to exit, any other key to continue): ")
    if (tolower(input) == "q") break else next
  }
  
  num2 <- as.numeric(readline(prompt = "Enter second number: "))
  
  # Show menu
  cat("\nChoose an operation:\n")
  cat("1: Addition\n")
  cat("2: Subtraction\n")
  cat("3: Multiplication\n")
  cat("4: Division\n")
  cat("5: Modulus (Remainder)\n")
  cat("q: Quit\n")
  
  choice <- readline(prompt = "Enter choice (1-5 or q): ")
  
  if (tolower(choice) == "q") {
    cat("\nExiting calculator. Goodbye!\n")
    break
  }
  
  choice <- as.integer(choice)
  
  # Perform operation
  result <- switch(choice,
                   num1 + num2,
                   num1 - num2,
                   num1 * num2,
                   if (num2 != 0) num1 / num2 else "Error: Division by zero",
                   if (num2 != 0) num1 %% num2 else "Error: Modulus by zero",
                   "Invalid choice")
  
  cat("\nResult: ", result, "\n\n")
}