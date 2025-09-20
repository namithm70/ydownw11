@echo off
title YouTube Downloader Windows - Dependency Installer
echo.
echo ===============================================
echo    YouTube Downloader Windows - Installer
echo ===============================================
echo.
echo This will install required Python packages for the YouTube Downloader.
echo.
echo Checking Python installation...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo ✓ Python is installed
echo.

echo Installing required packages...
echo.

echo Installing yt-dlp...
pip install yt-dlp
if %errorlevel% neq 0 (
    echo ERROR: Failed to install yt-dlp
    pause
    exit /b 1
)
echo ✓ yt-dlp installed successfully
echo.

echo ===============================================
echo    Installation Complete!
echo ===============================================
echo.
echo You can now run "Launch YouTube Downloader.bat" to start the application.
echo.
pause
