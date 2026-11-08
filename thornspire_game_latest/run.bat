@echo off
rem Windows launcher for THORNSPIRE
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Setting up Python environment...
  python -m venv .venv || exit /b 1
  .venv\Scripts\python.exe -m pip install -q --upgrade pip
  .venv\Scripts\python.exe -m pip install -q -r requirements.txt || exit /b 1
)
set PYGAME_HIDE_SUPPORT_PROMPT=1
.venv\Scripts\python.exe main.py %*
