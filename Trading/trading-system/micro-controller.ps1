#!/usr/bin/env powershell
<#
.SYNOPSIS
Micro Account Trading Controller - Optimized for $47.79 Balance
.DESCRIPTION
Controls automated trading system for small account balances
Safe risk management with micro lots
#>

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("Start", "Stop", "Status", "Monitor", "Balance")]
    [string]$Action = "Status"
)

$ScriptPath = $PSScriptRoot
$PythonScript = Join-Path $ScriptPath "micro-account-trader.py"
$LogFile = Join-Path $ScriptPath "micro_trading.log"

function Write-MicroHeader {
    Clear-Host
    Write-Host ""
    Write-Host "💰 MICRO ACCOUNT TRADING SYSTEM" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor DarkCyan
    Write-Host "🏦 FBS Account: 241926287 | Balance: $47.79" -ForegroundColor Yellow
    Write-Host "📊 Conservative Trading | Micro Lots Only" -ForegroundColor Green
    Write-Host "⚖️ Risk: 1.5% per trade | Max 2 trades" -ForegroundColor Magenta
    Write-Host ""
}

function Start-MicroTrading {
    Write-MicroHeader
    Write-Host "🚀 STARTING MICRO ACCOUNT TRADING..." -ForegroundColor Green
    Write-Host ""
    
    # Check if already running
    $existing = Get-Process -Name "python" -ErrorAction SilentlyContinue | 
                Where-Object { $_.CommandLine -like "*micro-account-trader.py*" }
    
    if ($existing) {
        Write-Host "⚠️ Micro trading system is already running!" -ForegroundColor Yellow
        Write-Host "PID: $($existing.Id)" -ForegroundColor Yellow
        return
    }
    
    Write-Host "📋 SYSTEM CONFIGURATION:" -ForegroundColor Cyan
    Write-Host "   💰 Account Balance: $47.79" -ForegroundColor White
    Write-Host "   📊 Risk per Trade: 1.5% ($0.72)" -ForegroundColor White
    Write-Host "   📏 Lot Size: 0.01 - 0.02" -ForegroundColor White
    Write-Host "   🎯 Max Trades: 2 concurrent" -ForegroundColor White
    Write-Host "   ⏱️ Cycle: 1 minute intervals" -ForegroundColor White
    Write-Host ""
    
    Write-Host "🎯 TRADING SYMBOLS:" -ForegroundColor Cyan
    Write-Host "   💶 EURUSD - Major pair, tight spreads" -ForegroundColor White
    Write-Host "   💷 GBPUSD - Good volatility" -ForegroundColor White
    Write-Host "   💴 USDJPY - Stable movements" -ForegroundColor White
    Write-Host "   🥇 XAUUSD - Gold trending" -ForegroundColor White
    Write-Host "   🇦🇺 AUDUSD - Range trading" -ForegroundColor White
    Write-Host ""
    
    Write-Host "⚠️ SAFETY FEATURES:" -ForegroundColor Yellow
    Write-Host "   🛡️ Daily loss limit: $5.00" -ForegroundColor White
    Write-Host "   🎯 Target: 1:2 Risk/Reward ratio" -ForegroundColor White
    Write-Host "   ⏹️ Tight stop losses (20-30 pips)" -ForegroundColor White
    Write-Host "   📊 Conservative entry signals only" -ForegroundColor White
    Write-Host ""
    
    $confirm = Read-Host "Start live trading with real money? (y/N)"
    if ($confirm -eq 'y' -or $confirm -eq 'Y') {
        Write-Host "🚀 Starting micro account trading..." -ForegroundColor Green
        Start-Process python -ArgumentList $PythonScript -NoNewWindow
        Start-Sleep -Seconds 3
        Get-MicroStatus
    } else {
        Write-Host "❌ Trading cancelled by user" -ForegroundColor Red
    }
}

function Stop-MicroTrading {
    Write-MicroHeader
    Write-Host "🛑 STOPPING MICRO TRADING SYSTEM..." -ForegroundColor Red
    
    $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | 
                 Where-Object { $_.CommandLine -like "*micro-account-trader.py*" }
    
    if ($processes) {
        foreach ($proc in $processes) {
            Stop-Process -Id $proc.Id -Force
            Write-Host "✅ Stopped trading process (PID: $($proc.Id))" -ForegroundColor Green
        }
    } else {
        Write-Host "ℹ️ No micro trading processes found" -ForegroundColor Yellow
    }
}

function Get-MicroStatus {
    Write-MicroHeader
    Write-Host "📊 MICRO ACCOUNT STATUS" -ForegroundColor Cyan
    Write-Host "-" * 30 -ForegroundColor DarkCyan
    
    # Check if running
    $process = Get-Process -Name "python" -ErrorAction SilentlyContinue | 
               Where-Object { $_.CommandLine -like "*micro-account-trader.py*" }
    
    if ($process) {
        $runtime = (Get-Date) - $process.StartTime
        Write-Host "🟢 Status: RUNNING" -ForegroundColor Green
        Write-Host "🆔 PID: $($process.Id)" -ForegroundColor White
        Write-Host "⏱️ Runtime: $($runtime.ToString('hh\:mm\:ss'))" -ForegroundColor White
        Write-Host "💾 Memory: $([math]::Round($process.WorkingSet64/1MB, 2)) MB" -ForegroundColor White
    } else {
        Write-Host "🔴 Status: STOPPED" -ForegroundColor Red
    }
    
    # Show recent log entries
    if (Test-Path $LogFile) {
        $logSize = (Get-Item $LogFile).Length
        Write-Host "📄 Log File: $([math]::Round($logSize/1KB, 2)) KB" -ForegroundColor White
        
        Write-Host ""
        Write-Host "📋 RECENT ACTIVITY:" -ForegroundColor Cyan
        Get-Content $LogFile -Tail 5 | ForEach-Object {
            Write-Host "   $_" -ForegroundColor Gray
        }
    }
    
    Write-Host ""
    Write-Host "🎯 AVAILABLE ACTIONS:" -ForegroundColor Cyan
    Write-Host "   .\micro-controller.ps1 -Action Start    # Start trading" -ForegroundColor White
    Write-Host "   .\micro-controller.ps1 -Action Stop     # Stop trading" -ForegroundColor White
    Write-Host "   .\micro-controller.ps1 -Action Status   # Check status" -ForegroundColor White
    Write-Host "   .\micro-controller.ps1 -Action Monitor  # Live monitor" -ForegroundColor White
    Write-Host "   .\micro-controller.ps1 -Action Balance  # Check balance" -ForegroundColor White
}

function Start-MicroMonitor {
    Write-MicroHeader
    Write-Host "📊 LIVE MICRO ACCOUNT MONITOR" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to exit monitoring..." -ForegroundColor Yellow
    Write-Host ""
    
    while ($true) {
        try {
            Clear-Host
            Write-MicroHeader
            
            # Get current market data
            Write-Host "📈 CURRENT MARKET PRICES:" -ForegroundColor Cyan
            python -c "
import yfinance as yf
symbols = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'GC=F', 'AUDUSD=X']
for symbol in symbols:
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period='1d', interval='1m')
        if not data.empty:
            price = data['Close'].iloc[-1]
            change = ((price - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100
            name = symbol.replace('=X', '').replace('=F', '')
            if name == 'GC': name = 'XAUUSD'
            print(f'   {name}: {price:.5f} ({change:+.2f}%)')
    except: pass
"
            
            Write-Host ""
            Get-MicroStatus
            
            Start-Sleep -Seconds 30
            
        } catch {
            break
        }
    }
}

function Get-BalanceInfo {
    Write-MicroHeader
    Write-Host "💰 ACCOUNT BALANCE ANALYSIS" -ForegroundColor Cyan
    Write-Host ""
    
    python live-account-checker.py
}

# Main execution
switch ($Action) {
    "Start" { Start-MicroTrading }
    "Stop" { Stop-MicroTrading }
    "Status" { Get-MicroStatus }
    "Monitor" { Start-MicroMonitor }
    "Balance" { Get-BalanceInfo }
}

Write-Host ""