#!/bin/bash

# Get a list of all modified and untracked files
files=$(git status --porcelain | awk '{print $2}')

# Check if there are any changes to process
if [ -z "$files" ]; then
    echo "No changes to commit."
    exit 0
fi

# Loop through each file one by one
for file in $files; do
    echo "----------------------------------------"
    echo "Processing file: $file"
    
    # 1. Add the specific file
    git add "$file"
    
    # 2. Commit the specific file
    git commit -m "Update: $file"
    
    # 3. Push the specific commit
    git push origin main
done

echo "----------------------------------------"
echo "All files have been pushed individually!"

