@echo off
echo 🔍 Aterges Backend System Check
echo ================================
echo.

echo 📋 Checking your system for Aterges backend requirements...
echo.

REM Check Node.js (already installed)
echo ✅ Node.js:
node --version
npm --version
echo.

REM Check Python installations
echo 🐍 Python Check:
echo ----------------

python --version >nul 2>&1
if not errorlevel 1 (
    echo ✅ python command available:
    python --version
    goto :python_ok
)

py --version >nul 2>&1
if not errorlevel 1 (
    echo ✅ py launcher available:
    py --version
    goto :python_ok
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    echo ✅ python3 command available:
    python3 --version
    goto :python_ok
)

echo ❌ Python is NOT installed
echo.
echo 📦 NEXT STEPS:
echo 1. Install Python from: https://www.python.org/downloads/
echo 2. ⚠️  CHECK "Add Python to PATH" during installation
echo 3. Restart terminal and run 'dev.bat'
echo.
goto :end

:python_ok
echo.
echo 🎯 SYSTEM READY! You can now run:
echo    dev.bat          - Start the backend server
echo    setup-and-run.bat - Alternative startup script
echo.

:end
pause
