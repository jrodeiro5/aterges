@echo off
echo ============================================
echo Detailed GA4 Connection Diagnostics
echo ============================================
echo.

cd /d "C:\Users\jrodeiro\Desktop\aterges\backend"

echo Running detailed GA4 diagnostics...
echo.

python diagnose_ga4.py

echo.
echo ============================================
echo Diagnostic completed!
echo ============================================
pause
