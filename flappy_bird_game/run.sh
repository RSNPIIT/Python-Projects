#!/bin/bash

# Change directory to script root
cd "$(dirname "$0")"

# Store original terminal state
SAVED_STTY=$(stty -g 2>/dev/null || true)

cleanup() {
    # Restore terminal state safely
    if [ -n "$SAVED_STTY" ]; then
        stty "$SAVED_STTY" 2>/dev/null || true
    fi
    stty sane 2>/dev/null || true
}

# Restore terminal on exit
trap cleanup EXIT

# Ignore interrupt, quit, and suspend signals in launcher
trap '' INT QUIT TSTP

# Disable terminal interrupt keys while GUI is running
if [ -t 0 ]; then
    stty intr undef quit undef susp undef eof undef 2>/dev/null || true
fi

# Detect Python interpreter with Pygame
PYTHON_EXEC=""
if [ -x "../venv/bin/python3" ]; then
    PYTHON_EXEC="../venv/bin/python3"
elif [ -x "./venv/bin/python3" ]; then
    PYTHON_EXEC="./venv/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_EXEC="python3"
else
    echo "Error: Python 3 was not found on your system."
    exit 1
fi

echo "==> Launching KFlapper (HD Edition) with $PYTHON_EXEC..."
"$PYTHON_EXEC" main.py "$@"
