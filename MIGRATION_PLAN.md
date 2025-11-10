# Code Migration & Consolidation Plan

## Overview
Migrate all code from C: drive to E: drive (Lexar NS100 SSD) and consolidate all repositories into one unified workspace.

## Current State

### Projects on C: Drive
1. **C:\Users\lengk\GenX_FX_Remote** (424 MB) - Git repo
2. **C:\Users\lengk\trading-bot-a69v** (238 MB) - Git repo  
3. **C:\Users\lengk\AI_Trading_System** - Small project
4. **C:\Users\lengk\GenX_FX-1** - Small project
5. **C:\Users\lengk\.config\trading-system\** - Multiple sub-projects
6. **C:\Dev\** - Development directory

### Target Structure on E: Drive
```
E:\Code\consolidated-workspace\
├── .git/                          # Single unified repository
├── .gitignore                     # Comprehensive ignore rules
├── README.md                      # Main documentation
├── CREDENTIALS_AUDIT.md           # Credentials tracking
├── .env.template                  # Environment template
├── .env.local                     # Local credentials (gitignored)
├── projects/                      # All consolidated projects
│   ├── genx-fx-remote/           # Main trading system
│   ├── trading-bot/              # Autonomous trading bot
│   ├── ai-trading-system/        # AI trading components
│   ├── trading-analysis/         # Analysis tools
│   ├── trading-microservice/     # Microservices
│   └── mt5-integration/          # MT5/FBS setup
├── shared/                        # Shared utilities
│   ├── config/                   # Shared configurations
│   ├── scripts/                  # Utility scripts
│   └── docs/                     # Documentation
└── credentials/                   # Secure credential storage (gitignored)
    ├── .env.production
    ├── .env.development
    └── mt5-accounts.json
```

## Migration Steps

### Phase 1: Setup & Preparation
- [x] Create consolidated workspace on E: drive
- [x] Initialize Git repository
- [ ] Set up SSH key for GitHub
- [ ] Create .gitignore
- [ ] Create credential vault structure

### Phase 2: Credential Audit & Security
- [ ] Scan all .env files
- [ ] Extract and secure all credentials
- [ ] Create credential templates
- [ ] Remove hardcoded secrets from code
- [ ] Set up environment variable management

### Phase 3: Project Migration
- [ ] Copy GenX_FX_Remote → projects/genx-fx-remote
- [ ] Copy trading-bot-a69v → projects/trading-bot
- [ ] Copy AI_Trading_System → projects/ai-trading-system
- [ ] Copy .config/trading-system sub-projects
- [ ] Copy C:\Dev projects if any

### Phase 4: Consolidation
- [ ] Merge duplicate code
- [ ] Organize shared utilities
- [ ] Update import paths
- [ ] Consolidate dependencies
- [ ] Create unified documentation

### Phase 5: Cleanup
- [ ] Remove old projects from C: (after verification)
- [ ] Update all references to new paths
- [ ] Test all projects in new location
- [ ] Create migration verification script

## SSH Key Setup
- **Key:** ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICw9/G//98IiSdsfAyn2tYS0ip9rE5wB6UAV1iue4dFm
- **Email:** genxapitrading@gmail.com
- **Purpose:** GitHub authentication

## Exness MT5 Account
- **Login:** 405347405
- **Email:** Lengkundee01@gmail.com
- **Server:** Exness-MT5Real8
- **Status:** Active (Real account)

## Notes
- Keep GitHub repositories intact (don't delete remote repos)
- Only clean up local copies after successful migration
- Maintain git history where possible
- Use git subtree or submodules if needed for large projects

