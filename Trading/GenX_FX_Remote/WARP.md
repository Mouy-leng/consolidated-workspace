# 🚀 GenX_FX Project Rules for Warp Terminal

## 🎯 Project Identity & Organization
- **Organization**: A6-9V (Professional trading system organization)
- **Project**: GenX_FX - AI-Powered Forex & Gold Trading Platform
- **Environment**: Windows PowerShell with cross-platform support
- **Repository**: Professional trading system with enterprise-grade security

## 🔧 Development Environment Rules

### PowerShell & Command Execution
- **Primary Shell**: Use PowerShell (pwsh) for all Windows operations
- **Script Execution**: Always use `.\script_name.ps1` format for PowerShell scripts
- **Cross-Platform**: Support both Windows native and WSL environments
- **A6-9V Tools**: Prioritize A6-9V branded scripts and tools when available

### File Path Conventions
- Use forward slashes `/` in documentation and cross-platform code
- Use backslashes `\` for Windows-specific PowerShell operations
- Always use absolute paths when referencing project files
- **Config Directory**: `config/` for all configuration files
- **Scripts Directory**: `scripts/` for automation scripts
- **Expert Advisors**: `expert-advisors/` for MT4/MT5 trading bots

## 🏗️ Architecture & Code Organization

### Core Components Priority
1. **Trading Engine**: Core trading logic and strategies (`core/`, `trading_engine.py`)
2. **AI Models**: Machine learning components (`ai_models/`, `ensemble_model.py`)
3. **Expert Advisors**: MT4/MT5 trading bots (`.mq4`, `.mq5` files)
4. **API Services**: FastAPI REST services (`api/`, WebSocket services)
5. **CLI Tools**: Unified command interface (`genx.ps1`, `head_cli.py`)

### Security & Credentials
- **Secrets Location**: `~/.genx_fx_secrets/a69v/` directory
- **Credential Management**: Windows Credential Manager integration
- **API Keys**: Never expose in plain text, use environment variables
- **Security Templates**: Follow `.github/` security policies

## 🤖 AI & Trading Specific Rules

### Expert Advisor Development
- **Gold Trading Focus**: XAUUSD, XAUEUR, XAUGBP pairs prioritized
- **Risk Management**: Confidence-based risk scaling implementation
- **Multi-Timeframe**: Support 1M, 5M, 15M, 1H, 4H, Daily analysis
- **Backtesting**: Always include performance metrics and Sharpe ratios

### Machine Learning Integration
- **Ensemble Models**: XGBoost, Random Forest, Neural Networks
- **Real-Time Processing**: Live market analysis every 5 minutes
- **Signal Generation**: ML-based trading signals with validation
- **Sentiment Analysis**: News and social media integration

### Broker & Platform Integration
- **Primary Brokers**: Exness, FXCM, ForexConnect
- **Platform Support**: MT4/MT5 Expert Advisors
- **API Integration**: RESTful APIs for real-time data
- **Cloud Deployment**: Google VM, AWS, Heroku ready

## 📊 Performance & Monitoring Rules

### System Performance Standards
- **Uptime Target**: 99.8% minimum
- **Response Time**: <200ms for API calls
- **Signal Frequency**: Every 5 minutes automated generation
- **Win Rate Targets**: 68%+ (Gold), 72%+ (Forex)

### Monitoring & Logging
- **System Status**: Use `./genx status` for health checks
- **Performance Metrics**: Track Sharpe ratios, drawdown, win rates
- **Live Monitoring**: Real-time VM and trading system monitoring
- **Audit Logging**: Complete system activity tracking

## 🛠️ Development Workflow Rules

### Command Usage Priority
```powershell
# Primary A6-9V Commands (Use These First)
.\a69v_repo_manager.ps1 configure    # Git identity setup
.\a69v_desktop_organizer.ps1 save    # Project backup
.\genx.ps1 status                     # System status
.\genx.ps1 dev                        # Development mode

# GenX CLI Commands
./genx overview              # System overview
./genx status               # Complete system status
./genx init                 # Initialize system
./genx chat                 # AI chat interface
```

### Testing & Validation
- **Demo First**: Always test on demo accounts before live trading
- **Backtesting**: Comprehensive historical testing required
- **Risk Validation**: Maximum 15% drawdown limits
- **Performance Testing**: Include Sharpe ratio calculations

## 🌐 Deployment & Production Rules

### Cloud Infrastructure
- **Primary Platform**: Google Cloud VM (US-Central)
- **Container Support**: Docker-ready with docker-compose.yml
- **24/7 Operation**: Automated signal generation and monitoring
- **Scalability**: Auto-scaling for high-frequency trading

### Production Standards
- **Security**: API key encryption, audit logging, access control
- **Monitoring**: Real-time system health tracking
- **Backup**: Complete project backup and restore capability
- **Documentation**: Comprehensive guides for all operations

## 📚 Documentation & Support Rules

### Documentation Priority
1. **Trading Guides**: `GOLD_MASTER_EA_GUIDE.md` (highest priority)
2. **Setup Guides**: `GETTING_STARTED.md`, `EA_SETUP_GUIDE.md`
3. **Technical Docs**: `SYSTEM_ARCHITECTURE_GUIDE.md`
4. **Deployment**: `DEPLOYMENT.md`, `VM_OPTIMIZATION_GUIDE.md`

### Support & Troubleshooting
- **Command Reference**: Use `./genx help-all` for complete commands
- **System Status**: Use `./genx overview` for quick status
- **Logs Access**: Use `./genx logs` for troubleshooting
- **Interactive Help**: Use `./genx chat` for AI assistance

## ⚠️ Trading Risk Management Rules

### Risk Warnings & Compliance
- **Capital Risk**: Only trade with money you can afford to lose
- **Demo Testing**: Mandatory testing before live deployment
- **Regulated Brokers**: Use only regulated forex brokers
- **Risk Disclosure**: Include trading risk warnings in all documentation

### Position Management
- **Dynamic Sizing**: Confidence-based position scaling
- **Drawdown Limits**: Maximum 15% drawdown protection
- **Multiple Pairs**: Diversification across forex and gold pairs
- **Stop Loss**: Always implement proper stop-loss mechanisms

## 🔄 Integration & Automation Rules

### A6-9V Organization Integration
- **Git Identity**: Use A6-9V organization credentials
- **Repository Management**: Follow A6-9V repository standards
- **Credential Storage**: Windows Credential Manager for A6-9V secrets
- **Project Structure**: Maintain A6-9V professional organization

### Automation Priorities
- **Desktop Organization**: Use `a69v_desktop_organizer.ps1` for file management
- **Repository Control**: Use `a69v_repo_manager.ps1` for Git operations  
- **Token Management**: Use `a69v_token_setup.ps1` for credential setup
- **Commit Automation**: Use `a69v_commit_all.ps1` for repository commits

---

## 🎯 Quick Action Commands

**Essential Commands for GenX_FX Development:**
```powershell
# System Status & Overview
.\genx.ps1 status                     # Complete system status
./genx overview                       # Quick system overview

# A6-9V Organization Tools  
.\a69v_repo_manager.ps1 configure    # Setup A6-9V Git identity
.\a69v_desktop_organizer.ps1 save    # Backup and organize project

# Trading System Operations
./genx init                           # Initialize trading system
./genx chat                           # Interactive AI trading chat
./genx amp status                     # AMP system status
./genx genx status                    # Trading engine status

# Development & Testing
python genx_24_7_service.py           # Start 24/7 service
python monitoring_dashboard.py       # Launch monitoring dashboard
```

**Remember**: Always follow A6-9V organization standards and prioritize trading system security and performance.