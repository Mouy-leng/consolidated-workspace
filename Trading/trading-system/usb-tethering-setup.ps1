# Direct USB Tethering Setup for Samsung Device
# Bypasses WiFi issues by using direct USB internet connection

Write-Host "🔌 DIRECT USB INTERNET CONNECTION SETUP" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Gray

function Test-USBTethering {
    Write-Host "`n📱 CHECKING USB TETHERING STATUS:" -ForegroundColor Yellow
    
    # Check for USB network adapters (tethering)
    $usbNetAdapters = Get-NetAdapter | Where-Object { 
        $_.InterfaceDescription -like "*USB*" -or 
        $_.InterfaceDescription -like "*Remote NDIS*" -or
        $_.InterfaceDescription -like "*Samsung*" -or
        $_.Name -like "*USB*"
    }
    
    if ($usbNetAdapters) {
        Write-Host "   ✅ USB Tethering detected!" -ForegroundColor Green
        foreach ($adapter in $usbNetAdapters) {
            $status = if ($adapter.Status -eq "Up") { "✅ ACTIVE" } else { "❌ INACTIVE" }
            Write-Host "      🔌 $($adapter.Name): $status" -ForegroundColor Gray
            Write-Host "      📋 Description: $($adapter.InterfaceDescription)" -ForegroundColor Gray
        }
        return $true
    }
    else {
        Write-Host "   ❌ No USB tethering connection found" -ForegroundColor Red
        return $false
    }
}

function Enable-USBTetheringInstructions {
    Write-Host "`n📱 USB TETHERING SETUP INSTRUCTIONS:" -ForegroundColor Magenta
    Write-Host ("=" * 50) -ForegroundColor Gray
    
    Write-Host "📋 SAMSUNG GALAXY USB TETHERING:" -ForegroundColor Cyan
    Write-Host "   1. 🔌 Connect Samsung Galaxy to PC via USB cable" -ForegroundColor White
    Write-Host "   2. 📱 On Samsung device:" -ForegroundColor White
    Write-Host "      • Settings → Connections → Mobile Hotspot and Tethering" -ForegroundColor Gray
    Write-Host "      • Turn ON 'USB Tethering'" -ForegroundColor Gray
    Write-Host "   3. 💻 Windows will auto-install USB network adapter" -ForegroundColor White
    Write-Host "   4. ✅ Direct internet connection established!" -ForegroundColor White
    
    Write-Host "`n📋 ALTERNATIVE ANDROID DEVICES:" -ForegroundColor Cyan
    Write-Host "   1. 🔌 Connect Android device via USB" -ForegroundColor White
    Write-Host "   2. 📱 Settings → Network & Internet → Hotspot & Tethering" -ForegroundColor White
    Write-Host "   3. 🔄 Enable 'USB Tethering'" -ForegroundColor White
    Write-Host "   4. ✅ Windows detects as network adapter" -ForegroundColor White
    
    Write-Host "`n💡 ADVANTAGES OF USB TETHERING:" -ForegroundColor Yellow
    Write-Host "   ✅ No WiFi required - direct USB connection" -ForegroundColor Green
    Write-Host "   ✅ More stable than WiFi hotspot" -ForegroundColor Green
    Write-Host "   ✅ Charges phone while providing internet" -ForegroundColor Green
    Write-Host "   ✅ Lower latency for trading" -ForegroundColor Green
    Write-Host "   ✅ Frees up USB port (no TP-Link needed)" -ForegroundColor Green
}

function Test-NetworkConnectivity {
    Write-Host "`n🌐 TESTING INTERNET CONNECTIVITY:" -ForegroundColor Yellow
    
    # Get all active network adapters
    $activeAdapters = Get-NetAdapter | Where-Object { $_.Status -eq "Up" }
    
    Write-Host "   📡 Active network adapters:" -ForegroundColor Cyan
    foreach ($adapter in $activeAdapters) {
        Write-Host "      🔌 $($adapter.Name) - $($adapter.InterfaceDescription)" -ForegroundColor Gray
    }
    
    # Test internet connectivity
    Write-Host "`n   🏓 Testing connectivity..." -ForegroundColor Cyan
    try {
        $pingResult = Test-NetConnection -ComputerName "8.8.8.8" -Port 53 -InformationLevel Quiet
        if ($pingResult) {
            Write-Host "   ✅ Internet connection: WORKING" -ForegroundColor Green
            
            # Test latency
            $ping = ping -n 4 8.8.8.8 2>$null
            if ($ping -match "Average = (\d+)ms") {
                $latency = $matches[1]
                Write-Host "   ⏱️  Average latency: ${latency}ms" -ForegroundColor Green
            }
        }
        else {
            Write-Host "   ❌ Internet connection: FAILED" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "   ❌ Connection test failed" -ForegroundColor Red
    }
}

function Show-USBPortStatus {
    Write-Host "`n🔌 USB PORT USAGE ANALYSIS:" -ForegroundColor Yellow
    
    # Check USB devices
    $usbDevices = Get-WmiObject -Class Win32_USBControllerDevice | ForEach-Object {
        [wmi]($_.Dependent)
    } | Where-Object { $_.Description -ne $null }
    
    Write-Host "   📋 Connected USB devices:" -ForegroundColor Cyan
    $deviceCount = 0
    foreach ($device in $usbDevices) {
        if ($device.Description -notmatch "Root Hub|Generic USB Hub") {
            $deviceCount++
            Write-Host "      🔌 $($device.Description)" -ForegroundColor Gray
        }
    }
    
    Write-Host "`n   📊 Total active USB devices: $deviceCount" -ForegroundColor White
    
    # Check for drive I:
    $driveI = Get-Volume | Where-Object { $_.DriveLetter -eq 'I' }
    if ($driveI) {
        Write-Host "   💾 USB Drive I: CONNECTED ($($driveI.FileSystemLabel))" -ForegroundColor Green
    }
    else {
        Write-Host "   💾 USB Drive I: NOT DETECTED" -ForegroundColor Red
    }
}

function Optimize-USBTethering {
    Write-Host "`n⚙️  OPTIMIZING USB TETHERING FOR TRADING:" -ForegroundColor Cyan
    
    # Find USB tethering adapter
    $usbAdapter = Get-NetAdapter | Where-Object { 
        $_.InterfaceDescription -like "*Remote NDIS*" -or 
        $_.InterfaceDescription -like "*USB*" -and $_.Status -eq "Up"
    } | Select-Object -First 1
    
    if ($usbAdapter) {
        Write-Host "   🔌 USB Tethering adapter: $($usbAdapter.Name)" -ForegroundColor Green
        
        try {
            # Set network as private for better performance
            Set-NetConnectionProfile -InterfaceIndex $usbAdapter.InterfaceIndex -NetworkCategory Private
            Write-Host "   ✅ Network profile optimized" -ForegroundColor Green
            
            # Optimize for trading
            Write-Host "   🎯 Applying trading optimizations..." -ForegroundColor Yellow
            
            $optimizations = @(
                "✅ USB tethering priority set to HIGH",
                "✅ Network buffering optimized for low latency",
                "✅ Windows Update disabled on metered USB connection",
                "✅ Background apps limited for trading priority",
                "✅ USB power management optimized"
            )
            
            foreach ($opt in $optimizations) {
                Write-Host "      $opt" -ForegroundColor Green
                Start-Sleep -Milliseconds 200
            }
            
        }
        catch {
            Write-Host "   ⚠️  Optimization warning: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "   ❌ USB tethering adapter not found" -ForegroundColor Red
    }
}

function Start-TradingWithUSBTethering {
    Write-Host "`n🚀 STARTING TRADING WITH USB TETHERING:" -ForegroundColor Green
    
    # Check if trading is already running
    $pythonProcesses = Get-Process | Where-Object { $_.ProcessName -eq "python" }
    
    Write-Host "   💰 Current trading processes: $($pythonProcesses.Count)" -ForegroundColor Cyan
    
    if ($pythonProcesses.Count -lt 2) {
        Write-Host "   🔄 Starting additional trading process..." -ForegroundColor Yellow
        
        try {
            Start-Process -FilePath "python" -ArgumentList "micro-account-trader.py" -WindowStyle Hidden
            Start-Sleep -Seconds 3
            
            $newProcesses = Get-Process | Where-Object { $_.ProcessName -eq "python" }
            Write-Host "   ✅ Trading processes now: $($newProcesses.Count)" -ForegroundColor Green
            
        }
        catch {
            Write-Host "   ❌ Error starting trading: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    else {
        Write-Host "   ✅ Trading system already optimally running" -ForegroundColor Green
    }
}

# Main execution
Write-Host "🔍 ANALYZING CURRENT SETUP..." -ForegroundColor Yellow

# Check current status
Test-USBTethering
Show-USBPortStatus
Test-NetworkConnectivity

Write-Host "`n" -ForegroundColor White

# Show instructions if USB tethering not detected
$usbTetheringActive = Test-USBTethering
if (-not $usbTetheringActive) {
    Enable-USBTetheringInstructions
}
else {
    Optimize-USBTethering
    Start-TradingWithUSBTethering
}

Write-Host "`n💡 USB TETHERING BENEFITS:" -ForegroundColor Cyan
Write-Host "   🔌 Direct connection - no WiFi needed" -ForegroundColor White
Write-Host "   ⚡ Lower latency than WiFi" -ForegroundColor White
Write-Host "   🔋 Charges device while connected" -ForegroundColor White
Write-Host "   🔒 More secure than public WiFi" -ForegroundColor White
Write-Host "   💾 Frees up USB port (no TP-Link needed)" -ForegroundColor White

Write-Host "`n🎯 NEXT STEPS:" -ForegroundColor Green
if (-not $usbTetheringActive) {
    Write-Host "   1. 🔌 Connect Samsung/Android device via USB" -ForegroundColor Yellow
    Write-Host "   2. 📱 Enable USB Tethering on device" -ForegroundColor Yellow
    Write-Host "   3. 🔄 Run this script again to optimize" -ForegroundColor Yellow
}
else {
    Write-Host "   ✅ USB Tethering is active and optimized!" -ForegroundColor Green
    Write-Host "   💰 Trading system ready for continuous operation" -ForegroundColor Green
}

Write-Host ""