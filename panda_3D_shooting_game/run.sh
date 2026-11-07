#!/usr/bin/env bash
set -euo pipefail

GAME_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Reuse either common virtualenv name; create one on a clean checkout.
if [[ -x "$GAME_DIR/.venv/bin/python3" ]]; then
    PYTHON_BIN="$GAME_DIR/.venv/bin/python3"
elif [[ -x "$GAME_DIR/venv/bin/python3" ]]; then
    PYTHON_BIN="$GAME_DIR/venv/bin/python3"
else
    if ! command -v python3 >/dev/null 2>&1; then
        echo "Python 3 is required. Install Python 3, then run ./run.sh again." >&2
        exit 1
    fi
    python3 -m venv "$GAME_DIR/.venv"
    PYTHON_BIN="$GAME_DIR/.venv/bin/python3"
fi

if ! "$PYTHON_BIN" -c 'import panda3d, simplepbr' >/dev/null 2>&1; then
    echo "Installing game dependencies into the project virtual environment..."
    "$PYTHON_BIN" -m pip install -r "$GAME_DIR/requirements.txt"
fi

cd "$GAME_DIR"
exec "$PYTHON_BIN" "$GAME_DIR/main.py" "$@"
