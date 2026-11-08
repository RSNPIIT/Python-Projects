#!/usr/bin/env bash
# Launch PRISM CALC using a Python 3 interpreter with modern Tcl/Tk (>= 8.6).
# Ignores Ctrl+C, Ctrl+X, Ctrl+D, Ctrl+\, and Ctrl+Z in the terminal while running.
trap '' INT QUIT TSTP

cd "$(dirname "$0")" || exit 1

export TK_SILENCE_DEPRECATION=1

has_modern_tk() {
  local py="$1"
  [ -n "$py" ] || return 1
  command -v "$py" >/dev/null 2>&1 || [ -x "$py" ] || return 1
  "$py" -c "import tkinter as tk; raise SystemExit(0 if float(tk.TkVersion) >= 8.6 else 1)" >/dev/null 2>&1
}

CANDIDATES=(
  "python3"
  "/opt/homebrew/bin/python3"
  "/opt/homebrew/opt/python@3.14/bin/python3.14"
  "/opt/homebrew/opt/python@3.13/bin/python3.13"
  "/opt/homebrew/opt/python@3.12/bin/python3.12"
  "/usr/local/bin/python3"
  "/Library/Frameworks/Python.framework/Versions/Current/bin/python3"
)

SELECTED_PY=""
for py in "${CANDIDATES[@]}"; do
  if has_modern_tk "$py"; then
    SELECTED_PY="$py"
    break
  fi
done

if [ -z "$SELECTED_PY" ] && command -v brew >/dev/null 2>&1; then
  BREW_PREFIX="$(brew --prefix 2>/dev/null || echo /opt/homebrew)"
  BREW_PY=""
  for cand in "${BREW_PREFIX}/bin/python3" \
              "${BREW_PREFIX}/opt/python@3.14/bin/python3.14" \
              "${BREW_PREFIX}/opt/python@3.13/bin/python3.13" \
              "${BREW_PREFIX}/opt/python@3.12/bin/python3.12" \
              "python3"; do
    if [ -x "$cand" ] || command -v "$cand" >/dev/null 2>&1; then
      REAL_EXE=$("$cand" -c "import sys; print(sys.executable)" 2>/dev/null || echo "")
      if [[ "$REAL_EXE" != "/usr/bin/"* && "$REAL_EXE" != "/Library/Developer/"* ]]; then
        BREW_PY="$cand"
        break
      fi
    fi
  done

  if [ -z "$BREW_PY" ]; then
    echo "✦ Installing Homebrew Python + python-tk (one-time setup)..."
    brew install python python-tk
    BREW_PY="${BREW_PREFIX}/bin/python3"
  else
    PY_VER=$("$BREW_PY" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "")
    echo "✦ Installing modern Tkinter (python-tk@${PY_VER}) via Homebrew (one-time setup)..."
    brew install "python-tk@${PY_VER}" || brew install python-tk
  fi

  for py in "$BREW_PY" "${CANDIDATES[@]}"; do
    if has_modern_tk "$py"; then
      SELECTED_PY="$py"
      break
    fi
  done
fi

if [ -z "$SELECTED_PY" ]; then
  echo "Error: Could not find Python 3 with modern Tcl/Tk (>= 8.6)." >&2
  echo "Install it on macOS with:  brew install python python-tk" >&2
  exit 1
fi

SAVED_STTY=""
if [ -t 0 ]; then
  SAVED_STTY=$(stty -g 2>/dev/null || true)
  cleanup_tty() {
    "$SELECTED_PY" -c "import sys, termios; termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)" 2>/dev/null || true
    if [ -n "$SAVED_STTY" ]; then
      stty "$SAVED_STTY" 2>/dev/null || true
    fi
  }
  trap cleanup_tty EXIT
  stty -echo -icanon -isig intr undef quit undef eof undef susp undef dsusp undef 2>/dev/null || true
fi

"$SELECTED_PY" main.py "$@"
