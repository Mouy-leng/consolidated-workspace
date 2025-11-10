#!/usr/bin/env powershell
<#
.SYNOPSIS
Live Trading Dashboard for $47.79 FBS Account
.DESCRIPTION
Complete dashboard showing account status, market data, and trading opportunities
#>

function Show-TradingDashboard {
    while ($true) {
        Clear-Host
        Write-Host ""
        Write-Host "🚀 LIVE TRADING DASHBOARD - FBS REAL ACCOUNT" -ForegroundColor Cyan
        Write-Host "=" * 65 -ForegroundColor DarkCyan
        Write-Host "🏦 Account: 241926287 | Server: FBS-Real-4 | Balance: $47.79" -ForegroundColor Yellow
        Write-Host "⏰ Last Update: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
        Write-Host ""
        
        # Account Status
        Write-Host "💰 ACCOUNT STATUS:" -ForegroundColor Green
        Write-Host "   Balance: $47.79" -ForegroundColor White
        Write-Host "   Risk per trade: $0.72 (1.5%)" -ForegroundColor White
        Write-Host "   Max trades: 2 concurrent" -ForegroundColor White
        Write-Host "   Daily limit: -$5.00 loss" -ForegroundColor White
        Write-Host ""
        
        # System Status
        $microProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | 
                       Where-Object { $_.CommandLine -like "*micro-account-trader.py*" }
        
        Write-Host "🤖 SYSTEM STATUS:" -ForegroundColor Magenta
        if ($microProcess) {
            Write-Host "   Trading Bot: 🟢 RUNNING (PID: $($microProcess.Id))" -ForegroundColor Green
            Write-Host "   Runtime: $((Get-Date) - $microProcess.StartTime | ForEach-Object {$_.ToString('hh\:mm\:ss')})" -ForegroundColor White
        } else {
            Write-Host "   Trading Bot: 🔴 STOPPED" -ForegroundColor Red
        }
        Write-Host ""
        
        # Current Market Data
        Write-Host "📈 LIVE MARKET DATA:" -ForegroundColor Cyan
        python -c "
import yfinance as yf
symbols = {'EURUSD=X': 'EURUSD', 'GBPUSD=X': 'GBPUSD', 'USDJPY=X': 'USDJPY', 'GC=F': 'XAUUSD', 'AUDUSD=X': 'AUDUSD'}
for yahoo_symbol, clean_symbol in symbols.items():
    try:
        ticker = yf.Ticker(yahoo_symbol)
        data = ticker.history(period='1d', interval='1m')
        if not data.empty:
            current = data['Close'].iloc[-1]
            open_price = data['Open'].iloc[0]
            change = ((current - open_price) / open_price) * 100
            
            # Calculate simple moving average
            sma_20 = data['Close'].iloc[-20:].mean()
            trend = 'UP' if current > sma_20 else 'DOWN'
            
            # Volatility check
            high_1h = data['High'].iloc[-60:].max()
            low_1h = data['Low'].iloc[-60:].min()
            volatility = ((high_1h - low_1h) / current) * 100
            
            status = '🟢 ACTIVE' if volatility > 0.3 else '🟡 QUIET'
            
            print(f'   {clean_symbol}: {current:.5f} ({change:+.2f}%) Trend: {trend} {status}')
    except:
        print(f'   {clean_symbol}: Data unavailable')
"
        Write-Host ""
        
        # Trading Signals
        Write-Host "🎯 TRADING SIGNALS:" -ForegroundColor Yellow
        python -c "
import yfinance as yf
import pandas as pd

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

symbols = {'EURUSD=X': 'EURUSD', 'GC=F': 'XAUUSD', 'GBPUSD=X': 'GBPUSD'}
signals = []

for yahoo_symbol, clean_symbol in symbols.items():
    try:
        ticker = yf.Ticker(yahoo_symbol)
        data = ticker.history(period='1d', interval='5m')
        if len(data) >= 20:
            current = data['Close'].iloc[-1]
            sma_10 = data['Close'].iloc[-10:].mean()
            sma_20 = data['Close'].iloc[-20:].mean()
            rsi = calculate_rsi(data['Close'])
            
            signal = 'HOLD'
            reason = 'Waiting for setup'
            
            # Simple signal logic
            if current > sma_10 > sma_20 and 30 < rsi < 45:
                signal = 'BUY'
                reason = 'Bullish momentum + RSI recovery'
            elif current < sma_10 < sma_20 and 55 < rsi < 70:
                signal = 'SELL' 
                reason = 'Bearish momentum + RSI decline'
            elif rsi < 30:
                signal = 'WATCH'
                reason = 'Oversold - potential reversal'
            elif rsi > 70:
                signal = 'WATCH'
                reason = 'Overbought - potential reversal'
                
            print(f'   {clean_symbol}: {signal} | RSI: {rsi:.1f} | {reason}')
    except:
        print(f'   {clean_symbol}: Signal calculation error')
"
        Write-Host ""
        
        # Quick Actions
        Write-Host "⚡ QUICK ACTIONS:" -ForegroundColor Green
        Write-Host "   [1] Start Trading: .\micro-controller.ps1 -Action Start" -ForegroundColor White
        Write-Host "   [2] Stop Trading: .\micro-controller.ps1 -Action Stop" -ForegroundColor White  
        Write-Host "   [3] Check Status: .\micro-controller.ps1 -Action Status" -ForegroundColor White
        Write-Host "   [4] Balance Check: .\micro-controller.ps1 -Action Balance" -ForegroundColor White
        Write-Host "   [5] Quick Analysis: python quick-status.py" -ForegroundColor White
        Write-Host ""
        
        # Risk Warning
        Write-Host "⚠️ RISK NOTICE:" -ForegroundColor Red
        Write-Host "   Trading with real money ($47.79)" -ForegroundColor Yellow
        Write-Host "   Maximum risk: $0.72 per trade (1.5%)" -ForegroundColor Yellow
        Write-Host "   Use only micro lots (0.01-0.02)" -ForegroundColor Yellow
        Write-Host ""
        
        Write-Host "Press Ctrl+C to exit dashboard | Auto-refresh in 30 seconds..." -ForegroundColor Gray
        Write-Host "=" * 65 -ForegroundColor DarkCyan
        
        Start-Sleep -Seconds 30
    }
}

# Start dashboard
Show-TradingDashboard