# Trading System Monitor
# Real-time monitoring of trading system components

param(
    [int]$RefreshSeconds = 10,
    [switch]$Continuous = $false
)

function Show-TradingStatus {
    Clear-Host
    Write-Host "📊 LIVE TRADING SYSTEM MONITOR" -ForegroundColor Green
    Write-Host "==============================" -ForegroundColor Green
    Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""
    
    # FBS Account Info
    Write-Host "💰 FBS Live Account:" -ForegroundColor Yellow
    Write-Host "   Login: 40933270" -ForegroundColor Green
    Write-Host "   Server: FBS-Real" -ForegroundColor Green
    Write-Host "   Mode: LIVE TRADING" -ForegroundColor Red
    Write-Host ""
    
    # System Components
    Write-Host "🖥️  System Components:" -ForegroundColor Yellow
    
    # MT5 Status
    $mt5Process = Get-Process | Where-Object { $_.ProcessName -like "*terminal*" }
    if ($mt5Process) {
        $mt5Uptime = (Get-Date) - $mt5Process.StartTime
        Write-Host "   ✅ MT5 Terminal: Running ($([math]::Round($mt5Uptime.TotalMinutes, 1)) min)" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ MT5 Terminal: Not running" -ForegroundColor Red
    }
    
    # Microservice Status
    try {
        $health = Invoke-RestMethod "http://localhost:3000/health" -Method GET -TimeoutSec 3
        Write-Host "   ✅ Microservice: Online (Uptime: $([math]::Round($health.uptime/60, 1)) min)" -ForegroundColor Green
    }
    catch {
        Write-Host "   ❌ Microservice: Offline" -ForegroundColor Red
    }
    
    # Phone Status
    try {
        $adbCheck = adb devices 2>$null
        if ($adbCheck -match "device$") {
            Write-Host "   ✅ Android Phone: Connected" -ForegroundColor Green
        }
        else {
            Write-Host "   ⚠️  Android Phone: Disconnected" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "   ⚠️  Android Phone: ADB unavailable" -ForegroundColor Yellow
    }
    
    Write-Host ""
    
    # Device Manager Status
    Write-Host "📱 Device Manager:" -ForegroundColor Yellow
    try {
        $devices = Invoke-RestMethod "http://localhost:3000/api/v1/devices" -Method GET -TimeoutSec 3
        Write-Host "   Total Devices: $($devices.total)" -ForegroundColor Green
        
        if ($devices.total -gt 0) {
            $devices.devices | ForEach-Object {
                $statusColor = switch ($_.status) {
                    "connected" { "Green" }
                    "syncing" { "Yellow" }
                    default { "Red" }
                }
                Write-Host "   📱 $($_.name) ($($_.type)) - $($_.status)" -ForegroundColor $statusColor
            }
        }
        
        # Sync Status
        $syncStatus = Invoke-RestMethod "http://localhost:3000/api/v1/devices/sync-status" -Method GET -TimeoutSec 3
        Write-Host "   Sync Service: $(if ($syncStatus.isRunning) { '✅ Running' } else { '❌ Stopped' })" -ForegroundColor $(if ($syncStatus.isRunning) { "Green" } else { "Red" })
        
    }
    catch {
        Write-Host "   ❌ Device API: Not responding" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "⚡ Quick Commands:" -ForegroundColor Yellow
    Write-Host "   Press Ctrl+C to stop monitoring" -ForegroundColor Gray
    Write-Host "   Sync devices: .\device-manager.ps1 -Command sync" -ForegroundColor Gray
    Write-Host "   Debug phone: .\debug-phone.ps1 -TestConnection" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "🔄 Next refresh in $RefreshSeconds seconds..." -ForegroundColor Gray
}

# Main execution
if ($Continuous) {
    Write-Host "🔄 Starting continuous monitoring..." -ForegroundColor Green
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""
    
    try {
        while ($true) {
            Show-TradingStatus
            Start-Sleep -Seconds $RefreshSeconds
        }
    }
    catch {
        Write-Host ""
        Write-Host "⏹️  Monitoring stopped" -ForegroundColor Yellow
    }
}
else {
    Show-TradingStatus
    Write-Host ""
    Write-Host "💡 For continuous monitoring: .\monitor-trading.ps1 -Continuous" -ForegroundColor Cyan
}