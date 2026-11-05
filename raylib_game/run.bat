@echo off
setlocal
cd /d "%~dp0"

set "RECREATE=0"
if not exist ".venv\Scripts\python.exe" set "RECREATE=1"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -c "import sys" >nul 2>&1
  if errorlevel 1 set "RECREATE=1"
)

if "%RECREATE%"=="1" (
  echo Creating local Python environment...
  if exist ".venv" rmdir /s /q ".venv"
  python -m venv .venv
  if errorlevel 1 goto :error
)

".venv\Scripts\python.exe" -c "import raylib" >nul 2>&1
if errorlevel 1 (
  echo Installing raylib...
  ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
  if errorlevel 1 goto :error
)

".venv\Scripts\python.exe" main.py %*
goto :eof

:error
echo.
echo Could not start NOVA STRIKE. Install Python 3.10+ and try again.
pause
