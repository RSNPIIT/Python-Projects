#!/bin/bash
# ==============================================================================
# REIMAGINED TETRIS // Cyber Matrix - Launcher
# Terminal Guard: Ignores Ctrl+C, Ctrl+X, Ctrl+D while running
# ==============================================================================

# Lock terminal against Ctrl+C, Ctrl+X, Ctrl+D
trap '' SIGINT SIGQUIT SIGTSTP

# Save initial terminal settings
SAVED_STTY=""
if [ -t 0 ]; then
    SAVED_STTY=$(stty -g 2>/dev/null || true)
    # Disable interrupt characters while running
    stty intr undef quit undef susp undef eof undef 2>/dev/null || true
fi

# Cleanup hook on exit
cleanup() {
    if [ -n "$SAVED_STTY" ]; then
        stty "$SAVED_STTY" 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Suppress Pygame-CE startup message
export PYGAME_HIDE_SUPPORT_PROMPT=1

# Resolve script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Locate python in virtual environment
PYTHON_BIN=""
if [ -f "$DIR/../venv/bin/python" ]; then
    PYTHON_BIN="$DIR/../venv/bin/python"
elif [ -f "$DIR/venv/bin/python" ]; then
    PYTHON_BIN="$DIR/venv/bin/python"
elif [ -n "$VIRTUAL_ENV" ] && [ -f "$VIRTUAL_ENV/bin/python" ]; then
    PYTHON_BIN="$VIRTUAL_ENV/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
else
    PYTHON_BIN="python"
fi

# Run the game
"$PYTHON_BIN" main.py "$@"
