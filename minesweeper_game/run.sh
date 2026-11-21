#!/bin/bash
set -e

# Change directory to script root
cd "$(dirname "$0")"

# Suppress macOS Tkinter deprecation warning
export TK_SILENCE_DEPRECATION=1

# Save terminal state
SAVED_STTY=$(stty -g 2>/dev/null || true)

cleanup() {
    if [ -n "$SAVED_STTY" ]; then
        stty "$SAVED_STTY" 2>/dev/null || true
    fi
    stty sane 2>/dev/null || true
}

# Trap termination signals
trap cleanup EXIT INT TERM QUIT TSTP

# Disable terminal interrupt keys while GUI is running so signals don't corrupt terminal
if [ -t 0 ]; then
    stty intr undef quit undef susp undef eof undef 2>/dev/null || true
fi

# Launch game
python3 main.py "$@"
