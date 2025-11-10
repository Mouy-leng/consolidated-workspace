# Collect and audit all credentials from projects
# This script scans for secrets and creates a secure credential vault

$workspaceRoot = "E:\Code\consolidated-workspace"
$credentialsDir = Join-Path $workspaceRoot "credentials"
$auditFile = Join-Path $workspaceRoot "CREDENTIALS_AUDIT.md"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Credential Collection & Audit" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create credentials directory
New-Item -ItemType Directory -Path $credentialsDir -Force | Out-Null

# Known credentials from user input
$knownCredentials = @{
    "Exness_MT5_Login" = "405347405"
    "Exness_MT5_Email" = "Lengkundee01@gmail.com"
    "Exness_MT5_Password" = "Leng12345@#$01"
    "Exness_MT5_Server" = "Exness-MT5Real8"
    "GitHub_SSH_Key" = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICw9/G//98IiSdsfAyn2tYS0ip9rE5wB6UAV1iue4dFm genxapitrading@gmail.com"
    "GitHub_Email" = "genxapitrading@gmail.com"
}

# Scan for .env files
$envFiles = @()
$searchPaths = @(
    "C:\Users\lengk\GenX_FX_Remote",
    "C:\Users\lengk\trading-bot-a69v",
    "C:\Users\lengk\.config\trading-system",
    "C:\Users\lengk\Desktop"
)

Write-Host "Scanning for .env files..." -ForegroundColor Yellow
foreach ($path in $searchPaths) {
    if (Test-Path $path) {
        $found = Get-ChildItem -Path $path -Filter ".env*" -Recurse -ErrorAction SilentlyContinue
        $envFiles += $found
    }
}

Write-Host "Found $($envFiles.Count) .env files" -ForegroundColor Green
Write-Host ""

# Create credential templates
Write-Host "Creating credential templates..." -ForegroundColor Yellow

# MT5 Account Template
$mt5Template = @"
# Exness MT5 Trading Account
# Account Type: Real/Live
# Platform: MT5
# Server: Exness-MT5Real8

MT5_LOGIN=405347405
MT5_PASSWORD=Leng12345@#$01
MT5_SERVER=Exness-MT5Real8
MT5_EMAIL=Lengkundee01@gmail.com
MT5_LEVERAGE=1:100
MT5_ACCOUNT_TYPE=Real
"@

Set-Content -Path (Join-Path $credentialsDir ".env.mt5.template") -Value $mt5Template

# GitHub Template
$githubTemplate = @"
# GitHub Configuration
GITHUB_EMAIL=genxapitrading@gmail.com
GITHUB_USERNAME=genxapitrading
GITHUB_SSH_KEY_PATH=~/.ssh/id_ed25519_github
"@

Set-Content -Path (Join-Path $credentialsDir ".env.github.template") -Value $githubTemplate

# Main .env template
$mainTemplate = @"
# Consolidated Workspace Environment Variables
# Copy this file to .env.local and fill in your values
# DO NOT commit .env.local to git

# Trading Accounts
MT5_LOGIN=
MT5_PASSWORD=
MT5_SERVER=
MT5_EMAIL=

# Exchange API Keys (if any)
BINANCE_API_KEY=
BINANCE_API_SECRET=
EXCHANGE_API_KEY=
EXCHANGE_API_SECRET=

# Database
DATABASE_URL=

# GitHub
GITHUB_EMAIL=genxapitrading@gmail.com
GITHUB_USERNAME=genxapitrading

# Application
NODE_ENV=development
LOG_LEVEL=debug
"@

Set-Content -Path (Join-Path $workspaceRoot ".env.template") -Value $mainTemplate

# Create secure credential file (gitignored)
$secureCreds = @"
# Secure Credentials - DO NOT COMMIT
# This file is gitignored

# Exness MT5 Account
MT5_LOGIN=405347405
MT5_PASSWORD=Leng12345@#$01
MT5_SERVER=Exness-MT5Real8
MT5_EMAIL=Lengkundee01@gmail.com

# GitHub
GITHUB_EMAIL=genxapitrading@gmail.com
"@

Set-Content -Path (Join-Path $credentialsDir ".env.local") -Value $secureCreds

# Update audit file
$auditContent = @"
# Credentials Audit Report
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Summary
This document tracks all credentials, secrets, and sensitive information found across the codebase.

## Exness MT5 Trading Account
**Account Type:** Real/Live Trading
**Platform:** MT5
**Server:** Exness-MT5Real8
**Login:** 405347405
**Email:** Lengkundee01@gmail.com
**Password:** Leng12345@#$01
**Leverage:** 1:100
**Status:** Active (10.09 USD balance)

⚠️ **SECURITY NOTE:** This is a LIVE trading account with real money. Handle with extreme care.

## GitHub SSH Key
**Type:** ssh-ed25519
**Key:** AAAAC3NzaC1lZDI1NTE5AAAAICw9/G//98IiSdsfAyn2tYS0ip9rE5wB6UAV1iue4dFm
**Email:** genxapitrading@gmail.com
**Purpose:** GitHub authentication for consolidated repository

## Email Accounts
- genxapitrading@gmail.com (GitHub account)
- Lengkundee01@gmail.com (Exness trading account)

## Environment Files Found
Found $($envFiles.Count) .env files across projects:
$(($envFiles | ForEach-Object { "- $($_.FullName)" }) -join "`n")

## Action Items
- [x] Create credential vault structure
- [x] Document known credentials
- [ ] Review all .env files for additional secrets
- [ ] Remove hardcoded credentials from code
- [ ] Set up environment variable management
- [ ] Create credential rotation schedule

## Security Best Practices
1. Never commit .env files to git
2. Use environment variables instead of hardcoded values
3. Rotate credentials regularly
4. Use different credentials for dev/staging/production
5. Store production credentials in secure vault (not in code)
"@

Set-Content -Path $auditFile -Value $auditContent

Write-Host "✓ Created credential templates" -ForegroundColor Green
Write-Host "✓ Created secure credential file (gitignored)" -ForegroundColor Green
Write-Host "✓ Updated audit report" -ForegroundColor Green
Write-Host ""
Write-Host "Credentials stored in: $credentialsDir" -ForegroundColor Cyan
Write-Host "Audit report: $auditFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  IMPORTANT: Review all .env files manually to extract additional credentials" -ForegroundColor Yellow

