# GenX_FX Environment Loader - Load environment variables into current session
# Run this script to activate GenX_FX environment in your current PowerShell session

Write-Host "Loading GenX_FX Environment..." -ForegroundColor Green

# Load all user environment variables into current session
$env:GENX_PROJECT_ROOT = [Environment]::GetEnvironmentVariable("GENX_PROJECT_ROOT", "User")
$env:GENX_HOME = [Environment]::GetEnvironmentVariable("GENX_HOME", "User")
$env:GENX_LOGS_DIR = [Environment]::GetEnvironmentVariable("GENX_LOGS_DIR", "User")
$env:GENX_CONFIG_DIR = [Environment]::GetEnvironmentVariable("GENX_CONFIG_DIR", "User")
$env:GENX_DATA_DIR = [Environment]::GetEnvironmentVariable("GENX_DATA_DIR", "User")
$env:PYCHARM_PATH = [Environment]::GetEnvironmentVariable("PYCHARM_PATH", "User")
$env:JETBRAINS_TOOLBOX = [Environment]::GetEnvironmentVariable("JETBRAINS_TOOLBOX", "User")
$env:GENX_SERVICE_CONFIG = [Environment]::GetEnvironmentVariable("GENX_SERVICE_CONFIG", "User")
$env:GENX_DASHBOARD_PORT = [Environment]::GetEnvironmentVariable("GENX_DASHBOARD_PORT", "User")
$env:GENX_API_PORT = [Environment]::GetEnvironmentVariable("GENX_API_PORT", "User")
$env:PYTHONPATH = $env:GENX_PROJECT_ROOT
$env:PYTHONUNBUFFERED = "1"

# Define helpful functions
function genx-start { 
    Set-Location $env:GENX_PROJECT_ROOT
    python genx_24_7_service.py start 
}

function genx-stop { 
    Set-Location $env:GENX_PROJECT_ROOT
    python genx_24_7_service.py stop 
}

function genx-status { 
    Set-Location $env:GENX_PROJECT_ROOT
    python genx_24_7_service.py status 
}

function genx-dashboard { 
    Set-Location $env:GENX_PROJECT_ROOT
    python monitoring_dashboard.py --host 0.0.0.0 --port $env:GENX_DASHBOARD_PORT 
}

function genx-web { 
    Start-Process "http://localhost:$env:GENX_DASHBOARD_PORT" 
}

function genx-pycharm { 
    if (Test-Path $env:PYCHARM_PATH) { 
        & $env:PYCHARM_PATH $env:GENX_PROJECT_ROOT 
    } else { 
        Write-Host "PyCharm not found at: $env:PYCHARM_PATH" -ForegroundColor Red
    } 
}

function genx-cd { 
    Set-Location $env:GENX_PROJECT_ROOT 
}

function Show-GenXCommands {
    Write-Host "GenX_FX Available Commands:" -ForegroundColor Yellow
    Write-Host "  genx-start      - Start GenX services" -ForegroundColor Cyan
    Write-Host "  genx-stop       - Stop GenX services" -ForegroundColor Cyan
    Write-Host "  genx-status     - Check service status" -ForegroundColor Cyan
    Write-Host "  genx-dashboard  - Start monitoring dashboard" -ForegroundColor Cyan
    Write-Host "  genx-web        - Open dashboard in browser" -ForegroundColor Cyan
    Write-Host "  genx-pycharm    - Open project in PyCharm" -ForegroundColor Cyan
    Write-Host "  genx-cd         - Navigate to project directory" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Environment Variables:" -ForegroundColor Yellow
    Write-Host "  PROJECT_ROOT: $env:GENX_PROJECT_ROOT" -ForegroundColor White
    Write-Host "  PYCHARM_PATH: $env:PYCHARM_PATH" -ForegroundColor White
    Write-Host "  DASHBOARD:    http://localhost:$env:GENX_DASHBOARD_PORT" -ForegroundColor White
}

# Display welcome message
Write-Host ""
Write-Host "GenX_FX Environment Loaded Successfully! " -ForegroundColor Green -NoNewline
Write-Host "🚀" -ForegroundColor Yellow
Write-Host ""

Show-GenXCommands