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

## Projects Found
1. **GenX_FX_Remote** - Main trading system (Git repository)
2. **trading-bot-a69v** - Autonomous trading bot (Git repository)
3. **AI_Trading_System** - AI trading system
4. **GenX_FX-1** - Trading system variant
5. **.config/trading-system/** - Multiple trading sub-projects:
   - ci
   - gdrive-scanner
   - mt5-fbs-setup
   - trading-analysis
   - trading-microservice
   - training
   - security

## Action Items
- [ ] Consolidate all credentials into secure vault
- [ ] Remove hardcoded credentials from code
- [ ] Set up environment variable management
- [ ] Create .gitignore for sensitive files
- [ ] Set up credential rotation schedule

