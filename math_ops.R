# math_ops.R
# This file is part of Python-Projects.
# Copyright (c) 2025 Ramrup Satpati
# Licensed under the GNU General Public License v3.0 (GPL-3.0).

args <- commandArgs(trailingOnly = TRUE)

if(length(args) < 2){
  stop("Please provide two numbers as arguments, e.g. Rscript math_ops.R 12 5")
}

num1 <- as.numeric(args[1])
num2 <- as.numeric(args[2])

sum_result <- num1 + num2
prod_result <- num1 * num2
diff_result <- num1 - num2
div_result <- num1 / num2
mod_result <- num1 %% num2

cat("Sum: ", sum_result, "\n")
cat("Product: ", prod_result, "\n")
cat("Difference: ", diff_result, "\n")
cat("Division: ", div_result, "\n")
cat("Remainder: ", mod_result, "\n")

