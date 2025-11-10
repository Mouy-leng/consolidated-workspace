# Start PyCharm with this project
# This script opens PyCharm and automatically loads the consolidated workspace

$projectPath = "E:\Code\consolidated-workspace"

Write-Host "Starting PyCharm for consolidated workspace..." -ForegroundColor Cyan
Write-Host "Project: $projectPath" -ForegroundColor Yellow

# Try to find PyCharm executable
$pycharmPaths = @(
    "C:\Users\$env:USERNAME\AppData\Local\JetBrains\Toolbox\scripts\pycharm.cmd",
    "C:\Program Files\JetBrains\PyCharm*\bin\pycharm64.exe",
    "C:\Program Files (x86)\JetBrains\PyCharm*\bin\pycharm64.exe",
    "$env:LOCALAPPDATA\Programs\PyCharm*\bin\pycharm64.exe"
)

$pycharmExe = $null
foreach ($path in $pycharmPaths) {
    $found = Get-Item $path -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $pycharmExe = $found.FullName
        break
    }
}

if (-not $pycharmExe) {
    # Try command
    $pycharmCmd = Get-Command pycharm -ErrorAction SilentlyContinue
    if ($pycharmCmd) {
        $pycharmExe = $pycharmCmd.Source
    }
}

if ($pycharmExe) {
    Write-Host "Found PyCharm: $pycharmExe" -ForegroundColor Green
    
    # Start PyCharm with project
    if ($pycharmExe -like "*.cmd") {
        Start-Process cmd.exe -ArgumentList "/c", "`"$pycharmExe`" `"$projectPath`""
    } else {
        Start-Process $pycharmExe -ArgumentList "`"$projectPath`""
    }
    
    Write-Host "PyCharm started successfully!" -ForegroundColor Green
} else {
    Write-Host "PyCharm not found. Please install PyCharm first." -ForegroundColor Red
    Write-Host "Download from: https://www.jetbrains.com/pycharm/download/" -ForegroundColor Yellow
    exit 1
}

