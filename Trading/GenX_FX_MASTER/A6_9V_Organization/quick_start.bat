@echo off
echo ========================================
echo   GenX_FX Quick Start Launcher
echo ========================================

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not installed or not running
    echo Please install Docker Desktop first
    pause
    exit /b 1
)

REM Stop existing containers
echo Stopping existing containers...
docker stop genx-fx-enhanced genx-fx-working 2>nul

REM Start enhanced trading system
echo Starting GenX_FX Enhanced Trading System...
docker run -d --name genx-fx-enhanced -p 8081:8080 --restart unless-stopped -e GEMINI_API_KEY=AIzaSyDnjcaXnDpm1TzmIAV7EnoluI6w7wGBagM genx-enhanced

REM Wait for startup
echo Waiting for system to start...
timeout /t 10 /nobreak >nul

REM Check health
curl -s http://localhost:8081/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: System may not be ready yet
) else (
    echo SUCCESS: GenX_FX is running!
)

echo.
echo ========================================
echo   GenX_FX Started Successfully!
echo ========================================
echo.
echo Dashboard: http://localhost:8081
echo MT4 Signals: http://localhost:8081/MT4_Signals.csv
echo Live Signals: http://localhost:8081/signals/live
echo Health Check: http://localhost:8081/health
echo.
echo Press any key to open dashboard...
pause >nul
start http://localhost:8081