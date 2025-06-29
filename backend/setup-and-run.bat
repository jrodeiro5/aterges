@echo off
echo 🔍 Checking Python installation...

REM Check if Python is available
python --version >nul 2>&1
if not errorlevel 1 (
    echo ✅ Python is installed:
    python --version
    echo.
    goto :start_server
)

REM Check if py launcher is available (common on Windows)
py --version >nul 2>&1
if not errorlevel 1 (
    echo ✅ Python is installed via py launcher:
    py --version
    echo.
    echo 🔄 Using 'py' command instead of 'python'...
    goto :start_server_py
)

REM Python not found
echo ❌ Python is not installed or not in PATH.
echo.
echo 📦 Please install Python 3.13+ from:
echo    https://www.python.org/downloads/
echo.
echo ⚠️  IMPORTANT: Check "Add Python to PATH" during installation
echo.
echo 🔄 After installation:
echo    1. Restart this terminal
echo    2. Run this script again
echo.
pause
exit /b 1

:start_server
echo 🚀 Starting Aterges Backend with python command...
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat
echo 📚 Installing dependencies...
pip install -r requirements.txt
if not exist ".env" (
    echo ⚠️  .env file not found. Using existing configuration...
)
echo 🎯 Starting FastAPI development server...
echo    API available at: http://localhost:8000
echo    API docs at: http://localhost:8000/docs
echo.
python main.py
goto :end

:start_server_py
echo 🚀 Starting Aterges Backend with py command...
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    py -m venv venv
)
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat
echo 📚 Installing dependencies...
pip install -r requirements.txt
if not exist ".env" (
    echo ⚠️  .env file not found. Using existing configuration...
)
echo 🎯 Starting FastAPI development server...
echo    API available at: http://localhost:8000
echo    API docs at: http://localhost:8000/docs
echo.
python main.py

:end
