@echo off
title YouTube Downloader Windows - Portable Edition
echo.
echo ===============================================
echo    YouTube Downloader Windows - Portable
echo ===============================================
echo.
echo Setting up portable environment...
echo.

REM Get the directory where this batch file is located
set "APP_DIR=%~dp0"

REM Add ffmpeg to PATH for this session
set "PATH=%APP_DIR%ffmpeg;%PATH%"

echo Testing ffmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ ffmpeg is ready
) else (
    echo ✗ ffmpeg not found - audio merging may not work
)
echo.

echo Testing Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python is available
) else (
    echo ✗ Python not found - please install Python 3.7+
    echo   Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo.

echo Testing yt-dlp...
python -c "import yt_dlp" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ yt-dlp is available
) else (
    echo ✗ yt-dlp not found - installing...
    pip install yt-dlp
    if %errorlevel% neq 0 (
        echo Failed to install yt-dlp
        pause
        exit /b 1
    )
    echo ✓ yt-dlp installed successfully
)
echo.

echo ===============================================
echo    Starting YouTube Downloader...
echo ===============================================
echo.

REM Run the application
python "%APP_DIR%Youtube_Downloader_Windows.py"

echo.
echo Application closed.
pause
