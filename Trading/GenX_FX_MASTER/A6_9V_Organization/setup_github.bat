@echo off
echo ========================================
echo A6_9V ORGANIZATION - GITHUB INTEGRATION
echo ========================================
echo Organization: A6_9V
echo Repository: GenX_FX
echo Branch: main
echo ========================================

echo.
echo [1/3] Setting up A6_9V organization...
cd /d "D:\GenX_FX\A6_9V_Organization"

echo.
echo [2/3] Running GitHub integration...
python github_integration.py
if %errorlevel% neq 0 (
    echo ERROR: GitHub integration failed
    pause
    exit /b 1
)

echo.
echo [3/3] A6_9V Organization GitHub integration complete!
echo.
echo A6_9V Organization Status:
echo - Organization: A6_9V
echo - Repository: GenX_FX
echo - Branch: main
echo - Status: ACTIVE
echo - GitHub Integration: ENABLED
echo - Auto-deployment: ENABLED
echo.
echo Press any key to continue...
pause
