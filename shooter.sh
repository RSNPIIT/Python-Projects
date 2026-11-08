# Define the files for the Panda3D game
files=(
  "panda_3D_shooting_game/README.md"
  "panda_3D_shooting_game/hud.py"
  "panda_3D_shooting_game/main.py"
  "panda_3D_shooting_game/map_manager.py"
  "panda_3D_shooting_game/player.py"
  "panda_3D_shooting_game/weapons.py"
  "panda_3D_shooting_game/run.sh"
)

# Individual commit messages mapping their specific changes
messages=(
  "docs(panda3d-game): update game mechanics description in readme"
  "feat(hud): upgrade heads-up display rendering metrics and overlays"
  "refactor(main): optimize main window loop and core engine systems"
  "feat(map): enhance map collision geometry and asset instantiation"
  "fix(player): tune player movement mechanics and boundary checks"
  "feat(weapons): calibrate weapon firing rates and ballistic tracking"
  "chore(scripts): introduce convenient runtime execution script shell"
)

# Loop to push one file at a time
for i in "${!files[@]}"; do
  file="${files[$i]}"
  msg="${messages[$i]}"
  
  if [ -f "$file" ]; then
    echo "---------------------------------------------"
    echo "Staging: $file"
    git add "$file"
    git commit -m "$msg"
    git push origin main
    sleep 1  # 1-second cooldown buffer
  else
    echo "Skipping: $file (not found)"
  fi
done

echo "---------------------------------------------"
echo "✅ All 7 components processed and pushed individually!"

