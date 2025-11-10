# Automated Trading System Controller
# Manages the automated trading bot

param(
    [string]$Action = "status",
    [switch]$Start = $false,
    [switch]$Stop = $false,
    [switch]$Status = $false,
    [decimal]$RiskPercent = 2.0,
    [int]$MaxPositions = 3,
    [decimal]$MinSignalStrength = 0.7
)

Write-Host "🤖 AUTOMATED TRADING SYSTEM CONTROLLER" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""

$botScript = "automated-trading-system.py"
$logFile = "automated_trading.log"

# Check if bot script exists
if (-not (Test-Path $botScript)) {
    Write-Host "❌ Automated trading script not found: $botScript" -ForegroundColor Red
    exit 1
}

function Show-BotStatus {
    Write-Host "📊 Bot Status Check:" -ForegroundColor Yellow
    
    # Check if Python process is running
    $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
        $_.MainWindowTitle -like "*automated*" -or 
        $_.ProcessName -eq "python" -and 
        (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine -like "*automated-trading-system*"
    }
    
    if ($pythonProcesses) {
        Write-Host "   ✅ Automated trading bot: RUNNING" -ForegroundColor Green
        $pythonProcesses | ForEach-Object {
            Write-Host "      PID: $($_.Id) | CPU: $($_.CPU)" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "   ❌ Automated trading bot: NOT RUNNING" -ForegroundColor Red
    }
    
    # Check MT5 connection
    $mt5Process = Get-Process -Name "terminal64" -ErrorAction SilentlyContinue
    if ($mt5Process) {
        Write-Host "   ✅ MT5 Terminal: RUNNING (PID: $($mt5Process.Id))" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ MT5 Terminal: NOT RUNNING" -ForegroundColor Red
    }
    
    # Check log file
    if (Test-Path $logFile) {
        $logSize = (Get-Item $logFile).Length / 1KB
        Write-Host "   📄 Log file: $logFile ($('{0:N1}' -f $logSize) KB)" -ForegroundColor Cyan
        
        # Show last few lines
        Write-Host "   📝 Recent activity:" -ForegroundColor Gray
        Get-Content $logFile -Tail 3 | ForEach-Object {
            Write-Host "      $_" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "   ⚠️ Log file not found" -ForegroundColor Yellow
    }
}

function Start-TradingBot {
    Write-Host "🚀 Starting Automated Trading Bot..." -ForegroundColor Cyan
    Write-Host ""
    
    # Validate parameters
    Write-Host "⚙️ Configuration:" -ForegroundColor Yellow
    Write-Host "   Risk per trade: $RiskPercent%" -ForegroundColor White
    Write-Host "   Max positions: $MaxPositions" -ForegroundColor White
    Write-Host "   Min signal strength: $MinSignalStrength" -ForegroundColor White
    Write-Host ""
    
    # Check MT5 first
    $mt5Process = Get-Process -Name "terminal64" -ErrorAction SilentlyContinue
    if (-not $mt5Process) {
        Write-Host "⚠️ MT5 Terminal not running. Starting..." -ForegroundColor Yellow
        # Try to start MT5
        if (Test-Path ".\start-mt5-fbs.ps1") {
            .\start-mt5-fbs.ps1
            Start-Sleep -Seconds 5
        }
        else {
            Write-Host "❌ MT5 startup script not found. Please start MT5 manually." -ForegroundColor Red
            return
        }
    }
    
    # Safety confirmation
    Write-Host "⚠️  LIVE TRADING WARNING:" -ForegroundColor Red
    Write-Host "   🚨 This will trade with REAL MONEY on account 40933270" -ForegroundColor Red
    Write-Host "   🚨 Bot will automatically place and manage trades" -ForegroundColor Red
    Write-Host "   🚨 Maximum risk: $RiskPercent% per trade" -ForegroundColor Red
    Write-Host ""
    
    $confirmation = Read-Host "Type 'CONFIRM' to start automated trading"
    if ($confirmation -ne "CONFIRM") {
        Write-Host "❌ Automated trading cancelled" -ForegroundColor Yellow
        return
    }
    
    # Start the bot
    Write-Host "▶️ Starting trading bot..." -ForegroundColor Green
    
    try {
        # Set environment variables
        $env:RISK_PERCENT = $RiskPercent
        $env:MAX_POSITIONS = $MaxPositions
        $env:MIN_SIGNAL_STRENGTH = $MinSignalStrength
        
        # Start bot in background
        Start-Process -FilePath "python" -ArgumentList $botScript -WindowStyle Minimized
        
        Start-Sleep -Seconds 3
        
        # Verify it started
        $botProcess = Get-Process -Name "python" -ErrorAction SilentlyContinue
        if ($botProcess) {
            Write-Host "✅ Automated trading bot started successfully!" -ForegroundColor Green
            Write-Host "   📊 Monitor with: .\auto-trading-controller.ps1 -Status" -ForegroundColor Cyan
            Write-Host "   📄 View logs: Get-Content $logFile -Wait" -ForegroundColor Cyan
            Write-Host "   ⏹️ Stop with: .\auto-trading-controller.ps1 -Stop" -ForegroundColor Cyan
        }
        else {
            Write-Host "❌ Failed to start trading bot" -ForegroundColor Red
        }
        
    }
    catch {
        Write-Host "❌ Error starting bot: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Stop-TradingBot {
    Write-Host "⏹️ Stopping Automated Trading Bot..." -ForegroundColor Yellow
    
    # Find and stop Python processes running the bot
    $botProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
    
    if ($botProcesses) {
        Write-Host "   🔍 Found $($botProcesses.Count) Python process(es)" -ForegroundColor Cyan
        
        foreach ($process in $botProcesses) {
            try {
                $process.Kill()
                Write-Host "   ✅ Stopped process PID: $($process.Id)" -ForegroundColor Green
            }
            catch {
                Write-Host "   ❌ Failed to stop PID: $($process.Id)" -ForegroundColor Red
            }
        }
        
        Start-Sleep -Seconds 2
        Write-Host "✅ Automated trading bot stopped" -ForegroundColor Green
    }
    else {
        Write-Host "   ℹ️ No trading bot processes found" -ForegroundColor Gray
    }
}

function Show-TradingLog {
    param([int]$Lines = 20)
    
    if (Test-Path $logFile) {
        Write-Host "📄 Trading Log (Last $Lines lines):" -ForegroundColor Yellow
        Write-Host "=====================================" -ForegroundColor Yellow
        Get-Content $logFile -Tail $Lines
    }
    else {
        Write-Host "❌ Log file not found: $logFile" -ForegroundColor Red
    }
}

function Show-LiveMonitoring {
    Write-Host "📊 LIVE TRADING MONITOR" -ForegroundColor Green
    Write-Host "======================" -ForegroundColor Green
    Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Gray
    Write-Host ""
    
    try {
        while ($true) {
            Clear-Host
            Write-Host "📊 LIVE TRADING MONITOR - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Green
            Write-Host "===========================================" -ForegroundColor Green
            
            # Show bot status
            Show-BotStatus
            
            Write-Host ""
            Write-Host "📈 Recent Trading Activity:" -ForegroundColor Yellow
            if (Test-Path $logFile) {
                Get-Content $logFile -Tail 5 | ForEach-Object {
                    if ($_ -match "Trade placed|Signal:") {
                        Write-Host "   $_" -ForegroundColor Green
                    }
                    elseif ($_ -match "ERROR|Failed") {
                        Write-Host "   $_" -ForegroundColor Red
                    }
                    else {
                        Write-Host "   $_" -ForegroundColor Gray
                    }
                }
            }
            
            Start-Sleep -Seconds 10
        }
    }
    catch {
        Write-Host "`n📊 Monitoring stopped" -ForegroundColor Yellow
    }
}

# Main execution logic
if ($Start) {
    Start-TradingBot
}
elseif ($Stop) {
    Stop-TradingBot
}
elseif ($Status -or $Action -eq "status") {
    Show-BotStatus
}
elseif ($Action -eq "log") {
    Show-TradingLog
}
elseif ($Action -eq "monitor") {
    Show-LiveMonitoring
}
else {
    Write-Host "🎯 Usage:" -ForegroundColor Yellow
    Write-Host "   .\auto-trading-controller.ps1 -Start                    # Start automated trading" -ForegroundColor Gray
    Write-Host "   .\auto-trading-controller.ps1 -Stop                     # Stop automated trading" -ForegroundColor Gray
    Write-Host "   .\auto-trading-controller.ps1 -Status                   # Check status" -ForegroundColor Gray
    Write-Host "   .\auto-trading-controller.ps1 -Action log               # View trading log" -ForegroundColor Gray
    Write-Host "   .\auto-trading-controller.ps1 -Action monitor           # Live monitoring" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🔧 Configuration Options:" -ForegroundColor Yellow
    Write-Host "   -RiskPercent 1.5                                       # Set risk per trade (default: 2%)" -ForegroundColor Gray
    Write-Host "   -MaxPositions 5                                        # Set max open positions (default: 3)" -ForegroundColor Gray
    Write-Host "   -MinSignalStrength 0.8                                 # Set min signal strength (default: 0.7)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⚠️  Examples:" -ForegroundColor Yellow
    Write-Host "   .\auto-trading-controller.ps1 -Start -RiskPercent 1.0   # Start with 1% risk" -ForegroundColor Gray
    Write-Host "   .\auto-trading-controller.ps1 -Start -MaxPositions 2    # Start with max 2 positions" -ForegroundColor Gray
}