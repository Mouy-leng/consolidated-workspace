@echo off
REM GenX_FX 24/7 Service Startup Script
REM This script starts the GenX_FX service manager for continuous operation

setlocal EnableDelayedExpansion

echo ========================================
echo GenX_FX 24/7 Service Manager
echo ========================================

REM Set working directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)

REM Check if service is already running
if exist "genx_service.pid" (
    set /p PID=<genx_service.pid
    tasklist /FI "PID eq !PID!" 2>nul | find /i "python.exe" >nul
    if !errorlevel! equ 0 (
        echo WARNING: GenX service appears to be already running (PID: !PID!)
        echo Do you want to stop it and restart? (Y/N)
        set /p CHOICE=
        if /i "!CHOICE!"=="Y" (
            echo Stopping existing service...
            python genx_24_7_service.py stop
            timeout /t 3 >nul
        ) else (
            echo Exiting...
            exit /b 0
        )
    )
)

REM Install required packages if needed
echo Checking dependencies...
python -c "import psutil, requests, schedule" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    python -m pip install psutil requests schedule
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

echo Starting GenX 24/7 Service Manager...

REM Create logs directory if it doesn't exist
if not exist "logs\service" mkdir "logs\service"

REM Start the service manager
python genx_24_7_service.py start

REM Check if service started successfully
timeout /t 3 >nul
if exist "genx_service.pid" (
    set /p PID=<genx_service.pid
    echo GenX service started successfully (PID: !PID!)
    echo Check logs\service\ for detailed logs
    echo Use 'python genx_24_7_service.py status' to check status
) else (
    echo ERROR: Failed to start GenX service
    echo Check logs for details
    pause
    exit /b 1
)

echo.
echo GenX_FX 24/7 Service is now running!
echo.
echo Management commands:
echo   python genx_24_7_service.py status   - Check service status
echo   python genx_24_7_service.py stop     - Stop all services
echo   python genx_24_7_service.py restart  - Restart all services
echo.

pause