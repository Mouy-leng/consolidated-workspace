# Trading System CLI - Live Trading Management Tool
# Complete command-line interface for FBS live trading operations

param(
    [Parameter(Position = 0)]
    [ValidateSet("start", "stop", "status", "monitor", "sync", "test", "login", "debug-phone", "help")]
    [string]$Command = "help",
    
    [switch]$Live = $false,
    [switch]$Force = $false,
    [switch]$Background = $false,
    [int]$Timeout = 30
)

# Global variables
$script:FBS_LOGIN = "40933270"
$script:FBS_SERVER = "FBS-Real"
$script:MICROSERVICE_PORT = 3000

function Write-TradingBanner {
    Write-Host ""
    Write-Host "🚀 FBS LIVE TRADING CLI" -ForegroundColor Green
    Write-Host "=======================" -ForegroundColor Green
    Write-Host "Account: $script:FBS_LOGIN | Server: $script:FBS_SERVER" -ForegroundColor Cyan
    Write-Host "Mode: $(if ($Live) { 'LIVE TRADING' } else { 'DEMO MODE' })" -ForegroundColor $(if ($Live) { "Red" } else { "Yellow" })
    Write-Host ""
}

function Test-Prerequisites {
    Write-Host "🔍 Checking Prerequisites..." -ForegroundColor Yellow
    
    $checks = @{
        "MT5_PATH"         = $false
        "ADB"              = $false
        "ENV_FILE"         = $false
        "MICROSERVICE_DIR" = $false
    }
    
    # Check MT5
    $mt5Paths = @(
        "C:\Program Files\MetaTrader 5\terminal64.exe",
        "C:\Program Files (x86)\MetaTrader 5\terminal64.exe"
    )
    
    foreach ($path in $mt5Paths) {
        if (Test-Path $path) {
            $checks.MT5_PATH = $path
            Write-Host "   ✅ MT5 Found: $path" -ForegroundColor Green
            break
        }
    }
    
    if (-not $checks.MT5_PATH) {
        Write-Host "   ❌ MT5 Not Found" -ForegroundColor Red
        Write-Host "      Download from: https://fbs.com/platforms/metatrader5" -ForegroundColor Yellow
    }
    
    # Check ADB
    try {
        $adbPath = where.exe adb 2>$null
        if ($adbPath) {
            $checks.ADB = $adbPath
            Write-Host "   ✅ ADB Found: $adbPath" -ForegroundColor Green
        }
        else {
            Write-Host "   ⚠️  ADB Not Found (Phone features limited)" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "   ⚠️  ADB Not Available" -ForegroundColor Yellow
    }
    
    # Check environment file
    if (Test-Path ".\.env") {
        $checks.ENV_FILE = $true
        Write-Host "   ✅ Environment File Found" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ Environment File Missing" -ForegroundColor Red
    }
    
    # Check microservice
    if (Test-Path ".\trading-microservice\src\index.js") {
        $checks.MICROSERVICE_DIR = $true
        Write-Host "   ✅ Microservice Directory Found" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ Microservice Directory Missing" -ForegroundColor Red
    }
    
    return $checks
}

function Start-TradingSystem {
    param([bool]$LiveMode = $false)
    
    Write-Host "🚀 Starting Trading System..." -ForegroundColor Green
    if ($LiveMode) {
        Write-Host "⚠️  LIVE TRADING MODE - REAL MONEY AT RISK!" -ForegroundColor Red
        Write-Host "Press Ctrl+C within 5 seconds to cancel..." -ForegroundColor Yellow
        Start-Sleep 5
    }
    
    $startupResults = @{
        Environment  = $false
        Microservice = $false
        MT5          = $false
        Phone        = $false
    }
    
    # Load environment
    Write-Host "📝 Loading Environment..." -ForegroundColor Yellow
    try {
        if (Test-Path ".\.env") {
            Get-Content ".\.env" | ForEach-Object {
                if ($_ -match '=' -and -not $_.StartsWith('#')) {
                    $name, $value = $_ -split '=', 2
                    [Environment]::SetEnvironmentVariable($name, $value, 'Process')
                }
            }
            Write-Host "   ✅ Environment Loaded" -ForegroundColor Green
            $startupResults.Environment = $true
        }
    }
    catch {
        Write-Host "   ❌ Environment Load Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Start microservice
    Write-Host "🖥️  Starting Microservice..." -ForegroundColor Yellow
    try {
        # Check if already running
        try {
            $health = Invoke-RestMethod "http://localhost:$script:MICROSERVICE_PORT/health" -Method GET -TimeoutSec 3
            Write-Host "   ✅ Microservice Already Running" -ForegroundColor Green
            $startupResults.Microservice = $true
        }
        catch {
            # Start new instance
            if ($Background) {
                Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\trading-microservice'; npm start"
            }
            else {
                $job = Start-Job -ScriptBlock {
                    param($dir)
                    Set-Location $dir
                    npm start
                } -ArgumentList "$PWD\trading-microservice"
            }
            
            # Wait for startup
            $retries = 0
            while ($retries -lt 10) {
                Start-Sleep 2
                try {
                    $health = Invoke-RestMethod "http://localhost:$script:MICROSERVICE_PORT/health" -Method GET -TimeoutSec 3
                    Write-Host "   ✅ Microservice Started Successfully" -ForegroundColor Green
                    $startupResults.Microservice = $true
                    break
                }
                catch {
                    $retries++
                    Write-Host "   🔄 Waiting for microservice... ($retries/10)" -ForegroundColor Gray
                }
            }
            
            if (-not $startupResults.Microservice) {
                Write-Host "   ❌ Microservice Failed to Start" -ForegroundColor Red
            }
        }
    }
    catch {
        Write-Host "   ❌ Microservice Startup Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Start MT5
    Write-Host "📈 Starting MT5..." -ForegroundColor Yellow
    try {
        # Check if already running
        $mt5Process = Get-Process | Where-Object { $_.ProcessName -like "*terminal*" }
        if ($mt5Process) {
            Write-Host "   ✅ MT5 Already Running" -ForegroundColor Green
            $startupResults.MT5 = $true
        }
        else {
            $mt5Paths = @(
                "C:\Program Files\MetaTrader 5\terminal64.exe",
                "C:\Program Files (x86)\MetaTrader 5\terminal64.exe"
            )
            
            $mt5Started = $false
            foreach ($path in $mt5Paths) {
                if (Test-Path $path) {
                    Start-Process -FilePath $path
                    Start-Sleep 3
                    
                    $mt5Process = Get-Process | Where-Object { $_.ProcessName -like "*terminal*" }
                    if ($mt5Process) {
                        Write-Host "   ✅ MT5 Started Successfully" -ForegroundColor Green
                        $startupResults.MT5 = $true
                        $mt5Started = $true
                        break
                    }
                }
            }
            
            if (-not $mt5Started) {
                Write-Host "   ❌ MT5 Failed to Start" -ForegroundColor Red
            }
        }
    }
    catch {
        Write-Host "   ❌ MT5 Startup Failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Check phone connection
    Write-Host "📱 Checking Phone Connection..." -ForegroundColor Yellow
    try {
        $adbCheck = adb devices 2>$null
        if ($adbCheck -match "device$") {
            Write-Host "   ✅ Android Phone Connected" -ForegroundColor Green
            $startupResults.Phone = $true
        }
        else {
            Write-Host "   ⚠️  Android Phone Not Connected" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "   ⚠️  ADB Not Available" -ForegroundColor Yellow
    }
    
    # Sync devices
    if ($startupResults.Microservice) {
        Write-Host "🔄 Syncing Devices..." -ForegroundColor Yellow
        try {
            & ".\device-manager.ps1" -Command sync | Out-Null
            Write-Host "   ✅ Device Sync Completed" -ForegroundColor Green
        }
        catch {
            Write-Host "   ⚠️  Device Sync Failed" -ForegroundColor Yellow
        }
    }
    
    return $startupResults
}

function Stop-TradingSystem {
    Write-Host "🛑 Stopping Trading System..." -ForegroundColor Yellow
    
    # Stop microservice
    try {
        Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
        Write-Host "   ✅ Microservice Stopped" -ForegroundColor Green
    }
    catch {
        Write-Host "   ⚠️  No Node.js processes found" -ForegroundColor Yellow
    }
    
    # Optionally stop MT5 (ask user)
    $mt5Process = Get-Process | Where-Object { $_.ProcessName -like "*terminal*" }
    if ($mt5Process) {
        if ($Force) {
            $mt5Process | Stop-Process -Force
            Write-Host "   ✅ MT5 Stopped" -ForegroundColor Green
        }
        else {
            Write-Host "   ⚠️  MT5 Still Running (use -Force to stop)" -ForegroundColor Yellow
        }
    }
    
    Write-Host "   ✅ Trading System Stopped" -ForegroundColor Green
}

function Show-TradingStatus {
    Write-Host "📊 Trading System Status" -ForegroundColor Green
    Write-Host "========================" -ForegroundColor Green
    
    # Microservice status
    try {
        $health = Invoke-RestMethod "http://localhost:$script:MICROSERVICE_PORT/health" -Method GET -TimeoutSec 5
        Write-Host "🖥️  Microservice: ✅ Online (Uptime: $([math]::Round($health.uptime/60, 1)) min)" -ForegroundColor Green
        
        # Get devices
        try {
            $devices = Invoke-RestMethod "http://localhost:$script:MICROSERVICE_PORT/api/v1/devices" -Method GET -TimeoutSec 3
            Write-Host "📱 Devices: $($devices.total) detected" -ForegroundColor Green
            
            if ($devices.total -gt 0) {
                $devices.devices | ForEach-Object {
                    $statusEmoji = switch ($_.status) {
                        "connected" { "🟢" }
                        "syncing" { "🟡" }
                        default { "🔴" }
                    }
                    Write-Host "   $statusEmoji $($_.name) ($($_.type))" -ForegroundColor Gray
                }
            }
        }
        catch {
            Write-Host "📱 Devices: ❌ API not responding" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "🖥️  Microservice: ❌ Offline" -ForegroundColor Red
    }
    
    # MT5 status
    $mt5Process = Get-Process | Where-Object { $_.ProcessName -like "*terminal*" }
    if ($mt5Process) {
        Write-Host "📈 MT5 Terminal: ✅ Running (PID: $($mt5Process.Id))" -ForegroundColor Green
    }
    else {
        Write-Host "📈 MT5 Terminal: ❌ Not running" -ForegroundColor Red
    }
    
    # Phone status
    try {
        $adbCheck = adb devices 2>$null
        if ($adbCheck -match "device$") {
            Write-Host "📱 Android Phone: ✅ Connected" -ForegroundColor Green
        }
        else {
            Write-Host "📱 Android Phone: ⚠️  Not connected" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "📱 Android Phone: ❌ ADB unavailable" -ForegroundColor Red
    }
    
    # Account status
    Write-Host ""
    Write-Host "💰 FBS Account Status:" -ForegroundColor Yellow
    Write-Host "   Login: $script:FBS_LOGIN" -ForegroundColor Green
    Write-Host "   Server: $script:FBS_SERVER" -ForegroundColor Green
    Write-Host "   Mode: $(if ($Live) { 'LIVE TRADING' } else { 'Ready for Live' })" -ForegroundColor $(if ($Live) { "Red" } else { "Yellow" })
}

function Start-LiveMonitoring {
    Write-Host "📊 Starting Live Trading Monitor..." -ForegroundColor Green
    Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Yellow
    Write-Host ""
    
    try {
        & ".\monitor-trading.ps1" -Continuous
    }
    catch {
        Write-Host "❌ Monitor failed to start" -ForegroundColor Red
    }
}

function Test-TradingConnections {
    Write-Host "🧪 Testing Trading Connections..." -ForegroundColor Green
    
    # Test microservice
    Write-Host "Testing microservice..." -ForegroundColor Yellow
    try {
        $health = Invoke-RestMethod "http://localhost:$script:MICROSERVICE_PORT/health" -Method GET -TimeoutSec 5
        Write-Host "   ✅ Microservice: Healthy" -ForegroundColor Green
    }
    catch {
        Write-Host "   ❌ Microservice: Failed" -ForegroundColor Red
    }
    
    # Test phone
    Write-Host "Testing phone connection..." -ForegroundColor Yellow
    try {
        & ".\debug-phone.ps1" -TestConnection | Out-Null
        Write-Host "   ✅ Phone: Connection test completed" -ForegroundColor Green
    }
    catch {
        Write-Host "   ❌ Phone: Test failed" -ForegroundColor Red
    }
    
    # Test device sync
    Write-Host "Testing device sync..." -ForegroundColor Yellow
    try {
        & ".\device-manager.ps1" -Command sync | Out-Null
        Write-Host "   ✅ Device Sync: Completed" -ForegroundColor Green
    }
    catch {
        Write-Host "   ❌ Device Sync: Failed" -ForegroundColor Red
    }
}

function Show-LoginInstructions {
    Write-Host "🔐 FBS Live Account Login Instructions" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 MT5 Login Steps:" -ForegroundColor Yellow
    Write-Host "   1. Open MT5 Terminal" -ForegroundColor Gray
    Write-Host "   2. Click 'File' → 'Login to Trade Account'" -ForegroundColor Gray
    Write-Host "   3. Enter Login: $script:FBS_LOGIN" -ForegroundColor Gray
    Write-Host "   4. Enter your FBS password" -ForegroundColor Gray
    Write-Host "   5. Select Server: $script:FBS_SERVER" -ForegroundColor Gray
    Write-Host "   6. Click 'Login'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📱 Phone App Setup:" -ForegroundColor Yellow
    Write-Host "   1. Install 'FBS Trader' from Google Play Store" -ForegroundColor Gray
    Write-Host "   2. Login with same credentials (Login: $script:FBS_LOGIN)" -ForegroundColor Gray
    Write-Host "   3. Enable push notifications" -ForegroundColor Gray
    Write-Host "   4. Use for trade authorization" -ForegroundColor Gray
}

function Show-Help {
    Write-Host "🚀 FBS Live Trading CLI - Help" -ForegroundColor Green
    Write-Host "==============================" -ForegroundColor Green
    Write-Host ""
    Write-Host "COMMANDS:" -ForegroundColor Yellow
    Write-Host "   start    Start the complete trading system" -ForegroundColor Gray
    Write-Host "   stop     Stop all trading system components" -ForegroundColor Gray
    Write-Host "   status   Show current system status" -ForegroundColor Gray
    Write-Host "   monitor  Start live trading monitor" -ForegroundColor Gray
    Write-Host "   sync     Sync devices and connections" -ForegroundColor Gray
    Write-Host "   test     Test all system connections" -ForegroundColor Gray
    Write-Host "   login    Show FBS login instructions" -ForegroundColor Gray
    Write-Host "   debug-phone Debug phone connection issues" -ForegroundColor Gray
    Write-Host "   help     Show this help message" -ForegroundColor Gray
    Write-Host ""
    Write-Host "OPTIONS:" -ForegroundColor Yellow
    Write-Host "   -Live        Enable live trading mode (REAL MONEY)" -ForegroundColor Gray
    Write-Host "   -Force       Force operations (stop MT5, etc.)" -ForegroundColor Gray
    Write-Host "   -Background  Run microservice in background" -ForegroundColor Gray
    Write-Host "   -Timeout     Set timeout for operations (default: 30s)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "   .\trading-cli.ps1 start -Live         # Start live trading" -ForegroundColor Gray
    Write-Host "   .\trading-cli.ps1 status              # Check system status" -ForegroundColor Gray
    Write-Host "   .\trading-cli.ps1 monitor             # Start monitoring" -ForegroundColor Gray
    Write-Host "   .\trading-cli.ps1 stop -Force         # Force stop everything" -ForegroundColor Gray
}

# Main execution
Write-TradingBanner

switch ($Command.ToLower()) {
    "start" {
        $prereqs = Test-Prerequisites
        if ($prereqs.MT5_PATH -and $prereqs.ENV_FILE -and $prereqs.MICROSERVICE_DIR) {
            $results = Start-TradingSystem -LiveMode $Live
            Write-Host ""
            Write-Host "🎯 Startup Results:" -ForegroundColor Green
            $results.GetEnumerator() | ForEach-Object {
                $status = if ($_.Value) { "✅" } else { "❌" }
                Write-Host "   $status $($_.Key)" -ForegroundColor $(if ($_.Value) { "Green" } else { "Red" })
            }
            
            if ($results.Values -contains $true) {
                Write-Host ""
                Write-Host "🎉 Trading System Started!" -ForegroundColor Green
                if ($Live) {
                    Write-Host "⚠️  LIVE TRADING MODE ACTIVE!" -ForegroundColor Red
                }
                Write-Host "Use '.\trading-cli.ps1 status' to check system health" -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "❌ Prerequisites not met. Please fix the issues above." -ForegroundColor Red
        }
    }
    "stop" {
        Stop-TradingSystem
    }
    "status" {
        Show-TradingStatus
    }
    "monitor" {
        Start-LiveMonitoring
    }
    "sync" {
        Write-Host "🔄 Syncing Trading System..." -ForegroundColor Yellow
        & ".\device-manager.ps1" -Command sync
    }
    "test" {
        Test-TradingConnections
    }
    "login" {
        Show-LoginInstructions
    }
    "debug-phone" {
        & ".\debug-phone.ps1" @args
    }
    "help" {
        Show-Help
    }
    default {
        Show-Help
    }
}