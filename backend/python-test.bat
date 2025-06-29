@echo off
echo 🔍 Python Detection Test for Aterges
echo ====================================
echo.

echo Your other app shows Python 3.13.3 is installed.
echo Let's find out how to access it:
echo.

echo Testing: python --version
python --version 2>nul
if not errorlevel 1 (
    echo ✅ 'python' command works!
    set WORKING_CMD=python
    goto :found
)
echo ❌ 'python' command not found

echo.
echo Testing: py --version
py --version 2>nul
if not errorlevel 1 (
    echo ✅ 'py' command works!
    set WORKING_CMD=py
    goto :found
)
echo ❌ 'py' command not found

echo.
echo Testing: python3 --version
python3 --version 2>nul
if not errorlevel 1 (
    echo ✅ 'python3' command works!
    set WORKING_CMD=python3
    goto :found
)
echo ❌ 'python3' command not found

echo.
echo ❌ None of the standard Python commands work in this terminal.
echo 📋 Your Python 3.13.3 is installed but not in PATH.
echo.
echo 🔧 SOLUTIONS:
echo 1. Add Python to PATH in Windows Environment Variables
echo 2. Or find where Python is installed and use full path
echo 3. Or reinstall Python with "Add to PATH" checked
echo.
goto :end

:found
echo.
echo ✅ SUCCESS! Use this command: %WORKING_CMD%
echo.
echo 🚀 Now let's start your Aterges backend:
echo.
%WORKING_CMD% --version
echo.

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment with %WORKING_CMD%...
    %WORKING_CMD% -m venv venv
)

echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

echo 📚 Installing dependencies...
pip install -r requirements.txt

echo 🎯 Starting Aterges Backend Server...
echo    API: http://localhost:8000
echo    Docs: http://localhost:8000/docs
echo.
python main.py

:end
pause
