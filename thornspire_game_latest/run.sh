#!/usr/bin/env bash
# Start THORNSPIRE (creates .venv on first run, boots straight into the game).
# Block/ignore Ctrl+C (INT), Ctrl+\ (QUIT), and Ctrl+Z (TSTP) while running.
trap '' INT QUIT TSTP

cd "$(dirname "$0")" || exit 1

SAVED_STTY=""
if [ -t 0 ]; then
  SAVED_STTY=$(stty -g 2>/dev/null || true)
  cleanup_tty() {
    if [ -x ".venv/bin/python" ]; then
      .venv/bin/python -c "import sys, termios; termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)" 2>/dev/null || true
    fi
    if [ -n "$SAVED_STTY" ]; then
      stty "$SAVED_STTY" 2>/dev/null || true
    fi
  }
  trap cleanup_tty EXIT
  stty -echo -icanon -isig intr undef quit undef eof undef susp undef dsusp undef 2>/dev/null || true
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "Setting up Python environment..."
  python3 -m venv .venv || exit 1
  .venv/bin/python -m pip install -q --upgrade pip
  .venv/bin/python -m pip install -q -r requirements.txt || exit 1
fi

export PYGAME_HIDE_SUPPORT_PROMPT=1
export SDL_HINT_NO_SIGNAL_HANDLERS=1
.venv/bin/python main.py "$@"
