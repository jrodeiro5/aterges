@echo off
echo 🚀 Starting Aterges Backend (Smart Setup)
echo.

REM Try to start with current dependencies
echo 🔧 Testing current configuration...
python test-config.py >nul 2>&1
if errorlevel 1 (
    echo ❌ Configuration test failed
    goto :end
)

echo ✅ Configuration OK

REM Try to import the auth models to check for missing dependencies
echo 🔍 Checking dependencies...
python -c "from auth.models import UserSignup" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Missing email-validator dependency
    echo 📦 Installing email-validator...
    pip install pydantic[email] email-validator
    if errorlevel 1 (
        echo ❌ Failed to install email-validator
        echo 🔄 Using simplified models without email validation...
        copy auth\models_simple.py auth\models.py
    )
)

echo ✅ Dependencies ready

echo 🎯 Starting Aterges Backend Server...
echo    API: http://localhost:8000
echo    Docs: http://localhost:8000/docs
echo    Health: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py

:end
pause
