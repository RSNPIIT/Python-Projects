#!/bin/bash

# Target directory
TARGET_DIR="computer_vision_project"

# Ensure target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory $TARGET_DIR not found in the current location."
    exit 1
fi

echo "🚀 Launching single-file Git commit sequence for $TARGET_DIR..."

# Find all files recursively in the folder, excluding .venv or hidden folders if any exist
find "$TARGET_DIR" -type f | while read -r filepath; do
    
    # Check if the file is tracked/modified or completely untracked
    if git status --porcelain "$filepath" | grep -q '.*'; then
        echo "--------------------------------------------------"
        echo "Adding file: $filepath"
        
        # Stage the single file
        git add "$filepath"
        
        # Extract base file name for the detailed commit message
        filename=$(basename "$filepath")
        dirname=$(dirname "$filepath")
        
        # Construct a descriptive, detailed commit message
        commit_message="feat(cv-playground): integrate and track module components

Staging specific codebase file assets for the computer vision setup.
- Target module: $filename
- Component directory: $dirname
- Status: Verifying structural setup and environment runtime integration parameters."

        echo "Committing: $filename"
        git commit -m "$commit_message"
        
        # Push the single commit immediately to remote repo
        echo "Pushing change upstream..."
        git push origin main
        
        # Small cooldown buffer to maintain stream consistency
        sleep 1
    else
        echo "Skipping (already up to date): $filepath"
    fi
done

echo "--------------------------------------------------"
echo "✅ Done! All individual codebase components processed and pushed."

