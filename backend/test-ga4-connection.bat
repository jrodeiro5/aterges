@echo off
echo ============================================
echo Testing Aterges GA4 Connection
echo ============================================
echo.

cd /d "C:\Users\jrodeiro\Desktop\aterges\backend"

echo Running configuration and GA4 tests...
echo.

python test_phase1.py

echo.
echo ============================================
echo Test completed!
echo ============================================
echo.
echo If you see errors, check:
echo 1. GA4 property permissions for service account
echo 2. Google Cloud APIs are enabled
echo 3. Internet connection
echo.
pause
