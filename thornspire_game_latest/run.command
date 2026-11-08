#!/bin/zsh
# Double-click on macOS to play THORNSPIRE.
cd "$(dirname "$0")" || exit 1
export PYGAME_HIDE_SUPPORT_PROMPT=1
exec ./run.sh "$@"
