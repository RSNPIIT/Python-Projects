#!/bin/bash

# Target directory containing the untracked game files
TARGET_DIR="thornspire_game_latest"

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory $TARGET_DIR does not exist."
    exit 1
fi

echo "Scanning for files to commit one by one..."

# Find all files in the target directory, excluding virtual environments and pycache folders
find "$TARGET_DIR" -type f ! -path '*/venv/*' ! -path '*/__pycache__/*' | while read -r filepath; do
    
    echo "----------------------------------------"
    echo "Processing: $filepath"
    
    # 1. Add the individual file
    git add "$filepath"
    
    # Extract file name for a clean, detailed commit message
    filename=$(basename "$filepath")
    
    # 2. Commit the file with a descriptive message
    git commit -m "Add core module component: $filename from track $filepath"
    
    # 3. Push the specific commit to the remote repository
    echo "Pushing changes for $filename..."
    git push origin main
    
    # Check if the operations succeeded
    if [ $? -eq 0 ]; then
        echo "Successfully added, committed, and pushed: $filename"
    else
        echo "Failed processing: $filepath"
    fi
done

echo "----------------------------------------"
echo "All files handled successfully!"

