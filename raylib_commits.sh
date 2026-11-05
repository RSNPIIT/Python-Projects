#!/bin/bash

# Target directory relative to root
TARGET_DIR="raylib_game"

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' not found from this root path."
    exit 1
fi

echo "Scanning for modified and untracked changes inside $TARGET_DIR from root workspace..."

# Captures both modified ( M) and untracked (??) paths cleanly
git status --porcelain -uall "$TARGET_DIR" | grep -E '^(\?\?| M|M ) ' | sed 's/^...//' | while read -r FILE; do
    
    # Strip wrapping quotes if git outputs them for paths containing spaces/special chars
    FILE=$(echo "$FILE" | sed -e 's/^"//' -e 's/"$//')

    # Guard against directories or bytecode caches
    if [ -d "$FILE" ] || [[ "$FILE" == *__pycache__* ]]; then
        continue
    fi

    # Dynamically structure granular, descriptive commit messages based on layout paths
    if [[ "$FILE" == "$TARGET_DIR/assets/audio/"* ]]; then
        MSG="Asset Management: Integrating high-fidelity audio asset and sound effect layer components ($FILE) into the global raylib game sound infrastructure loop"
    elif [[ "$FILE" == "$TARGET_DIR/assets/fonts/"* ]]; then
        MSG="Asset Management: Embedding required typography, font face files, and open font license text metrics ($FILE) to update user interface rendering consistency"
    elif [[ "$FILE" == "$TARGET_DIR/screenshots/"* ]]; then
        MSG="Documentation Update: Capturing high-resolution visual interface capture frames ($FILE) to demonstrate recent gameplay systems, UI overlays, and engine state progress"
    elif [[ "$FILE" == "$TARGET_DIR/game/"* ]] || [[ "$FILE" == "$TARGET_DIR/main.py" ]]; then
        MSG="Source Refactoring: Progressing architectural codebase enhancements, game state logic routines, or engine compatibility rendering matrices for $FILE source structure"
    else
        MSG="Maintenance Update: Staging routine structural workspace synchronization protocols and tracking configurations for utility asset $FILE"
    fi

    echo "Staging file from root: $FILE"
    git add "$FILE"

    echo "Committing with detailed message: '$MSG'"
    git commit -m "$MSG"
    
    echo "----------------------------------------------------------------------"
done

# Push the final chain of individual commits to the repository remote
echo "Pushing all individual commits sequentially generated to the remote repository branch..."
git push

