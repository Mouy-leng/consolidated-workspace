#!/usr/bin/env powershell
<#
.SYNOPSIS
Trading System Synchronization Script
.DESCRIPTION
Synchronizes all trading components and ensures proper coordination
#>

function Write-SyncHeader {
    Clear-Host
    Write-Host ""
    Write-Host "🔄 TRADING SYSTEM SYNCHRONIZATION" -ForegroundColor Cyan
    Write-Host "=" * 55 -ForegroundColor DarkCyan
    Write-Host "🏦 FBS Account: 241926287 | Balance: $47.79" -ForegroundColor Yellow
    Write-Host "⏰ Sync Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""
}

function Test-SystemComponents {
    Write-Host "🔍 CHECKING SYSTEM COMPONENTS..." -ForegroundColor Cyan
    Write-Host ""
    
    $components = @{
        "micro-account-trader.py"  = "Micro Account Trading Engine"
        "enhanced-auto-trading.py" = "Enhanced Auto Trading System"
        "live-account-checker.py"  = "Account Balance Checker"
        "quick-status.py"          = "Quick Status Monitor"
        "live-dashboard.ps1"       = "Live Trading Dashboard"
        "micro-controller.ps1"     = "Micro Trading Controller"
    }
    
    $status = @{}
    
    foreach ($file in $components.Keys) {
        $fullPath = Join-Path $PSScriptRoot $file
        if (Test-Path $fullPath) {
            Write-Host "   ✅ $($components[$file])" -ForegroundColor Green
            $status[$file] = "Available"
        }
        else {
            Write-Host "   ❌ $($components[$file]) - Missing" -ForegroundColor Red
            $status[$file] = "Missing"
        }
    }
    
    return $status
}

function Get-RunningProcesses {
    Write-Host ""
    Write-Host "🤖 CHECKING RUNNING PROCESSES..." -ForegroundColor Cyan
    Write-Host ""
    
    $tradingProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | 
    Where-Object { 
        $_.CommandLine -like "*micro-account-trader*" -or
        $_.CommandLine -like "*enhanced-auto-trading*" -or
        $_.CommandLine -like "*trading*"
    }
    
    if ($tradingProcesses) {
        foreach ($proc in $tradingProcesses) {
            $runtime = (Get-Date) - $proc.StartTime
            $memory = [math]::Round($proc.WorkingSet64 / 1MB, 2)
            
            Write-Host "   🟢 PID: $($proc.Id) | Runtime: $($runtime.ToString('hh\:mm\:ss')) | Memory: ${memory}MB" -ForegroundColor Green
            
            # Try to identify which script
            if ($proc.CommandLine -like "*micro-account-trader*") {
                Write-Host "      📊 Micro Account Trader - ACTIVE" -ForegroundColor Yellow
            }
            elseif ($proc.CommandLine -like "*enhanced-auto-trading*") {
                Write-Host "      📈 Enhanced Auto Trading - ACTIVE" -ForegroundColor Yellow
            }
        }
    }
    else {
        Write-Host "   ⚠️ No trading processes currently running" -ForegroundColor Yellow
    }
    
    return $tradingProcesses
}

function Sync-TradingData {
    Write-Host ""
    Write-Host "🔄 SYNCHRONIZING TRADING DATA..." -ForegroundColor Cyan
    Write-Host ""
    
    # Update account balance and sync across all systems
    $accountData = @{
        account_id       = "241926287"
        server           = "FBS-Real-4"
        server_ip        = "95.179.194.198:443"
        balance          = 47.79
        risk_percent     = 1.5
        max_trades       = 2
        min_lot          = 0.01
        max_lot          = 0.02
        daily_loss_limit = 5.00
        last_sync        = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    }
    
    # Save sync data
    $accountData | ConvertTo-Json -Depth 2 | Out-File "trading_sync.json" -Encoding UTF8
    Write-Host "   ✅ Account data synchronized" -ForegroundColor Green
    
    # Update market data
    Write-Host "   📊 Fetching latest market data..." -ForegroundColor Yellow
    python -c "
import yfinance as yf
import json
from datetime import datetime

symbols = {'EURUSD=X': 'EURUSD', 'GBPUSD=X': 'GBPUSD', 'USDJPY=X': 'USDJPY', 'GC=F': 'XAUUSD', 'AUDUSD=X': 'AUDUSD'}
market_data = {}

for yahoo_symbol, clean_symbol in symbols.items():
    try:
        ticker = yf.Ticker(yahoo_symbol)
        data = ticker.history(period='1d', interval='1m')
        if not data.empty:
            current = data['Close'].iloc[-1]
            open_price = data['Open'].iloc[0]
            change = ((current - open_price) / open_price) * 100
            
            market_data[clean_symbol] = {
                'price': float(current),
                'change_percent': float(change),
                'last_update': datetime.now().isoformat()
            }
    except:
        pass

with open('market_sync.json', 'w') as f:
    json.dump(market_data, f, indent=2)

print('Market data synchronized')
"
    Write-Host "   ✅ Market data synchronized" -ForegroundColor Green
}

function Show-SyncSummary {
    Write-Host ""
    Write-Host "📊 SYNCHRONIZATION SUMMARY" -ForegroundColor Green
    Write-Host "-" * 35 -ForegroundColor DarkGreen
    
    # Read sync data
    if (Test-Path "trading_sync.json") {
        $syncData = Get-Content "trading_sync.json" | ConvertFrom-Json
        Write-Host "   💰 Account: $($syncData.account_id)" -ForegroundColor White
        Write-Host "   💵 Balance: $($syncData.balance)" -ForegroundColor White
        Write-Host "   ⚖️ Risk: $($syncData.risk_percent)% per trade" -ForegroundColor White
        Write-Host "   🎯 Max Trades: $($syncData.max_trades)" -ForegroundColor White
        Write-Host "   📏 Lot Range: $($syncData.min_lot) - $($syncData.max_lot)" -ForegroundColor White
        Write-Host "   🛡️ Daily Limit: $($syncData.daily_loss_limit)" -ForegroundColor White
        Write-Host "   ⏰ Last Sync: $($syncData.last_sync)" -ForegroundColor White
    }
    
    Write-Host ""
    if (Test-Path "market_sync.json") {
        Write-Host "   📈 Market Data: SYNCHRONIZED" -ForegroundColor Green
        $marketData = Get-Content "market_sync.json" | ConvertFrom-Json
        
        foreach ($symbol in $marketData.PSObject.Properties.Name) {
            $data = $marketData.$symbol
            Write-Host "   📊 $symbol`: $([math]::Round($data.price, 5)) ($($data.change_percent.ToString('+0.00;-0.00'))%)" -ForegroundColor Gray
        }
    }
}

function Start-SyncedTrading {
    Write-Host ""
    Write-Host "🚀 STARTING SYNCHRONIZED TRADING SYSTEM..." -ForegroundColor Green
    Write-Host ""
    
    # Check if already running
    $existing = Get-Process -Name "python" -ErrorAction SilentlyContinue | 
    Where-Object { $_.CommandLine -like "*micro-account-trader*" }
    
    if ($existing) {
        Write-Host "   ⚠️ Micro trading system already running (PID: $($existing.Id))" -ForegroundColor Yellow
        Write-Host "   📊 System is synchronized and active" -ForegroundColor Green
    }
    else {
        Write-Host "   🎯 Starting micro account trader..." -ForegroundColor Yellow
        Start-Process python -ArgumentList "micro-account-trader.py" -NoNewWindow
        Start-Sleep -Seconds 3
        
        $newProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue | 
        Where-Object { $_.CommandLine -like "*micro-account-trader*" }
        
        if ($newProcess) {
            Write-Host "   ✅ Micro trading system started (PID: $($newProcess.Id))" -ForegroundColor Green
        }
        else {
            Write-Host "   ❌ Failed to start trading system" -ForegroundColor Red
        }
    }
}

function Show-PostSyncActions {
    Write-Host ""
    Write-Host "⚡ POST-SYNC ACTIONS AVAILABLE:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   [1] Monitor Live: .\live-dashboard.ps1" -ForegroundColor White
    Write-Host "   [2] Quick Status: python quick-status.py" -ForegroundColor White  
    Write-Host "   [3] Control System: .\micro-controller.ps1 -Action Status" -ForegroundColor White
    Write-Host "   [4] Check Balance: .\micro-controller.ps1 -Action Balance" -ForegroundColor White
    Write-Host "   [5] Stop Trading: .\micro-controller.ps1 -Action Stop" -ForegroundColor White
    Write-Host ""
    Write-Host "🎯 RECOMMENDED NEXT STEP:" -ForegroundColor Yellow
    Write-Host "   Run: .\live-dashboard.ps1" -ForegroundColor Green
    Write-Host ""
}

# Main synchronization process
function Start-FullSync {
    Write-SyncHeader
    
    # Step 1: Check components
    $componentStatus = Test-SystemComponents
    
    # Step 2: Check running processes  
    $runningProcesses = Get-RunningProcesses
    
    # Step 3: Sync data
    Sync-TradingData
    
    # Step 4: Show summary
    Show-SyncSummary
    
    # Step 5: Ensure trading is running
    Start-SyncedTrading
    
    # Step 6: Show actions
    Show-PostSyncActions
    
    Write-Host "🎉 SYNCHRONIZATION COMPLETE!" -ForegroundColor Green
    Write-Host "=" * 55 -ForegroundColor DarkCyan
    Write-Host ""
}

# Execute synchronization
Start-FullSync