#!/bin/bash
cd "$(dirname "$0")"
# Prefer the polished, terminal-free app bundle.
if [ -d "NOVA STRIKE.app" ]; then
  open "NOVA STRIKE.app"
  exit 0
fi
exec ./run.sh
