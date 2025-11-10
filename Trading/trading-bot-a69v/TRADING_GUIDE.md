# Complete Trading Bot Guide - A6-9V

## 🚀 Quick Start to Real Trading

### Step 1: Get API Keys

#### For Paper Trading (Testnet - RECOMMENDED FIRST)
1. Visit: https://testnet.binance.vision/
2. Click "Generate HMAC_SHA256 Key"
3. Save your API Key and Secret Key
4. **Important**: Testnet uses fake money - perfect for testing!

#### For Live Trading (Real Money - USE WITH CAUTION)
1. Visit: https://www.binance.com/
2. Create account and complete verification
3. Go to API Management
4. Create new API key with spot trading permissions
5. Enable IP whitelist for security

### Step 2: Configure API Keys

Edit the `.env` file in the project root:

```bash
# For Testnet (Paper Trading)
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_secret_here

# Organization
ORGANIZATION=A6-9V
USER=mouy-leng
```

### Step 3: Configure Trading Parameters

Edit `config.yaml`:

```yaml
exchange:
  exchange_id: binance
  testnet: true  # Keep TRUE for paper trading!

trading:
  symbol: BTC/USDT  # Trading pair
  timeframe: 5m     # Analysis interval
```

### Step 4: Run the Bot

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the trading bot
python src\main.py
```

## 📊 How It Works

### Trading Strategy: Momentum-Based
The bot uses a momentum strategy that:

1. **Analyzes Market Data**
   - Fetches OHLCV (price) data every 60 seconds
   - Calculates price momentum and volume ratios
   - Generates BUY/SELL/HOLD signals

2. **BUY Signal Triggers When**:
   - Price momentum > 0.1% (positive trend)
   - Price is moving up
   - Volume is 20% higher than average
   - No existing position

3. **SELL Signal Triggers When**:
   - Momentum turns negative (< -0.1%)
   - OR price drops > 0.2%
   - Has an open position

4. **Risk Management**:
   - Uses only 5% of balance per trade
   - Minimum $10 balance required
   - Automatically monitors order execution
   - Tracks all trades and statistics

### Execution Flow

```
Start Bot
    ↓
Connect to Exchange
    ↓
Check Balance
    ↓
┌─────────────────┐
│ Every 60 Seconds│
└────────┬────────┘
         ↓
    Fetch Market Data
         ↓
    Analyze Momentum
         ↓
    Generate Signal
         ↓
   ┌─────┴─────┐
   │           │
  BUY        SELL       HOLD
   │           │          │
Place       Place      Wait
Order       Order    for Signal
   │           │          │
   └─────┬─────┘          │
         ↓                │
    Monitor Order         │
         ↓                │
  Track Position          │
         │                │
         └────────────────┘
```

## 💰 Example Trade Execution

### Scenario: BUY Signal

```
Initial Balance: $1000 USDT
BTC Price: $50,000
Risk: 5% of balance = $50

1. Bot analyzes market
   Momentum: +0.15% ✓
   Price change: +0.5% ✓
   Volume ratio: 1.4x ✓
   
2. Signal: BUY

3. Calculate position size
   Amount = $50 / $50,000 = 0.001 BTC
   
4. Place market order
   → BUY 0.001 BTC @ $50,000
   
5. Order executes
   ✓ Position opened
   Entry: $50,000
   
6. Monitor for SELL signal...
```

### Scenario: SELL Signal

```
Current Position: 0.001 BTC @ $50,000
Current Price: $51,000

1. Bot analyzes market
   Momentum: -0.12% ✗
   Price change: -0.3% ✗
   
2. Signal: SELL

3. Place market order
   → SELL 0.001 BTC @ $51,000
   
4. Order executes
   ✓ Position closed
   P&L: +$1 (2% gain)
```

## 🛡️ Safety Features

### Built-in Protection
- ✅ Paper trading mode by default
- ✅ Minimum balance requirements
- ✅ Position size limits (5% max)
- ✅ Maximum 1 concurrent position
- ✅ Order execution monitoring
- ✅ Error handling and retry logic
- ✅ Comprehensive logging

### Testing Checklist

Before live trading:
- [ ] Test with paper trading (testnet)
- [ ] Verify API keys work
- [ ] Check balance calculations
- [ ] Monitor several complete buy/sell cycles
- [ ] Review logs for errors
- [ ] Understand P&L tracking
- [ ] Test emergency stop (Ctrl+C)

## 📈 Monitoring Your Bot

### Real-time Logs

The bot shows:
```
============================================================
Trading Cycle - 2025-10-23 01:00:00
============================================================
Signal: BUY | Price: $50000.00
Momentum: 0.0015 | Price Change: 0.0025
Available balance: 1000 USDT
Calculated position size: 0.001 @ 50000.0 = $50.00
Executing BUY: 0.001 BTC/USDT
Creating MARKET buy order: 0.001 BTC/USDT
Order created: 123456 - Status: filled
✓ BUY order executed successfully! Order ID: 123456

Stats: Total=1 | Active=0 | Success Rate=100.0%

Waiting 60 seconds until next analysis...
```

### Log Files

All activity is logged to `trading_bot.log`:
- Market analysis results
- Order executions
- Balance changes
- Errors and warnings
- Performance statistics

## ⚙️ Configuration Options

### Key Parameters to Adjust

```yaml
# In config.yaml

strategy:
  risk_percentage: 0.05      # % of balance per trade (0.05 = 5%)
  min_balance: 10            # Minimum balance to trade
  momentum_threshold: 0.001  # Signal sensitivity (lower = more trades)
  
monitoring:
  analysis_interval: 60      # Seconds between analysis

risk:
  max_position_size: 0.1     # Max 10% of balance
  max_daily_trades: 10       # Daily trade limit
```

## 🚨 Going Live

### When You're Ready for Real Money

1. **Test Thoroughly**
   - Run testnet for at least 24 hours
   - Verify strategy performance
   - Check all trades execute correctly

2. **Update Configuration**
   ```yaml
   exchange:
     testnet: false  # ⚠️ ENABLE LIVE TRADING
   
   safety:
     paper_trading: false  # ⚠️ USE REAL MONEY
   ```

3. **Get Live API Keys**
   - Follow Step 1 "For Live Trading"
   - Update `.env` with live keys

4. **Start Small**
   - Use minimum balance initially
   - Gradually increase as confidence grows

5. **Monitor Closely**
   - Watch first few trades carefully
   - Keep emergency stop ready (Ctrl+C)

## 🔧 Troubleshooting

### Common Issues

**Error: "Failed to connect to exchange"**
- Check API keys in `.env`
- Verify testnet setting matches key type
- Check internet connection

**Error: "Insufficient balance"**
- Testnet: Get testnet funds from Binance testnet
- Verify `min_balance` in config
- Check balance: logged at startup

**No trades executing**
- Market may not meet signal criteria
- Check momentum_threshold setting
- Review logs for analysis results

**Orders failing**
- Check trading permissions on API key
- Verify symbol is correct (BTC/USDT)
- Check minimum order sizes

## 📞 Support

For issues or questions:
- Check `trading_bot.log` for detailed errors
- Review configuration files
- Verify API keys and permissions

## ⚠️ Disclaimer

**IMPORTANT**: 
- Cryptocurrency trading carries significant risk
- Past performance doesn't guarantee future results
- Only trade with money you can afford to lose
- This bot is for educational purposes
- Test extensively before live trading
- A6-9V organization assumes no liability for trading losses

## 🎯 Next Steps

1. ✅ Get testnet API keys
2. ✅ Add keys to `.env`
3. ✅ Run: `python src\main.py`
4. ✅ Monitor first trades
5. ✅ Test for 24+ hours
6. ✅ Review performance
7. ⚠️ Only then consider live trading

---

**Happy Trading! 🚀**

*A6-9V Organization - Autonomous Trading Systems*
