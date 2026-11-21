#!/bin/bash
set -e

# Change directory to the script's root directory
cd "$(dirname "$0")"

# Store current terminal attributes
SAVED_STTY=$(stty -g 2>/dev/null || true)

cleanup() {
    # Restore terminal attributes cleanly
    if [ -n "$SAVED_STTY" ]; then
        stty "$SAVED_STTY" 2>/dev/null || true
    fi
    stty sane 2>/dev/null || true
    # Restore normal cursor and alternate screen buffer if ncurses left it active
    tput cnorm 2>/dev/null || true
    tput rmcup 2>/dev/null || true
}

# Trap signals to prevent terminal corruption
trap cleanup EXIT INT TERM QUIT TSTP

# Build the project
echo "==> Compiling Pong OOP (Pure C)..."
make -j4

# Disable interrupt keys (Ctrl+C, Ctrl+\, Ctrl+Z, Ctrl+D) during game execution
# so in-game input handling takes full precedence
if [ -t 0 ]; then
    stty intr undef quit undef susp undef eof undef 2>/dev/null || true
fi

# Launch the game binary
./bin/pong_c_oop "$@"
