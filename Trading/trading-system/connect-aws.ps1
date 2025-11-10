		
# AWS EC2 Connection for GenX Trading System
# This script connects to your AWS EC2 instance and executes trading commands

param(
    [string]$Command = "",
    [switch]$Interactive = $false,
    [switch]$UseSSM = $false
)

# Load environment variables
. "$PSScriptRoot\load-env.ps1"

if (-not (Test-TradingEnvironment)) {
    Write-Error "Environment not properly configured. Please check your .env file."
    exit 1
}

# Get AWS configuration from environment
$awsRegion = [Environment]::GetEnvironmentVariable('AWS_REGION', 'Process')
$instanceId = [Environment]::GetEnvironmentVariable('AWS_INSTANCE_ID', 'Process')
$keyName = [Environment]::GetEnvironmentVariable('AWS_KEY_NAME', 'Process')
$privateKeyPath = [Environment]::GetEnvironmentVariable('AWS_PRIVATE_KEY_PATH', 'Process')
$ec2User = [Environment]::GetEnvironmentVariable('EC2_USER', 'Process')
$ec2Host = [Environment]::GetEnvironmentVariable('EC2_HOST', 'Process')

function Test-AWSCli {
    try {
        $result = aws --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ AWS CLI found: $result" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Warning "AWS CLI not found. Please install AWS CLI: https://aws.amazon.com/cli/"
        return $false
    }
    return $false
}

function Test-EC2Instance {
    Write-Host "Checking EC2 instance status..." -ForegroundColor Yellow
    
    try {
        $instanceStatus = aws ec2 describe-instances --instance-ids $instanceId --region $awsRegion --query 'Reservations[0].Instances[0].State.Name' --output text
        
        if ($instanceStatus -eq "running") {
            Write-Host "✓ EC2 instance $instanceId is running" -ForegroundColor Green
            
            # Get public IP
            $publicIp = aws ec2 describe-instances --instance-ids $instanceId --region $awsRegion --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
            if ($publicIp -and $publicIp -ne "None") {
                Write-Host "✓ Public IP: $publicIp" -ForegroundColor Cyan
                return $publicIp
            }
        } elseif ($instanceStatus -eq "stopped") {
            Write-Host "⚠️ EC2 instance is stopped. Starting instance..." -ForegroundColor Yellow
            Start-EC2Instance
            return $false
        } else {
            Write-Host "✗ EC2 instance status: $instanceStatus" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Error "Failed to check EC2 instance: $($_.Exception.Message)"
        return $false
    }
}

function Start-EC2Instance {
    Write-Host "Starting EC2 instance $instanceId..." -ForegroundColor Yellow
    
    try {
        aws ec2 start-instances --instance-ids $instanceId --region $awsRegion
        
        Write-Host "Waiting for instance to be running..." -ForegroundColor Yellow
        aws ec2 wait instance-running --instance-ids $instanceId --region $awsRegion
        
        Write-Host "✅ EC2 instance started successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to start EC2 instance: $($_.Exception.Message)"
        return $false
    }
}

function Connect-ToEC2 {
    param(
        [string]$Host,
        [string]$User,
        [string]$KeyPath,
        [string]$RemoteCommand = "",
        [bool]$Interactive = $false
    )
    
    Write-Host "Connecting to EC2: $User@$Host" -ForegroundColor Yellow
    
    # Expand the key path
    $expandedKeyPath = [System.Environment]::ExpandEnvironmentVariables($KeyPath)
    if ($expandedKeyPath.StartsWith("~")) {
        $expandedKeyPath = $expandedKeyPath.Replace("~", $env:USERPROFILE)
    }
    
    # Build SSH command
    $sshArgs = @(
        "-i", $expandedKeyPath,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null"
    )
    
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
        Write-Error "Failed to connect to EC2: $($_.Exception.Message)"
    }
}

function Connect-WithSSM {
    param([string]$RemoteCommand = "")
    
    Write-Host "Connecting via AWS Systems Manager (SSM)..." -ForegroundColor Yellow
    
    if ($RemoteCommand) {
        try {
            $result = aws ssm send-command --instance-ids $instanceId --document-name "AWS-RunShellScript" --parameters "commands=$RemoteCommand" --region $awsRegion --output text --query 'Command.CommandId'
            
            if ($result) {
                Write-Host "✓ SSM command sent. Command ID: $result" -ForegroundColor Green
                
                # Wait a moment and get output
                Start-Sleep -Seconds 3
                $output = aws ssm get-command-invocation --command-id $result --instance-id $instanceId --region $awsRegion --query 'StandardOutputContent' --output text
                
                if ($output) {
                    Write-Host "Command Output:" -ForegroundColor Cyan
                    Write-Host $output
                }
            }
        }
        catch {
            Write-Error "SSM command failed: $($_.Exception.Message)"
        }
    } else {
        # Start SSM session
        aws ssm start-session --target $instanceId --region $awsRegion
    }
}

function Show-EC2Info {
    Write-Host "`n🖥️  EC2 Instance Information" -ForegroundColor Green
    Write-Host "=============================" -ForegroundColor Green
    Write-Host "Region: $awsRegion" -ForegroundColor Cyan
    Write-Host "Instance ID: $instanceId" -ForegroundColor Cyan
    Write-Host "Key Name: $keyName" -ForegroundColor Cyan
    Write-Host "User: $ec2User" -ForegroundColor Cyan
    Write-Host "Host: $ec2Host" -ForegroundColor Cyan
    Write-Host ""
}

# Main execution logic
if (-not (Test-AWSCli)) {
    Write-Error "AWS CLI is required. Please install and configure it."
    exit 1
}

Show-EC2Info

# Check instance status
$publicIp = Test-EC2Instance

if (-not $publicIp) {
    Write-Error "EC2 instance is not available or failed to start."
    exit 1
}

# Update host with current public IP if needed
if ($publicIp -ne "None") {
    $ec2Host = $publicIp
}

# Execute based on parameters
if ($UseSSM) {
    Connect-WithSSM -RemoteCommand $Command
} elseif ($Interactive) {
    Write-Host "Opening interactive SSH session..." -ForegroundColor Green
    Connect-ToEC2 -Host $ec2Host -User $ec2User -KeyPath $privateKeyPath -Interactive $true
} elseif ($Command) {
    Connect-ToEC2 -Host $ec2Host -User $ec2User -KeyPath $privateKeyPath -RemoteCommand $Command
} else {
    Write-Host "AWS EC2 Connection Script for Trading System" -ForegroundColor Green
    Write-Host "===========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage Examples:"
    Write-Host "  Test connection:    .\connect-aws.ps1 -Command 'echo test && date'"
    Write-Host "  Execute script:     .\connect-aws.ps1 -Command 'cd /opt/genx-fx && ./execute-now-96591326.sh'"
    Write-Host "  Interactive shell:  .\connect-aws.ps1 -Interactive"
    Write-Host "  Use SSM:           .\connect-aws.ps1 -UseSSM -Command 'whoami'"
    Write-Host ""
    
    # Test connection by default
    Write-Host "Testing connection..."
    Connect-ToEC2 -Host $ec2Host -User $ec2User -KeyPath $privateKeyPath -RemoteCommand "echo 'AWS EC2 connection successful' && date && whoami"
}
