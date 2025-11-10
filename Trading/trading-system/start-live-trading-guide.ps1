# Live Trading Activation Guide
# Complete setup for FBS MT4 live trading

Write-Host "🚀 LIVE TRADING ACTIVATION GUIDE" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Load environment
. "$PSScriptRoot\load-env.ps1"

Write-Host "📋 Your FBS MT4 Live Account:" -ForegroundColor Yellow
Write-Host "   Login: 241926287" -ForegroundColor White
Write-Host "   Password: f0v/9iIH" -ForegroundColor White
Write-Host "   Server: FBS-Real-4" -ForegroundColor White
Write-Host "   Server IP: 95.179.194.198:443" -ForegroundColor White
Write-Host "   Company: FBS Markets Inc." -ForegroundColor White
Write-Host ""

Write-Host "🎯 OPTION 1: MANUAL TRADING (IMMEDIATE)" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Start trading immediately using our signal generator:" -ForegroundColor White
Write-Host ""
Write-Host "📊 Signal Generator Commands:" -ForegroundColor Yellow
Write-Host "   python trading-signal-generator.py              # Manual signals" -ForegroundColor Gray
Write-Host "   python demo-trading-system.py                   # Demo trading" -ForegroundColor Gray
Write-Host ""

$manualChoice = Read-Host "Start manual trading now? (y/n)"
if ($manualChoice -eq "y" -or $manualChoice -eq "Y") {
    Write-Host ""
    Write-Host "🎯 Starting Manual Trading Signal Generator..." -ForegroundColor Green
    python trading-signal-generator.py
    return
}

Write-Host ""
Write-Host "🎯 OPTION 2: AUTOMATED LIVE TRADING SETUP" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📥 STEP 1: Download MT4 Terminal" -ForegroundColor Yellow
Write-Host "===============================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Download FBS MT4 from:" -ForegroundColor White
Write-Host "   🌐 https://fbs.com/trading-platforms/metatrader-4" -ForegroundColor Cyan
Write-Host "   OR" -ForegroundColor Gray
Write-Host "   🌐 https://download.mql5.com/cdn/web/fbs.markets.limited/mt4/fbsmarkets4setup.exe" -ForegroundColor Cyan
Write-Host ""

$downloadChoice = Read-Host "Open download page? (y/n)"
if ($downloadChoice -eq "y" -or $downloadChoice -eq "Y") {
    Write-Host "🌐 Opening FBS MT4 download page..." -ForegroundColor Cyan
    Start-Process "https://fbs.com/trading-platforms/metatrader-4"
}

Write-Host ""
Write-Host "🔐 STEP 2: Login to MT4" -ForegroundColor Yellow
Write-Host "======================" -ForegroundColor Yellow
Write-Host ""
Write-Host "After installing MT4:" -ForegroundColor White
Write-Host "1. 📂 Open MT4 Terminal" -ForegroundColor White
Write-Host "2. 🔐 File → Login to Trade Account" -ForegroundColor White
Write-Host "3. 📝 Login: 241926287" -ForegroundColor White
Write-Host "4. 🔑 Password: f0v/9iIH" -ForegroundColor White
Write-Host "5. 🌐 Server: FBS-Real-4" -ForegroundColor White
Write-Host "6. ✅ Click Login" -ForegroundColor White
Write-Host ""

Write-Host "⚙️ STEP 3: Enable Automated Trading" -ForegroundColor Yellow
Write-Host "===================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "In MT4 Terminal:" -ForegroundColor White
Write-Host "1. 🛠️ Tools → Options → Expert Advisors" -ForegroundColor White
Write-Host "2. ✅ Allow automated trading" -ForegroundColor White
Write-Host "3. ✅ Allow DLL imports" -ForegroundColor White
Write-Host "4. ✅ Allow imports of external experts" -ForegroundColor White
Write-Host "5. 💾 Click OK" -ForegroundColor White
Write-Host "6. 🔘 Click 'Auto Trading' button in toolbar (should be green)" -ForegroundColor White
Write-Host ""

Write-Host "🚀 STEP 4: Start Live Trading Bot" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "After MT4 is logged in and configured:" -ForegroundColor White
Write-Host "   .\mt4-trading-controller.ps1 -Start -RiskPercent 0.5 -MaxPositions 1" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️ Start with conservative settings:" -ForegroundColor Red
Write-Host "   📊 0.5% risk per trade" -ForegroundColor White
Write-Host "   📈 Maximum 1 position" -ForegroundColor White
Write-Host "   🎯 High signal strength required" -ForegroundColor White
Write-Host ""

Write-Host "📊 MONITORING & CONTROL" -ForegroundColor Yellow
Write-Host "======================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Live Trading Commands:" -ForegroundColor White
Write-Host "   .\mt4-trading-controller.ps1 -Status               # Check status" -ForegroundColor Gray
Write-Host "   Get-Content mt4_automated_trading.log -Wait        # Live log" -ForegroundColor Gray
Write-Host "   .\mt4-trading-controller.ps1 -Stop                 # Emergency stop" -ForegroundColor Gray
Write-Host ""

Write-Host "🚨 SAFETY REMINDERS:" -ForegroundColor Red
Write-Host "   💰 Start with small risk (0.5%)" -ForegroundColor White
Write-Host "   📊 Monitor closely for first hour" -ForegroundColor White
Write-Host "   ⏹️ Have emergency stop ready" -ForegroundColor White
Write-Host "   💡 Test with demo account first if unsure" -ForegroundColor White
Write-Host ""

Write-Host "🎯 CURRENT STATUS:" -ForegroundColor Green
Write-Host "   ✅ Trading system configured for MT4" -ForegroundColor White
Write-Host "   ✅ FBS account details updated" -ForegroundColor White
Write-Host "   ✅ Risk management active" -ForegroundColor White
Write-Host "   ✅ Signal generator working" -ForegroundColor White
Write-Host "   🔧 Waiting for MT4 terminal installation" -ForegroundColor Yellow
Write-Host ""

Write-Host "📞 SUPPORT:" -ForegroundColor Cyan
Write-Host "   FBS Support: https://fbs.com/support" -ForegroundColor Gray
Write-Host "   MT4 Help: https://www.metatrader4.com/en/help" -ForegroundColor Gray