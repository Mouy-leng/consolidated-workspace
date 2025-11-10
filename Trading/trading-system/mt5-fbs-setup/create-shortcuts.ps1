# Create MT5 FBS shortcuts and startup files

Write-Host "Creating MT5 FBS shortcuts..." -ForegroundColor Yellow

# Find MT5 installation path
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

# Create desktop shortcut
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\MT5 FBS.lnk")
$Shortcut.TargetPath = $mt5Path
$Shortcut.WorkingDirectory = Split-Path $mt5Path
$Shortcut.IconLocation = "$mt5Path,0"
$Shortcut.Description = "MetaTrader 5 - FBS Broker"
$Shortcut.Save()

Write-Host "Desktop shortcut created" -ForegroundColor Green

# Create startup batch file
$batchContent = @"
@echo off
title MT5 FBS Trading Terminal
echo Starting MT5 with FBS...
cd /d "$(Split-Path $mt5Path)"
start "" "$(Split-Path $mt5Path -Leaf)"
echo MT5 started successfully!
pause
"@

$batchPath = "$env:USERPROFILE\Desktop\Start MT5 FBS.bat"
$batchContent | Out-File -FilePath $batchPath -Encoding ASCII

Write-Host "Startup batch file created" -ForegroundColor Green

# Create trading workspace
$workspaceDir = "$env:USERPROFILE\Documents\MT5-FBS-Trading"
New-Item -ItemType Directory -Force -Path $workspaceDir | Out-Null

# Copy config files to workspace
Copy-Item "*.json" -Destination $workspaceDir -ErrorAction SilentlyContinue
Copy-Item "*.ini" -Destination $workspaceDir -ErrorAction SilentlyContinue

Write-Host "Trading workspace created at: $workspaceDir" -ForegroundColor Green

Write-Host "`nSetup completed!" -ForegroundColor Cyan
Write-Host "You can now:" -ForegroundColor Yellow
Write-Host "1. Double-click 'MT5 FBS' shortcut on desktop" -ForegroundColor White
Write-Host "2. Or run 'Start MT5 FBS.bat' from desktop" -ForegroundColor White