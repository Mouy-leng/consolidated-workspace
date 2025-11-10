@echo off
echo ========================================
echo   GenX_FX System Restart
echo ========================================

echo Stopping all GenX_FX containers...
docker stop genx-fx-enhanced genx-fx-working genx-fx-production 2>nul
docker rm genx-fx-enhanced genx-fx-working genx-fx-production 2>nul

echo Cleaning up unused containers...
docker container prune -f >nul 2>&1

echo Restarting enhanced trading system...
docker run -d --name genx-fx-enhanced -p 8081:8080 --restart unless-stopped -e GEMINI_API_KEY=AIzaSyDnjcaXnDpm1TzmIAV7EnoluI6w7wGBagM genx-enhanced

echo Waiting for startup...
timeout /t 15 /nobreak >nul

REM Health check
curl -s http://localhost:8081/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: System may still be starting...
    echo Check logs: docker logs genx-fx-enhanced
) else (
    echo SUCCESS: System restarted successfully!
    echo Dashboard: http://localhost:8081
)

pause