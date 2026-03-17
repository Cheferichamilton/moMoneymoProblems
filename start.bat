@echo off
REM ------------------------------
REM Budget Buddy Launcher for Windows
REM ------------------------------

:: Check for Python executable
where python >nul 2>&1
IF ERRORLEVEL 1 (
  echo Python not found. Please install Python 3.7+ and check "Add Python to PATH".
  pause
  exit /b 1
)

:: Create virtual environment if missing
IF NOT EXIST venv (
  echo Creating virtual environment...
  python -m venv venv
  echo Activating venv and installing dependencies...
  call venv\Scripts\activate.bat
  pip install --upgrade pip
  pip install .
) ELSE (
  echo Activating virtual environment...
  call venv\Scripts\activate.bat
)

echo Launching Budget Buddy...
python -m budgetbuddy.cli

echo.
echo Press any key to exit...
pause >nul
