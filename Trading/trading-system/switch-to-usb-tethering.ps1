# Automated Switch Script
Write-Host "🔄 Automated USB Tethering Switch" -ForegroundColor Magenta

# Step 1: Check for USB tethering
$usbTethering = Get-NetAdapter | Where-Object { 
    $_.InterfaceDescription -like "*Remote NDIS*" -and $_.Status -eq "Up" 
}

if ($usbTethering) {
    Write-Host "✅ USB Tethering detected and active!" -ForegroundColor Green
    Write-Host "🔌 Adapter: $($usbTethering.Name)" -ForegroundColor Cyan
    
    # Test connectivity
    $ping = Test-NetConnection -ComputerName "8.8.8.8" -Port 53 -InformationLevel Quiet
    if ($ping) {
        Write-Host "✅ Internet via USB tethering: WORKING" -ForegroundColor Green
        
        Write-Host "🎯 Safe to remove TP-Link USB WiFi adapter!" -ForegroundColor Yellow
        Write-Host "💾 You can now insert USB Drive I:" -ForegroundColor Green
        
        # Optimize USB tethering
        try {
            Set-NetConnectionProfile -InterfaceIndex $usbTethering.InterfaceIndex -NetworkCategory Private
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
$trading = Get-Process | Where-Object { $_.ProcessName -eq "python" }
Write-Host "💰 Trading processes: $($trading.Count) running" -ForegroundColor Cyan
