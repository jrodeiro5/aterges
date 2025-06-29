@echo off
title Aterges Repository Manager
echo 🚀 ATERGES REPOSITORY MANAGER
echo =============================
echo.
echo Welcome! This tool helps you manage your repository size and organization.
echo.
echo Current repository size issue: 76.27 MiB (too large!)
echo Target: Less than 10 MiB for optimal performance
echo.
echo Available tools:
echo   📊 Health Dashboard - Check current status
echo   🧹 Cleanup Tool - Organize and reduce size
echo   📈 Size Analysis - Detailed breakdown
echo   🔧 Git LFS Setup - Handle large files
echo   📚 Best Practices - Documentation
echo.
pause

python repository_manager.py

echo.
echo Thanks for using Aterges Repository Manager!
pause
