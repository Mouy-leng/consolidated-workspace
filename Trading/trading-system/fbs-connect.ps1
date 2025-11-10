# FBS Trading Connection Script
# Secure connection to FBS trading platform via VPS

param(
    [string]$Command = "",
    [switch]$Interactive = $false,
    [switch]$StartMT5 = $false
)

# Load environment variables
. "$PSScriptRoot\load-env.ps1"

if (-not (Test-TradingEnvironment)) {
    Write-Error "Environment not properly configured. Please check your .env file."
    exit 1
}

# Get FBS configuration from environment
$fbsLogin = [Environment]::GetEnvironmentVariable('FBS_LOGIN', 'Process')
$fbsServer = [Environment]::GetEnvironmentVariable('FBS_SERVER', 'Process')
$vpsHost = [Environment]::GetEnvironmentVariable('VPS_HOST', 'Process')
$vpsUser = [Environment]::GetEnvironmentVariable('VPS_USER', 'Process')
$vpsKeyPath = [Environment]::GetEnvironmentVariable('VPS_KEY_PATH', 'Process')

function Connect-ToVPS {
    param(
        [string]$Host,
        [string]$User,
        [string]$KeyPath = "",
        [string]$RemoteCommand = "",
        [bool]$Interactive = $false
    )
    
    Write-Host "Connecting to VPS: $User@$Host" -ForegroundColor Yellow
    
    $sshArgs = @()
    
    if ($KeyPath -and (Test-Path $KeyPath)) {
        $sshArgs += "-i", $KeyPath
    }
    
    $sshArgs += "-o", "StrictHostKeyChecking=no"
    
    if (-not $Interactive -and $RemoteCommand) {
        $sshArgs += "$User@$Host", $RemoteCommand
    } else {
        $sshArgs += "$User@$Host"
    }
    
    try {
        if ($RemoteCommand) {
            Write-Host "Executing: $RemoteCommand" -ForegroundColor Cyan
        }
        
        ssh @sshArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Command executed successfully" -ForegroundColor Green
        } else {
            Write-Warning "Command execution failed with exit code: $LASTEXITCODE"
        }
    }
    catch {
        Write-Error "Failed to connect to VPS: $($_.Exception.Message)"
    }
}

function Start-MT5OnVPS {
    Write-Host "Starting MT5 on VPS with FBS configuration..." -ForegroundColor Yellow
    
    $mt5Command = @"
cd /opt/mt5 && 
./metatrader5 -login:$fbsLogin -server:$fbsServer -portable
"@
    
    Connect-ToVPS -Host $vpsHost -User $vpsUser -KeyPath $vpsKeyPath -RemoteCommand $mt5Command
}

function Show-FBSInfo {
    Write-Host "`n📊 FBS Trading Configuration" -ForegroundColor Green
    Write-Host "=============================" -ForegroundColor Green
    Write-Host "Login: $fbsLogin" -ForegroundColor Cyan
    Write-Host "Server: $fbsServer" -ForegroundColor Cyan
    Write-Host "VPS Host: $vpsHost" -ForegroundColor Cyan
    Write-Host "VPS User: $vpsUser" -ForegroundColor Cyan
    Write-Host ""
}

# Main execution
Show-FBSInfo

if ($StartMT5) {
    Start-MT5OnVPS
} elseif ($Interactive) {
    Write-Host "Opening interactive VPS session..." -ForegroundColor Green
    Connect-ToVPS -Host $vpsHost -User $vpsUser -KeyPath $vpsKeyPath -Interactive $true
} elseif ($Command) {
    Connect-ToVPS -Host $vpsHost -User $vpsUser -KeyPath $vpsKeyPath -RemoteCommand $Command
} else {
    Write-Host "FBS Trading Connection Script" -ForegroundColor Green
    Write-Host "============================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage Examples:"
    Write-Host "  Start MT5:         .\fbs-connect.ps1 -StartMT5"
    Write-Host "  Interactive shell: .\fbs-connect.ps1 -Interactive"
    Write-Host "  Custom command:    .\fbs-connect.ps1 -Command 'ps aux | grep mt5'"
    Write-Host ""
    
    # Test connection
    Write-Host "Testing VPS connection..."
    Connect-ToVPS -Host $vpsHost -User $vpsUser -KeyPath $vpsKeyPath -RemoteCommand "echo 'FBS VPS connection successful' && date"
}