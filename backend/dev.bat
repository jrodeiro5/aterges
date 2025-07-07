@echo off
REM Aterges Backend Development Setup Script
REM Run this script to set up and start the backend server

echo 🚀 Starting Aterges Backend Development Server...

REM Check multiple Python installation methods
python --version >nul 2>&1
if not errorlevel 1 goto :python_found

py --version >nul 2>&1
if not errorlevel 1 goto :py_found

python3 --version >nul 2>&1
if not errorlevel 1 goto :python3_found

REM Python not found - provide installation help
echo ❌ Python is not installed or not in PATH.
echo.
echo 📦 TO INSTALL PYTHON:
echo    1. Go to: https://www.python.org/downloads/
echo    2. Download Python 3.13+ for Windows
echo    3. ⚠️  IMPORTANT: Check "Add Python to PATH" during installation
echo    4. Restart this terminal after installation
echo    5. Run this script again
echo.
echo 🔄 Alternative: Install from Microsoft Store
echo    1. Open Microsoft Store
echo    2. Search for "Python 3.13"
echo    3. Install the official Python package
echo.
pause
exit /b 1

:python_found
echo ✅ Python found:
python --version
set PYTHON_CMD=python
goto :setup

:py_found
echo ✅ Python found via py launcher:
py --version
set PYTHON_CMD=py
goto :setup

:python3_found
echo ✅ Python found as python3:
python3 --version
set PYTHON_CMD=python3
goto :setup

:setup
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found. Please ensure you have a .env file with your configuration.
    echo    You can copy .env.example and fill in your values.
    echo    Or the .env file should have been created automatically.
    pause
)

REM Start the development server
echo 🎯 Starting FastAPI development server...
echo    API will be available at: http://localhost:8000
echo    API docs will be available at: http://localhost:8000/docs
echo    Health check: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

python main_robust.py
