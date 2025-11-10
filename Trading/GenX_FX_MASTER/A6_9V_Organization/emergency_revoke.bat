@echo off
echo ========================================
echo   EMERGENCY CREDENTIAL REVOCATION
echo ========================================

echo STEP 1: Revoking GitHub tokens...
gh auth login
gh secret delete GITHUB_TOKEN 2>nul
gh secret delete GITHUB_ACCESS_TOKEN 2>nul
gh secret delete DOCKER_PASSWORD 2>nul

echo STEP 2: Manual revocation required:
echo - GitHub: https://github.com/settings/tokens
echo - Bybit: https://www.bybit.com/app/user/api-management
echo - Telegram: @BotFather /revoke
echo - Gmail: https://myaccount.google.com/apppasswords

echo STEP 3: Cleaning git history...
git rm --cached .env 2>nul
git rm --cached .env.deployment 2>nul
git add .gitignore
git commit -m "Remove exposed secrets"

echo EMERGENCY REVOCATION COMPLETE
echo Please manually revoke tokens at the URLs above
pause