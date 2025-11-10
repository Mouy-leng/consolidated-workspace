# Secure VPS Connection for Trading System
# This script connects to your VPS and executes trading commands securely

param(
    [string]$Command = "",
    [switch]$Interactive = $false
)

# Load environment variables
. "$PSScriptRoot\load-env.ps1"

if (-not (Test-TradingEnvironment)) {
    Write-Error "Environment not properly configured. Please check your .env file."
    exit 1
}

# Get VPS connection details from environment
$vpsHost = [Environment]::GetEnvironmentVariable('VPS_HOST', 'Process')
$vpsUser = [Environment]::GetEnvironmentVariable('VPS_USER', 'Process')
$vpsKeyPath = [Environment]::GetEnvironmentVariable('VPS_KEY_PATH', 'Process')

function Connect-ToVPS {
    param(
        [string]$VpsHost,
        [string]$User,
        [string]$KeyPath = "",
        [string]$RemoteCommand = "",
        [bool]$Interactive = $false
    )
    
    Write-Host "Connecting to VPS: $User@$VpsHost" -ForegroundColor Yellow
    
    # Build SSH command
    $sshArgs = @()
    
    if ($KeyPath -and (Test-Path $KeyPath)) {
        $sshArgs += "-i", $KeyPath
    }
    
    if (-not $Interactive -and $RemoteCommand) {
        $sshArgs += "$User@$VpsHost", $RemoteCommand
    }
    else {
        $sshArgs += "$User@$VpsHost"
    }
    
    try {
        if ($RemoteCommand) {
            Write-Host "Executing: $RemoteCommand" -ForegroundColor Cyan
        }
        
        ssh @sshArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Command executed successfully" -ForegroundColor Green
        }
        else {
            Write-Warning "Command execution failed with exit code: $LASTEXITCODE"
        }
    }
    catch {
        Write-Error "Failed to connect to VPS: $($_.Exception.Message)"
    }
}

function Test-VPSConnection {
    Write-Host "Testing VPS connection..." -ForegroundColor Yellow
    Connect-ToVPS -VpsHost $vpsHost -User $vpsUser -KeyPath $vpsKeyPath -RemoteCommand "echo 'Connection test successful' && date"
}

function Execute-TradingScript {
    param([string]$ScriptName)
    
    if (-not $ScriptName) {
        Write-Error "Script name is required"
        return
    }
    
    $remoteCommand = "cd /opt/genx-fx && ./$ScriptName"
    Write-Host "Executing trading script: $ScriptName" -ForegroundColor Yellow
    
    Connect-ToVPS -VpsHost $vpsHost -User $vpsUser -KeyPath $vpsKeyPath -RemoteCommand $remoteCommand
}

# Main execution logic
if ($Interactive) {
    Write-Host "Opening interactive SSH session..." -ForegroundColor Green
    Connect-ToVPS -VpsHost $vpsHost -User $vpsUser -KeyPath $vpsKeyPath -Interactive $true
}
elseif ($Command) {
    Connect-ToVPS -VpsHost $vpsHost -User $vpsUser -KeyPath $vpsKeyPath -RemoteCommand $Command
}
else {
    Write-Host "VPS Connection Script for Trading System" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage Examples:"
    Write-Host "  Test connection:    .\connect-vps.ps1 -Command 'echo test'"
    Write-Host "  Execute script:     .\connect-vps.ps1 -Command 'cd /opt/genx-fx && ./execute-now-96591326.sh'"
    Write-Host "  Interactive shell:  .\connect-vps.ps1 -Interactive"
    Write-Host ""
    
    # Test connection by default
    Test-VPSConnection
}
