@echo off
title GenX_FX System Monitor

:MONITOR_LOOP
cls
echo ========================================
echo   GenX_FX System Monitor
echo   %date% %time%
echo ========================================

REM Check Docker containers
echo.
echo CONTAINER STATUS:
echo ----------------
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | findstr genx

REM Check API health
echo.
echo API HEALTH CHECK:
echo -----------------
curl -s http://localhost:8081/health 2>nul | findstr "healthy" >nul
if errorlevel 1 (
    echo [ERROR] API not responding
) else (
    echo [OK] API healthy
)

REM Check recent signals
echo.
echo RECENT SIGNALS:
echo ---------------
curl -s http://localhost:8081/signals/live 2>nul | findstr "XAUUSD\|EURUSD" >nul
if errorlevel 1 (
    echo [WARNING] No recent signals
) else (
    echo [OK] Signals generating
)

REM System resources
echo.
echo SYSTEM RESOURCES:
echo -----------------
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | findstr genx

echo.
echo ========================================
echo Press 'Q' to quit, any other key to refresh...
echo ========================================

choice /c QR /n /t 30 /d R >nul
if errorlevel 2 goto MONITOR_LOOP
if errorlevel 1 goto END

:END
echo Monitor stopped.