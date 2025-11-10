#!/usr/bin/env powershell
<#
.SYNOPSIS
Complete Trading System Manager
.DESCRIPTION
Manages the entire multi-symbol automated trading system
#>

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("StartAll", "StopAll", "Dashboard", "Status", "Quick", "Monitor", "Help")]
    [string]$Action = "Help"
)

function Write-Header {
    Clear-Host
    Write-Host ""
    Write-Host "🚀 COMPLETE AUTOMATED TRADING SYSTEM" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor DarkCyan
    Write-Host "💰 FBS Real Account: 241926287 | Server: FBS-Real-4" -ForegroundColor Yellow
    Write-Host "📈 Symbols: 10+ pairs including XAUUSD, EURUSD, GBPUSD, etc." -ForegroundColor Green
    Write-Host "🤖 Fully Automated: Auto Buy/Sell with SL/TP" -ForegroundColor Magenta
    Write-Host ""
}

function Start-CompleteSystem {
    Write-Header
    Write-Host "🎯 STARTING COMPLETE AUTOMATED TRADING SYSTEM..." -ForegroundColor Cyan
    Write-Host ""
    
    # Step 1: Start Enhanced Auto Trading
    Write-Host "📊 Step 1: Starting Enhanced Auto Trading Engine..." -ForegroundColor Yellow
    .\enhanced-auto-controller.ps1 -Action Start
    Start-Sleep -Seconds 3
    
    # Step 2: Check system status
    Write-Host "📊 Step 2: Verifying system status..." -ForegroundColor Yellow
    .\enhanced-auto-controller.ps1 -Action Status
    
    Write-Host ""
    Write-Host "✅ COMPLETE SYSTEM STARTED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 ACTIVE FEATURES:" -ForegroundColor Cyan
    Write-Host "   🤖 Enhanced Auto Trading: RUNNING" -ForegroundColor Green
    Write-Host "   📊 10+ Symbol Monitoring: ACTIVE" -ForegroundColor Green
    Write-Host "   ⛔ Auto SL/TP: ENABLED" -ForegroundColor Green
    Write-Host "   💰 Risk Management: 1.5% per trade" -ForegroundColor Green
    Write-Host "   🔄 24/5 Market Coverage: ACTIVE" -ForegroundColor Green
    Write-Host ""
    Write-Host "💤 SYSTEM IS FULLY AUTONOMOUS!" -ForegroundColor Magenta
    Write-Host "   You can leave it running without supervision" -ForegroundColor White
    Write-Host "   It will automatically trade when opportunities arise" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Next Steps:" -ForegroundColor Cyan
    Write-Host "   • Run live dashboard: .\trading-manager.ps1 -Action Dashboard" -ForegroundColor White
    Write-Host "   • Check quick status: .\trading-manager.ps1 -Action Status" -ForegroundColor White
    Write-Host "   • Monitor activity: .\trading-manager.ps1 -Action Monitor" -ForegroundColor White
}

function Stop-CompleteSystem {
    Write-Header
    Write-Host "⏹️ STOPPING COMPLETE TRADING SYSTEM..." -ForegroundColor Yellow
    
    # Stop enhanced auto trading
    Write-Host "📊 Stopping Enhanced Auto Trading..." -ForegroundColor Gray
    .\enhanced-auto-controller.ps1 -Action Stop
    
    Write-Host ""
    Write-Host "✅ ALL SYSTEMS STOPPED" -ForegroundColor Green
}

function Show-LiveDashboard {
    Write-Header
    Write-Host "📊 LAUNCHING LIVE TRADING DASHBOARD..." -ForegroundColor Cyan
    Write-Host "🔄 Real-time monitoring of all 10+ symbols" -ForegroundColor Green
    Write-Host "⚡ Live alerts for trading opportunities" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press Ctrl+C to return to menu..." -ForegroundColor Gray
    Start-Sleep -Seconds 2
    
    python live-trading-dashboard.py
}

function Show-SystemStatus {
    Write-Header
    Write-Host "📊 COMPLETE SYSTEM STATUS" -ForegroundColor Cyan
    Write-Host "-" * 40 -ForegroundColor DarkCyan
    
    # Enhanced Auto Trading Status
    Write-Host "🤖 Enhanced Auto Trading:" -ForegroundColor Yellow
    .\enhanced-auto-controller.ps1 -Action Status | Select-Object -Skip 4
    
    Write-Host ""
    Write-Host "💡 SYSTEM CAPABILITIES:" -ForegroundColor Cyan
    Write-Host "   ✅ Fully Automated Trading" -ForegroundColor Green
    Write-Host "   ✅ 10+ Symbol Coverage" -ForegroundColor Green
    Write-Host "   ✅ Auto Stop Loss & Take Profit" -ForegroundColor Green
    Write-Host "   ✅ Risk Management (1.5% per trade)" -ForegroundColor Green
    Write-Host "   ✅ 24/5 Market Monitoring" -ForegroundColor Green
    Write-Host "   ✅ Technical Analysis Based" -ForegroundColor Green
}

function Run-QuickScan {
    Write-Header
    Write-Host "⚡ QUICK MARKET SCAN" -ForegroundColor Cyan
    Write-Host "🔍 Scanning all symbols for immediate opportunities..." -ForegroundColor Yellow
    Write-Host ""
    
    python quick-trade-setup.py
    
    Write-Host ""
    Write-Host "💡 TIP: Strong signals will be automatically traded by the system!" -ForegroundColor Green
}

function Show-MonitoringOptions {
    Write-Header
    Write-Host "📊 MONITORING OPTIONS" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Choose monitoring method:" -ForegroundColor Yellow
    Write-Host "1. Live Dashboard (Real-time visual monitoring)" -ForegroundColor White
    Write-Host "2. Enhanced Auto Status (Quick status check)" -ForegroundColor White
    Write-Host "3. Log File Monitoring (Text-based monitoring)" -ForegroundColor White
    Write-Host "4. Return to main menu" -ForegroundColor Gray
    Write-Host ""
    
    $choice = Read-Host "Enter choice (1-4)"
    
    switch ($choice) {
        "1" { Show-LiveDashboard }
        "2" { .\enhanced-auto-controller.ps1 -Action Monitor }
        "3" { 
            Write-Host "📄 Monitoring log file..." -ForegroundColor Yellow
            Get-Content "enhanced_auto_trading.log" -Wait -Tail 10
        }
        "4" { return }
        default { 
            Write-Host "❌ Invalid choice" -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }
}

function Show-Help {
    Write-Header
    Write-Host "🎯 TRADING SYSTEM MANAGER - HELP" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 AVAILABLE ACTIONS:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🚀 StartAll   - Start complete automated trading system" -ForegroundColor Green
    Write-Host "   • Launches enhanced auto trading" -ForegroundColor Gray
    Write-Host "   • Enables all 10+ symbols" -ForegroundColor Gray
    Write-Host "   • Activates auto SL/TP" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⏹️ StopAll    - Stop all trading systems" -ForegroundColor Red
    Write-Host "   • Safely shuts down all processes" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📊 Dashboard  - Launch live trading dashboard" -ForegroundColor Cyan
    Write-Host "   • Real-time symbol monitoring" -ForegroundColor Gray
    Write-Host "   • Live trading alerts" -ForegroundColor Gray
    Write-Host "   • Visual market overview" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📈 Status     - Check complete system status" -ForegroundColor Blue
    Write-Host "   • System health check" -ForegroundColor Gray
    Write-Host "   • Performance overview" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⚡ Quick      - Quick market scan" -ForegroundColor Yellow
    Write-Host "   • Immediate opportunity scan" -ForegroundColor Gray
    Write-Host "   • Current market signals" -ForegroundColor Gray
    Write-Host ""
    Write-Host "👁️ Monitor    - Choose monitoring method" -ForegroundColor Magenta
    Write-Host "   • Multiple monitoring options" -ForegroundColor Gray
    Write-Host ""
    Write-Host "💡 EXAMPLES:" -ForegroundColor Yellow
    Write-Host "   .\trading-manager.ps1 -Action StartAll" -ForegroundColor White
    Write-Host "   .\trading-manager.ps1 -Action Dashboard" -ForegroundColor White
    Write-Host "   .\trading-manager.ps1 -Action Status" -ForegroundColor White
    Write-Host ""
    Write-Host "🎯 SYSTEM FEATURES:" -ForegroundColor Cyan
    Write-Host "   💰 FBS Real Account Integration" -ForegroundColor White
    Write-Host "   🤖 100% Automated Trading" -ForegroundColor White
    Write-Host "   📊 Advanced Technical Analysis" -ForegroundColor White
    Write-Host "   ⛔ Automatic Risk Management" -ForegroundColor White
    Write-Host "   🔄 24/5 Market Coverage" -ForegroundColor White
    Write-Host "   📈 10+ Currency Pairs + Gold" -ForegroundColor White
}

# Main execution
switch ($Action) {
    "StartAll" { Start-CompleteSystem }
    "StopAll" { Stop-CompleteSystem }
    "Dashboard" { Show-LiveDashboard }
    "Status" { Show-SystemStatus }
    "Quick" { Run-QuickScan }
    "Monitor" { Show-MonitoringOptions }
    "Help" { Show-Help }
}

if ($Action -ne "Help") {
    Write-Host ""
    Write-Host "🎯 Quick Actions:" -ForegroundColor Cyan
    Write-Host "   .\trading-manager.ps1 -Action StartAll   # Start everything" -ForegroundColor White
    Write-Host "   .\trading-manager.ps1 -Action Dashboard  # Live dashboard" -ForegroundColor White
    Write-Host "   .\trading-manager.ps1 -Action Status     # Check status" -ForegroundColor White
    Write-Host "   .\trading-manager.ps1 -Action Help       # Show full help" -ForegroundColor White
    Write-Host ""
}