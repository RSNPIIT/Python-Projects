# Define array of modified files
files=(
  "computer_vision_project/README.md"
  "computer_vision_project/apps/face_detection.py"
  "computer_vision_project/apps/finger_arithmetic.py"
  "computer_vision_project/apps/hand_plane.py"
  "computer_vision_project/assets/playground-poster.svg"
  "computer_vision_project/main.py"
)

# Custom commit messages mapped to each file
messages=(
  "docs(readme): update computer vision setup instructions and feature list"
  "fix(face-detection): resolve mediapipe paths and stabilize window constraints"
  "feat(finger-calc): integrate mathematical gesture parsing and logic matrix"
  "feat(hand-plane): implement spatial vertex calculation drawing tracking"
  "asset(poster): update visual rendering asset framework for playground poster"
  "refactor(main): consolidate interface operational routers for choice loop"
)

# Execution loop
for i in "${!files[@]}"; do
  file="${files[$i]}"
  msg="${messages[$i]}"
  
  if [ -f "$file" ]; then
    echo "---------------------------------------------"
    echo "Processing: $file"
    git add "$file"
    git commit -m "$msg"
    git push origin main
    sleep 1 # Cooldown buffer for timeline synchronization
  else
    echo "Skipping (file not found): $file"
  fi
done

echo "---------------------------------------------"
echo "✅ All 6 modifications pushed as individual commits!"

