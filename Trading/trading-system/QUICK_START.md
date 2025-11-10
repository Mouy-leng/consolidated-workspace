# Quick Start Guide for Automated Trading System

## 🚀 QUICK START (Step by Step)

### 1. Start MT5 Terminal

```powershell
.\start-mt5-fbs.ps1
```

- Wait for MT5 to load
- Login: 40933270 / Leng1234@#$01
- Server: ForexBrokersStandard-Server

### 2. Start Automated Trading

```powershell
.\auto-trading-controller.ps1 -Start
```

### 3. Monitor Trading

```powershell
.\auto-trading-controller.ps1 -Action monitor
```

## 🎯 MAIN COMMANDS

| Command | Purpose |
|---------|---------|
| `.\auto-trading-controller.ps1 -Start` | Start automated trading |
| `.\auto-trading-controller.ps1 -Stop` | Stop automated trading |
| `.\auto-trading-controller.ps1 -Status` | Check system status |
| `.\auto-trading-controller.ps1 -Action monitor` | Live monitoring |
| `.\auto-trading-controller.ps1 -Action log` | View trading log |

## ⚙️ CONFIGURATION OPTIONS

```powershell
# Conservative trading (1% risk, max 2 positions)
.\auto-trading-controller.ps1 -Start -RiskPercent 1.0 -MaxPositions 2

# Aggressive trading (3% risk, max 5 positions)
.\auto-trading-controller.ps1 -Start -RiskPercent 3.0 -MaxPositions 5

# High-quality signals only
.\auto-trading-controller.ps1 -Start -MinSignalStrength 0.8
```

## 🔧 SYSTEM COMPONENTS

### 📁 Files Created

- `automated-trading-system.py` - Main trading bot
- `auto-trading-controller.ps1` - System controller
- `start-mt5-fbs.ps1` - MT5 startup
- `automated_trading.log` - Trading log
- `SYSTEM_NOTES.md` - Complete documentation

### 🤖 What the System Does

1. **Technical Analysis**: RSI, MACD, Bollinger Bands
2. **Smart Money Concepts**: Order blocks, liquidity zones
3. **Pattern Recognition**: Support/resistance, trends
4. **Automated Execution**: Place, manage, close trades
5. **Risk Management**: 2% risk per trade, stop losses
6. **Multi-Symbol Trading**: XAUUSD, EURUSD, GBPUSD

## 🚨 SAFETY FEATURES

- **Maximum Risk**: 2% per trade (configurable)
- **Position Limits**: Max 3 open positions (configurable)
- **Stop Losses**: Automatic on every trade
- **Signal Filtering**: Minimum 70% signal strength
- **Error Handling**: Comprehensive logging and recovery
- **Manual Override**: Can stop anytime

## 📊 MONITORING

### Real-time Status

```powershell
.\auto-trading-controller.ps1 -Status
```

### Live Log Monitoring

```powershell
Get-Content automated_trading.log -Wait
```

### Dashboard (Manual Analysis)

```powershell
python trading-analysis/dashboard.py
```

## ⚠️ IMPORTANT REMINDERS

1. **LIVE ACCOUNT**: System trades with REAL MONEY
2. **ALWAYS MONITOR**: Check regularly, especially initially
3. **RISK MANAGEMENT**: Start with lower risk until comfortable
4. **MARKET CONDITIONS**: System works best in trending markets
5. **BACKUP PLAN**: Always have manual override ready

## 🎯 TYPICAL WORKFLOW

1. **Morning Setup** (5 minutes):

   ```powershell
   .\start-mt5-fbs.ps1
   .\auto-trading-controller.ps1 -Start -RiskPercent 1.5
   ```

2. **Monitor** (Throughout day):

   ```powershell
   .\auto-trading-controller.ps1 -Action monitor
   ```

3. **Evening Shutdown**:

   ```powershell
   .\auto-trading-controller.ps1 -Stop
   ```

## 📞 TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| MT5 won't connect | Check internet, restart MT5 |
| Bot won't start | Check MT5 connection first |
| No trades placed | Check signal strength, market conditions |
| High losses | Reduce risk percentage |
| System errors | Check log file for details |

## 🏆 SUCCESS TIPS

1. **Start Conservative**: Use 1% risk initially
2. **Monitor Actively**: First few days of operation
3. **Test Different Times**: Find best trading hours
4. **Adjust Parameters**: Based on performance
5. **Keep Learning**: Review trades and patterns

---

**🚀 READY TO START? Run: `.\auto-trading-controller.ps1 -Start`**
