@echo off
echo ========================================
echo   GenX_FX Security & Status Check
echo ========================================

echo CREDENTIAL STATUS:
echo ------------------
if exist .env (
    echo [WARNING] .env file still present
) else (
    echo [OK] .env file removed/quarantined
)

if exist .env.leaked.* (
    echo [OK] Leaked files quarantined
) else (
    echo [INFO] No quarantined files found
)

echo.
echo GITHUB CLI STATUS:
echo ------------------
gh auth status 2>nul || echo [WARNING] GitHub CLI not authenticated

echo.
echo DOCKER STATUS:
echo --------------
docker --version 2>nul || echo [ERROR] Docker not available
docker compose version 2>nul || echo [WARNING] Docker Compose not available

echo.
echo CONTAINER STATUS:
echo -----------------
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | findstr -i "genx\|postgres\|redis\|NAMES"

echo.
echo DATABASE STATUS:
echo ----------------
docker logs genx-postgres 2>nul | findstr "ready to accept connections" >nul
if errorlevel 1 (
    echo [WARNING] PostgreSQL may not be ready
) else (
    echo [OK] PostgreSQL ready
)

echo.
echo SECURITY RECOMMENDATIONS:
echo -------------------------
echo 1. Revoke tokens at: https://github.com/settings/tokens
echo 2. Rotate API keys at broker dashboards
echo 3. Generate new credentials for production
echo 4. Never commit .env files to git

pause