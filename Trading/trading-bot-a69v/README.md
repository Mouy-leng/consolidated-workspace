# Autonomous Trading Bot - A6-9V

## Organization
**A6-9V** - Advanced Autonomous Trading System  
**User**: mouy-leng

## Overview
Fully autonomous trading bot with self-executing strategies, continuous market monitoring, and risk management.

## Features
- ✅ Autonomous strategy execution
- ✅ Real-time market analysis
- ✅ Automated risk management
- ✅ VSCode integrated development
- ✅ Continuous monitoring loops
- ✅ Asynchronous execution framework

## Quick Start

### 1. Setup Virtual Environment
```powershell
cd C:\Users\lengk\trading-bot-a69v
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Run Autonomous Trading Bot
```powershell
python src\main.py
```

## VSCode Integration

### Open in VSCode
```powershell
code C:\Users\lengk\trading-bot-a69v
```

### Available Tasks (Ctrl+Shift+B)
- **Run Autonomous Trading Bot** - Start the bot
- **Setup Virtual Environment** - Initialize Python venv
- **Install Dependencies** - Install all required packages
- **Run Tests** - Execute test suite
- **Auto Deploy** - Deploy to GitHub

## Project Structure
```
trading-bot-a69v/
├── src/
│   ├── main.py                    # Main entry point
│   └── strategies/
│       └── autonomous_executor.py # Strategy execution engine
├── .vscode/
│   ├── settings.json              # VSCode configuration
│   └── tasks.json                 # Automated tasks
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## GitHub Repository Setup

### Create Remote Repository
```powershell
# Set user configuration
git config user.name "mouy-leng"
git config user.email "mouy-leng@users.noreply.github.com"

# Add remote (replace with actual repo URL from A6-9V org)
git remote add origin https://github.com/A6-9V/trading-bot-a69v.git

# Initial commit
git add .
git commit -m "Initial autonomous trading bot setup"
git branch -M main
git push -u origin main
```

## Network Drive Mapping (Optional)

### Map Network Drive
```powershell
# Map Z: drive to network share
net use Z: \\NETWORK_PATH\share /persistent:yes

# Verify mapping
net use
```

## Autonomous Execution

The bot runs continuously with:
- **60-second market analysis cycles**
- **30-second strategy execution intervals**
- **Real-time risk monitoring**
- **Automatic logging to `trading_bot.log`**

## Configuration

Edit configuration in `src/main.py`:
```python
config = {
    "organization": "A6-9V",
    "user": "mouy-leng",
    "mode": "autonomous",
    "risk_level": "moderate"
}
```

## License
Proprietary - A6-9V Organization

## Support
For issues and questions, contact the A6-9V development team.
