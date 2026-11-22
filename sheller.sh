#!/usr/bin/env zsh
set -euo pipefail

# 1. Ensure .gitignore ignores Python cache & macOS files
if [[ ! -f .gitignore ]] || ! grep -q "__pycache__" .gitignore; then
  printf "__pycache__/\n*.py[cod]\n.DS_Store\n" >> .gitignore
  git add .gitignore
  git commit -m "chore: ignore Python cache and macOS files"
  git push origin main
fi

# 2. Loop through every valid file in flappy_bird_game
for file in flappy_bird_game/**/*(.N); do
  # Skip cache, system files, .wav files, and anything else in .gitignore
  [[ "$file" == *__pycache__* || "$file" == *.pyc || "$file" == *.wav || "$file:t" == .DS_Store ]] && continue
  git check-ignore -q "$file" && continue

  # Pick a clean Conventional Commit prefix based on file type
  case "$file" in
    *.png|*.jpg) prefix="assets" ;;
    *tests/*)    prefix="test" ;;
    *.md)        prefix="docs" ;;
    *.sh)        prefix="build" ;;
    *)           prefix="feat" ;;
  esac

  echo "🚀 Pushing: $file"
  git add "$file"
  git commit -m "${prefix}: add ${file#flappy_bird_game/}"
  git push origin main
done

echo "✅ All valid files committed and pushed!"

