# Launch MT5 with Real FBS Account Configuration

Write-Host "Launching MT5 with Real FBS Account..." -ForegroundColor Cyan

# Find MT5 installation
$mt5Paths = @(
    "C:\Program Files\MetaTrader 5\terminal64.exe",
    "C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
    "$env:LOCALAPPDATA\Programs\MetaTrader 5\terminal64.exe"
)

$mt5Path = $null
foreach ($path in $mt5Paths) {
    if (Test-Path $path) {
        $mt5Path = $path
        break
    }
}

if (-not $mt5Path) {
    Write-Host "MT5 not found. Please install MT5 first." -ForegroundColor Red
    exit 1
}

Write-Host "Found MT5 at: $mt5Path" -ForegroundColor Green

# Launch MT5 with real account config
Write-Host "Starting MT5 with FBS Real Account..." -ForegroundColor Yellow

$configPath = Join-Path $PWD "mt5_fbs_real_config.ini"
$workingDir = Split-Path $mt5Path

# Start MT5
Start-Process -FilePath $mt5Path -ArgumentList "/config:`"$configPath`"" -WorkingDirectory $workingDir

Write-Host "MT5 launched with real account configuration" -ForegroundColor Green

Write-Host "`nReal Account Details:" -ForegroundColor Cyan
Write-Host "Login: 40933210" -ForegroundColor White
Write-Host "Server: FBS-Real" -ForegroundColor White
Write-Host "Server IP: 185.237.98.177:443" -ForegroundColor White

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. MT5 should open automatically" -ForegroundColor White
Write-Host "2. Login with your credentials if prompted" -ForegroundColor White
Write-Host "3. Verify connection and account balance" -ForegroundColor White
Write-Host "4. Start trading!" -ForegroundColor White

# Create desktop shortcut for real account
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\MT5 FBS Real.lnk")
$Shortcut.TargetPath = $mt5Path
$Shortcut.Arguments = "/config:`"$configPath`""
$Shortcut.WorkingDirectory = $workingDir
$Shortcut.IconLocation = "$mt5Path,0"
$Shortcut.Description = "MetaTrader 5 - FBS Real Account"
$Shortcut.Save()

Write-Host "`nDesktop shortcut 'MT5 FBS Real' created" -ForegroundColor Green