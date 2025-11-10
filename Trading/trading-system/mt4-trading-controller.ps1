# MT4 Automated Trading Controller
# Controls the MT4 automated trading bot

param(
    [string]$Action = "status",
    [switch]$Start = $false,
    [switch]$Stop = $false,
    [switch]$Status = $false,
    [decimal]$RiskPercent = 1.0,
    [int]$MaxPositions = 2,
    [decimal]$MinSignalStrength = 0.8
)

Write-Host "🎯 MT4 AUTOMATED TRADING CONTROLLER" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host ""

$botScript = "mt4-automated-trading-system.py"
$logFile = "mt4_automated_trading.log"

# Load environment
. "$PSScriptRoot\load-env.ps1"

# FBS MT4 Account Details
Write-Host "📋 FBS MT4 Account Details:" -ForegroundColor Yellow
Write-Host "   Login: 241926287" -ForegroundColor White
Write-Host "   Server: FBS-Real-4" -ForegroundColor White
Write-Host "   Server IP: 95.179.194.198:443" -ForegroundColor White
Write-Host "   Company: FBS Markets Inc." -ForegroundColor White
Write-Host ""

function Show-BotStatus {
    Write-Host "📊 MT4 Bot Status Check:" -ForegroundColor Yellow
    
    # Check if Python process is running the MT4 bot
    $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
        $_.MainWindowTitle -like "*mt4*" -or 
        $_.ProcessName -eq "python"
    }
    
    if ($pythonProcesses) {
        Write-Host "   ✅ MT4 automated trading bot: RUNNING" -ForegroundColor Green
        $pythonProcesses | ForEach-Object {
            Write-Host "      PID: $($_.Id) | CPU: $($_.CPU)" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "   ❌ MT4 automated trading bot: NOT RUNNING" -ForegroundColor Red
    }
    
    # Check MT4 terminal
    $mt4Process = Get-Process -Name "terminal" -ErrorAction SilentlyContinue
    if (-not $mt4Process) {
        $mt4Process = Get-Process -Name "metatrader" -ErrorAction SilentlyContinue
    }
    
    if ($mt4Process) {
        Write-Host "   ✅ MT4 Terminal: RUNNING (PID: $($mt4Process.Id))" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ MT4 Terminal: NOT RUNNING" -ForegroundColor Red
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

function Start-MT4TradingBot {
    Write-Host "🚀 Starting MT4 Automated Trading Bot..." -ForegroundColor Cyan
    Write-Host ""
    
    # Check if bot script exists
    if (-not (Test-Path $botScript)) {
        Write-Host "❌ MT4 trading script not found: $botScript" -ForegroundColor Red
        return
    }
    
    # Validate parameters
    Write-Host "⚙️ Configuration:" -ForegroundColor Yellow
    Write-Host "   Risk per trade: $RiskPercent%" -ForegroundColor White
    Write-Host "   Max positions: $MaxPositions" -ForegroundColor White
    Write-Host "   Min signal strength: $MinSignalStrength" -ForegroundColor White
    Write-Host ""
    
    # Safety confirmation
    Write-Host "⚠️  LIVE TRADING WARNING:" -ForegroundColor Red
    Write-Host "   🚨 This will trade with REAL MONEY on MT4 account 241926287" -ForegroundColor Red
    Write-Host "   🚨 Bot will automatically place and manage trades" -ForegroundColor Red
    Write-Host "   🚨 Maximum risk: $RiskPercent% per trade" -ForegroundColor Red
    Write-Host "   🚨 Server: FBS-Real-4 (95.179.194.198:443)" -ForegroundColor Red
    Write-Host ""
    
    $confirmation = Read-Host "Type 'START MT4 TRADING' to begin (case sensitive)"
    if ($confirmation -ne "START MT4 TRADING") {
        Write-Host "❌ MT4 automated trading cancelled" -ForegroundColor Yellow
        return
    }
    
    # Start the bot
    Write-Host "▶️ Starting MT4 trading bot..." -ForegroundColor Green
    
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
            Write-Host "✅ MT4 automated trading bot started successfully!" -ForegroundColor Green
            Write-Host "   📊 Monitor with: .\mt4-trading-controller.ps1 -Status" -ForegroundColor Cyan
            Write-Host "   📄 View logs: Get-Content $logFile -Wait" -ForegroundColor Cyan
            Write-Host "   ⏹️ Stop with: .\mt4-trading-controller.ps1 -Stop" -ForegroundColor Cyan
        }
        else {
            Write-Host "❌ Failed to start MT4 trading bot" -ForegroundColor Red
        }
        
    }
    catch {
        Write-Host "❌ Error starting MT4 bot: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Stop-MT4TradingBot {
    Write-Host "⏹️ Stopping MT4 Automated Trading Bot..." -ForegroundColor Yellow
    
    # Find and stop Python processes running the MT4 bot
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
        Write-Host "✅ MT4 automated trading bot stopped" -ForegroundColor Green
    }
    else {
        Write-Host "   ℹ️ No MT4 trading bot processes found" -ForegroundColor Gray
    }
}

function Show-MT4TradingLog {
    param([int]$Lines = 20)
    
    if (Test-Path $logFile) {
        Write-Host "📄 MT4 Trading Log (Last $Lines lines):" -ForegroundColor Yellow
        Write-Host "=======================================" -ForegroundColor Yellow
        Get-Content $logFile -Tail $Lines
    }
    else {
        Write-Host "❌ Log file not found: $logFile" -ForegroundColor Red
    }
}

function Start-MT4Terminal {
    Write-Host "🏢 Starting MT4 Terminal..." -ForegroundColor Cyan
    
    # Common MT4 installation paths
    $mt4Paths = @(
        "C:\Program Files\MetaTrader 4\terminal.exe",
        "C:\Program Files (x86)\MetaTrader 4\terminal.exe",
        "C:\Program Files\FBS MetaTrader 4\terminal.exe",
        "C:\Program Files (x86)\FBS MetaTrader 4\terminal.exe"
    )
    
    $mt4Found = $false
    foreach ($path in $mt4Paths) {
        if (Test-Path $path) {
            Write-Host "✅ MT4 found at: $path" -ForegroundColor Green
            Start-Process -FilePath $path
            $mt4Found = $true
            break
        }
    }
    
    if (-not $mt4Found) {
        Write-Host "❌ MT4 Terminal not found!" -ForegroundColor Red
        Write-Host "   Please download MT4 from: https://fbs.com/trading-platforms/metatrader-4" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "📋 Manual Setup Required:" -ForegroundColor Yellow
        Write-Host "   1. Download and install MT4" -ForegroundColor White
        Write-Host "   2. Login with: 241926287 / f0v/9iIH" -ForegroundColor White
        Write-Host "   3. Server: FBS-Real-4" -ForegroundColor White
        Write-Host "   4. Enable automated trading" -ForegroundColor White
    }
    else {
        Write-Host ""
        Write-Host "📋 Next Steps:" -ForegroundColor Yellow
        Write-Host "   1. Login to MT4 with account 241926287" -ForegroundColor White
        Write-Host "   2. Password: f0v/9iIH" -ForegroundColor White
        Write-Host "   3. Server: FBS-Real-4" -ForegroundColor White
        Write-Host "   4. Enable Expert Advisors/Auto Trading" -ForegroundColor White
    }
}

# Main execution logic
if ($Start) {
    Start-MT4TradingBot
}
elseif ($Stop) {
    Stop-MT4TradingBot
}
elseif ($Status -or $Action -eq "status") {
    Show-BotStatus
}
elseif ($Action -eq "log") {
    Show-MT4TradingLog
}
elseif ($Action -eq "start-mt4") {
    Start-MT4Terminal
}
else {
    Write-Host "🎯 MT4 Trading Controller Usage:" -ForegroundColor Yellow
    Write-Host "   .\mt4-trading-controller.ps1 -Start                    # Start MT4 automated trading" -ForegroundColor Gray
    Write-Host "   .\mt4-trading-controller.ps1 -Stop                     # Stop MT4 automated trading" -ForegroundColor Gray
    Write-Host "   .\mt4-trading-controller.ps1 -Status                   # Check status" -ForegroundColor Gray
    Write-Host "   .\mt4-trading-controller.ps1 -Action log               # View trading log" -ForegroundColor Gray
    Write-Host "   .\mt4-trading-controller.ps1 -Action start-mt4         # Start MT4 terminal" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🔧 Configuration Options:" -ForegroundColor Yellow
    Write-Host "   -RiskPercent 1.5                                       # Set risk per trade (default: 1%)" -ForegroundColor Gray
    Write-Host "   -MaxPositions 3                                        # Set max open positions (default: 2)" -ForegroundColor Gray
    Write-Host "   -MinSignalStrength 0.9                                 # Set min signal strength (default: 0.8)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⚠️  Examples:" -ForegroundColor Yellow
    Write-Host "   .\mt4-trading-controller.ps1 -Start -RiskPercent 0.5   # Start with 0.5% risk" -ForegroundColor Gray
    Write-Host "   .\mt4-trading-controller.ps1 -Start -MaxPositions 1    # Start with max 1 position" -ForegroundColor Gray
    Write-Host ""
    Show-BotStatus
}