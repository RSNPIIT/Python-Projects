#!/bin/zsh
# Double-click on macOS to play THORNSPIRE.
cd "$(dirname "$0")" || exit 1
if [ ! -x ".venv/bin/python" ]; then
  echo "Setting up Python environment..."
  python3 -m venv .venv || exit 1
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -r requirements.txt || exit 1
fi
exec .venv/bin/python main.py "$@"
