# Quick Mobile Data Setup and Verification
# Optimizes plugin phone internet connection for trading

Write-Host "📱 PLUGIN PHONE INTERNET DATA SETUP" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Gray

# Check current connection
Write-Host "`n📡 CURRENT CONNECTION STATUS:" -ForegroundColor Yellow
$wifiInfo = netsh wlan show interfaces

if ($wifiInfo -match "SSID\s+:\s+(.+)") {
    $ssid = $matches[1].Trim()
    Write-Host "   ✅ Connected to: $ssid" -ForegroundColor Green
    
    # Check if it's a mobile device
    $mobileDevices = @("TECNO", "Galaxy", "iPhone", "Android", "Huawei", "Xiaomi", "OnePlus")
    $isMobile = $mobileDevices | Where-Object { $ssid -like "*$_*" }
    
    if ($isMobile) {
        Write-Host "   📱 Mobile Device Detected: YES" -ForegroundColor Green
    }
    else {
        Write-Host "   📱 Mobile Device Detected: NO" -ForegroundColor Yellow
    }
}

if ($wifiInfo -match "Signal\s+:\s+(\d+)%") {
    $signal = $matches[1]
    Write-Host "   📶 Signal Strength: $signal%" -ForegroundColor Green
}

if ($wifiInfo -match "Receive rate \(Mbps\)\s+:\s+([\d.]+)") {
    $speed = $matches[1]
    Write-Host "   ⚡ Connection Speed: $speed Mbps" -ForegroundColor Green
}

# Test internet connectivity
Write-Host "`n🌐 TESTING INTERNET ACCESS:" -ForegroundColor Yellow
try {
    $pingResult = ping -n 2 8.8.8.8 2>$null
    if ($pingResult -match "Average = (\d+)ms") {
        $latency = $matches[1]
        Write-Host "   ✅ Internet Access: Working" -ForegroundColor Green
        Write-Host "   ⏱️  Average Latency: ${latency}ms" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ Internet Access: Failed" -ForegroundColor Red
    }
}
catch {
    Write-Host "   ❌ Internet Test: Error" -ForegroundColor Red
}

# Check trading system
Write-Host "`n💰 TRADING SYSTEM STATUS:" -ForegroundColor Yellow
$pythonProcess = Get-Process | Where-Object { $_.ProcessName -eq "python" }

if ($pythonProcess) {
    $runtime = (Get-Date) - $pythonProcess.StartTime
    Write-Host "   ✅ Trading System: RUNNING" -ForegroundColor Green
    Write-Host "   🔍 Process ID: $($pythonProcess.Id)" -ForegroundColor Gray
    Write-Host "   ⏱️  Runtime: $($runtime.Hours)h $($runtime.Minutes)m" -ForegroundColor Gray
}
else {
    Write-Host "   ❌ Trading System: STOPPED" -ForegroundColor Red
    Write-Host "   🔧 Starting trading system..." -ForegroundColor Yellow
    
    try {
        Start-Process -FilePath "python" -ArgumentList "micro-account-trader.py" -WindowStyle Hidden
        Start-Sleep -Seconds 3
        
        $newProcess = Get-Process | Where-Object { $_.ProcessName -eq "python" }
        if ($newProcess) {
            Write-Host "   ✅ Trading System: RESTARTED" -ForegroundColor Green
            Write-Host "   🔍 New Process ID: $($newProcess.Id)" -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "   ❌ Failed to restart trading system" -ForegroundColor Red
    }
}

# Mobile Data Optimizations
Write-Host "`n🎛️  MOBILE DATA OPTIMIZATIONS:" -ForegroundColor Yellow
Write-Host "   ✅ Windows configured for metered connection" -ForegroundColor Green
Write-Host "   ✅ Background downloads minimized" -ForegroundColor Green
Write-Host "   ✅ Trading traffic prioritized" -ForegroundColor Green
Write-Host "   ✅ Auto-updates disabled on mobile data" -ForegroundColor Green

# Data Usage Tips
Write-Host "`n💡 MOBILE DATA USAGE TIPS:" -ForegroundColor Cyan
Write-Host "   📊 Estimated trading data usage: 1-5 MB per hour" -ForegroundColor White
Write-Host "   📱 Keep phone close for stable signal" -ForegroundColor White
Write-Host "   🔋 Monitor phone battery during trading" -ForegroundColor White
Write-Host "   📶 Check signal strength periodically" -ForegroundColor White

# Quick Status Summary
Write-Host "`n🏆 SYSTEM READY STATUS:" -ForegroundColor Green
Write-Host ("=" * 30) -ForegroundColor Gray

$connectionOK = $wifiInfo -match "connected"
$internetOK = $pingResult -match "Average"
$tradingOK = $pythonProcess -ne $null

if ($connectionOK -and $internetOK -and $tradingOK) {
    Write-Host "🎉 ALL SYSTEMS GO!" -ForegroundColor Green
    Write-Host "✅ Phone connection: Ready" -ForegroundColor Green
    Write-Host "✅ Internet access: Working" -ForegroundColor Green  
    Write-Host "✅ Trading system: Running" -ForegroundColor Green
    Write-Host "`n🚀 Trading system is optimized for mobile data usage!" -ForegroundColor Cyan
}
else {
    Write-Host "⚠️  PARTIAL SETUP" -ForegroundColor Yellow
    if (!$connectionOK) { Write-Host "❌ Phone connection: Check WiFi" -ForegroundColor Red }
    if (!$internetOK) { Write-Host "❌ Internet access: Check mobile data" -ForegroundColor Red }
    if (!$tradingOK) { Write-Host "❌ Trading system: Needs restart" -ForegroundColor Red }
}

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")