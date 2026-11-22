#!/usr/bin/env zsh
set -euo pipefail

TARGET_DIR="${1:-kapman_game}"

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "❌ Directory '$TARGET_DIR' not found."
  exit 1
fi

for file in "$TARGET_DIR"/**/*(.N); do
  [[ "$file" == *__pycache__* || "$file" == *.pyc || "$file" == *.wav || "$file:t" == .DS_Store ]] && continue
  git check-ignore -q "$file" && continue

  case "$file" in
    *.png|*.jpg) prefix="assets" ;;
    *tests/*)    prefix="test" ;;
    *.md)        prefix="docs" ;;
    *.sh)        prefix="build" ;;
    *)           prefix="feat" ;;
  esac

  echo "🚀 Pushing: $file"
  git add "$file"
  git commit -m "${prefix}: add ${file#$TARGET_DIR/}"
  git push origin main
done

echo "✅ All valid files in '$TARGET_DIR' committed and pushed!"
