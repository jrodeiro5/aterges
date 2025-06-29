@echo off
REM Debug script to test signup functionality
echo 🧪 Testing Aterges Signup Functionality...

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    echo    Make sure you're in the backend directory
    pause
    exit /b 1
)

REM Run the debug test
echo 🔍 Running signup debug test...
python test_signup_debug.py

echo.
echo ✅ Debug test completed.
pause
