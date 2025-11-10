# GenX Trading System Controller
# Main control script for secure trading operations

param(
    [string]$Action = "status",
    [switch]$Force = $false,
    [switch]$TestMode = $false
)

# Load environment configuration
. "$PSScriptRoot\load-env.ps1"

if (-not (Test-TradingEnvironment)) {
    Write-Error "Environment not properly configured. Please check your .env file."
    exit 1
}

# Get configuration from environment
$awsRegion = [Environment]::GetEnvironmentVariable('AWS_REGION', 'Process')
$instanceId = [Environment]::GetEnvironmentVariable('AWS_INSTANCE_ID', 'Process')
$tradingScript = [Environment]::GetEnvironmentVariable('TRADING_SCRIPT_PATH', 'Process')
$testModeStr = [Environment]::GetEnvironmentVariable('TEST_MODE', 'Process')
$testMode = ($testModeStr -eq 'true')

function Write-TradingLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry
    # Also log to file
    $logEntry | Out-File -FilePath "$PSScriptRoot\trading.log" -Append
}

function Test-AWSConnection {
    Write-TradingLog "Testing AWS EC2 connection to instance $instanceId"
    
    $testResult = & "$PSScriptRoot\connect-aws.ps1" -Command "echo 'AWS_EC2_TEST_OK' && date && whoami"
    
    if ($LASTEXITCODE -eq 0) {
        Write-TradingLog "✓ AWS EC2 connection successful" "SUCCESS"
        return $true
    }
    else {
        Write-TradingLog "✗ AWS EC2 connection failed" "ERROR"
        return $false
    }
}

function Get-TradingStatus {
    Write-TradingLog "Checking trading system status on EC2"
    
    # Check if trading script exists on EC2
    $scriptCheck = & "$PSScriptRoot\connect-aws.ps1" -Command "ls -la /opt/genx-fx/ | grep execute"
    
    if ($LASTEXITCODE -eq 0) {
        Write-TradingLog "✓ Trading scripts found on EC2"
        Write-Host $scriptCheck
        return $true
    }
    else {
        Write-TradingLog "✗ Trading scripts not found" "WARNING"
        return $false
    }
}

function Start-TradingSystem {
    param([bool]$TestMode = $true)
    
    if ($TestMode -and -not $Force) {
        Write-TradingLog "🔒 SAFETY MODE: Test mode enabled. Use -Force to override" "WARNING"
    }
    
    Write-TradingLog "🚀 Starting GenX trading system..."
    
    # Pre-flight checks
    Write-TradingLog "Running pre-flight safety checks"
    
    if (-not (Test-AWSConnection)) {
        Write-TradingLog "❌ Pre-flight check failed: AWS EC2 connection" "ERROR"
        return $false
    }
    
    if (-not (Get-TradingStatus)) {
        Write-TradingLog "⚠️ Pre-flight warning: Trading scripts status unclear" "WARNING"
    }
    
    # Execute the trading script
    Write-TradingLog "Executing trading script: $tradingScript"
    
    $result = & "$PSScriptRoot\connect-aws.ps1" -Command "cd /opt/genx-fx && chmod +x execute-now-96591326.sh && ./execute-now-96591326.sh"
    
    if ($LASTEXITCODE -eq 0) {
        Write-TradingLog "✅ Trading system started successfully" "SUCCESS"
        Write-TradingLog "📊 Result: $result"
        
        # Start monitoring
        Start-TradingMonitor
        return $true
    }
    else {
        Write-TradingLog "❌ Trading system failed to start" "ERROR"
        return $false
    }
}

function Start-TradingMonitor {
    Write-TradingLog "🔍 Starting trading system monitoring"
    
    # Check system health every 5 minutes for the next hour
    for ($i = 1; $i -le 12; $i++) {
        Write-TradingLog "Monitor check #$i/12"
        
        # Check EC2 system health
        $healthCheck = & "$PSScriptRoot\connect-aws.ps1" -Command "ps aux | grep -E '(python|node|genx)' | grep -v grep"
        
        if ($healthCheck) {
            Write-TradingLog "✓ Trading processes detected: $healthCheck"
        }
        else {
            Write-TradingLog "⚠️ No trading processes detected" "WARNING"
        }
        
        if ($i -lt 12) {
            Write-TradingLog "Waiting 5 minutes for next check..."
            Start-Sleep -Seconds 300  # 5 minutes
        }
    }
    
    Write-TradingLog "🏁 Monitoring session completed"
}

function Stop-TradingSystem {
    Write-TradingLog "🛑 Stopping trading system"
    
    $result = & "$PSScriptRoot\connect-aws.ps1" -Command "pkill -f 'genx\|trading\|execute-now' || echo 'No processes to stop'"
    
    Write-TradingLog "Stop command result: $result"
}

function Show-TradingMenu {
    Clear-Host
    Write-Host "🚀 GenX Trading System Controller" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "AWS Region: $awsRegion" -ForegroundColor Cyan
    Write-Host "Instance ID: $instanceId" -ForegroundColor Cyan
    Write-Host "Test Mode: $testMode" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Available Actions:"
    Write-Host "  1. status    - Check system status"
    Write-Host "  2. start     - Start trading system (safe mode)"
    Write-Host "  3. force     - Start trading system (force mode)"
    Write-Host "  4. stop      - Stop trading system"
    Write-Host "  5. monitor   - Monitor system only"
    Write-Host "  6. logs      - View recent logs"
    Write-Host "  7. exit      - Exit controller"
    Write-Host ""
}

function Show-Logs {
    if (Test-Path "$PSScriptRoot\trading.log") {
        Write-Host "📋 Recent Trading Logs:" -ForegroundColor Yellow
        Get-Content "$PSScriptRoot\trading.log" -Tail 20
    }
    else {
        Write-Host "No logs found" -ForegroundColor Gray
    }
}

# Main execution logic
switch ($Action.ToLower()) {
    "status" {
        Write-TradingLog "Checking system status"
        Test-AWSConnection
        Get-TradingStatus
    }
    "start" {
        Start-TradingSystem -TestMode (!$Force)
    }
    "force" {
        Start-TradingSystem -TestMode $false
    }
    "stop" {
        Stop-TradingSystem
    }
    "monitor" {
        Start-TradingMonitor
    }
    "logs" {
        Show-Logs
    }
    "menu" {
        do {
            Show-TradingMenu
            $choice = Read-Host "Enter your choice (1-7)"
            
            switch ($choice) {
                "1" { & $PSCommandPath -Action "status" }
                "2" { & $PSCommandPath -Action "start" }
                "3" { & $PSCommandPath -Action "force" }
                "4" { & $PSCommandPath -Action "stop" }
                "5" { & $PSCommandPath -Action "monitor" }
                "6" { & $PSCommandPath -Action "logs" }
                "7" { break }
                default { Write-Host "Invalid choice. Please try again." -ForegroundColor Red }
            }
            
            if ($choice -ne "7") {
                Write-Host "`nPress Enter to continue..." -ForegroundColor Gray
                Read-Host
            }
        } while ($choice -ne "7")
    }
    default {
        Show-TradingMenu
        Write-Host "Usage: .\trading-controller.ps1 -Action [status|start|force|stop|monitor|logs|menu]"
    }
}
