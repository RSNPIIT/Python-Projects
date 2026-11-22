#!/usr/bin/env zsh
set -euo pipefail

# Parse git status for all modified and untracked files across the repo
git status --porcelain -uall | while IFS= read -r line; do
  status_code="${line:0:2}"
  file="${line:3}"

  # Skip the script itself, cache, and system files
  [[ "$file" == "sheller.sh" || "$file" == *__pycache__* || "$file" == *.pyc || "$file" == *.wav || "$file:t" == .DS_Store ]] && continue

  # Pick action verb based on git status (?? = untracked/new, otherwise modified)
  if [[ "$status_code" == "??" ]]; then
    action="add"
  else
    action="update"
  fi

  # Pick Conventional Commit prefix
  case "$file" in
    *.png|*.jpg) prefix="assets" ;;
    *tests/*)    prefix="test" ;;
    *.md)        prefix="docs" ;;
    *.sh)        prefix="build" ;;
    *)           prefix="feat" ;;
  esac

  echo "🚀 Pushing ($action): $file"
  git add "$file"
  git commit -m "${prefix}: ${action} ${file}"
  git push origin main
done

echo "✅ All modified and new files committed and pushed!"
