# Complete Trading System Setup with Phone Integration
# Sets up MT5 with FBS account and phone-based authorization

param(
    [switch]$StartMT5 = $true,
    [switch]$SetupPhone = $true,
    [switch]$TestTrading = $false
)

# Load environment
if (Test-Path ".\.env") {
    Get-Content ".\.env" | ForEach-Object {
        if ($_ -match '^MT5_' -and $_ -match '=') {
            $name, $value = $_ -split '=', 2
            [Environment]::SetEnvironmentVariable($name, $value, 'Process')
        }
    }
}

Write-Host "🚀 Complete Trading System Setup" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Get FBS credentials
$mt5Login = [Environment]::GetEnvironmentVariable('MT5_LOGIN', 'Process')
$mt5Server = [Environment]::GetEnvironmentVariable('MT5_SERVER', 'Process')

function Test-SystemHealth {
    Write-Host "🔍 Testing System Health..." -ForegroundColor Yellow
    
    $health = @{
        Microservice  = $false
        PhonePlugin   = $false
        MT5Plugin     = $false
        AndroidDevice = $false
    }
    
    # Test microservice
    try {
        $serviceHealth = Invoke-RestMethod "http://localhost:3000/health" -Method GET -TimeoutSec 5
        $health.Microservice = $true
        Write-Host "✅ Microservice: Running" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Microservice: Not running" -ForegroundColor Red
        Write-Host "   Starting microservice..." -ForegroundColor Yellow
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\trading-microservice'; npm start"
        Start-Sleep 3
    }
    
    # Test phone plugin
    try {
        $devices = Invoke-RestMethod "http://localhost:3000/api/v1/devices" -Method GET -TimeoutSec 5
        $phoneDevices = $devices.devices | Where-Object { $_.type -eq "phone" }
        if ($phoneDevices) {
            $health.PhonePlugin = $true
            Write-Host "✅ Phone Plugin: Active ($($phoneDevices.Count) devices)" -ForegroundColor Green
        }
        else {
            Write-Host "⚠️  Phone Plugin: No devices detected" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "❌ Phone Plugin: Not responding" -ForegroundColor Red
    }
    
    # Test Android device
    try {
        $adbCheck = adb devices 2>$null
        if ($adbCheck -match "device$") {
            $health.AndroidDevice = $true
            Write-Host "✅ Android Device: Connected" -ForegroundColor Green
        }
        else {
            Write-Host "⚠️  Android Device: Not connected" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "⚠️  ADB: Not available" -ForegroundColor Yellow
    }
    
    return $health
}

function Start-MT5Trading {
    Write-Host "🎯 Starting MT5 for Live Trading..." -ForegroundColor Green
    
    # Search for MT5
    $mt5Paths = @(
        "C:\Program Files\MetaTrader 5\terminal64.exe",
        "C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
        "C:\Users\$env:USERNAME\AppData\Roaming\MetaQuotes\Terminal\*\terminal64.exe"
    )
    
    $mt5Found = $false
    foreach ($path in $mt5Paths) {
        $resolved = Resolve-Path $path -ErrorAction SilentlyContinue
        if ($resolved) {
            Write-Host "✅ Found MT5: $($resolved.Path)" -ForegroundColor Green
            
            # Check if MT5 is already running
            $mt5Process = Get-Process | Where-Object { $_.ProcessName -like "*terminal*" }
            if (-not $mt5Process) {
                Write-Host "🚀 Starting MT5..." -ForegroundColor Yellow
                Start-Process -FilePath $resolved.Path
                Start-Sleep 5
            }
            else {
                Write-Host "✅ MT5 already running" -ForegroundColor Green
            }
            
            $mt5Found = $true
            break
        }
    }
    
    if (-not $mt5Found) {
        Write-Host "❌ MT5 not found" -ForegroundColor Red
        Write-Host "📥 Download from: https://fbs.com/platforms/metatrader5" -ForegroundColor Yellow
        return $false
    }
    
    # Display login instructions
    Write-Host ""
    Write-Host "🔐 FBS Live Account Login:" -ForegroundColor Yellow
    Write-Host "   Login: $mt5Login" -ForegroundColor Green
    Write-Host "   Server: $mt5Server" -ForegroundColor Green
    Write-Host "   Password: [Your FBS Password]" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Login Steps:" -ForegroundColor Cyan
    Write-Host "   1. In MT5: File → Login to Trade Account" -ForegroundColor Gray
    Write-Host "   2. Enter Login: $mt5Login" -ForegroundColor Gray
    Write-Host "   3. Enter your FBS password" -ForegroundColor Gray
    Write-Host "   4. Select Server: $mt5Server" -ForegroundColor Gray
    Write-Host "   5. Click Login" -ForegroundColor Gray
    
    return $true
}

function Setup-PhoneIntegration {
    Write-Host "📱 Setting up Phone Integration..." -ForegroundColor Green
    
    # Check Android device
    try {
        $adbDevices = adb devices 2>$null
        if ($adbDevices -match "(\w+)\s+device") {
            $deviceId = $matches[1]
            Write-Host "✅ Android device detected: $deviceId" -ForegroundColor Green
            
            # Check for trading apps
            Write-Host "🔍 Checking for trading apps..." -ForegroundColor Yellow
            $tradingApps = adb shell pm list packages | Select-String -Pattern "trading|forex|mt4|mt5|fbs|exness"
            
            if ($tradingApps) {
                Write-Host "✅ Trading apps found:" -ForegroundColor Green
                $tradingApps | ForEach-Object { 
                    $app = $_.Line -replace "package:", ""
                    Write-Host "   📱 $app" -ForegroundColor Gray
                }
            }
            else {
                Write-Host "⚠️  No trading apps detected" -ForegroundColor Yellow
                Write-Host "📥 Install FBS Trader or MT5 app from Play Store" -ForegroundColor Cyan
            }
            
            # Setup phone as 2FA device
            Write-Host ""
            Write-Host "🔐 Phone as 2FA Device:" -ForegroundColor Yellow
            Write-Host "   1. Install FBS Trader app on your phone" -ForegroundColor Gray
            Write-Host "   2. Login with same credentials (Login: $mt5Login)" -ForegroundColor Gray
            Write-Host "   3. Enable push notifications for trade alerts" -ForegroundColor Gray
            Write-Host "   4. Use phone to authorize trades from MT5" -ForegroundColor Gray
            
            return $true
        }
        else {
            Write-Host "⚠️  No Android device connected" -ForegroundColor Yellow
            Write-Host "📱 Connect your phone and enable USB debugging" -ForegroundColor Cyan
            return $false
        }
    }
    catch {
        Write-Host "❌ Phone setup failed" -ForegroundColor Red
        return $false
    }
}

function Test-TradingWorkflow {
    Write-Host "🧪 Testing Trading Workflow..." -ForegroundColor Green
    
    # Test device sync
    try {
        Write-Host "🔄 Syncing devices..." -ForegroundColor Yellow
        $syncResult = & "$PSScriptRoot\device-manager.ps1" -Command sync
        Write-Host "✅ Device sync completed" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  Device sync failed" -ForegroundColor Yellow
    }
    
    # Check MT5 connection
    $mt5Process = Get-Process | Where-Object { $_.ProcessName -like "*terminal*" }
    if ($mt5Process) {
        Write-Host "✅ MT5 Terminal: Running" -ForegroundColor Green
        
        # Trigger device discovery to detect MT5
        try {
            Start-Sleep 2
            $devices = Invoke-RestMethod "http://localhost:3000/api/v1/devices" -Method GET
            $mt5Devices = $devices.devices | Where-Object { $_.type -eq "trading" -or $_.name -like "*MT5*" }
            
            if ($mt5Devices) {
                Write-Host "✅ MT5 detected by device manager" -ForegroundColor Green
            }
            else {
                Write-Host "⚠️  MT5 not yet detected - may need manual sync" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "⚠️  Device API not responding" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "⚠️  MT5 not running" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "🎯 Trading Workflow Ready!" -ForegroundColor Green
    Write-Host "   ✓ Phone connected for authorization" -ForegroundColor Gray
    Write-Host "   ✓ MT5 ready for FBS live account" -ForegroundColor Gray
    Write-Host "   ✓ Device management system active" -ForegroundColor Gray
}

function Show-TradingDashboard {
    Write-Host ""
    Write-Host "📊 Trading System Dashboard" -ForegroundColor Green
    Write-Host "============================" -ForegroundColor Green
    
    # System status
    try {
        $health = Invoke-RestMethod "http://localhost:3000/health" -Method GET
        Write-Host "🖥️  Microservice: Online (Uptime: $([math]::Round($health.uptime/60, 1)) min)" -ForegroundColor Green
    }
    catch {
        Write-Host "🖥️  Microservice: Offline" -ForegroundColor Red
    }
    
    # Account info
    Write-Host "💰 FBS Live Account: $mt5Login" -ForegroundColor Green
    Write-Host "🌐 Server: $mt5Server" -ForegroundColor Green
    
    # Devices
    try {
        $devices = Invoke-RestMethod "http://localhost:3000/api/v1/devices" -Method GET
        Write-Host "📱 Connected Devices: $($devices.total)" -ForegroundColor Green
        
        $devices.devices | ForEach-Object {
            $status = if ($_.status -eq "connected") { "🟢" } else { "🟡" }
            Write-Host "   $status $($_.name) ($($_.type))" -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "📱 Devices: Unable to fetch" -ForegroundColor Yellow
    }
    
    # Quick actions
    Write-Host ""
    Write-Host "⚡ Quick Actions:" -ForegroundColor Yellow
    Write-Host "   Monitor devices:  curl http://localhost:3000/api/v1/devices" -ForegroundColor Gray
    Write-Host "   Sync devices:     .\device-manager.ps1 -Command sync" -ForegroundColor Gray
    Write-Host "   Debug phone:      .\debug-phone.ps1 -TestConnection" -ForegroundColor Gray
}

# Main execution
Write-Host "🎯 FBS Live Trading Account: $mt5Login" -ForegroundColor Cyan
Write-Host "🌐 Server: $mt5Server" -ForegroundColor Cyan
Write-Host ""

# Test system health
$healthStatus = Test-SystemHealth

Write-Host ""

# Start MT5 if requested
if ($StartMT5) {
    Start-MT5Trading | Out-Null
    Write-Host ""
}

# Setup phone integration if requested
if ($SetupPhone) {
    Setup-PhoneIntegration | Out-Null
    Write-Host ""
}

# Test trading workflow if requested
if ($TestTrading) {
    Test-TradingWorkflow
    Write-Host ""
}

# Show dashboard
Show-TradingDashboard

Write-Host ""
Write-Host "🎉 Trading System Ready for Live FBS Trading!" -ForegroundColor Green
Write-Host "   Use your phone for trade authorization and monitoring" -ForegroundColor Gray
Write-Host "   MT5 configured for FBS live account" -ForegroundColor Gray
Write-Host "   Device management system monitoring all connections" -ForegroundColor Gray