#!/bin/zsh

set -e

TARGET_DIR="modern_chess_game"

find "$TARGET_DIR" -type f \
  ! -name ".DS_Store" \
  ! -path "*/__pycache__/*" \
  ! -name "*.pyc" | sort | while IFS= read -r file; do
    echo "----------------------------------------"
    echo "Processing: $file"
    
    git add "$file"
    git commit -m "Add $file"
    git push origin main
done

echo "----------------------------------------"
echo "Done! All valid files in $TARGET_DIR pushed one by one."
