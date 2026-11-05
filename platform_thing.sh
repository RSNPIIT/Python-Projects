#!/bin/bash

# Target directory relative to root
TARGET_DIR="platformer_game"

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' not found from this root path."
    exit 1
fi

echo "Scanning for modified and untracked changes inside $TARGET_DIR from root workspace..."

# Captures modified ( M) alongside untracked (??) paths cleanly inside the platformer directory tree
git status --porcelain -uall "$TARGET_DIR" | grep -E '^(\?\?| M|M ) ' | sed 's/^...//' | while read -r FILE; do
    
    # Strip wrapping quotes if git outputs them for paths containing spaces/special chars
    FILE=$(echo "$FILE" | sed -e 's/^"//' -e 's/"$//')

    # Guard against directories or bytecode caches
    if [ -d "$FILE" ] || [[ "$FILE" == *__pycache__* ]]; then
        continue
    fi

    # Dynamically structure granular, descriptive commit messages based on platformer paths
    if [[ "$FILE" == "$TARGET_DIR/game/player.py" ]] || [[ "$FILE" == "$TARGET_DIR/game/enemies.py" ]] || [[ "$FILE" == "$TARGET_DIR/game/bot.py" ]]; then
        MSG="Source Refactoring: Progressing physics interaction loops, entity behavior trees, and kinematic runtime controller systems for $FILE structure"
    elif [[ "$FILE" == "$TARGET_DIR/game/shaders.py" ]] || [[ "$FILE" == "$TARGET_DIR/game/renderer.py" ]] || [[ "$FILE" == "$TARGET_DIR/game/particles.py" ]]; then
        MSG="Source Refactoring: Implementing low-level graphics processing routines, visual effect pipelines, and hardware accelerated buffer rendering matrix configurations for $FILE"
    elif [[ "$FILE" == "$TARGET_DIR/game/"* ]] || [[ "$FILE" == "$TARGET_DIR/main.py" ]]; then
        MSG="Source Refactoring: Advancing game state state machine logic, core environmental parameters, and architectural layout updates for $FILE framework layer"
    elif [[ "$FILE" == "$TARGET_DIR/tools/"* ]]; then
        MSG="Development Tooling: Integrating functional workspace instrumentation scripts, utility pipelines, or frame recording automation logic ($FILE) to optimize workflow mechanics"
    elif [[ "$FILE" == "$TARGET_DIR/screenshots/"* ]]; then
        MSG="Documentation Update: Capturing high-resolution visual interface capture frames ($FILE) to demonstrate recent gameplay systems, UI overlays, and engine state progress"
    else
        MSG="Maintenance Update: Staging routine structural workspace synchronization protocols and tracking configurations for utility workspace file $FILE"
    fi

    echo "Staging file from root: $FILE"
    git add "$FILE"

    echo "Committing with detailed message: '$MSG'"
    git commit -m "$MSG"
    
    echo "----------------------------------------------------------------------"
done

# Push the final chain of individual commits to the repository remote
echo "Pushing all individual platformer commits sequentially generated to the remote repository branch..."
git push

