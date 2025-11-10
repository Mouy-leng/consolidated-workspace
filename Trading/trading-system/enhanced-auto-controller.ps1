#!/usr/bin/env powershell
<#
.SYNOPSIS
Enhanced Multi-Symbol Auto Trading Controller
.DESCRIPTION
Controls the enhanced automated trading system with multiple symbols
Includes start, stop, status, and monitoring functions
#>

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("Start", "Stop", "Status", "Monitor", "Config")]
    [string]$Action = "Status"
)

# Script configuration
$ScriptPath = $PSScriptRoot
$PythonScript = Join-Path $ScriptPath "enhanced-auto-trading.py"
$LogFile = Join-Path $ScriptPath "enhanced_auto_trading.log"
$StatusFile = Join-Path $ScriptPath "enhanced_trading_status.json"

function Write-Banner {
    Write-Host ""
    Write-Host "🚀 ENHANCED MULTI-SYMBOL AUTO TRADING CONTROLLER" -ForegroundColor Cyan
    Write-Host "=" * 65 -ForegroundColor DarkCyan
    Write-Host "✅ 10+ Symbols | ✅ Auto SL/TP | ✅ No Manual Intervention" -ForegroundColor Green
    Write-Host ""
}

function Test-PythonDependencies {
    Write-Host "🔍 Checking Python dependencies..." -ForegroundColor Yellow
    
    $required_packages = @("yfinance", "pandas", "numpy")
    $missing_packages = @()
    
    foreach ($package in $required_packages) {
        try {
            python -c "import $package" 2>$null
            if ($LASTEXITCODE -ne 0) {
                $missing_packages += $package
            }
        }
        catch {
            $missing_packages += $package
        }
    }
    
    if ($missing_packages.Count -gt 0) {
        Write-Host "❌ Missing packages: $($missing_packages -join ', ')" -ForegroundColor Red
        Write-Host "📦 Installing missing packages..." -ForegroundColor Yellow
        
        foreach ($package in $missing_packages) {
            Write-Host "   Installing $package..." -ForegroundColor Gray
            pip install $package --quiet
        }
        
        Write-Host "✅ Dependencies installed!" -ForegroundColor Green
    }
    else {
        Write-Host "✅ All dependencies satisfied!" -ForegroundColor Green
    }
}

function Start-EnhancedTrading {
    Write-Host "🎯 Starting Enhanced Automated Trading System..." -ForegroundColor Cyan
    
    # Check if already running
    $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | 
    Where-Object { $_.CommandLine -like "*enhanced-auto-trading.py*" }
    
    if ($processes) {
        Write-Host "⚠️ Enhanced trading system is already running (PID: $($processes.Id -join ', '))" -ForegroundColor Yellow
        return
    }
    
    # Check dependencies
    Test-PythonDependencies
    
    # Start the system
    Write-Host "🚀 Launching enhanced auto trading system..." -ForegroundColor Green
    
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = "python"
    $startInfo.Arguments = "`"$PythonScript`""
    $startInfo.WorkingDirectory = $ScriptPath
    $startInfo.CreateNoWindow = $false
    $startInfo.UseShellExecute = $true
    
    try {
        $process = [System.Diagnostics.Process]::Start($startInfo)
        
        # Wait a moment for startup
        Start-Sleep -Seconds 3
        
        Write-Host "✅ Enhanced Auto Trading System started successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🤖 SYSTEM FEATURES:" -ForegroundColor Cyan
        Write-Host "   📈 Symbols: XAUUSD, EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, NZDUSD, USDCAD, EURJPY, GBPJPY" -ForegroundColor White
        Write-Host "   🎯 Auto Buy/Sell based on technical analysis" -ForegroundColor White
        Write-Host "   ⛔ Automatic Stop Loss & Take Profit" -ForegroundColor White
        Write-Host "   💰 Risk Management: 1.5% per trade" -ForegroundColor White
        Write-Host "   🔄 24/5 Market monitoring" -ForegroundColor White
        Write-Host "   🚫 NO manual intervention required" -ForegroundColor White
        Write-Host ""
        Write-Host "💤 You can leave the system running unsupervised!" -ForegroundColor Green
        Write-Host "📊 Check status with: .\enhanced-auto-controller.ps1 -Action Status" -ForegroundColor Cyan
        
    }
    catch {
        Write-Host "❌ Failed to start enhanced trading system: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Stop-EnhancedTrading {
    Write-Host "⏹️ Stopping Enhanced Automated Trading System..." -ForegroundColor Yellow
    
    $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | 
    Where-Object { $_.CommandLine -like "*enhanced-auto-trading.py*" }
    
    if ($processes) {
        foreach ($process in $processes) {
            Write-Host "   Terminating process PID: $($process.Id)" -ForegroundColor Gray
            $process.Kill()
        }
        Write-Host "✅ Enhanced trading system stopped" -ForegroundColor Green
    }
    else {
        Write-Host "ℹ️ Enhanced trading system is not running" -ForegroundColor Blue
    }
}

function Get-EnhancedTradingStatus {
    Write-Host "📊 ENHANCED AUTO TRADING STATUS" -ForegroundColor Cyan
    Write-Host "-" * 40 -ForegroundColor DarkCyan
    
    # Check if process is running
    $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue | 
    Where-Object { $_.CommandLine -like "*enhanced-auto-trading.py*" }
    
    if ($processes) {
        Write-Host "🟢 Status: RUNNING (PID: $($processes.Id -join ', '))" -ForegroundColor Green
        Write-Host "⏰ Started: $($processes[0].StartTime)" -ForegroundColor White
        
        # Check memory usage
        $memoryMB = [math]::Round(($processes | Measure-Object WorkingSet -Sum).Sum / 1MB, 2)
        Write-Host "💾 Memory: $memoryMB MB" -ForegroundColor White
    }
    else {
        Write-Host "🔴 Status: STOPPED" -ForegroundColor Red
    }
    
    # Display log file info
    if (Test-Path $LogFile) {
        $logInfo = Get-Item $LogFile
        Write-Host "📄 Log File: $($logInfo.Length) bytes (Modified: $($logInfo.LastWriteTime))" -ForegroundColor White
        
        # Show last few log entries
        Write-Host "📊 Recent Activity:" -ForegroundColor Cyan
        $lastLines = Get-Content $LogFile -Tail 5 -ErrorAction SilentlyContinue
        if ($lastLines) {
            foreach ($line in $lastLines) {
                if ($line -match "AUTO TRADE|SIGNAL|Balance") {
                    Write-Host "   $line" -ForegroundColor Yellow
                }
                else {
                    Write-Host "   $line" -ForegroundColor Gray
                }
            }
        }
    }
    
    Write-Host ""
    Write-Host "🎯 MONITORED SYMBOLS:" -ForegroundColor Cyan
    Write-Host "   💰 XAUUSD (Gold)" -ForegroundColor Yellow
    Write-Host "   💶 EURUSD, GBPUSD, AUDUSD, NZDUSD" -ForegroundColor Green
    Write-Host "   💴 USDJPY, EURJPY, GBPJPY" -ForegroundColor Magenta
    Write-Host "   🇨🇭 USDCHF, USDCAD" -ForegroundColor Blue
}

function Monitor-EnhancedTrading {
    Write-Host "📊 LIVE MONITORING - Enhanced Auto Trading" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop monitoring..." -ForegroundColor Yellow
    Write-Host ""
    
    $lastLogSize = 0
    
    try {
        while ($true) {
            Clear-Host
            Write-Banner
            Get-EnhancedTradingStatus
            
            # Show live log updates
            if (Test-Path $LogFile) {
                $currentLogSize = (Get-Item $LogFile).Length
                if ($currentLogSize -gt $lastLogSize) {
                    Write-Host "🆕 NEW LOG ENTRIES:" -ForegroundColor Green
                    $newContent = Get-Content $LogFile -Tail 10 | Select-Object -Last 3
                    foreach ($line in $newContent) {
                        if ($line -match "ERROR") {
                            Write-Host "   $line" -ForegroundColor Red
                        }
                        elseif ($line -match "AUTO TRADE|SIGNAL") {
                            Write-Host "   $line" -ForegroundColor Green
                        }
                        else {
                            Write-Host "   $line" -ForegroundColor White
                        }
                    }
                    $lastLogSize = $currentLogSize
                }
            }
            
            Start-Sleep -Seconds 30
        }
    }
    catch {
        Write-Host "📊 Monitoring stopped" -ForegroundColor Yellow
    }
}

function Show-Configuration {
    Write-Host "⚙️ ENHANCED AUTO TRADING CONFIGURATION" -ForegroundColor Cyan
    Write-Host "-" * 45 -ForegroundColor DarkCyan
    Write-Host ""
    Write-Host "🏦 FBS Account Settings:" -ForegroundColor Yellow
    Write-Host "   Account: 241926287" -ForegroundColor White
    Write-Host "   Server: FBS-Real-4" -ForegroundColor White
    Write-Host "   Server IP: 95.179.194.198:443" -ForegroundColor White
    Write-Host ""
    Write-Host "⚙️ Trading Parameters:" -ForegroundColor Yellow
    Write-Host "   Risk per trade: 1.5%" -ForegroundColor White
    Write-Host "   Maximum positions: 5" -ForegroundColor White
    Write-Host "   Signal strength threshold: 75%" -ForegroundColor White
    Write-Host "   Stop Loss: 2 ATR" -ForegroundColor White
    Write-Host "   Take Profit: 3 ATR" -ForegroundColor White
    Write-Host ""
    Write-Host "📈 Trading Symbols (10):" -ForegroundColor Yellow
    Write-Host "   🥇 XAUUSD (Gold/USD)" -ForegroundColor Yellow
    Write-Host "   🌍 EURUSD (Euro/USD)" -ForegroundColor Green
    Write-Host "   🇬🇧 GBPUSD (Pound/USD)" -ForegroundColor Blue
    Write-Host "   🇯🇵 USDJPY (USD/Yen)" -ForegroundColor Red
    Write-Host "   🇨🇭 USDCHF (USD/Swiss)" -ForegroundColor Cyan
    Write-Host "   🇦🇺 AUDUSD (Aussie/USD)" -ForegroundColor Magenta
    Write-Host "   🇳🇿 NZDUSD (Kiwi/USD)" -ForegroundColor DarkGreen
    Write-Host "   🇨🇦 USDCAD (USD/Canadian)" -ForegroundColor DarkBlue
    Write-Host "   💶 EURJPY (Euro/Yen)" -ForegroundColor DarkYellow
    Write-Host "   🇬🇧 GBPJPY (Pound/Yen)" -ForegroundColor DarkMagenta
    Write-Host ""
    Write-Host "🔧 Technical Indicators:" -ForegroundColor Yellow
    Write-Host "   • RSI (14-period)" -ForegroundColor White
    Write-Host "   • MACD (12,26,9)" -ForegroundColor White
    Write-Host "   • Bollinger Bands (20,2)" -ForegroundColor White
    Write-Host "   • EMA (20,50)" -ForegroundColor White
    Write-Host "   • Stochastic (14,3)" -ForegroundColor White
    Write-Host "   • ATR (14-period)" -ForegroundColor White
}

# Main execution
Write-Banner

switch ($Action) {
    "Start" { Start-EnhancedTrading }
    "Stop" { Stop-EnhancedTrading }
    "Status" { Get-EnhancedTradingStatus }
    "Monitor" { Monitor-EnhancedTrading }
    "Config" { Show-Configuration }
}

Write-Host ""
Write-Host "🎯 Available Actions:" -ForegroundColor Cyan
Write-Host "   .\enhanced-auto-controller.ps1 -Action Start     # Start automated trading" -ForegroundColor White
Write-Host "   .\enhanced-auto-controller.ps1 -Action Stop      # Stop trading system" -ForegroundColor White
Write-Host "   .\enhanced-auto-controller.ps1 -Action Status    # Check system status" -ForegroundColor White
Write-Host "   .\enhanced-auto-controller.ps1 -Action Monitor   # Live monitoring" -ForegroundColor White
Write-Host "   .\enhanced-auto-controller.ps1 -Action Config    # View configuration" -ForegroundColor White
Write-Host ""