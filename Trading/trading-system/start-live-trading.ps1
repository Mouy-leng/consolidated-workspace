# Live Trading Setup - Step by Step Guide
# Comprehensive setup for FBS live trading account

Write-Host "🚀 LIVE TRADING SETUP" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host ""

# Load environment
. "$PSScriptRoot\load-env.ps1"

Write-Host "📋 Your FBS Live Account Details:" -ForegroundColor Yellow
Write-Host "   Login: 40933210" -ForegroundColor White
Write-Host "   Password: 8IA.KFIB" -ForegroundColor White
Write-Host "   Server: FBS-Real" -ForegroundColor White
Write-Host "   Server IP: 185.237.98.177:443" -ForegroundColor White
Write-Host ""

Write-Host "🔧 STEP 1: Verify MT5 Installation" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check MT5 installation
$mt5Paths = @(
    "C:\Program Files\MetaTrader 5\terminal64.exe",
    "C:\Program Files (x86)\MetaTrader 5\terminal64.exe"
)

$mt5Found = $false
$mt5Path = ""

foreach ($path in $mt5Paths) {
    if (Test-Path $path) {
        Write-Host "✅ MT5 found at: $path" -ForegroundColor Green
        $mt5Found = $true
        $mt5Path = $path
        break
    }
}

if (-not $mt5Found) {
    Write-Host "❌ MT5 not found. Please install MT5 first." -ForegroundColor Red
    Write-Host "   Download from: https://www.metatrader5.com/en/download" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "🏢 STEP 2: Start MT5 Terminal" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan

# Check if MT5 is running
$mt5Process = Get-Process -Name "terminal64" -ErrorAction SilentlyContinue

if (-not $mt5Process) {
    Write-Host "🚀 Starting MT5 Terminal..." -ForegroundColor Yellow
    Start-Process -FilePath $mt5Path -ArgumentList "/server:FBS-Real"
    Start-Sleep -Seconds 8
    
    $mt5Process = Get-Process -Name "terminal64" -ErrorAction SilentlyContinue
    if ($mt5Process) {
        Write-Host "✅ MT5 Terminal started (PID: $($mt5Process.Id))" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Failed to start MT5 Terminal" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "✅ MT5 Terminal already running (PID: $($mt5Process.Id))" -ForegroundColor Green
}

Write-Host ""
Write-Host "🔐 STEP 3: Manual Login to FBS Account" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 IMPORTANT: You must manually login to MT5 first!" -ForegroundColor Red
Write-Host ""
Write-Host "In the MT5 Terminal window:" -ForegroundColor Yellow
Write-Host "1. 📂 Click 'File' → 'Login to Trade Account'" -ForegroundColor White
Write-Host "2. 📝 Enter Login: 40933210" -ForegroundColor White
Write-Host "3. 🔑 Enter Password: 8IA.KFIB" -ForegroundColor White
Write-Host "4. 🌐 Select Server: FBS-Real" -ForegroundColor White
Write-Host "   (If FBS-Real not in list, click 'Scan' or add manually)" -ForegroundColor Gray
Write-Host "5. ✅ Click 'OK' to connect" -ForegroundColor White
Write-Host ""
Write-Host "🔧 If server not found:" -ForegroundColor Yellow
Write-Host "   - Click 'Cancel' and go to File → 'Open an Account'" -ForegroundColor Gray
Write-Host "   - Click 'Add Broker' and enter: 185.237.98.177:443" -ForegroundColor Gray
Write-Host "   - Search for FBS and select FBS-Real server" -ForegroundColor Gray
Write-Host ""

$loginDone = Read-Host "Press Enter when you've successfully logged into MT5"

Write-Host ""
Write-Host "⚙️ STEP 4: Enable Automated Trading" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "In MT5 Terminal:" -ForegroundColor Yellow
Write-Host "1. 🛠️ Go to Tools → Options" -ForegroundColor White
Write-Host "2. 📂 Click 'Expert Advisors' tab" -ForegroundColor White
Write-Host "3. ✅ Check 'Allow automated trading'" -ForegroundColor White
Write-Host "4. ✅ Check 'Allow DLL imports'" -ForegroundColor White
Write-Host "5. ✅ Check 'Allow imports of external experts'" -ForegroundColor White
Write-Host "6. ✅ Check 'Allow WebRequest for listed URL'" -ForegroundColor White
Write-Host "7. 💾 Click 'OK'" -ForegroundColor White
Write-Host ""
Write-Host "🔄 Also check that 'Auto Trading' button is enabled in toolbar" -ForegroundColor White
Write-Host "   (Should show green icon, not red)" -ForegroundColor Gray
Write-Host ""

$settingsDone = Read-Host "Press Enter when automated trading is enabled"

Write-Host ""
Write-Host "🧪 STEP 5: Test Connection" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

Write-Host "Testing MT5 connection..." -ForegroundColor Yellow
python test-mt5-connection.py

Write-Host ""
Write-Host "🚀 STEP 6: Start Live Trading" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan

Write-Host "🚨 FINAL WARNING:" -ForegroundColor Red
Write-Host "   You are about to start LIVE TRADING with REAL MONEY!" -ForegroundColor Red
Write-Host "   Account: 40933210 on FBS-Real server" -ForegroundColor Red
Write-Host "   Risk per trade: 2% of account balance" -ForegroundColor Red
Write-Host "   Max open positions: 3" -ForegroundColor Red
Write-Host ""

$confirmation = Read-Host "Type 'START LIVE TRADING' to begin (case sensitive)"

if ($confirmation -eq "START LIVE TRADING") {
    Write-Host ""
    Write-Host "🚀 Starting Live Trading System..." -ForegroundColor Green
    
    # Start with conservative settings for live trading
    .\auto-trading-controller.ps1 -Start -RiskPercent 1.0 -MaxPositions 2 -MinSignalStrength 0.8
    
}
else {
    Write-Host ""
    Write-Host "❌ Live trading cancelled. Use demo mode instead:" -ForegroundColor Yellow
    Write-Host "   python demo-trading-system.py" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "📊 Live Trading Commands:" -ForegroundColor Green
Write-Host "   .\auto-trading-controller.ps1 -Status      # Check status" -ForegroundColor Gray
Write-Host "   .\auto-trading-controller.ps1 -Action monitor # Live monitor" -ForegroundColor Gray
Write-Host "   .\auto-trading-controller.ps1 -Stop        # Emergency stop" -ForegroundColor Gray
Write-Host "   Get-Content automated_trading.log -Wait    # View live log" -ForegroundColor Gray