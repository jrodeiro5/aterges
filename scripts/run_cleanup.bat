@echo off
echo 🧹 ATERGES REPOSITORY CLEANUP
echo ============================
echo.
echo ⚠️  WARNING: This script will move and reorganize files!
echo Make sure you have committed any important changes first.
echo.
echo This cleanup will:
echo   📁 Create organized directory structure
echo   📚 Move documentation to docs/
echo   🔧 Move scripts to scripts/
echo   ⚙️ Move config files to config/
echo   🔒 Remove sensitive files (with confirmation)
echo   🧹 Clean backup files
echo   📖 Update README.md
echo.
pause

python cleanup_repository_interactive.py

echo.
echo ✅ Cleanup complete!
pause
