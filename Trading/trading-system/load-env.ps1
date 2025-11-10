# Trading System Environment Loader
# This script securely loads environment variables from .env file

param(
    [string]$EnvFile = "$PSScriptRoot\.env"
)

function Load-TradingEnvironment {
    param([string]$EnvFilePath)
    
    if (-not (Test-Path $EnvFilePath)) {
        Write-Error "Environment file not found: $EnvFilePath"
        Write-Host "Please copy .env.template to .env and configure your credentials"
        return $false
    }
    
    Write-Host "Loading trading environment from: $EnvFilePath" -ForegroundColor Green
    
    # Read and set environment variables
    Get-Content $EnvFilePath | Where-Object { $_ -notmatch '^#' -and $_ -notmatch '^\s*$' } | ForEach-Object {
        $name, $value = $_ -split '=', 2
        if ($name -and $value) {
            [Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim(), 'Process')
            Write-Host "✓ Loaded: $($name.Trim())" -ForegroundColor Cyan
        }
    }
    
    return $true
}

function Test-TradingEnvironment {
    $requiredVars = @('AWS_REGION', 'AWS_INSTANCE_ID', 'AMP_API_KEY', 'GEMINI_API_KEY')
    $missing = @()
    
    foreach ($var in $requiredVars) {
        if (-not [Environment]::GetEnvironmentVariable($var, 'Process')) {
            $missing += $var
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-Warning "Missing required environment variables: $($missing -join ', ')"
        return $false
    }
    
    Write-Host "✓ All required environment variables are set" -ForegroundColor Green
    return $true
}

# Load environment if this script is run directly
if ($MyInvocation.InvocationName -ne '.') {
    if (Load-TradingEnvironment -EnvFilePath $EnvFile) {
        Test-TradingEnvironment
    }
}
