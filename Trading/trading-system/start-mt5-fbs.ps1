# Start MT5 with FBS Live Account
# This script helps launch MT5 and connect to your FBS live account

param(
    [switch]$Download = $false,
    [switch]$AutoLogin = $true
)

# Load environment
. "$PSScriptRoot\load-env.ps1"

if (-not (Test-TradingEnvironment)) {
    Write-Error "Environment not properly configured. Please check your .env file."
    exit 1
}

# Get FBS credentials
$mt5Login = [Environment]::GetEnvironmentVariable('MT5_LOGIN', 'Process')
$mt5Password = [Environment]::GetEnvironmentVariable('MT5_PASSWORD', 'Process')
$mt5Server = [Environment]::GetEnvironmentVariable('MT5_SERVER', 'Process')

function Download-MT5 {
    Write-Host "📥 Downloading MT5 Terminal..." -ForegroundColor Yellow
    
    $downloadUrl = "https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe"
    $downloadPath = "$env:TEMP\mt5setup.exe"
    
    try {
        Write-Host "Downloading from: $downloadUrl" -ForegroundColor Cyan
        Invoke-WebRequest -Uri $downloadUrl -OutFile $downloadPath -UseBasicParsing
        
        Write-Host "✅ Download complete: $downloadPath" -ForegroundColor Green
        Write-Host "🚀 Starting MT5 installer..." -ForegroundColor Yellow
        
        Start-Process -FilePath $downloadPath -Wait
        
        Write-Host "✅ MT5 installation completed" -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to download MT5: $($_.Exception.Message)"
        Write-Host "Please download manually from: https://fbs.com/platforms/metatrader5" -ForegroundColor Yellow
    }
}

function Find-MT5Terminal {
    $searchPaths = @(
        "C:\Program Files\MetaTrader 5\terminal64.exe",
        "C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
        "$env:USERPROFILE\AppData\Roaming\MetaQuotes\Terminal\*\terminal64.exe",
        "C:\Users\*\AppData\Roaming\MetaQuotes\Terminal\*\terminal64.exe"
    )
    
    foreach ($path in $searchPaths) {
        $resolved = Resolve-Path $path -ErrorAction SilentlyContinue
        if ($resolved) {
            return $resolved.Path | Select-Object -First 1
        }
    }
    
    # Search in Program Files
    $programFiles = Get-ChildItem "C:\Program Files*" -Recurse -Filter "terminal64.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($programFiles) {
        return $programFiles.FullName
    }
    
    return $null
}

function Start-MT5WithFBS {
    param([string]$MT5Path)
    
    Write-Host "🚀 Starting MT5 with FBS configuration..." -ForegroundColor Green
    
    if (-not (Test-Path $MT5Path)) {
        Write-Error "MT5 executable not found: $MT5Path"
        return $false
    }
    
    try {
        # Start MT5
        $process = Start-Process -FilePath $MT5Path -PassThru
        Write-Host "✅ MT5 Terminal started (PID: $($process.Id))" -ForegroundColor Green
        
        # Wait a moment for MT5 to initialize
        Start-Sleep -Seconds 5
        
        if ($AutoLogin) {
            Write-Host "🔐 FBS Account Login Information:" -ForegroundColor Yellow
            Write-Host "   Login: $mt5Login" -ForegroundColor Green
            Write-Host "   Server: $mt5Server" -ForegroundColor Green
            Write-Host "   Password: [PROTECTED]" -ForegroundColor Green
            Write-Host ""
            Write-Host "⚠️  Please manually login to MT5 with these credentials" -ForegroundColor Yellow
            Write-Host "   1. Click 'File' -> 'Login to Trade Account'" -ForegroundColor Gray
            Write-Host "   2. Enter Login: $mt5Login" -ForegroundColor Gray
            Write-Host "   3. Enter Password: [Your FBS Password]" -ForegroundColor Gray
            Write-Host "   4. Select Server: $mt5Server" -ForegroundColor Gray
        }
        
        return $true
    }
    catch {
        Write-Error "Failed to start MT5: $($_.Exception.Message)"
        return $false
    }
}

# Main execution
Write-Host "🎯 FBS MT5 Live Trading Launcher" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

if ($Download) {
    Download-MT5
    return
}

# Check if MT5 is already running
$runningMT5 = Get-Process | Where-Object { $_.ProcessName -like "*terminal*" }
if ($runningMT5) {
    Write-Host "✅ MT5 already running:" -ForegroundColor Green
    $runningMT5 | ForEach-Object { Write-Host "   Process: $($_.ProcessName) (PID: $($_.Id))" -ForegroundColor Gray }
    Write-Host ""
    Write-Host "🔌 Checking device sync..." -ForegroundColor Yellow
    
    # Trigger device sync to detect the running MT5
    try {
        $syncResult = Invoke-RestMethod "http://localhost:3000/api/v1/devices/sync" -Method POST -ErrorAction SilentlyContinue
        Write-Host "✅ Device sync triggered" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  Device sync failed - ensure microservice is running" -ForegroundColor Yellow
    }
}
else {
    Write-Host "🔍 Searching for MT5 installation..." -ForegroundColor Yellow
    $mt5Path = Find-MT5Terminal
    
    if ($mt5Path) {
        Write-Host "✅ Found MT5: $mt5Path" -ForegroundColor Green
        $started = Start-MT5WithFBS -MT5Path $mt5Path
        
        if ($started) {
            Write-Host ""
            Write-Host "🎉 MT5 launched successfully!" -ForegroundColor Green
            Write-Host "   Now sync with device manager..." -ForegroundColor Yellow
            
            # Wait and trigger device sync
            Start-Sleep -Seconds 3
            try {
                $syncResult = Invoke-RestMethod "http://localhost:3000/api/v1/devices/sync" -Method POST -ErrorAction SilentlyContinue
                Write-Host "✅ Device sync completed" -ForegroundColor Green
            }
            catch {
                Write-Host "⚠️  Device sync failed - run manually: .\device-manager.ps1 -Command sync" -ForegroundColor Yellow
            }
        }
    }
    else {
        Write-Host "❌ MT5 not found on this system" -ForegroundColor Red
        Write-Host ""
        Write-Host "📥 Installation Options:" -ForegroundColor Yellow
        Write-Host "   1. Run: .\start-mt5-fbs.ps1 -Download" -ForegroundColor Cyan
        Write-Host "   2. Download from: https://fbs.com/platforms/metatrader5" -ForegroundColor Cyan
        Write-Host "   3. Install and then run this script again" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Login to MT5 with FBS credentials" -ForegroundColor Gray
Write-Host "   2. Verify connection to FBS-Real server" -ForegroundColor Gray
Write-Host "   3. Check account balance and trading permissions" -ForegroundColor Gray
Write-Host "   4. Ready for live trading!" -ForegroundColor Green