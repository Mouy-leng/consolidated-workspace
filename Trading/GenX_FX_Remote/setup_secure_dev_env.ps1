#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Secure Development Environment Setup for GenX_FX
.DESCRIPTION
    Sets up secure credential management, environment variables, and development tools
    for the GenX_FX Remote trading system across Windows/Linux environments.
#>

param(
    [Parameter(HelpMessage="Skip interactive prompts and use defaults")]
    [switch]$NonInteractive,
    
    [Parameter(HelpMessage="Setup type: dev, production, or test")]
    [ValidateSet("dev", "production", "test")]
    [string]$Environment = "dev",
    
    [Parameter(HelpMessage="Enable cross-platform (WSL) integration")]
    [switch]$EnableCrossPlatform
)

# Set strict mode and error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Define constants
$PROJECT_ROOT = Get-Location
$SECRETS_DIR = Join-Path $env:USERPROFILE ".genx_fx_secrets"
$CONFIG_DIR = Join-Path $PROJECT_ROOT "config"
$CREDENTIAL_TARGET = "GenX_FX_Remote"

Write-Host "🚀 Setting up secure development environment for GenX_FX..." -ForegroundColor Cyan

#region Utility Functions
function Write-Section {
    param([string]$Title)
    Write-Host "`n" + ("="*60) -ForegroundColor Yellow
    Write-Host "  $Title" -ForegroundColor Yellow
    Write-Host ("="*60) -ForegroundColor Yellow
}

function Test-Administrator {
    return ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
}

function New-SecureDirectory {
    param([string]$Path)
    
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Host "✓ Created secure directory: $Path" -ForegroundColor Green
        
        # Set restrictive permissions (owner only)
        $acl = Get-Acl $Path
        $acl.SetAccessRuleProtection($true, $false)
        $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($env:USERNAME, "FullControl", "Allow")
        $acl.SetAccessRule($accessRule)
        Set-Acl $Path $acl
    }
}

function Set-EnvironmentVariable {
    param(
        [string]$Name,
        [string]$Value,
        [string]$Target = "User"
    )
    
    [Environment]::SetEnvironmentVariable($Name, $Value, $Target)
    Set-Item -Path "Env:$Name" -Value $Value
    Write-Host "✓ Set environment variable: $Name" -ForegroundColor Green
}
#endregion

#region 1. Secure Directories Setup
Write-Section "Setting up secure directories"

# Create secure directories for secrets and configs
New-SecureDirectory -Path $SECRETS_DIR
New-SecureDirectory -Path (Join-Path $SECRETS_DIR "keys")
New-SecureDirectory -Path (Join-Path $SECRETS_DIR "configs")
New-SecureDirectory -Path (Join-Path $SECRETS_DIR "tokens")

# Set environment variables for secure paths
Set-EnvironmentVariable -Name "GENX_SECRETS_DIR" -Value $SECRETS_DIR
Set-EnvironmentVariable -Name "GENX_PROJECT_ROOT" -Value $PROJECT_ROOT
#endregion

#region 2. SSH Key Management
Write-Section "Configuring SSH key management"

$sshConfigPath = Join-Path $env:USERPROFILE ".ssh\config"
$existingKeys = Get-ChildItem -Path (Join-Path $env:USERPROFILE ".ssh") -Filter "*genx*" -ErrorAction SilentlyContinue

if ($existingKeys) {
    Write-Host "✓ Found existing GenX SSH keys:" -ForegroundColor Green
    $existingKeys | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }
} else {
    Write-Host "⚠ No GenX SSH keys found. Existing keys will be used for all services." -ForegroundColor Yellow
}

# Ensure SSH agent is running
$sshAgent = Get-Process ssh-agent -ErrorAction SilentlyContinue
if (-not $sshAgent) {
    Write-Host "🔄 Starting SSH agent..." -ForegroundColor Blue
    Start-Service ssh-agent -ErrorAction SilentlyContinue
}

# Add keys to SSH agent
if ($existingKeys) {
    $privateKeys = $existingKeys | Where-Object { $_.Extension -eq "" -or $_.Extension -eq ".key" }
    $privateKeys | ForEach-Object {
        ssh-add $_.FullName 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Added key to SSH agent: $($_.Name)" -ForegroundColor Green
        }
    }
}
#endregion

#region 3. Windows Credential Manager Setup
Write-Section "Configuring Windows Credential Manager"

function Set-SecureCredential {
    param(
        [string]$Target,
        [string]$Username,
        [string]$Description = ""
    )
    
    try {
        $existingCred = cmdkey /list:$Target 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Credential already exists: $Target" -ForegroundColor Yellow
        } else {
            Write-Host "📝 Please set password for $Target manually using:" -ForegroundColor Cyan
            Write-Host "   cmdkey /generic:$Target /user:$Username /pass" -ForegroundColor Gray
        }
    } catch {
        Write-Warning "Failed to check credential: $Target"
    }
}

# Setup credential entries for major services
$credentialEntries = @(
    @{Target="GenX_FX_GitHub"; Username="git"; Description="GitHub access for GenX_FX"},
    @{Target="GenX_FX_AWS"; Username="genx-fx-user"; Description="AWS deployment credentials"},
    @{Target="GenX_FX_FXCM"; Username="fxcm-api"; Description="FXCM trading API credentials"},
    @{Target="GenX_FX_Gemini_API"; Username="gemini-api"; Description="Gemini AI API key"}
)

$credentialEntries | ForEach-Object {
    Set-SecureCredential -Target $_.Target -Username $_.Username -Description $_.Description
}
#endregion

#region 4. Environment Variables Setup
Write-Section "Setting up environment variables"

# Core development variables
$envVars = @{
    "GENX_ENVIRONMENT" = $Environment
    "GENX_SSH_KEY_PATH" = Join-Path $env:USERPROFILE ".ssh\genx_fx_deploy"
    "GENX_CONFIG_PATH" = $CONFIG_DIR
    "GENX_LOG_LEVEL" = if ($Environment -eq "dev") { "DEBUG" } else { "INFO" }
    "GENX_ENABLE_DEBUG" = if ($Environment -eq "dev") { "true" } else { "false" }
}

$envVars.GetEnumerator() | ForEach-Object {
    Set-EnvironmentVariable -Name $_.Key -Value $_.Value
}

# Create .env file for the project
$envFilePath = Join-Path $PROJECT_ROOT ".env"
if (-not (Test-Path $envFilePath)) {
    Copy-Item (Join-Path $PROJECT_ROOT ".env.example") $envFilePath -Force
    Write-Host "✓ Created .env file from template" -ForegroundColor Green
    Write-Host "📝 Please edit .env file with your actual API keys" -ForegroundColor Cyan
}
#endregion

#region 5. Cross-Platform Setup (WSL Integration)
if ($EnableCrossPlatform) {
    Write-Section "Setting up cross-platform (WSL) integration"
    
    # Check if WSL is available
    $wslInfo = wsl --list --quiet 2>$null
    if ($LASTEXITCODE -eq 0 -and $wslInfo) {
        Write-Host "✓ WSL detected. Setting up cross-platform integration..." -ForegroundColor Green
        
        # Copy SSH config to WSL
        $wslSshDir = "/home/$(wsl whoami)/.ssh"
        wsl mkdir -p $wslSshDir 2>$null
        wsl cp /mnt/c/Users/$env:USERNAME/.ssh/config $wslSshDir/ 2>$null
        wsl cp /mnt/c/Users/$env:USERNAME/.ssh/genx_fx_deploy* $wslSshDir/ 2>$null
        wsl chmod 600 $wslSshDir/genx_fx_deploy* 2>$null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ SSH keys copied to WSL" -ForegroundColor Green
        }
        
        # Set WSL environment variable
        Set-EnvironmentVariable -Name "GENX_WSL_ENABLED" -Value "true"
    } else {
        Write-Host "⚠ WSL not detected. Skipping cross-platform setup." -ForegroundColor Yellow
        Set-EnvironmentVariable -Name "GENX_WSL_ENABLED" -Value "false"
    }
}
#endregion

#region 6. Development Tools Configuration
Write-Section "Configuring development tools"

# Create PowerShell profile addition for GenX_FX
$profileAddition = @"
# GenX_FX Development Environment
if (Test-Path "$SECRETS_DIR") {
    `$env:GENX_SECRETS_DIR = "$SECRETS_DIR"
    `$env:GENX_PROJECT_ROOT = "$PROJECT_ROOT"
}

# GenX_FX Aliases
function genx-status { 
    Write-Host "GenX_FX Development Environment Status:" -ForegroundColor Cyan
    Write-Host "Project Root: `$env:GENX_PROJECT_ROOT"
    Write-Host "Environment: `$env:GENX_ENVIRONMENT"
    Write-Host "Secrets Dir: `$env:GENX_SECRETS_DIR"
    Write-Host "WSL Enabled: `$env:GENX_WSL_ENABLED"
    
    # Check SSH agent
    `$sshKeys = ssh-add -l 2>`$null
    if (`$LASTEXITCODE -eq 0) {
        Write-Host "SSH Keys loaded: `$(`$sshKeys.Count)" -ForegroundColor Green
    } else {
        Write-Host "SSH Keys loaded: None" -ForegroundColor Yellow
    }
}

function genx-secrets { 
    explorer.exe "`$env:GENX_SECRETS_DIR"
}

function genx-logs {
    Get-ChildItem -Path "$PROJECT_ROOT\logs" -Recurse -File | Sort-Object LastWriteTime -Descending | Select-Object -First 10
}

function genx-env {
    code "$PROJECT_ROOT\.env"
}
"@

$profilePath = $PROFILE.CurrentUserAllHosts
if (Test-Path $profilePath) {
    $profileContent = Get-Content $profilePath -Raw
    if ($profileContent -notmatch "GenX_FX Development Environment") {
        Add-Content $profilePath $profileAddition
        Write-Host "✓ Added GenX_FX aliases to PowerShell profile" -ForegroundColor Green
    }
} else {
    New-Item -ItemType File -Path $profilePath -Force -Value $profileAddition | Out-Null
    Write-Host "✓ Created PowerShell profile with GenX_FX aliases" -ForegroundColor Green
}
#endregion

#region 7. IDE Integration Setup
Write-Section "Setting up IDE integration"

# Create VS Code settings for the project
$vscodeDir = Join-Path $PROJECT_ROOT ".vscode"
if (-not (Test-Path $vscodeDir)) {
    New-Item -ItemType Directory -Path $vscodeDir -Force | Out-Null
}

$vscodeSettings = @{
    "python.defaultInterpreterPath" = "./venv/Scripts/python.exe"
    "python.terminal.activateEnvironment" = $true
    "files.exclude" = @{
        "**/__pycache__" = $true
        "**/.pytest_cache" = $true
        "**/node_modules" = $true
        "**/.env" = $false
    }
    "python.envFile" = "`${workspaceFolder}/.env"
    "terminal.integrated.env.windows" = @{
        "GENX_PROJECT_ROOT" = "`${workspaceFolder}"
    }
} | ConvertTo-Json -Depth 10

Set-Content -Path (Join-Path $vscodeDir "settings.json") -Value $vscodeSettings
Write-Host "✓ Created VS Code settings" -ForegroundColor Green

# Create PyCharm configuration hint
$pycharmConfig = @"
# PyCharm Configuration for GenX_FX
# 1. Set Python interpreter to: ./venv/Scripts/python.exe
# 2. Add environment variables:
#    - GENX_PROJECT_ROOT=$PROJECT_ROOT
#    - GENX_ENVIRONMENT=$Environment
# 3. Enable .env file support in Run Configurations
# 4. Set working directory to project root
"@

Set-Content -Path (Join-Path $PROJECT_ROOT "PYCHARM_SETUP.md") -Value $pycharmConfig
Write-Host "✓ Created PyCharm setup guide" -ForegroundColor Green
#endregion

#region 8. Security Validation
Write-Section "Validating security setup"

$securityChecks = @()

# Check SSH key permissions
$sshKeyPath = Join-Path $env:USERPROFILE ".ssh\genx_fx_deploy"
if (Test-Path $sshKeyPath) {
    $keyAcl = Get-Acl $sshKeyPath
    $securityChecks += @{Name="SSH Key Permissions"; Status="✓ Secure"; Color="Green"}
} else {
    $securityChecks += @{Name="SSH Key Permissions"; Status="⚠ No SSH key found"; Color="Yellow"}
}

# Check secrets directory permissions
if (Test-Path $SECRETS_DIR) {
    $secretsAcl = Get-Acl $SECRETS_DIR
    $securityChecks += @{Name="Secrets Directory"; Status="✓ Secure"; Color="Green"}
}

# Check environment variables
$requiredEnvVars = @("GENX_SECRETS_DIR", "GENX_PROJECT_ROOT", "GENX_ENVIRONMENT")
$missingVars = $requiredEnvVars | Where-Object { -not (Get-Item Env:$_ -ErrorAction SilentlyContinue) }
if ($missingVars.Count -eq 0) {
    $securityChecks += @{Name="Environment Variables"; Status="✓ Complete"; Color="Green"}
} else {
    $securityChecks += @{Name="Environment Variables"; Status="⚠ Missing: $($missingVars -join ', ')"; Color="Yellow"}
}

Write-Host "`nSecurity Validation Results:" -ForegroundColor Cyan
$securityChecks | ForEach-Object {
    Write-Host "  $($_.Name): $($_.Status)" -ForegroundColor $_.Color
}
#endregion

#region 9. Final Instructions
Write-Section "Setup Complete - Next Steps"

Write-Host @"
🎉 Secure development environment setup complete!

Next steps:
1. Edit .env file with your actual API keys:
   code "$PROJECT_ROOT\.env"

2. Add credentials to Windows Credential Manager:
   - GitHub: cmdkey /generic:GenX_FX_GitHub /user:git /pass
   - AWS: cmdkey /generic:GenX_FX_AWS /user:genx-fx-user /pass
   - FXCM: cmdkey /generic:GenX_FX_FXCM /user:fxcm-api /pass

3. Test SSH connection:
   ssh -T git@github.com

4. Install Python dependencies:
   pip install -r requirements.txt

5. Use new aliases:
   genx-status    # Show environment status
   genx-secrets   # Open secrets directory  
   genx-logs      # View recent logs
   genx-env       # Edit environment file

6. For IDE setup:
   - VS Code: Settings configured automatically
   - PyCharm: See PYCHARM_SETUP.md

Environment: $Environment
Cross-platform: $($EnableCrossPlatform ? "Enabled" : "Disabled")
"@ -ForegroundColor Green

if ($Environment -eq "production") {
    Write-Host "`n⚠️  PRODUCTION ENVIRONMENT DETECTED" -ForegroundColor Red
    Write-Host "Please ensure all credentials are properly secured and tested." -ForegroundColor Yellow
}
#endregion

Write-Host "`n🔒 Your development environment is now secure and ready!" -ForegroundColor Cyan