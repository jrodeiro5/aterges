@echo off
echo.
echo 🚀 Supabase Vault BYOK Setup
echo ================================
echo.

REM Check if .env.local exists
if not exist ".env.local" (
    echo ❌ Error: .env.local file not found!
    echo Please make sure you're in the project root directory.
    pause
    exit /b 1
)

REM Check if service role key is already set
findstr /c:"SUPABASE_SERVICE_ROLE_KEY=" .env.local >nul
if %errorlevel% equ 0 (
    echo ✅ SUPABASE_SERVICE_ROLE_KEY is already configured!
    echo.
) else (
    echo ⚠️  SUPABASE_SERVICE_ROLE_KEY is not yet configured.
    echo.
    echo To complete the setup:
    echo 1. Go to your Supabase Dashboard
    echo 2. Navigate to Settings → API
    echo 3. Copy the 'service_role' key
    echo 4. Add it to your .env.local file:
    echo.
    echo    SUPABASE_SERVICE_ROLE_KEY="your_service_role_key_here"
    echo.
    
    set /p "addkey=Do you want to add it now? (y/n): "
    
    if /i "%addkey%"=="y" (
        echo.
        set /p "service_key=Paste your service role key: "
        
        if not "!service_key!"=="" (
            echo. >> .env.local
            echo # Supabase Service Role Key (for Vault API operations) >> .env.local
            echo SUPABASE_SERVICE_ROLE_KEY="!service_key!" >> .env.local
            echo.
            echo ✅ Service role key added successfully!
        ) else (
            echo ❌ No key provided. Please add it manually to .env.local
        )
    )
)

echo.
echo 🧪 Testing Setup...
echo ================================

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Node.js found
) else (
    echo ❌ Node.js not found. Please install Node.js to continue.
    pause
    exit /b 1
)

REM Check if dependencies are installed
if exist "node_modules" (
    echo ✅ Dependencies installed
) else (
    echo ⚠️  Dependencies not found. Installing...
    npm install
)

echo.
echo 🚀 Setup Instructions:
echo ================================
echo 1. Start the development server:
echo    npm run dev
echo.
echo 2. Test the vault integration:
echo    Visit: http://localhost:3000/test-vault
echo.
echo 3. Use the integrations page:
echo    Visit: http://localhost:3000/app/integrations
echo.
echo ✅ Supabase Vault BYOK is ready!
echo.
echo 📚 Documentation:
echo    - docs/VAULT_IMPLEMENTATION_COMPLETE.md
echo    - docs/supabase-vault-byok-implementation.md
echo.
pause
