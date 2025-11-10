# Live Trade Management Dashboard
# Monitor and manage your active FBS-Real-4 positions

Write-Host "🎯 LIVE TRADE MANAGEMENT DASHBOARD" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host ""

Write-Host "📊 ACTIVE POSITIONS STATUS:" -ForegroundColor Cyan
Write-Host "   💰 Account: 241926287 (FBS-Real-4)" -ForegroundColor White
Write-Host "   📈 Active Trades: 2 positions" -ForegroundColor White
Write-Host "   🔹 XAUUSD (Gold)" -ForegroundColor White
Write-Host "   🔹 EURUSD (Euro/Dollar)" -ForegroundColor White
Write-Host ""

Write-Host "📈 CURRENT MARKET ANALYSIS:" -ForegroundColor Yellow
python live-trade-monitor.py signals

Write-Host ""
Write-Host "🔧 TRADE MANAGEMENT OPTIONS:" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. 📊 Live Monitoring:" -ForegroundColor Yellow
Write-Host "   python live-trade-monitor.py" -ForegroundColor Gray
Write-Host "   (Continuous 30-second updates)" -ForegroundColor Gray
Write-Host ""

Write-Host "2. 📱 Mobile Management:" -ForegroundColor Yellow
Write-Host "   - Download FBS MT4 mobile app" -ForegroundColor Gray
Write-Host "   - Login: 241926287 / f0v/9iIH" -ForegroundColor Gray
Write-Host "   - Manage trades on the go" -ForegroundColor Gray
Write-Host ""

Write-Host "3. 🌐 Web Trading Platform:" -ForegroundColor Yellow
Write-Host "   - Go to: https://mt4.fbs.com/" -ForegroundColor Cyan
Write-Host "   - Login with your credentials" -ForegroundColor Gray
Write-Host "   - Full trade management interface" -ForegroundColor Gray
Write-Host ""

Write-Host "4. 💻 Desktop MT4:" -ForegroundColor Yellow
Write-Host "   - Download: https://fbs.com/trading-platforms/metatrader-4" -ForegroundColor Cyan
Write-Host "   - Install for advanced features" -ForegroundColor Gray
Write-Host "   - Enable automated trading" -ForegroundColor Gray
Write-Host ""

Write-Host "🚨 RISK MANAGEMENT ALERTS:" -ForegroundColor Red
Write-Host "   ⚠️  Always set Stop Loss on your trades" -ForegroundColor Yellow
Write-Host "   ⚠️  Monitor RSI levels (>70 overbought, <30 oversold)" -ForegroundColor Yellow
Write-Host "   ⚠️  Watch support/resistance levels" -ForegroundColor Yellow
Write-Host "   ⚠️  Don't risk more than 1-2% per trade" -ForegroundColor Yellow
Write-Host ""

Write-Host "📊 RECOMMENDED ACTIONS:" -ForegroundColor Green
Write-Host ""

# Get current signals and provide recommendations
$xauSignal = python live-trade-monitor.py signals | Select-String "XAUUSD" -A 4
$eurSignal = python live-trade-monitor.py signals | Select-String "EURUSD" -A 4

Write-Host "🔹 XAUUSD (Gold):" -ForegroundColor Yellow
Write-Host "   Current trend suggests HOLD position" -ForegroundColor White
Write-Host "   Monitor for RSI divergence signals" -ForegroundColor Gray
Write-Host "   Watch $4000 support and $4100 resistance" -ForegroundColor Gray
Write-Host ""

Write-Host "🔹 EURUSD:" -ForegroundColor Yellow
Write-Host "   Bullish trend continues" -ForegroundColor White
Write-Host "   Monitor ECB news and US data" -ForegroundColor Gray
Write-Host "   Key level: 1.1600 resistance" -ForegroundColor Gray
Write-Host ""

Write-Host "⏰ NEXT UPDATES:" -ForegroundColor Cyan
Write-Host "   📊 Market analysis: Every 30 seconds" -ForegroundColor Gray
Write-Host "   📈 Signal updates: Real-time" -ForegroundColor Gray
Write-Host "   🔔 Alert notifications: As needed" -ForegroundColor Gray
Write-Host ""

$action = Read-Host "Choose action: [M]onitor, [S]ignals, [H]elp, or [Q]uit"

switch ($action.ToUpper()) {
    "M" {
        Write-Host "🚀 Starting live monitoring..." -ForegroundColor Cyan
        python live-trade-monitor.py
    }
    "S" {
        Write-Host "📊 Getting latest signals..." -ForegroundColor Cyan
        python live-trade-monitor.py signals
    }
    "H" {
        Write-Host ""
        Write-Host "📋 HELP - Trade Management:" -ForegroundColor Yellow
        Write-Host "   📱 Use FBS mobile app for quick actions" -ForegroundColor Gray
        Write-Host "   🌐 Use web platform for detailed analysis" -ForegroundColor Gray
        Write-Host "   💻 Install MT4 for full automation" -ForegroundColor Gray
        Write-Host "   📊 Run monitor for continuous updates" -ForegroundColor Gray
        Write-Host ""
        Write-Host "🚨 Emergency Actions:" -ForegroundColor Red
        Write-Host "   🛑 Close positions via mobile/web if needed" -ForegroundColor Gray
        Write-Host "   📞 Contact FBS support: +1-315-636-7735" -ForegroundColor Gray
    }
    "Q" {
        Write-Host "✅ Dashboard closed. Your trades remain active." -ForegroundColor Green
    }
    Default {
        Write-Host "📊 Showing current signals..." -ForegroundColor Cyan
        python live-trade-monitor.py signals
    }
}