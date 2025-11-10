# GenX_FX Environment Variables Setup Script
# This script sets up all necessary environment variables for smooth operation

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GenX_FX Environment Setup" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Define project paths
$GENX_PROJECT_ROOT = "C:\Users\lengk\GenX_FX_Remote"
$GENX_HOME = "C:\Users\lengk"
$GENX_LOGS = "$GENX_PROJECT_ROOT\logs"
$GENX_CONFIG = "$GENX_PROJECT_ROOT\config"
$GENX_DATA = "$GENX_PROJECT_ROOT\data"

# JetBrains and PyCharm paths
$JETBRAINS_TOOLBOX = "$env:LOCALAPPDATA\JetBrains\Toolbox"
$PYCHARM_PATH = ""
$JETBRAINS_CONFIG = "$env:APPDATA\JetBrains"

# Find PyCharm installation
Write-Host "🔍 Looking for PyCharm installation..." -ForegroundColor Yellow

# Common PyCharm installation paths
$PycharmPaths = @(
    "$env:LOCALAPPDATA\JetBrains\Toolbox\apps\PyCharm-P\ch-0\*\bin\pycharm64.exe",
    "$env:LOCALAPPDATA\JetBrains\Toolbox\apps\PyCharm-C\ch-0\*\bin\pycharm64.exe",
    "$env:ProgramFiles\JetBrains\PyCharm *\bin\pycharm64.exe",
    "${env:ProgramFiles(x86)}\JetBrains\PyCharm *\bin\pycharm64.exe",
    "$env:LOCALAPPDATA\Programs\PyCharm *\bin\pycharm64.exe"
)

foreach ($path in $PycharmPaths) {
    $found = Get-ChildItem -Path (Split-Path $path) -Filter (Split-Path $path -Leaf) -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($found) {
        $PYCHARM_PATH = $found.FullName
        Write-Host "✅ Found PyCharm: $PYCHARM_PATH" -ForegroundColor Green
        break
    }
}

if (-not $PYCHARM_PATH) {
    Write-Host "⚠️  PyCharm not found in common locations" -ForegroundColor Yellow
    $PYCHARM_PATH = "pycharm64"  # Use from PATH if available
}

# Python paths
$PYTHON_PATH = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PYTHON_PATH) {
    $PYTHON_PATH = "python"  # Use from PATH
}

Write-Host "🐍 Python path: $PYTHON_PATH" -ForegroundColor Green

# Create directories if they don't exist
$Directories = @($GENX_LOGS, $GENX_CONFIG, $GENX_DATA)
foreach ($dir in $Directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "📁 Created directory: $dir" -ForegroundColor Green
    }
}

# Set environment variables for current session
Write-Host "⚙️  Setting up environment variables..." -ForegroundColor Yellow

# GenX Project Variables
$env:GENX_PROJECT_ROOT = $GENX_PROJECT_ROOT
$env:GENX_HOME = $GENX_HOME
$env:GENX_LOGS_DIR = $GENX_LOGS
$env:GENX_CONFIG_DIR = $GENX_CONFIG
$env:GENX_DATA_DIR = $GENX_DATA

# JetBrains Variables
$env:PYCHARM_PATH = $PYCHARM_PATH
$env:JETBRAINS_TOOLBOX = $JETBRAINS_TOOLBOX
$env:JETBRAINS_CONFIG = $JETBRAINS_CONFIG

# Service Variables
$env:GENX_SERVICE_CONFIG = "$GENX_PROJECT_ROOT\service_config.json"
$env:GENX_SERVICE_STATUS = "$GENX_PROJECT_ROOT\service_status.json"
$env:GENX_SERVICE_PID = "$GENX_PROJECT_ROOT\genx_service.pid"
$env:GENX_DASHBOARD_PORT = "9000"
$env:GENX_API_PORT = "8000"

# Python Environment
$env:PYTHONPATH = $GENX_PROJECT_ROOT
$env:PYTHONUNBUFFERED = "1"

Write-Host "✅ Session variables set!" -ForegroundColor Green

# Create permanent environment variables (User level)
Write-Host "💾 Setting permanent user environment variables..." -ForegroundColor Yellow

$UserEnvVars = @{
    "GENX_PROJECT_ROOT" = $GENX_PROJECT_ROOT
    "GENX_HOME" = $GENX_HOME
    "GENX_LOGS_DIR" = $GENX_LOGS
    "GENX_CONFIG_DIR" = $GENX_CONFIG
    "GENX_DATA_DIR" = $GENX_DATA
    "PYCHARM_PATH" = $PYCHARM_PATH
    "JETBRAINS_TOOLBOX" = $JETBRAINS_TOOLBOX
    "GENX_SERVICE_CONFIG" = "$GENX_PROJECT_ROOT\service_config.json"
    "GENX_DASHBOARD_PORT" = "9000"
    "GENX_API_PORT" = "8000"
}

foreach ($var in $UserEnvVars.GetEnumerator()) {
    [Environment]::SetEnvironmentVariable($var.Key, $var.Value, "User")
    Write-Host "  ✓ $($var.Key) = $($var.Value)" -ForegroundColor DarkGreen
}

# Update PATH to include project root and scripts
$CurrentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($CurrentPath -notlike "*$GENX_PROJECT_ROOT*") {
    $NewPath = "$CurrentPath;$GENX_PROJECT_ROOT;$GENX_PROJECT_ROOT\scripts"
    [Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")
    Write-Host "✅ Added project paths to USER PATH" -ForegroundColor Green
}

# Create PowerShell profile for automatic loading
$ProfilePath = $PROFILE.CurrentUserCurrentHost
$ProfileDir = Split-Path $ProfilePath -Parent

if (-not (Test-Path $ProfileDir)) {
    New-Item -ItemType Directory -Path $ProfileDir -Force | Out-Null
}

$ProfileContent = @"
# GenX_FX PowerShell Profile Configuration
# Auto-generated on $(Get-Date)

# GenX_FX Project Variables
`$env:GENX_PROJECT_ROOT = "$GENX_PROJECT_ROOT"
`$env:GENX_HOME = "$GENX_HOME"
`$env:GENX_LOGS_DIR = "$GENX_LOGS"
`$env:GENX_CONFIG_DIR = "$GENX_CONFIG"
`$env:GENX_DATA_DIR = "$GENX_DATA"
`$env:PYCHARM_PATH = "$PYCHARM_PATH"
`$env:JETBRAINS_TOOLBOX = "$JETBRAINS_TOOLBOX"
`$env:PYTHONPATH = "$GENX_PROJECT_ROOT"
`$env:PYTHONUNBUFFERED = "1"

# GenX_FX Helper Functions
function Start-GenXService {
    param([string]`$ServiceName = "")
    Set-Location "$GENX_PROJECT_ROOT"
    if (`$ServiceName) {
        python genx_24_7_service.py start --service `$ServiceName
    } else {
        python genx_24_7_service.py start
    }
}

function Stop-GenXService {
    param([string]`$ServiceName = "")
    Set-Location "$GENX_PROJECT_ROOT"
    if (`$ServiceName) {
        python genx_24_7_service.py stop --service `$ServiceName
    } else {
        python genx_24_7_service.py stop
    }
}

function Get-GenXStatus {
    Set-Location "$GENX_PROJECT_ROOT"
    python genx_24_7_service.py status
}

function Start-GenXDashboard {
    Set-Location "$GENX_PROJECT_ROOT"
    python monitoring_dashboard.py --host 0.0.0.0 --port `$env:GENX_DASHBOARD_PORT
}

function Open-GenXDashboard {
    Start-Process "http://localhost:`$env:GENX_DASHBOARD_PORT"
}

function Start-GenXPyCharm {
    if (Test-Path "`$env:PYCHARM_PATH") {
        & "`$env:PYCHARM_PATH" "`$env:GENX_PROJECT_ROOT"
    } else {
        Write-Host "PyCharm not found at: `$env:PYCHARM_PATH" -ForegroundColor Red
        Write-Host "Please update the PYCHARM_PATH variable" -ForegroundColor Yellow
    }
}

# GenX_FX Aliases
Set-Alias -Name genx-start -Value Start-GenXService
Set-Alias -Name genx-stop -Value Stop-GenXService
Set-Alias -Name genx-status -Value Get-GenXStatus
Set-Alias -Name genx-dashboard -Value Start-GenXDashboard
Set-Alias -Name genx-web -Value Open-GenXDashboard
Set-Alias -Name genx-pycharm -Value Start-GenXPyCharm
Set-Alias -Name genx-cd -Value "Set-Location `$env:GENX_PROJECT_ROOT"

# Welcome message
Write-Host "GenX_FX Environment Loaded! 🚀" -ForegroundColor Green
Write-Host "Available commands:" -ForegroundColor Yellow
Write-Host "  genx-start      - Start GenX services" -ForegroundColor Cyan
Write-Host "  genx-stop       - Stop GenX services" -ForegroundColor Cyan
Write-Host "  genx-status     - Check service status" -ForegroundColor Cyan
Write-Host "  genx-dashboard  - Start monitoring dashboard" -ForegroundColor Cyan
Write-Host "  genx-web        - Open dashboard in browser" -ForegroundColor Cyan
Write-Host "  genx-pycharm    - Open project in PyCharm" -ForegroundColor Cyan
Write-Host "  genx-cd         - Navigate to project directory" -ForegroundColor Cyan
"@

# Backup existing profile if it exists
if (Test-Path $ProfilePath) {
    $BackupPath = "$ProfilePath.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $ProfilePath $BackupPath
    Write-Host "📋 Backed up existing profile to: $BackupPath" -ForegroundColor Yellow
}

# Write new profile
Set-Content -Path $ProfilePath -Value $ProfileContent -Encoding UTF8
Write-Host "✅ PowerShell profile updated: $ProfilePath" -ForegroundColor Green

# Create batch files for easy access
$BatchFiles = @{
    "start_genx_service.bat" = @"
@echo off
cd /d "$GENX_PROJECT_ROOT"
python genx_24_7_service.py start
pause
"@
    
    "stop_genx_service.bat" = @"
@echo off
cd /d "$GENX_PROJECT_ROOT"
python genx_24_7_service.py stop
pause
"@
    
    "genx_status.bat" = @"
@echo off
cd /d "$GENX_PROJECT_ROOT"
python genx_24_7_service.py status
pause
"@
    
    "open_genx_dashboard.bat" = @"
@echo off
start "" http://localhost:9000
"@
    
    "start_genx_pycharm.bat" = @"
@echo off
if exist "$PYCHARM_PATH" (
    start "" "$PYCHARM_PATH" "$GENX_PROJECT_ROOT"
) else (
    echo PyCharm not found at: $PYCHARM_PATH
    echo Please check your PyCharm installation
    pause
)
"@
}

Write-Host "📝 Creating batch files..." -ForegroundColor Yellow
foreach ($batch in $BatchFiles.GetEnumerator()) {
    $batchPath = Join-Path $GENX_PROJECT_ROOT $batch.Key
    Set-Content -Path $batchPath -Value $batch.Value -Encoding ASCII
    Write-Host "  ✓ Created: $($batch.Key)" -ForegroundColor DarkGreen
}

# Create desktop shortcuts
Write-Host "🖥️  Creating desktop shortcuts..." -ForegroundColor Yellow

$DesktopPath = [Environment]::GetFolderPath("Desktop")
$WScriptShell = New-Object -ComObject WScript.Shell

$Shortcuts = @{
    "GenX Service Manager" = @{
        "Target" = "powershell.exe"
        "Arguments" = "-NoProfile -Command `"& '$GENX_PROJECT_ROOT\start_genx_service.bat'`""
        "WorkingDirectory" = $GENX_PROJECT_ROOT
        "IconLocation" = "shell32.dll,21"
    }
    
    "GenX Dashboard" = @{
        "Target" = "http://localhost:9000"
        "WorkingDirectory" = $GENX_PROJECT_ROOT
        "IconLocation" = "shell32.dll,14"
    }
    
    "GenX PyCharm" = @{
        "Target" = "$PYCHARM_PATH"
        "Arguments" = "`"$GENX_PROJECT_ROOT`""
        "WorkingDirectory" = $GENX_PROJECT_ROOT
        "IconLocation" = "$PYCHARM_PATH,0"
    }
}

foreach ($shortcut in $Shortcuts.GetEnumerator()) {
    $ShortcutPath = Join-Path $DesktopPath "$($shortcut.Key).lnk"
    $Shortcut_Object = $WScriptShell.CreateShortcut($ShortcutPath)
    $Shortcut_Object.TargetPath = $shortcut.Value.Target
    if ($shortcut.Value.Arguments) {
        $Shortcut_Object.Arguments = $shortcut.Value.Arguments
    }
    $Shortcut_Object.WorkingDirectory = $shortcut.Value.WorkingDirectory
    if ($shortcut.Value.IconLocation) {
        $Shortcut_Object.IconLocation = $shortcut.Value.IconLocation
    }
    $Shortcut_Object.Save()
    Write-Host "  ✓ Created: $($shortcut.Key).lnk" -ForegroundColor DarkGreen
}

# Display environment summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎉 ENVIRONMENT SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "📁 PROJECT PATHS:" -ForegroundColor Yellow
Write-Host "   Root:    $env:GENX_PROJECT_ROOT" -ForegroundColor White
Write-Host "   Logs:    $env:GENX_LOGS_DIR" -ForegroundColor White
Write-Host "   Config:  $env:GENX_CONFIG_DIR" -ForegroundColor White
Write-Host "   Data:    $env:GENX_DATA_DIR" -ForegroundColor White

Write-Host ""
Write-Host "🎯 JETBRAINS/PYCHARM:" -ForegroundColor Yellow
Write-Host "   PyCharm: $env:PYCHARM_PATH" -ForegroundColor White
Write-Host "   Toolbox: $env:JETBRAINS_TOOLBOX" -ForegroundColor White

Write-Host ""
Write-Host "🌐 SERVICE PORTS:" -ForegroundColor Yellow
Write-Host "   Dashboard: http://localhost:$env:GENX_DASHBOARD_PORT" -ForegroundColor White
Write-Host "   API:       http://localhost:$env:GENX_API_PORT" -ForegroundColor White

Write-Host ""
Write-Host "🚀 QUICK COMMANDS (after restarting PowerShell):" -ForegroundColor Yellow
Write-Host "   genx-start      - Start services" -ForegroundColor Cyan
Write-Host "   genx-status     - Check status" -ForegroundColor Cyan
Write-Host "   genx-dashboard  - Start dashboard" -ForegroundColor Cyan
Write-Host "   genx-web        - Open in browser" -ForegroundColor Cyan
Write-Host "   genx-pycharm    - Open in PyCharm" -ForegroundColor Cyan

Write-Host ""
Write-Host "🖥️  DESKTOP SHORTCUTS CREATED:" -ForegroundColor Yellow
Write-Host "   - GenX Service Manager.lnk" -ForegroundColor Cyan
Write-Host "   - GenX Dashboard.lnk" -ForegroundColor Cyan
Write-Host "   - GenX PyCharm.lnk" -ForegroundColor Cyan

Write-Host ""
Write-Host "⚡ TO ACTIVATE:" -ForegroundColor Yellow
Write-Host "   1. Close and reopen PowerShell" -ForegroundColor White
Write-Host "   2. Or run: . `$PROFILE" -ForegroundColor White
Write-Host "   3. Use genx-* commands!" -ForegroundColor White

Write-Host ""
Write-Host "✅ Environment variables are now permanent!" -ForegroundColor Green
Write-Host "🎯 Ready for smooth GenX_FX operation!" -ForegroundColor Green