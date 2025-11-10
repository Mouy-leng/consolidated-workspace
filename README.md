# Consolidated Workspace

Unified workspace for all trading system projects, migrated from C: drive to E: drive (Lexar NS100 SSD).

## 🎯 Purpose

This workspace consolidates all code projects into a single, organized repository on the Lexar NS100 SSD (E: drive), providing:
- **Unified codebase** - All projects in one place
- **Better organization** - Clean, structured layout
- **Secure credential management** - Centralized, gitignored secrets
- **Single Git repository** - Easier version control and collaboration
- **Performance** - Fast SSD storage for development

## 📁 Structure

```
consolidated-workspace/
├── projects/              # All project code
│   ├── genx-fx-remote/   # Main trading system
│   ├── trading-bot/      # Autonomous trading bot
│   ├── ai-trading-system/ # AI trading components
│   └── ...
├── shared/               # Shared utilities and configs
├── credentials/          # Secure credential storage (gitignored)
├── scripts/             # Utility scripts
└── docs/                # Documentation
```

## 🚀 Quick Start

### 1. Start PyCharm (Auto-configured)
PyCharm is already configured for this project and will auto-start on Windows boot.

**Manual start:**
```powershell
.\start-pycharm.ps1
```

**First-time setup in PyCharm:**
1. File > Settings > Project > Python Interpreter
2. Create/select a virtual environment
3. Install dependencies: `pip install -r requirements.txt`

### 2. Setup SSH Key for GitHub
```powershell
.\shared\scripts\setup-ssh-key.ps1
```
Then add your private key and configure GitHub.

### 3. Collect and Audit Credentials
```powershell
.\shared\scripts\collect-credentials.ps1
```
This scans for all credentials and creates secure templates.

### 4. Migrate Projects (Dry Run First)
```powershell
# Preview what will be migrated
.\migrate-projects.ps1 -DryRun

# Perform actual migration
.\migrate-projects.ps1
```

### 5. Initialize Git Repository
```powershell
git add .
git commit -m "Initial consolidated workspace"
git remote add origin git@github.com:genxapitrading/consolidated-workspace.git
git push -u origin main
```

## 🔐 Credentials Management

### Exness MT5 Account
- **Login:** 405347405
- **Email:** Lengkundee01@gmail.com
- **Server:** Exness-MT5Real8
- **Status:** Active (Real account)

⚠️ **SECURITY:** This is a LIVE trading account. Credentials are stored in `credentials/.env.local` (gitignored).

### GitHub
- **Email:** genxapitrading@gmail.com
- **SSH Key:** ssh-ed25519 (see `setup-ssh-key.ps1`)

## 📋 Migration Status

See [MIGRATION_PLAN.md](./MIGRATION_PLAN.md) for detailed migration plan and status.

## 🔒 Security

- All `.env` files are gitignored
- Credentials stored in `credentials/` directory (gitignored)
- Never commit secrets to git
- Use environment variables in code
- See [CREDENTIALS_AUDIT.md](./CREDENTIALS_AUDIT.md) for credential tracking

## 📚 Projects

### Main Projects
1. **GenX_FX_Remote** - Main trading system with full features
2. **Trading Bot** - Autonomous trading bot with AI strategies
3. **AI Trading System** - AI/ML components for trading
4. **Trading Analysis** - Analysis and backtesting tools
5. **MT5 Integration** - MetaTrader 5 integration

## 🛠️ Scripts

All scripts are located in `shared/scripts/`:

- `setup-ssh-key.ps1` - Configure SSH key for GitHub
- `collect-credentials.ps1` - Scan and organize credentials
- `migrate-projects.ps1` - Migrate projects from C: to E: drive
- `cleanup-workspace.ps1` - Clean up temporary files, logs, and caches
- `organize-structure.ps1` - Organize workspace directory structure

## 📝 Notes

- Original projects remain on C: drive until migration is verified
- GitHub repositories are NOT deleted (only local consolidation)
- All git history is preserved where possible
- Large directories (node_modules, __pycache__) are excluded during migration

## 🔄 Next Steps

1. ✅ Create workspace structure
2. ✅ Set up credential management
3. ⏳ Migrate all projects
4. ⏳ Consolidate and organize code
5. ⏳ Update import paths and dependencies
6. ⏳ Test all projects
7. ⏳ Clean up C: drive (after verification)

## 📞 Support

For issues or questions, refer to:
- [MIGRATION_PLAN.md](./MIGRATION_PLAN.md) - Migration details
- [CREDENTIALS_AUDIT.md](./CREDENTIALS_AUDIT.md) - Credential tracking

---

**Created:** $(Get-Date -Format "yyyy-MM-dd")
**Workspace Location:** E:\Code\consolidated-workspace
**Drive:** Lexar NS100 SSD (512GB)
