@echo off
title GenX_FX Complete Setup

echo ========================================
echo   GenX_FX Complete Setup Wizard
echo ========================================

REM Check prerequisites
echo Step 1: Checking prerequisites...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not found. Please install Docker Desktop first.
    echo Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+ first.
    pause
    exit /b 1
)

echo [OK] Prerequisites check passed

REM Setup environment
echo.
echo Step 2: Setting up environment...
if not exist .env (
    echo Creating .env from template...
    copy .env.template .env >nul
    echo Please edit .env file with your credentials
    notepad .env
    pause
)

REM Build Docker image
echo.
echo Step 3: Building Docker image...
docker build -f Dockerfile.enhanced -t genx-enhanced . || (
    echo ERROR: Docker build failed
    pause
    exit /b 1
)

REM Create directories
echo.
echo Step 4: Creating directories...
mkdir logs 2>nul
mkdir signal_output 2>nul
mkdir backups 2>nul

REM Start services
echo.
echo Step 5: Starting services...
docker stop genx-fx-enhanced 2>nul
docker rm genx-fx-enhanced 2>nul
docker run -d --name genx-fx-enhanced -p 8081:8080 --restart unless-stopped --env-file .env genx-enhanced

REM Wait and test
echo.
echo Step 6: Testing system...
timeout /t 15 /nobreak >nul

curl -s http://localhost:8081/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: System may still be starting...
    echo Run 'status.bat' to check system status
) else (
    echo SUCCESS: GenX_FX setup complete!
)

REM Create desktop shortcuts
echo.
echo Step 7: Creating shortcuts...
echo @echo off > "%USERPROFILE%\Desktop\GenX_FX_Dashboard.bat"
echo start http://localhost:8081 >> "%USERPROFILE%\Desktop\GenX_FX_Dashboard.bat"

echo @echo off > "%USERPROFILE%\Desktop\GenX_FX_Status.bat"
echo cd /d "%CD%" >> "%USERPROFILE%\Desktop\GenX_FX_Status.bat"
echo status.bat >> "%USERPROFILE%\Desktop\GenX_FX_Status.bat"

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Dashboard: http://localhost:8081
echo MT4 Signals: http://localhost:8081/MT4_Signals.csv
echo.
echo Desktop shortcuts created:
echo - GenX_FX_Dashboard.bat
echo - GenX_FX_Status.bat
echo.
echo Next steps:
echo 1. Check system status: status.bat
echo 2. Monitor system: monitor_system.bat
echo 3. View logs: view_logs.bat
echo.
pause