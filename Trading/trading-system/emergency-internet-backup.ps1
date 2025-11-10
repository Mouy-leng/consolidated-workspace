# Emergency Internet Backup System
# Ensures continuous internet for trading when TECNO hotspot goes down

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("prepare", "monitor", "backup", "status", "emergency")]
    [string]$Action = "prepare"
)

Write-Host "🚨 EMERGENCY INTERNET BACKUP SYSTEM" -ForegroundColor Red
Write-Host ("=" * 60) -ForegroundColor Gray

function Get-CurrentConnectionStatus {
    Write-Host "`n📡 CURRENT CONNECTION STATUS:" -ForegroundColor Yellow
    
    $wifiInfo = netsh wlan show interfaces
    if ($wifiInfo -match "SSID\s+:\s+(.+)") {
        $ssid = $matches[1].Trim()
        Write-Host "   ✅ Connected to: $ssid" -ForegroundColor Green
        
        if ($ssid -match "TECNO") {
            Write-Host "   ⚠️  WARNING: TECNO connection will be lost in 10 minutes!" -ForegroundColor Red
        }
        
        if ($wifiInfo -match "Signal\s+:\s+(\d+)%") {
            $signal = $matches[1]
            Write-Host "   📶 Signal: $signal%" -ForegroundColor Green
        }
        
        return $ssid
    }
    else {
        Write-Host "   ❌ No WiFi connection!" -ForegroundColor Red
        return $null
    }
}

function Find-BackupConnections {
    Write-Host "`n🔍 SCANNING FOR BACKUP INTERNET OPTIONS:" -ForegroundColor Cyan
    
    # Scan for all available networks
    $networks = netsh wlan show network mode=bssid
    
    Write-Host "   📡 Scanning all available WiFi networks..." -ForegroundColor Yellow
    
    # Check for mobile hotspots
    $mobilePatterns = @("Galaxy", "iPhone", "Android", "Samsung", "Huawei", "Xiaomi", "OnePlus", "hotspot", "mobile")
    $wifiPatterns = @("WIFI", "Internet", "Home", "Office", "Guest")
    
    $backupOptions = @()
    
    # Parse available networks
    $networkBlocks = $networks -split "SSID \d+ :"
    
    foreach ($block in $networkBlocks) {
        $lines = $block -split "`n"
        $ssid = ""
        $signal = ""
        $auth = ""
        
        foreach ($line in $lines) {
            if ($line -match "^\s*(.+)$" -and !$ssid -and $line -notmatch "Network type|Authentication|Encryption") {
                $ssid = $matches[1].Trim()
            }
            if ($line -match "Signal\s+:\s+(\d+)%") {
                $signal = $matches[1]
            }
            if ($line -match "Authentication\s+:\s+(.+)") {
                $auth = $matches[1].Trim()
            }
        }
        
        if ($ssid -and $ssid -ne "TECNO POVA 6 Pro 5G") {
            $isMobile = $mobilePatterns | Where-Object { $ssid -like "*$_*" }
            $isWiFi = $wifiPatterns | Where-Object { $ssid -like "*$_*" }
            
            if ($isMobile -or $isWiFi) {
                $backupOptions += [PSCustomObject]@{
                    SSID   = $ssid
                    Signal = $signal
                    Auth   = $auth
                    Type   = if ($isMobile) { "Mobile Backup" } else { "WiFi Backup" }
                }
                
                $color = if ($isMobile) { "Magenta" } else { "Cyan" }
                Write-Host "   📱 Backup Found: $ssid ($signal%)" -ForegroundColor $color
            }
        }
    }
    
    if ($backupOptions.Count -eq 0) {
        Write-Host "   ❌ No backup internet connections found!" -ForegroundColor Red
        Write-Host "   💡 Emergency solutions:" -ForegroundColor Yellow
        Write-Host "      1. Enable hotspot on another device" -ForegroundColor White
        Write-Host "      2. Use Ethernet/wired connection" -ForegroundColor White
        Write-Host "      3. Use USB tethering from phone" -ForegroundColor White
    }
    
    return $backupOptions
}

function Prepare-EmergencyMode {
    Write-Host "`n🚨 PREPARING EMERGENCY MODE:" -ForegroundColor Red
    
    # Save current trading state
    Write-Host "   💾 Saving current trading state..." -ForegroundColor Yellow
    
    # Check if trading is running
    $pythonProcesses = Get-Process | Where-Object { $_.ProcessName -eq "python" }
    
    if ($pythonProcesses) {
        Write-Host "   ✅ Trading system is running - preparing for connection switch" -ForegroundColor Green
        
        # Create backup connection profile
        $backupConfig = @{
            'current_connection' = (Get-CurrentConnectionStatus)
            'trading_active'     = $true
            'backup_time'        = (Get-Date).ToString()
            'process_ids'        = @($pythonProcesses | ForEach-Object { $_.Id })
        }
        
        $backupConfig | ConvertTo-Json | Out-File "emergency_backup_config.json" -Encoding UTF8
        Write-Host "   💾 Emergency config saved" -ForegroundColor Green
    }
    else {
        Write-Host "   ⚠️  No trading system running" -ForegroundColor Yellow
    }
    
    # Prepare auto-reconnect script
    $autoScript = @"
# Auto-reconnect after TECNO disconnect
`$backupNetworks = Find-BackupConnections
if (`$backupNetworks.Count -gt 0) {
    `$bestBackup = `$backupNetworks | Sort-Object { [int]`$_.Signal } -Descending | Select-Object -First 1
    Write-Host "🔄 Attempting backup connection: `$(`$bestBackup.SSID)" -ForegroundColor Cyan
    netsh wlan connect name="`$(`$bestBackup.SSID)"
}
"@
    
    $autoScript | Out-File "auto_reconnect.ps1" -Encoding UTF8
    Write-Host "   🔄 Auto-reconnect script prepared" -ForegroundColor Green
}

function Monitor-Connection {
    Write-Host "`n👁️  MONITORING CONNECTION STATUS:" -ForegroundColor Cyan
    
    $startTime = Get-Date
    $monitorDuration = 600 # 10 minutes
    
    while ((Get-Date) -lt $startTime.AddSeconds($monitorDuration)) {
        $currentSSID = Get-CurrentConnectionStatus
        
        if ($currentSSID -match "TECNO") {
            $timeLeft = [math]::Round(($startTime.AddSeconds($monitorDuration) - (Get-Date)).TotalMinutes, 1)
            Write-Host "   ⏰ Time until TECNO disconnect: $timeLeft minutes" -ForegroundColor Yellow
        }
        elseif ($null -eq $currentSSID) {
            Write-Host "   🚨 CONNECTION LOST! Activating backup..." -ForegroundColor Red
            .\auto_reconnect.ps1
            break
        }
        else {
            Write-Host "   ✅ Connected to backup: $currentSSID" -ForegroundColor Green
            break
        }
        
        Start-Sleep -Seconds 30
    }
}

function Test-EthernetConnection {
    Write-Host "`n🔌 CHECKING ETHERNET CONNECTION:" -ForegroundColor Cyan
    
    $ethernetAdapters = Get-NetAdapter | Where-Object { $_.MediaType -eq "802.3" -and $_.Status -eq "Up" }
    
    if ($ethernetAdapters) {
        Write-Host "   ✅ Ethernet connection available!" -ForegroundColor Green
        foreach ($adapter in $ethernetAdapters) {
            Write-Host "      🔌 $($adapter.Name): $($adapter.LinkSpeed)" -ForegroundColor Gray
        }
        return $true
    }
    else {
        Write-Host "   ❌ No ethernet connection available" -ForegroundColor Red
        return $false
    }
}

function Enable-MobileHotspotInstructions {
    Write-Host "`n📱 MOBILE HOTSPOT EMERGENCY INSTRUCTIONS:" -ForegroundColor Magenta
    Write-Host "   If no backup found, enable hotspot on any available device:" -ForegroundColor Yellow
    Write-Host "   " -ForegroundColor White
    Write-Host "   📱 Android/Samsung:" -ForegroundColor Cyan
    Write-Host "      Settings → Connections → Mobile Hotspot → ON" -ForegroundColor White
    Write-Host "   " -ForegroundColor White
    Write-Host "   📱 iPhone:" -ForegroundColor Cyan  
    Write-Host "      Settings → Personal Hotspot → ON" -ForegroundColor White
    Write-Host "   " -ForegroundColor White
    Write-Host "   💻 Windows Hotspot:" -ForegroundColor Cyan
    Write-Host "      Settings → Network → Mobile hotspot → ON" -ForegroundColor White
}

# Main execution
switch ($Action) {
    "prepare" {
        Get-CurrentConnectionStatus
        $backups = Find-BackupConnections
        Prepare-EmergencyMode
        Test-EthernetConnection
        Enable-MobileHotspotInstructions
        
        Write-Host "`n🚨 EMERGENCY BACKUP STATUS:" -ForegroundColor Red
        if ($backups.Count -gt 0) {
            Write-Host "   ✅ $($backups.Count) backup connection(s) available" -ForegroundColor Green
        }
        else {
            Write-Host "   ⚠️  No backup connections found - manual setup required" -ForegroundColor Yellow
        }
    }
    "monitor" {
        Monitor-Connection
    }
    "backup" {
        .\auto_reconnect.ps1
    }
    "emergency" {
        Write-Host "🚨 EMERGENCY: Attempting all backup connections..." -ForegroundColor Red
        $backups = Find-BackupConnections
        if ($backups.Count -gt 0) {
            foreach ($backup in ($backups | Sort-Object { [int]$_.Signal } -Descending)) {
                Write-Host "   🔄 Trying: $($backup.SSID)" -ForegroundColor Cyan
                netsh wlan connect name="$($backup.SSID)"
                Start-Sleep -Seconds 5
                
                $currentConnection = Get-CurrentConnectionStatus
                if ($currentConnection -eq $backup.SSID) {
                    Write-Host "   ✅ Successfully connected to: $($backup.SSID)" -ForegroundColor Green
                    break
                }
            }
        }
    }
    default {
        Get-CurrentConnectionStatus
        Find-BackupConnections
    }
}

Write-Host "`n💡 QUICK COMMANDS:" -ForegroundColor Cyan
Write-Host "   🚨 Emergency connect: .\emergency-internet-backup.ps1 -Action emergency" -ForegroundColor Red
Write-Host "   👁️  Monitor mode:     .\emergency-internet-backup.ps1 -Action monitor" -ForegroundColor Yellow
Write-Host "   🔄 Auto backup:      .\emergency-internet-backup.ps1 -Action backup" -ForegroundColor Green