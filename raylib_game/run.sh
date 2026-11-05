#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if [ ! -x ".venv/bin/python" ] || ! .venv/bin/python -c "import sys" >/dev/null 2>&1; then
  echo "Creating local Python environment..."
  rm -rf .venv
  "$PYTHON_BIN" -m venv .venv
fi

if ! .venv/bin/python -c "import raylib" >/dev/null 2>&1; then
  echo "Installing raylib..."
  .venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt
fi

exec .venv/bin/python main.py "$@"
