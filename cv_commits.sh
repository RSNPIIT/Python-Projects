#!/bin/bash

TARGET_DIR="computer_vision_project"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory $TARGET_DIR not found."
    exit 1
fi

echo "🚀 Launching single-file Git commit sequence for $TARGET_DIR..."

# Use -not -path to completely exclude the virtual environment folder
find "$TARGET_DIR" -not -path "*/.venv*" -type f | while read -r filepath; do
    
    # Check if the file itself is modified or untracked (handles new files inside untracked directories)
    if git status --porcelain "$filepath" | grep -q '.*' || [ ! -z "$(git status --porcelain | grep "$filepath")" ]; then
        echo "--------------------------------------------------"
        echo "Adding file: $filepath"
        
        git add "$filepath"
        
        filename=$(basename "$filepath")
        dirname=$(dirname "$filepath")
        
        commit_message="feat(cv-playground): integrate and track module components

Staging specific codebase file assets for the computer vision setup.
- Target module: $filename
- Component directory: $dirname
- Status: Verifying structural setup and environment runtime integration parameters."

        echo "Committing: $filename"
        git commit -m "$commit_message"
        
        echo "Pushing change upstream..."
        git push origin main
        
        sleep 1
    else
        echo "Skipping (already up to date): $filepath"
    fi
done

echo "--------------------------------------------------"
echo "✅ Done! Real source code components processed."

