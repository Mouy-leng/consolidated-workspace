# Manual MT5 Setup and Connection Helper
# Helps troubleshoot and manually configure MT5 for FBS account

Write-Host "🔧 MT5 Manual Setup Helper" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host ""

# Your FBS Account Details
Write-Host "📋 Your FBS Account Details:" -ForegroundColor Yellow
Write-Host "   Login: 40933210" -ForegroundColor White
Write-Host "   Password: 8IA.KFIB" -ForegroundColor White
Write-Host "   Server: FBS-Real" -ForegroundColor White
Write-Host "   Server IP: 185.237.98.177:443" -ForegroundColor White
Write-Host ""

# Check if MT5 is installed
$mt5Paths = @(
    "C:\Program Files\MetaTrader 5\terminal64.exe",
    "C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
    "$env:APPDATA\MetaQuotes\Terminal\*\terminal64.exe"
)

$mt5Found = $false
foreach ($path in $mt5Paths) {
    if (Test-Path $path) {
        Write-Host "✅ MT5 found at: $path" -ForegroundColor Green
        $mt5Found = $true
        $mt5Path = $path
        break
    }
}

if (-not $mt5Found) {
    Write-Host "❌ MT5 Terminal not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 Download MT5 from:" -ForegroundColor Yellow
    Write-Host "   https://www.metatrader5.com/en/download" -ForegroundColor Cyan
    Write-Host "   OR" -ForegroundColor Gray
    Write-Host "   https://fbs.com/trading-platforms/metatrader-5" -ForegroundColor Cyan
    Write-Host ""
    
    $download = Read-Host "Download MT5 now? (y/n)"
    if ($download -eq "y" -or $download -eq "Y") {
        Write-Host "🌐 Opening download page..." -ForegroundColor Cyan
        Start-Process "https://www.metatrader5.com/en/download"
    }
    exit
}

# Start MT5 if not running
$mt5Process = Get-Process -Name "terminal64" -ErrorAction SilentlyContinue
if (-not $mt5Process) {
    Write-Host "🚀 Starting MT5 Terminal..." -ForegroundColor Cyan
    Start-Process -FilePath $mt5Path
    Start-Sleep -Seconds 5
}

Write-Host "📋 Manual Setup Steps:" -ForegroundColor Yellow
Write-Host "1. 🔐 In MT5, go to File → Login to Trade Account" -ForegroundColor White
Write-Host "2. 📝 Enter your login: 40933210" -ForegroundColor White
Write-Host "3. 🔑 Enter your password: 8IA.KFIB" -ForegroundColor White
Write-Host "4. 🌐 Select server: FBS-Real" -ForegroundColor White
Write-Host "   (If not in list, add manually: 185.237.98.177:443)" -ForegroundColor Gray
Write-Host "5. ✅ Click OK to connect" -ForegroundColor White
Write-Host ""

Write-Host "⚙️ Enable Automated Trading:" -ForegroundColor Yellow
Write-Host "1. 🛠️ Go to Tools → Options → Expert Advisors" -ForegroundColor White
Write-Host "2. ✅ Check 'Allow automated trading'" -ForegroundColor White
Write-Host "3. ✅ Check 'Allow DLL imports'" -ForegroundColor White
Write-Host "4. ✅ Check 'Allow imports of external experts'" -ForegroundColor White
Write-Host "5. 💾 Click OK to save" -ForegroundColor White
Write-Host ""

Write-Host "🔍 Verify Connection:" -ForegroundColor Yellow
Write-Host "1. 📊 Check connection status in MT5 (bottom right)" -ForegroundColor White
Write-Host "2. 💰 Verify account balance is displayed" -ForegroundColor White
Write-Host "3. 📈 Check that symbols load (XAUUSD, EURUSD, etc.)" -ForegroundColor White
Write-Host ""

Write-Host "🚨 Common Issues & Solutions:" -ForegroundColor Red
Write-Host "❌ 'Invalid account' → Check login number and server" -ForegroundColor Gray
Write-Host "❌ 'Authorization failed' → Check password and server" -ForegroundColor Gray
Write-Host "❌ 'Connection timeout' → Check internet and server address" -ForegroundColor Gray
Write-Host "❌ 'Server not found' → Manually add server 185.237.98.177:443" -ForegroundColor Gray
Write-Host ""

$continue = Read-Host "Press Enter when MT5 is connected and ready..."

# Test connection again
Write-Host "🔄 Testing connection..." -ForegroundColor Cyan
python test-mt5-connection.py

Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Green
Write-Host "If connection test passed:" -ForegroundColor White
Write-Host "   .\auto-trading-controller.ps1 -Start" -ForegroundColor Cyan
Write-Host ""
Write-Host "If still having issues:" -ForegroundColor White
Write-Host "   1. Double-check MT5 login credentials" -ForegroundColor Gray
Write-Host "   2. Verify automated trading is enabled" -ForegroundColor Gray
Write-Host "   3. Check internet connection" -ForegroundColor Gray
Write-Host "   4. Contact FBS support if needed" -ForegroundColor Gray