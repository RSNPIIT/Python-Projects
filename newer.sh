#!/bin/bash

# Target directory relative to root
TARGET_DIR="panda_3D_shooting_game"

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' not found from this root path."
    exit 1
fi

echo "Scanning for modified and untracked changes inside $TARGET_DIR from root workspace..."

# Captures modified ( M), staged modifications (M ), and untracked (??) paths cleanly inside the Panda3D tree
git status --porcelain -uall "$TARGET_DIR" | grep -E '^(\?\?| M|M ) ' | sed 's/^...//' | while read -r FILE; do
    
    # Strip wrapping quotes if git outputs them for paths containing spaces/special chars
    FILE=$(echo "$FILE" | sed -e 's/^"//' -e 's/"$//')

    # Guard against directories, bytecode caches, or local virtual environments
    if [ -d "$FILE" ] || [[ "$FILE" == *__pycache__* ]] || [[ "$FILE" == *"$TARGET_DIR/venv/"* ]]; then
        continue
    fi

    # Dynamically structure granular, descriptive commit messages based on Panda3D layout paths
    if [[ "$FILE" == "$TARGET_DIR/mesh_builder.py" ]] || [[ "$FILE" == "$TARGET_DIR/map_manager.py" ]]; then
        MSG="Graphics Engineering: Optimizing 3D polygon vertex arrays, custom mesh builder algorithms, and geometric environmental node graph matrices for $FILE"
    elif [[ "$FILE" == "$TARGET_DIR/texture_generator.py" ]] || [[ "$FILE" == "$TARGET_DIR/textures/"* ]]; then
        MSG="Graphics Engineering: Deploying procedural texture generation assets, surface normal mapping, and hardware-accelerated materials tracking configurations for $FILE"
    elif [[ "$FILE" == "$TARGET_DIR/weapons.py" ]] || [[ "$FILE" == "$TARGET_DIR/player.py" ]] || [[ "$FILE" == "$TARGET_DIR/enemy.py" ]]; then
        MSG="Gameplay Mechanics: Implementing real-time weapon raycasting pipelines, state vectors, and spatial kinematics tracking routines for $FILE actor layers"
    elif [[ "$FILE" == "$TARGET_DIR/sound_manager.py" ]] || [[ "$FILE" == "$TARGET_DIR/audio_generator.py" ]] || [[ "$FILE" == "$TARGET_DIR/sounds/"* ]]; then
        MSG="Audio Subsystem: Integrating high-fidelity spatial audio waveforms, trigger cues, and sound manager playback looping states for $FILE hardware layers"
    elif [[ "$FILE" == "$TARGET_DIR/hud.py" ]] || [[ "$FILE" == "$TARGET_DIR/minimap.py" ]]; then
        MSG="User Interface: Architecting persistent screen space canvas overlays, dynamic radar minimap coordinates, and viewport aspect calculations for $FILE"
    elif [[ "$FILE" == "$TARGET_DIR/main.py" ]] || [[ "$FILE" == "$TARGET_DIR/particles.py" ]]; then
        MSG="Engine Lifecycle: Advancing global runtime execution loops, delta-time update pipelines, and particle effect subsystem configurations inside $FILE"
    else
        MSG="Maintenance Update: Staging routine structural workspace synchronization protocols and tracking configurations for utility project file $FILE"
    fi

    echo "Staging file from root: $FILE"
    git add "$FILE"

    echo "Committing with detailed message: '$MSG'"
    git commit -m "$MSG"
    
    echo "----------------------------------------------------------------------"
done

# Push the final chain of individual commits to the repository remote
echo "Pushing all individual Panda3D commits sequentially generated to the remote repository branch..."
git push

