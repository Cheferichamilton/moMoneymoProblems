@echo off

REM Budget Buddy Zero-Step Launcher for Windows



REM Change to the script directory

cd /d %~dp0



REM Check for Python 3

where python >nul 2>&1

IF ERRORLEVEL 1 (

  echo Python not found. Please install Python 3.7+ and add to PATH.

  pause

  exit /b 1

)



REM Create virtual environment (if missing)

IF NOT EXIST venv (

  echo Creating virtual environment...

  python -m venv venv

)



REM Activate venv

echo Activating virtual environment...

call venv\Scripts\activate.bat



REM Install dependencies

echo Installing dependencies...

pip install --upgrade pip

pip install -r requirements.txt



REM Launch Streamlit app

echo Launching Budget Buddy...

python -m streamlit run run.py



REM Keep window open

echo.

echo Press any key to exit...

pause >nul