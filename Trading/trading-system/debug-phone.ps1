# Phone Connection Debug Script
# Helps troubleshoot phone connectivity for trading system

param(
    [switch]$InstallADB = $false,
    [switch]$TestConnection = $false,
    [string]$PhoneIP = ""
)

Write-Host "📱 Phone Connection Debugging Tool" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host ""

function Test-ADBConnection {
    Write-Host "🔍 Testing ADB Connection..." -ForegroundColor Yellow
    
    try {
        $adbPath = where.exe adb 2>$null
        if (-not $adbPath) {
            Write-Host "❌ ADB not found" -ForegroundColor Red
            Write-Host "📥 To install ADB:" -ForegroundColor Yellow
            Write-Host "   1. Download Android SDK Platform Tools" -ForegroundColor Gray
            Write-Host "   2. Add to PATH environment variable" -ForegroundColor Gray
            Write-Host "   3. Or run: .\debug-phone.ps1 -InstallADB" -ForegroundColor Gray
            return $false
        }
        
        Write-Host "✅ ADB found: $adbPath" -ForegroundColor Green
        
        # Test ADB devices
        $devices = adb devices 2>$null
        Write-Host "📱 ADB Devices:" -ForegroundColor Cyan
        Write-Host $devices
        
        if ($devices -match "device$") {
            Write-Host "✅ Android device connected and authorized" -ForegroundColor Green
            return $true
        }
        elseif ($devices -match "unauthorized") {
            Write-Host "⚠️  Android device connected but unauthorized" -ForegroundColor Yellow
            Write-Host "   Enable USB Debugging on your phone" -ForegroundColor Gray
            return $false
        }
        else {
            Write-Host "⚠️  No Android devices detected" -ForegroundColor Yellow
            return $false
        }
        
    }
    catch {
        Write-Host "❌ ADB test failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Install-ADBTools {
    Write-Host "📥 Installing ADB Tools..." -ForegroundColor Yellow
    
    try {
        # Check if chocolatey is available
        $choco = where.exe choco 2>$null
        if ($choco) {
            Write-Host "Installing via Chocolatey..." -ForegroundColor Cyan
            choco install adb -y
            return $true
        }
        
        # Manual download approach
        Write-Host "Downloading Android SDK Platform Tools..." -ForegroundColor Cyan
        $downloadUrl = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
        $downloadPath = "$env:TEMP\platform-tools.zip"
        $extractPath = "C:\Android\platform-tools"
        
        # Download
        Invoke-WebRequest -Uri $downloadUrl -OutFile $downloadPath -UseBasicParsing
        
        # Extract
        Expand-Archive -Path $downloadPath -DestinationPath "C:\Android" -Force
        
        # Add to PATH
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($currentPath -notlike "*$extractPath*") {
            [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$extractPath", "User")
            Write-Host "✅ ADB installed to: $extractPath" -ForegroundColor Green
            Write-Host "⚠️  Please restart PowerShell to use ADB" -ForegroundColor Yellow
        }
        
        return $true
        
    }
    catch {
        Write-Host "❌ ADB installation failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-USBDevices {
    Write-Host "🔍 Testing USB Devices..." -ForegroundColor Yellow
    
    # Check for mobile-related USB devices
    $mobileDevices = Get-PnpDevice | Where-Object { 
        ($_.FriendlyName -like "*phone*") -or 
        ($_.FriendlyName -like "*android*") -or 
        ($_.FriendlyName -like "*samsung*") -or 
        ($_.FriendlyName -like "*iphone*") -or
        ($_.FriendlyName -like "*apple*") -or
        ($_.Class -eq "AndroidUsbDeviceClass") -or
        ($_.Class -eq "USBDevice" -and $_.FriendlyName -like "*mobile*")
    }
    
    if ($mobileDevices) {
        Write-Host "✅ Found USB mobile devices:" -ForegroundColor Green
        $mobileDevices | Select-Object FriendlyName, Status, Class | Format-Table -AutoSize
        return $true
    }
    else {
        Write-Host "⚠️  No USB mobile devices found" -ForegroundColor Yellow
        Write-Host "📋 Troubleshooting steps:" -ForegroundColor Cyan
        Write-Host "   1. Connect phone via USB cable" -ForegroundColor Gray
        Write-Host "   2. Enable USB Debugging (Developer Options)" -ForegroundColor Gray
        Write-Host "   3. Set USB mode to 'File Transfer' or 'MTP'" -ForegroundColor Gray
        Write-Host "   4. Install phone drivers if needed" -ForegroundColor Gray
        return $false
    }
}

function Test-USBStorage {
    Write-Host "🔍 Testing USB Storage..." -ForegroundColor Yellow
    
    $usbStorage = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DriveType -eq 2 }
    
    if ($usbStorage) {
        Write-Host "✅ Found USB storage devices:" -ForegroundColor Green
        $usbStorage | Select-Object DeviceID, VolumeName, @{Name = "Size(GB)"; Expression = { [math]::Round($_.Size / 1GB, 2) } } | Format-Table -AutoSize
        
        # Check if any look like phones
        $phoneStorage = $usbStorage | Where-Object { 
            $_.VolumeName -like "*phone*" -or 
            $_.VolumeName -like "*android*" -or 
            $_.VolumeName -like "*samsung*" -or
            $_.VolumeName -like "*pixel*"
        }
        
        if ($phoneStorage) {
            Write-Host "📱 Potential phone storage detected:" -ForegroundColor Green
            $phoneStorage | ForEach-Object {
                Write-Host "   $($_.DeviceID) - $($_.VolumeName)" -ForegroundColor Gray
            }
        }
        
        return $true
    }
    else {
        Write-Host "⚠️  No USB storage devices found" -ForegroundColor Yellow
        return $false
    }
}

function Test-NetworkConnection {
    param([string]$IP)
    
    if (-not $IP) {
        Write-Host "🔍 Scanning for phones on network..." -ForegroundColor Yellow
        Write-Host "⚠️  This is a basic scan - provide IP with -PhoneIP for direct test" -ForegroundColor Yellow
        return $false
    }
    
    Write-Host "🔍 Testing network connection to phone: $IP" -ForegroundColor Yellow
    
    # Common mobile trading app ports
    $ports = @(8080, 3000, 8000, 9000, 22, 5555)
    
    foreach ($port in $ports) {
        try {
            $connection = Test-NetConnection -ComputerName $IP -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
            if ($connection) {
                Write-Host "✅ Connection successful: ${IP}:${port}" -ForegroundColor Green
                return $true
            }
        }
        catch {
            # Ignore connection failures
        }
    }
    
    Write-Host "⚠️  No open ports found on ${IP}" -ForegroundColor Yellow
    return $false
}

function Test-PhonePluginAPI {
    Write-Host "🔍 Testing Phone Plugin API..." -ForegroundColor Yellow
    
    try {
        # Test microservice health
        $health = Invoke-RestMethod "http://localhost:3000/health" -Method GET -ErrorAction Stop
        Write-Host "✅ Microservice running (Uptime: $([math]::Round($health.uptime, 1))s)" -ForegroundColor Green
        
        # Get current devices
        $devices = Invoke-RestMethod "http://localhost:3000/api/v1/devices" -Method GET
        Write-Host "📱 Detected devices: $($devices.total)" -ForegroundColor Green
        
        if ($devices.total -gt 0) {
            Write-Host "✅ Devices found:" -ForegroundColor Green
            $devices.devices | ForEach-Object {
                Write-Host "   $($_.name) ($($_.type)) - Status: $($_.status)" -ForegroundColor Gray
            }
        }
        
        return $true
        
    }
    catch {
        Write-Host "❌ Phone Plugin API test failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   Make sure microservice is running: npm start" -ForegroundColor Yellow
        return $false
    }
}

# Main execution
if ($InstallADB) {
    Install-ADBTools
    exit
}

if ($TestConnection) {
    Write-Host "🚀 Running comprehensive phone connection test..." -ForegroundColor Green
    Write-Host ""
    
    $results = @{
        ADB     = Test-ADBConnection
        USB     = Test-USBDevices
        Storage = Test-USBStorage
        API     = Test-PhonePluginAPI
    }
    
    if ($PhoneIP) {
        $results.Network = Test-NetworkConnection -IP $PhoneIP
    }
    
    Write-Host ""
    Write-Host "📊 Connection Test Results:" -ForegroundColor Green
    Write-Host "===========================" -ForegroundColor Green
    $results.GetEnumerator() | ForEach-Object {
        $status = if ($_.Value) { "✅ PASS" } else { "❌ FAIL" }
        Write-Host "   $($_.Key): $status" -ForegroundColor $(if ($_.Value) { "Green" } else { "Red" })
    }
    
    Write-Host ""
    if ($results.Values -contains $true) {
        Write-Host "🎉 Some connections working! Phone plugin should detect devices." -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  No phone connections detected. Check troubleshooting steps above." -ForegroundColor Yellow
    }
}
else {
    Write-Host "📋 Usage Examples:" -ForegroundColor Yellow
    Write-Host "   Test all connections:     .\debug-phone.ps1 -TestConnection" -ForegroundColor Gray
    Write-Host "   Test specific phone IP:   .\debug-phone.ps1 -TestConnection -PhoneIP 192.168.1.100" -ForegroundColor Gray
    Write-Host "   Install ADB tools:        .\debug-phone.ps1 -InstallADB" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🔧 Quick checks:" -ForegroundColor Yellow
    Test-USBDevices | Out-Null
    Test-PhonePluginAPI | Out-Null
}