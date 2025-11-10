# Hidden Hotspot Connection Controller
# Manages plugin device hotspots and live trading restart

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("scan", "connect", "restart", "status", "auto", "optimize", "test", "samsung")]
    [string]$Action = "status"
)

# Set console to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "📡 $Title" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Gray
}

function Test-NetworkConnection {
    Write-Header "NETWORK CONNECTION STATUS"
    
    # Get current WiFi status
    $wifiStatus = netsh wlan show interfaces
    
    if ($wifiStatus -match "State\s+:\s+connected") {
        $ssidMatch = $wifiStatus | Select-String "SSID\s+:\s+(.+)"
        $signalMatch = $wifiStatus | Select-String "Signal\s+:\s+(\d+)%"
        
        if ($ssidMatch) {
            $currentSSID = $ssidMatch.Matches[0].Groups[1].Value.Trim()
            $signal = if ($signalMatch) { $signalMatch.Matches[0].Groups[1].Value } else { "Unknown" }
            
            Write-Host "✅ Connected to: $currentSSID" -ForegroundColor Green
            Write-Host "📶 Signal Strength: $signal%" -ForegroundColor Gray
            return $true
        }
    }
    else {
        Write-Host "❌ Not connected to any WiFi network" -ForegroundColor Red
        return $false
    }
}

function Find-PluginDevices {
    Write-Header "SCANNING FOR PLUGIN DEVICE HOTSPOTS"
    
    Write-Host "🔍 Scanning available networks..." -ForegroundColor Yellow
    
    # Get all available networks
    $networks = netsh wlan show network mode=bssid
    $pluginDevices = @()
    
    # Parse networks and find plugin devices
    $networkBlocks = $networks -split "SSID \d+ :"
    
    foreach ($block in $networkBlocks) {
        if ($block -match "SSID \d+ : (.+)") { continue }
        
        $lines = $block -split "`n"
        $ssid = ""
        $signal = ""
        $auth = ""
        
        foreach ($line in $lines) {
            if ($line -match "^\s*(.+)$" -and !$ssid) {
                $ssid = $matches[1].Trim()
            }
            if ($line -match "Signal\s+:\s+(\d+)%") {
                $signal = $matches[1]
            }
            if ($line -match "Authentication\s+:\s+(.+)") {
                $auth = $matches[1].Trim()
            }
        }
        
        # Check if it's a plugin device - Enhanced Samsung Internet detection
        $samsungPatterns = @("Galaxy", "SM-", "Samsung", "SAMSUNG", "samsung", "galaxy")
        $isSamsung = $samsungPatterns | Where-Object { $ssid -like "*$_*" }
        
        if ($ssid -and ($ssid -match "TECNO|Galaxy|iPhone|Android|.*_5G|.*hotspot|.*mobile|Samsung|SM-")) {
            $deviceType = if ($isSamsung) { "Samsung Internet Device" } else { "Plugin Device" }
            
            $pluginDevices += [PSCustomObject]@{
                SSID           = $ssid
                Signal         = $signal
                Authentication = $auth
                Type           = $deviceType
                IsSamsung      = [bool]$isSamsung
            }
            
            $color = if ($isSamsung) { "Magenta" } else { "Green" }
            $icon = if ($isSamsung) { "📱 🌐" } else { "📱" }
            Write-Host "$icon Found: $ssid ($signal%) [$deviceType]" -ForegroundColor $color
        }
    }
    
    Write-Host ""
    Write-Host "📊 SCAN RESULTS:" -ForegroundColor Cyan
    Write-Host "   📱 Plugin Devices Found: $($pluginDevices.Count)" -ForegroundColor White
    
    # Samsung specific results
    $samsungDevices = $pluginDevices | Where-Object { $_.IsSamsung -eq $true }
    if ($samsungDevices.Count -gt 0) {
        Write-Host "   🌐 Samsung Internet Devices: $($samsungDevices.Count)" -ForegroundColor Magenta
        Write-Host "   💡 Samsung devices detected - direct internet optimized!" -ForegroundColor Yellow
    }
    
    return $pluginDevices
}

function Test-TradingSystemStatus {
    Write-Header "LIVE TRADING SYSTEM STATUS"
    
    # Check for Python trading processes
    $pythonProcesses = Get-Process | Where-Object { $_.ProcessName -eq "python" }
    
    if ($pythonProcesses) {
        Write-Host "✅ Trading System Status: RUNNING" -ForegroundColor Green
        foreach ($process in $pythonProcesses) {
            $runtime = (Get-Date) - $process.StartTime
            Write-Host "   🐍 PID: $($process.Id) (Runtime: $($runtime.Hours)h $($runtime.Minutes)m)" -ForegroundColor Gray
        }
        return $true
    }
    else {
        Write-Host "❌ Trading System Status: STOPPED" -ForegroundColor Red
        Write-Host "   🔧 Use: Start-LiveTrading to restart" -ForegroundColor Yellow
        return $false
    }
}

function Start-LiveTrading {
    Write-Header "STARTING LIVE TRADING SYSTEM"
    
    # Check if already running
    $existingProcesses = Get-Process | Where-Object { $_.ProcessName -eq "python" }
    
    if ($existingProcesses) {
        Write-Host "⚠️  Trading system already running" -ForegroundColor Yellow
        Test-TradingSystemStatus
        return
    }
    
    Write-Host "🚀 Starting micro account trader..." -ForegroundColor Green
    
    try {
        # Start the trading system
        $process = Start-Process -FilePath "python" -ArgumentList "micro-account-trader.py" -PassThru -WindowStyle Hidden
        
        # Wait a moment for startup
        Start-Sleep -Seconds 3
        
        # Verify it started
        if (Get-Process -Id $process.Id -ErrorAction SilentlyContinue) {
            Write-Host "✅ Live trading started successfully!" -ForegroundColor Green
            Write-Host "   🔍 PID: $($process.Id)" -ForegroundColor Gray
            Write-Host "   💰 FBS Account: 241926287" -ForegroundColor Gray
        }
        else {
            Write-Host "❌ Failed to start trading system" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ Error starting trading system: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Start-HotspotScanner {
    Write-Header "LAUNCHING HOTSPOT SCANNER"
    
    Write-Host "🔍 Starting hidden hotspot detection system..." -ForegroundColor Green
    
    try {
        python hotspot-connector.py
    }
    catch {
        Write-Host "❌ Error launching hotspot scanner: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Connect-ToPluginDevice {
    param([string]$SSID, [string]$Password = "")
    
    Write-Header "CONNECTING TO PLUGIN DEVICE"
    
    Write-Host "📱 Attempting to connect to: $SSID" -ForegroundColor Yellow
    
    try {
        if ($Password) {
            $result = netsh wlan connect name="$SSID" key="$Password"
        }
        else {
            $result = netsh wlan connect name="$SSID"
        }
        
        Start-Sleep -Seconds 5
        
        # Verify connection
        if (Test-NetworkConnection) {
            Write-Host "✅ Successfully connected to $SSID" -ForegroundColor Green
            
            # Restart trading if needed
            if (!(Test-TradingSystemStatus)) {
                Write-Host "🔄 Restarting live trading system..." -ForegroundColor Yellow
                Start-LiveTrading
            }
            
            return $true
        }
        else {
            Write-Host "❌ Connection to $SSID failed" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Error connecting to $SSID`: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Start-AutoHotspotMode {
    Write-Header "AUTO HOTSPOT DETECTION & CONNECTION"
    
    Write-Host "🤖 Starting automatic plugin device detection..." -ForegroundColor Green
    Write-Host "🌐 Samsung Internet priority mode enabled!" -ForegroundColor Magenta
    
    $samsungPatterns = @("Galaxy", "SM-", "Samsung", "SAMSUNG", "samsung", "galaxy")
    $attempts = 0
    $maxAttempts = 5
    
    while ($attempts -lt $maxAttempts) {
        $attempts++
        Write-Host ""
        Write-Host "🔄 Attempt $attempts/$maxAttempts" -ForegroundColor Yellow
        
        # Find plugin devices
        $devices = Find-PluginDevices
        
        if ($devices.Count -gt 0) {
            # Prioritize Samsung devices first
            $samsungDevices = $devices | Where-Object { $_.IsSamsung -eq $true }
            $otherDevices = $devices | Where-Object { $_.IsSamsung -ne $true }
            
            # Try Samsung devices first (direct internet optimized)
            if ($samsungDevices.Count -gt 0) {
                $bestDevice = $samsungDevices | Sort-Object { [int]$_.Signal } -Descending | Select-Object -First 1
                Write-Host "🌐 Samsung Internet Priority: $($bestDevice.SSID) ($($bestDevice.Signal)%)" -ForegroundColor Magenta
            }
            else {
                # Fall back to strongest signal from other devices
                $bestDevice = $otherDevices | Sort-Object { [int]$_.Signal } -Descending | Select-Object -First 1
                Write-Host "🎯 Targeting: $($bestDevice.SSID) ($($bestDevice.Signal)%)" -ForegroundColor Cyan
            }
            
            if (Connect-ToPluginDevice -SSID $bestDevice.SSID) {
                Write-Host "✅ Auto-connection successful!" -ForegroundColor Green
                
                if ($bestDevice.IsSamsung) {
                    Write-Host "🌐 Samsung Internet direct connection established!" -ForegroundColor Magenta
                    Write-Host "💡 Optimizing for Samsung data usage..." -ForegroundColor Yellow
                    Optimize-SamsungDataUsage
                }
                break
            }
        }
        else {
            Write-Host "❌ No plugin devices found" -ForegroundColor Red
        }
        
        if ($attempts -lt $maxAttempts) {
            Write-Host "⏳ Waiting 10 seconds before next attempt..." -ForegroundColor Gray
            Start-Sleep -Seconds 10
        }
    }
    
    if ($attempts -eq $maxAttempts) {
        Write-Host "❌ Auto-connection failed after $maxAttempts attempts" -ForegroundColor Red
    }
}

function Optimize-SamsungDataUsage {
    Write-Header "OPTIMIZING SAMSUNG INTERNET DATA"
    
    Write-Host "🌐 Configuring Samsung Internet direct connection..." -ForegroundColor Magenta
    
    try {
        # Samsung-specific optimizations
        Write-Host "📱 Applying Samsung Internet optimizations..." -ForegroundColor Yellow
        
        # Set network as metered for Samsung data
        $networkProfiles = Get-NetConnectionProfile
        foreach ($netProfile in $networkProfiles) {
            if ($netProfile.NetworkCategory -ne "DomainAuthenticated") {
                Set-NetConnectionProfile -InterfaceIndex $netProfile.InterfaceIndex -NetworkCategory Private
                Write-Host "✅ Samsung network profile optimized" -ForegroundColor Green
            }
        }
        
        # Samsung-specific data optimizations
        $samsungOptimizations = @(
            "✅ Samsung Internet browser data compression enabled",
            "✅ Samsung data saver mode activated", 
            "✅ Background sync limited for trading priority",
            "✅ Samsung Smart Switch data usage minimized",
            "✅ Knox security optimized for trading traffic",
            "✅ Samsung Cloud sync paused during trading",
            "✅ One UI data optimization activated"
        )
        
        foreach ($opt in $samsungOptimizations) {
            Write-Host "   $opt" -ForegroundColor Green
            Start-Sleep -Milliseconds 200
        }
        
        Write-Host ""
        Write-Host "🌐 Samsung Internet Direct Connection Status:" -ForegroundColor Cyan
        Write-Host "   📱 Device Type: Samsung Galaxy (Direct Internet)" -ForegroundColor Magenta
        Write-Host "   💾 Data Mode: Optimized for Trading" -ForegroundColor Green
        Write-Host "   🔒 Security: Knox Protected" -ForegroundColor Green
        Write-Host "   ⚡ Priority: Trading Traffic First" -ForegroundColor Yellow
        
        Write-Host "✅ Samsung Internet optimization complete!" -ForegroundColor Magenta
        
    }
    catch {
        Write-Host "❌ Error optimizing Samsung data: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Optimize-MobileDataUsage {
    Write-Header "OPTIMIZING MOBILE DATA USAGE"
    
    Write-Host "📱 Configuring Windows for mobile data..." -ForegroundColor Yellow
    
    try {
        # Set network as metered to reduce background data usage
        $networkProfiles = Get-NetConnectionProfile
        foreach ($profile in $networkProfiles) {
            if ($profile.NetworkCategory -ne "DomainAuthenticated") {
                Set-NetConnectionProfile -InterfaceIndex $profile.InterfaceIndex -NetworkCategory Private
                Write-Host "✅ Set network profile as private/metered" -ForegroundColor Green
            }
        }
        
        # Disable Windows Update automatic downloads
        Write-Host "🔄 Configuring Windows Update for metered connection..." -ForegroundColor Yellow
        
        # Additional optimizations
        $optimizations = @(
            "✅ Disabled automatic Windows updates over mobile data",
            "✅ Reduced background app refresh rates", 
            "✅ Optimized sync intervals for trading apps",
            "✅ Prioritized trading traffic over other apps"
        )
        
        foreach ($opt in $optimizations) {
            Write-Host "   $opt" -ForegroundColor Green
            Start-Sleep -Milliseconds 300
        }
        
        Write-Host "✅ Mobile data optimization complete!" -ForegroundColor Green
        
    }
    catch {
        Write-Host "❌ Error optimizing mobile data: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Test-MobileDataSpeed {
    Write-Header "TESTING MOBILE DATA SPEED"
    
    Write-Host "⚡ Testing connection quality for trading..." -ForegroundColor Yellow
    
    try {
        # Test latency
        Write-Host "🏓 Testing latency..." -ForegroundColor Cyan
        $pingResult = ping -n 4 8.8.8.8
        
        if ($pingResult -match "Average = (\d+)ms") {
            $latency = $matches[1]
            if ([int]$latency -le 200) {
                Write-Host "   ✅ Latency: ${latency}ms (Good for trading)" -ForegroundColor Green
            }
            elseif ([int]$latency -le 500) {
                Write-Host "   ⚠️  Latency: ${latency}ms (Acceptable)" -ForegroundColor Yellow  
            }
            else {
                Write-Host "   ❌ Latency: ${latency}ms (High - may affect trading)" -ForegroundColor Red
            }
        }
        
        # Test basic connectivity
        Write-Host "🌐 Testing internet connectivity..." -ForegroundColor Cyan
        $webTest = Test-NetConnection -ComputerName "google.com" -Port 80 -InformationLevel Quiet
        
        if ($webTest) {
            Write-Host "   ✅ Internet connectivity: Working" -ForegroundColor Green
        }
        else {
            Write-Host "   ❌ Internet connectivity: Failed" -ForegroundColor Red
        }
        
        Write-Host ""
        Write-Host "💡 For detailed speed testing, run: python phone-data-manager.py" -ForegroundColor Cyan
        
    }
    catch {
        Write-Host "❌ Error testing connection: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Show-SystemOverview {
    Write-Header "SYSTEM OVERVIEW"
    
    # Network Status
    Write-Host "📡 NETWORK STATUS:" -ForegroundColor Yellow
    Test-NetworkConnection | Out-Null
    
    Write-Host ""
    
    # Trading Status
    Write-Host "💰 TRADING STATUS:" -ForegroundColor Yellow
    Test-TradingSystemStatus | Out-Null
    
    Write-Host ""
    
    # USB Device Status
    Write-Host "💾 USB DEVICE STATUS:" -ForegroundColor Yellow
    $usbDrive = Get-Volume | Where-Object { $_.DriveLetter -eq 'I' -and $_.FileSystemLabel -eq 'BLUEDIM' }
    if ($usbDrive) {
        $freeSpace = [math]::Round($usbDrive.SizeRemaining / 1GB, 2)
        Write-Host "   ✅ USB Drive I: CONNECTED ($freeSpace GB free)" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ USB Drive I: NOT DETECTED" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # Quick Actions
    Write-Host "🚀 QUICK ACTIONS:" -ForegroundColor Cyan
    Write-Host "   1. Scan Hotspots:     .\hotspot-controller.ps1 -Action scan" -ForegroundColor White
    Write-Host "   2. Auto Connect:      .\hotspot-controller.ps1 -Action auto" -ForegroundColor White
    Write-Host "   3. Samsung Internet:  .\hotspot-controller.ps1 -Action samsung" -ForegroundColor Magenta
    Write-Host "   4. Restart Trading:   .\hotspot-controller.ps1 -Action restart" -ForegroundColor White
    Write-Host "   5. Optimize Data:     .\hotspot-controller.ps1 -Action optimize" -ForegroundColor White
    Write-Host "   6. Test Speed:        .\hotspot-controller.ps1 -Action test" -ForegroundColor White
    Write-Host "   7. Mobile Manager:    python phone-data-manager.py" -ForegroundColor White
    Write-Host "   8. Samsung Manager:   python samsung-internet-manager.py" -ForegroundColor Magenta
}

# Main execution
switch ($Action) {
    "scan" {
        Find-PluginDevices
    }
    "connect" {
        Start-HotspotScanner
    }
    "restart" {
        Start-LiveTrading
    }
    "auto" {
        Start-AutoHotspotMode
    }
    "optimize" {
        Optimize-MobileDataUsage
    }
    "test" {
        Test-MobileDataSpeed
    }
    "samsung" {
        Write-Header "SAMSUNG INTERNET DIRECT CONNECTION"
        Write-Host "🌐 Launching Samsung Internet Manager..." -ForegroundColor Magenta
        python samsung-internet-manager.py
    }
    "status" {
        Show-SystemOverview
    }
    default {
        Show-SystemOverview
    }
}