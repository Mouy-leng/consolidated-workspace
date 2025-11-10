@echo off
echo ========================================
echo   Security Hardening Checklist
echo ========================================

echo Checking .env security...
if exist .env (
    echo [CHECK] .env file exists
    findstr /C:".env" .gitignore >nul
    if errorlevel 1 (
        echo [FAIL] .env not in .gitignore
    ) else (
        echo [PASS] .env properly ignored
    )
) else (
    echo [WARN] .env file not found
)

echo.
echo Checking GitHub CLI...
gh auth status >nul 2>&1
if errorlevel 1 (
    echo [FAIL] GitHub CLI not authenticated
    echo Run: gh auth login
) else (
    echo [PASS] GitHub CLI authenticated
)

echo.
echo Checking repository secrets...
gh secret list >nul 2>&1
if errorlevel 1 (
    echo [WARN] Cannot list secrets (may need repo access)
) else (
    echo [PASS] Can access repository secrets
    gh secret list
)

echo.
echo ========================================
echo   Manual Actions Required:
echo ========================================
echo 1. Regenerate Telegram bot token via @BotFather
echo 2. Create new GitHub PAT with minimal scopes
echo 3. Generate new Gmail app password
echo 4. Enable 2FA on all accounts
echo 5. Run: scripts\update_github_secrets.bat owner/repo
echo 6. Run: scripts\secure_backup.bat
echo ========================================

pause