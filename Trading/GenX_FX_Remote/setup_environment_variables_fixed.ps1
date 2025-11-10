# GenX_FX Environment Variables Setup Script
# This script sets up all necessary environment variables for smooth operation

Write-Host "========================================"
Write-Host "GenX_FX Environment Setup"
Write-Host "========================================"

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
Write-Host "Looking for PyCharm installation..."

# Common PyCharm installation paths
$PycharmPaths = @(
    "$env:LOCALAPPDATA\JetBrains\Toolbox\apps\PyCharm-P\ch-0\*\bin\pycharm64.exe",
    "$env:LOCALAPPDATA\JetBrains\Toolbox\apps\PyCharm-C\ch-0\*\bin\pycharm64.exe",
    "$env:ProgramFiles\JetBrains\PyCharm *\bin\pycharm64.exe"
)

foreach ($pathPattern in $PycharmPaths) {
    try {
        $found = Get-ChildItem -Path $pathPattern -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($found) {
            $PYCHARM_PATH = $found.FullName
            Write-Host "Found PyCharm: $PYCHARM_PATH"
            break
        }
    }
    catch {
        # Continue to next path
    }
}

if (-not $PYCHARM_PATH) {
    Write-Host "PyCharm not found in common locations"
    $PYCHARM_PATH = "pycharm64"
}

# Python paths
$PYTHON_PATH = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PYTHON_PATH) {
    $PYTHON_PATH = "python"
}

Write-Host "Python path: $PYTHON_PATH"

# Create directories if they don't exist
$Directories = @($GENX_LOGS, $GENX_CONFIG, $GENX_DATA)
foreach ($dir in $Directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created directory: $dir"
    }
}

# Set environment variables for current session
Write-Host "Setting up environment variables..."

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

Write-Host "Session variables set!"

# Create permanent environment variables (User level)
Write-Host "Setting permanent user environment variables..."

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
    Write-Host "  Set: $($var.Key) = $($var.Value)"
}

# Update PATH to include project root
$CurrentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($CurrentPath -notlike "*$GENX_PROJECT_ROOT*") {
    $NewPath = "$CurrentPath;$GENX_PROJECT_ROOT"
    [Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")
    Write-Host "Added project path to USER PATH"
}

# Create batch files for easy access
Write-Host "Creating batch files..."

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

foreach ($batch in $BatchFiles.GetEnumerator()) {
    $batchPath = Join-Path $GENX_PROJECT_ROOT $batch.Key
    Set-Content -Path $batchPath -Value $batch.Value -Encoding ASCII
    Write-Host "  Created: $($batch.Key)"
}

# Create desktop shortcuts
Write-Host "Creating desktop shortcuts..."

$DesktopPath = [Environment]::GetFolderPath("Desktop")

try {
    $WScriptShell = New-Object -ComObject WScript.Shell

    # GenX Service Manager shortcut
    $Shortcut = $WScriptShell.CreateShortcut("$DesktopPath\GenX Service Manager.lnk")
    $Shortcut.TargetPath = "$GENX_PROJECT_ROOT\start_genx_service.bat"
    $Shortcut.WorkingDirectory = $GENX_PROJECT_ROOT
    $Shortcut.Save()
    Write-Host "  Created: GenX Service Manager.lnk"

    # GenX Dashboard shortcut
    $Shortcut = $WScriptShell.CreateShortcut("$DesktopPath\GenX Dashboard.lnk")
    $Shortcut.TargetPath = "$GENX_PROJECT_ROOT\open_genx_dashboard.bat"
    $Shortcut.WorkingDirectory = $GENX_PROJECT_ROOT
    $Shortcut.Save()
    Write-Host "  Created: GenX Dashboard.lnk"

    # GenX PyCharm shortcut
    if (Test-Path $PYCHARM_PATH) {
        $Shortcut = $WScriptShell.CreateShortcut("$DesktopPath\GenX PyCharm.lnk")
        $Shortcut.TargetPath = $PYCHARM_PATH
        $Shortcut.Arguments = "`"$GENX_PROJECT_ROOT`""
        $Shortcut.WorkingDirectory = $GENX_PROJECT_ROOT
        $Shortcut.Save()
        Write-Host "  Created: GenX PyCharm.lnk"
    }
}
catch {
    Write-Host "Could not create desktop shortcuts: $($_.Exception.Message)"
}

# Create a simple PowerShell profile addition
$ProfilePath = $PROFILE.CurrentUserCurrentHost
$ProfileAddition = @"

# GenX_FX Environment Variables
`$env:GENX_PROJECT_ROOT = "$GENX_PROJECT_ROOT"
`$env:GENX_HOME = "$GENX_HOME"
`$env:PYCHARM_PATH = "$PYCHARM_PATH"
`$env:GENX_DASHBOARD_PORT = "9000"
`$env:GENX_API_PORT = "8000"
`$env:PYTHONPATH = "$GENX_PROJECT_ROOT"

# GenX_FX Aliases
function genx-start { Set-Location "$GENX_PROJECT_ROOT"; python genx_24_7_service.py start }
function genx-stop { Set-Location "$GENX_PROJECT_ROOT"; python genx_24_7_service.py stop }
function genx-status { Set-Location "$GENX_PROJECT_ROOT"; python genx_24_7_service.py status }
function genx-dashboard { Set-Location "$GENX_PROJECT_ROOT"; python monitoring_dashboard.py --host 0.0.0.0 --port `$env:GENX_DASHBOARD_PORT }
function genx-web { Start-Process "http://localhost:`$env:GENX_DASHBOARD_PORT" }
function genx-pycharm { if (Test-Path "`$env:PYCHARM_PATH") { & "`$env:PYCHARM_PATH" "`$env:GENX_PROJECT_ROOT" } else { Write-Host "PyCharm not found" } }
function genx-cd { Set-Location "`$env:GENX_PROJECT_ROOT" }

Write-Host "GenX_FX Environment Loaded!" -ForegroundColor Green
"@

# Add to profile
try {
    $ProfileDir = Split-Path $ProfilePath -Parent
    if (-not (Test-Path $ProfileDir)) {
        New-Item -ItemType Directory -Path $ProfileDir -Force | Out-Null
    }
    
    Add-Content -Path $ProfilePath -Value $ProfileAddition
    Write-Host "PowerShell profile updated: $ProfilePath"
}
catch {
    Write-Host "Could not update PowerShell profile: $($_.Exception.Message)"
}

# Display environment summary
Write-Host ""
Write-Host "========================================"
Write-Host "ENVIRONMENT SETUP COMPLETE!"
Write-Host "========================================"

Write-Host ""
Write-Host "PROJECT PATHS:"
Write-Host "   Root:    $env:GENX_PROJECT_ROOT"
Write-Host "   Logs:    $env:GENX_LOGS_DIR"
Write-Host "   Config:  $env:GENX_CONFIG_DIR"
Write-Host "   Data:    $env:GENX_DATA_DIR"

Write-Host ""
Write-Host "JETBRAINS/PYCHARM:"
Write-Host "   PyCharm: $env:PYCHARM_PATH"
Write-Host "   Toolbox: $env:JETBRAINS_TOOLBOX"

Write-Host ""
Write-Host "SERVICE PORTS:"
Write-Host "   Dashboard: http://localhost:$env:GENX_DASHBOARD_PORT"
Write-Host "   API:       http://localhost:$env:GENX_API_PORT"

Write-Host ""
Write-Host "QUICK COMMANDS (after restarting PowerShell):"
Write-Host "   genx-start      - Start services"
Write-Host "   genx-status     - Check status"
Write-Host "   genx-dashboard  - Start dashboard"
Write-Host "   genx-web        - Open in browser"
Write-Host "   genx-pycharm    - Open in PyCharm"
Write-Host "   genx-cd         - Navigate to project"

Write-Host ""
Write-Host "BATCH FILES CREATED:"
foreach ($batch in $BatchFiles.Keys) {
    Write-Host "   $batch"
}

Write-Host ""
Write-Host "TO ACTIVATE:"
Write-Host "   1. Close and reopen PowerShell"
Write-Host "   2. Or run: . `$PROFILE"
Write-Host "   3. Use genx-* commands!"

Write-Host ""
Write-Host "Environment variables are now permanent!"
Write-Host "Ready for smooth GenX_FX operation!"