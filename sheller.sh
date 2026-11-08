#!/bin/bash

# Extract only the modified/tracked file paths from git status
files=$(git status --porcelain | grep '^.M' | awk '{print $2}')

if [ -z "$files" ]; then
    echo "No modified files found to process."
    exit 0
fi

for file in $files; do
    echo "----------------------------------------"
    echo "Processing: $file"
    
    # 1. Add the specific file
    git add "$file"
    
    # 2. Extract just the filename for a clean commit message
    filename=$(basename "$file")
    git commit -m "Update $filename"
    
    # 3. Push the individual commit
    git push origin main
done

echo "----------------------------------------"
echo "Done! Both files have been pushed individually."

