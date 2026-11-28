#!/bin/bash

# Find all files, excluding .git, __pycache__, and .DS_Store
find 2048_game -type f -not -path '*/.*' -not -path '*__pycache__*' | while read -r file; do
    echo "Processing: $file"
    
    # Stage the single file
    git add "$file"
    
    # Commit with a message containing the filename
    git commit -m "Add $(basename "$file")"
    
    # Push the commit to the current branch
    git push
done

