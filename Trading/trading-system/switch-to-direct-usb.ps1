# Switch from USB WiFi to USB Tethering
# Frees up USB port and provides direct internet connection

Write-Host "🔄 SWITCHING TO DIRECT USB TETHERING" -ForegroundColor Magenta
Write-Host ("=" * 60) -ForegroundColor Gray

Write-Host "`n📊 CURRENT SITUATION ANALYSIS:" -ForegroundColor Yellow
Write-Host "   📡 Current: Using TP-Link USB WiFi adapter" -ForegroundColor Cyan
Write-Host "   🔌 Problem: Need USB port for Drive I:" -ForegroundColor Red
Write-Host "   💡 Solution: Switch to USB tethering (direct connection)" -ForegroundColor Green

Write-Host "`n🎯 BENEFITS OF SWITCHING:" -ForegroundColor Cyan
Write-Host "   ✅ Frees up USB port for Drive I:" -ForegroundColor Green
Write-Host "   ✅ More stable internet (direct USB vs WiFi)" -ForegroundColor Green
Write-Host "   ✅ Lower latency for trading" -ForegroundColor Green
Write-Host "   ✅ Phone charges while providing internet" -ForegroundColor Green
Write-Host "   ✅ No WiFi signal issues" -ForegroundColor Green

function Show-SwitchInstructions {
    Write-Host "`n📋 STEP-BY-STEP SWITCHING PROCESS:" -ForegroundColor Magenta
    Write-Host ("=" * 50) -ForegroundColor Gray
    
    Write-Host "`n🔌 STEP 1: PREPARE USB TETHERING" -ForegroundColor Cyan
    Write-Host "   1. 📱 Get USB cable for your Samsung Galaxy A51" -ForegroundColor White
    Write-Host "   2. 🔌 Connect Samsung Galaxy to PC via USB" -ForegroundColor White
    Write-Host "   3. 📱 On Samsung device:" -ForegroundColor White
    Write-Host "      • Settings → Connections → Mobile Hotspot and Tethering" -ForegroundColor Gray
    Write-Host "      • Enable 'USB Tethering'" -ForegroundColor Gray
    Write-Host "   4. 💻 Windows will detect as 'Remote NDIS based Internet Sharing Device'" -ForegroundColor White
    
    Write-Host "`n⏸️  STEP 2: SAFELY DISCONNECT TP-LINK WiFi" -ForegroundColor Cyan
    Write-Host "   1. ✅ FIRST verify USB tethering is working" -ForegroundColor Yellow
    Write-Host "   2. 🔌 Safely remove TP-Link USB WiFi adapter" -ForegroundColor White
    Write-Host "   3. 💾 Insert USB Drive I: in freed port" -ForegroundColor White
    Write-Host "   4. 🚀 Continue trading with direct USB internet" -ForegroundColor White
    
    Write-Host "`n🎯 STEP 3: VERIFY AND OPTIMIZE" -ForegroundColor Cyan
    Write-Host "   1. 🌐 Test internet connection speed" -ForegroundColor White
    Write-Host "   2. 📊 Verify trading processes continue running" -ForegroundColor White
    Write-Host "   3. ⚙️  Apply USB tethering optimizations" -ForegroundColor White
    Write-Host "   4. 💾 Confirm USB Drive I: is accessible" -ForegroundColor White
}

function Test-CurrentConnection {
    Write-Host "`n📊 CURRENT CONNECTION STATUS:" -ForegroundColor Yellow
    
    # Get current connection details
    $currentAdapter = Get-NetAdapter | Where-Object { $_.Status -eq "Up" -and $_.Name -like "*Wi-Fi*" }
    
    if ($currentAdapter) {
        Write-Host "   📡 Active adapter: $($currentAdapter.Name)" -ForegroundColor Cyan
        Write-Host "   🔌 Type: $($currentAdapter.InterfaceDescription)" -ForegroundColor Gray
        
        # Test current performance
        Write-Host "   🏓 Testing current performance..." -ForegroundColor Yellow
        try {
            $ping = ping -n 4 8.8.8.8 2>$null
            if ($ping -match "Average = (\d+)ms") {
                $latency = $matches[1]
                Write-Host "   ⏱️  Current latency: ${latency}ms" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "   ❌ Performance test failed" -ForegroundColor Red
        }
    }
}

function Show-USB-TetheringSetup {
    Write-Host "`n📱 SAMSUNG GALAXY A51 USB TETHERING SETUP:" -ForegroundColor Magenta
    Write-Host ("=" * 50) -ForegroundColor Gray
    
    Write-Host "🔧 Samsung Galaxy A51 Instructions:" -ForegroundColor Cyan
    Write-Host "   1. 🔌 Connect Galaxy A51 to PC with USB-C cable" -ForegroundColor White
    Write-Host "   2. 📱 Swipe down notifications, tap USB options" -ForegroundColor White
    Write-Host "   3. 📱 Select 'USB Tethering' or go to:" -ForegroundColor White
    Write-Host "      Settings → Connections → Mobile Hotspot and Tethering" -ForegroundColor Gray
    Write-Host "   4. 🔄 Toggle 'USB Tethering' ON" -ForegroundColor White
    Write-Host "   5. 💻 Windows will show 'Setting up device...' notification" -ForegroundColor White
    Write-Host "   6. ✅ New network adapter appears: 'Remote NDIS...' or similar" -ForegroundColor White
    
    Write-Host "`n🔋 POWER MANAGEMENT:" -ForegroundColor Yellow
    Write-Host "   📱 Galaxy A51 will charge while providing internet" -ForegroundColor Green
    Write-Host "   ⚡ Faster charging than wireless charging" -ForegroundColor Green
    Write-Host "   🔋 Can run indefinitely while plugged in" -ForegroundColor Green
}

function Create-SwitchScript {
    Write-Host "`n📝 CREATING AUTOMATED SWITCH SCRIPT..." -ForegroundColor Yellow
    
    $switchScript = @"
# Automated Switch Script
Write-Host "🔄 Automated USB Tethering Switch" -ForegroundColor Magenta

# Step 1: Check for USB tethering
`$usbTethering = Get-NetAdapter | Where-Object { 
    `$_.InterfaceDescription -like "*Remote NDIS*" -and `$_.Status -eq "Up" 
}

if (`$usbTethering) {
    Write-Host "✅ USB Tethering detected and active!" -ForegroundColor Green
    Write-Host "🔌 Adapter: `$(`$usbTethering.Name)" -ForegroundColor Cyan
    
    # Test connectivity
    `$ping = Test-NetConnection -ComputerName "8.8.8.8" -Port 53 -InformationLevel Quiet
    if (`$ping) {
        Write-Host "✅ Internet via USB tethering: WORKING" -ForegroundColor Green
        
        Write-Host "🎯 Safe to remove TP-Link USB WiFi adapter!" -ForegroundColor Yellow
        Write-Host "💾 You can now insert USB Drive I:" -ForegroundColor Green
        
        # Optimize USB tethering
        try {
            Set-NetConnectionProfile -InterfaceIndex `$usbTethering.InterfaceIndex -NetworkCategory Private
            Write-Host "✅ USB tethering optimized for trading" -ForegroundColor Green
        }
        catch {
            Write-Host "⚠️  Optimization needs admin privileges" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "❌ USB tethering not providing internet" -ForegroundColor Red
    }
}
else {
    Write-Host "❌ USB tethering not detected" -ForegroundColor Red
    Write-Host "📱 Please enable USB tethering on your Samsung Galaxy A51" -ForegroundColor Yellow
}

# Check trading processes
`$trading = Get-Process | Where-Object { `$_.ProcessName -eq "python" }
Write-Host "💰 Trading processes: `$(`$trading.Count) running" -ForegroundColor Cyan
"@

    $switchScript | Out-File "switch-to-usb-tethering.ps1" -Encoding UTF8
    Write-Host "   📄 Script saved: switch-to-usb-tethering.ps1" -ForegroundColor Green
}

# Main execution
Test-CurrentConnection
Show-SwitchInstructions
Show-USB-TetheringSetup
Create-SwitchScript

Write-Host "`n🚨 IMPORTANT SAFETY STEPS:" -ForegroundColor Red
Write-Host "   1. ✅ Setup USB tethering FIRST before removing TP-Link" -ForegroundColor Yellow
Write-Host "   2. 🧪 Test internet connectivity via USB tethering" -ForegroundColor Yellow
Write-Host "   3. ✅ Verify trading processes keep running" -ForegroundColor Yellow
Write-Host "   4. 🔌 Only then safely remove TP-Link WiFi USB" -ForegroundColor Yellow
Write-Host "   5. 💾 Insert USB Drive I: in freed port" -ForegroundColor Yellow

Write-Host "`n🎯 QUICK TEST COMMANDS:" -ForegroundColor Cyan
Write-Host "   📱 Check USB tethering: .\switch-to-usb-tethering.ps1" -ForegroundColor White
Write-Host "   📊 Monitor trading: .\hotspot-controller.ps1 -Action status" -ForegroundColor White
Write-Host "   🌐 Test connectivity: ping 8.8.8.8" -ForegroundColor White

Write-Host "`n✅ READY TO SWITCH TO DIRECT USB CONNECTION!" -ForegroundColor Green
Write-Host "This will free up your USB port for Drive I: while maintaining stable internet." -ForegroundColor Cyan

Write-Host ""