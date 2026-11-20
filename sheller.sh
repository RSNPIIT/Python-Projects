#!/bin/zsh

# Stop immediately if a git command fails (e.g., network/auth error during push)
set -e

TARGET_DIR="chess_engine"

# Find all files recursively inside chess_engine, ignoring .DS_Store
find "$TARGET_DIR" -type f ! -name ".DS_Store" | sort | while IFS= read -r file; do
    echo "----------------------------------------"
    echo "Processing: $file"
    
    git add "$file"
    git commit -m "Add $file"
    git push origin main
done

echo "----------------------------------------"
echo "Done! All files have been added, committed, and pushed one by one."

