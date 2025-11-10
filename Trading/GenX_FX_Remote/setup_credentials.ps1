#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Simplified Credential Management for GenX_FX
.DESCRIPTION
    Sets up secure credential storage and environment variables for GenX_FX development.
#>

param(
    [Parameter(HelpMessage="Environment type")]
    [ValidateSet("dev", "production", "test")]
    [string]$Environment = "dev"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

# Define paths
$PROJECT_ROOT = $PWD.Path
$SECRETS_DIR = Join-Path $env:USERPROFILE ".genx_fx_secrets"

Write-Host "🔐 Setting up GenX_FX credential management..." -ForegroundColor Cyan

#region Create Secure Directories
function New-SecureDirectory {
    param([string]$Path)
    
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Host "✓ Created secure directory: $Path" -ForegroundColor Green
        
        # Set restrictive permissions
        try {
            $acl = Get-Acl $Path
            $acl.SetAccessRuleProtection($true, $false)
            $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($env:USERNAME, "FullControl", "Allow")
            $acl.SetAccessRule($accessRule)
            Set-Acl $Path $acl
            Write-Host "  └─ Permissions secured" -ForegroundColor Gray
        } catch {
            Write-Warning "Could not set permissions on $Path"
        }
    } else {
        Write-Host "✓ Directory exists: $Path" -ForegroundColor Yellow
    }
}

Write-Host "`n📁 Creating secure directories..."
New-SecureDirectory -Path $SECRETS_DIR
New-SecureDirectory -Path (Join-Path $SECRETS_DIR "keys")
New-SecureDirectory -Path (Join-Path $SECRETS_DIR "configs") 
New-SecureDirectory -Path (Join-Path $SECRETS_DIR "tokens")
New-SecureDirectory -Path (Join-Path $SECRETS_DIR "backups")
#endregion

#region Environment Variables
Write-Host "`n🌐 Setting up environment variables..."

$envVars = @{
    "GENX_SECRETS_DIR" = $SECRETS_DIR
    "GENX_PROJECT_ROOT" = $PROJECT_ROOT
    "GENX_ENVIRONMENT" = $Environment
    "GENX_SSH_KEY_PATH" = Join-Path $env:USERPROFILE ".ssh\genx_fx_deploy"
    "GENX_CONFIG_PATH" = Join-Path $PROJECT_ROOT "config"
    "GENX_LOG_LEVEL" = if ($Environment -eq "dev") { "DEBUG" } else { "INFO" }
}

$envVars.GetEnumerator() | ForEach-Object {
    try {
        [Environment]::SetEnvironmentVariable($_.Key, $_.Value, "User")
        Set-Item -Path "Env:$($_.Key)" -Value $_.Value -Force
        Write-Host "✓ Set $($_.Key)" -ForegroundColor Green
    } catch {
        Write-Warning "Failed to set environment variable: $($_.Key)"
    }
}
#endregion

#region .env File Setup
Write-Host "`n📄 Setting up .env file..."

$envFilePath = Join-Path $PROJECT_ROOT ".env"
$envExamplePath = Join-Path $PROJECT_ROOT ".env.example"

if (-not (Test-Path $envFilePath) -and (Test-Path $envExamplePath)) {
    Copy-Item $envExamplePath $envFilePath -Force
    Write-Host "✓ Created .env file from template" -ForegroundColor Green
} elseif (Test-Path $envFilePath) {
    Write-Host "✓ .env file already exists" -ForegroundColor Yellow
} else {
    Write-Host "⚠ No .env.example template found" -ForegroundColor Yellow
}
#endregion

#region Credential Manager Setup
Write-Host "`n🔑 Setting up Windows Credential Manager entries..."

$credentials = @(
    @{Name="GenX_FX_GitHub"; User="git"; Desc="GitHub SSH access"},
    @{Name="GenX_FX_FXCM_API"; User="fxcm-user"; Desc="FXCM trading API"},
    @{Name="GenX_FX_Gemini_API"; User="gemini-api"; Desc="Gemini AI API key"},
    @{Name="GenX_FX_AWS"; User="genx-aws"; Desc="AWS deployment"}
)

Write-Host "To add credentials manually, use these commands:" -ForegroundColor Cyan
$credentials | ForEach-Object {
    Write-Host "  cmdkey /generic:$($_.Name) /user:$($_.User) /pass" -ForegroundColor Gray
    Write-Host "    # $($_.Desc)" -ForegroundColor DarkGray
}
#endregion

#region SSH Key Information
Write-Host "`n🔐 SSH Key Status..."

$sshDir = Join-Path $env:USERPROFILE ".ssh"
$sshConfigPath = Join-Path $sshDir "config"
$genxKeyPath = Join-Path $sshDir "genx_fx_deploy"
$genxKeyPubPath = Join-Path $sshDir "genx_fx_deploy.pub"

if (Test-Path $genxKeyPath) {
    Write-Host "✓ GenX SSH private key found: genx_fx_deploy" -ForegroundColor Green
} else {
    Write-Host "⚠ GenX SSH private key not found" -ForegroundColor Yellow
}

if (Test-Path $genxKeyPubPath) {
    Write-Host "✓ GenX SSH public key found: genx_fx_deploy.pub" -ForegroundColor Green
    $pubKeyContent = Get-Content $genxKeyPubPath -Raw
    Write-Host "  └─ Public key: $($pubKeyContent.Trim())" -ForegroundColor Gray
} else {
    Write-Host "⚠ GenX SSH public key not found" -ForegroundColor Yellow
}

if (Test-Path $sshConfigPath) {
    Write-Host "✓ SSH config file found" -ForegroundColor Green
} else {
    Write-Host "⚠ SSH config file not found" -ForegroundColor Yellow
}
#endregion

#region IDE Configuration
Write-Host "`n🛠️ Setting up IDE configurations..."

# VS Code settings
$vscodeDir = Join-Path $PROJECT_ROOT ".vscode"
if (-not (Test-Path $vscodeDir)) {
    New-Item -ItemType Directory -Path $vscodeDir -Force | Out-Null
}

$vscodeSettings = @{
    "python.defaultInterpreterPath" = "./venv/Scripts/python.exe"
    "python.terminal.activateEnvironment" = $true
    "python.envFile" = "`${workspaceFolder}/.env"
    "files.exclude" = @{
        "**/__pycache__" = $true
        "**/.pytest_cache" = $true
        "**/node_modules" = $true
        "**/.env" = $false
    }
    "terminal.integrated.env.windows" = @{
        "GENX_PROJECT_ROOT" = "`${workspaceFolder}"
        "GENX_ENVIRONMENT" = $Environment
    }
} | ConvertTo-Json -Depth 10

Set-Content -Path (Join-Path $vscodeDir "settings.json") -Value $vscodeSettings
Write-Host "✓ VS Code settings configured" -ForegroundColor Green

# PyCharm setup guide
$pycharmGuide = @"
# PyCharm/IntelliJ Setup for GenX_FX

## Environment Setup
1. **Python Interpreter**: Set to `./venv/Scripts/python.exe`
2. **Working Directory**: Set to project root
3. **Environment Variables** (in Run Configurations):
   - `GENX_PROJECT_ROOT`: $PROJECT_ROOT
   - `GENX_ENVIRONMENT`: $Environment
   - `GENX_SECRETS_DIR`: $SECRETS_DIR

## Plugin Recommendations
- Python
- .env files support
- Docker
- GitToolBox
- Rainbow Brackets

## Run Configuration Template
1. Create new Python configuration
2. Set script path to your main script
3. Add environment variables above
4. Enable "Include parent environment variables"
5. Set .env file path to `.env`

## Database Integration
- Database URL: `postgresql://genx_user:password@localhost:5432/genx_trading`
- Redis URL: `redis://localhost:6379`

## Code Style
- Use Black formatter
- Enable import sorting (isort)
- Set line length to 88 characters
"@

Set-Content -Path (Join-Path $PROJECT_ROOT "JETBRAINS_SETUP.md") -Value $pycharmGuide
Write-Host "✓ JetBrains setup guide created" -ForegroundColor Green
#endregion

#region PowerShell Profile
Write-Host "`n📜 Setting up PowerShell aliases..."

$profileContent = @"
# GenX_FX Development Environment Aliases
if (`$env:GENX_PROJECT_ROOT) {
    function genx-status {
        Write-Host "GenX_FX Development Environment Status:" -ForegroundColor Cyan
        Write-Host "Project Root: `$env:GENX_PROJECT_ROOT"
        Write-Host "Environment: `$env:GENX_ENVIRONMENT" 
        Write-Host "Secrets Dir: `$env:GENX_SECRETS_DIR"
        Write-Host "SSH Key: `$env:GENX_SSH_KEY_PATH"
        
        if (Test-Path "`$env:GENX_PROJECT_ROOT\.env") {
            Write-Host ".env file: ✓ Found" -ForegroundColor Green
        } else {
            Write-Host ".env file: ⚠ Missing" -ForegroundColor Yellow
        }
    }
    
    function genx-secrets { 
        if (Test-Path `$env:GENX_SECRETS_DIR) {
            explorer.exe `$env:GENX_SECRETS_DIR
        } else {
            Write-Host "Secrets directory not found" -ForegroundColor Red
        }
    }
    
    function genx-logs {
        `$logDir = Join-Path `$env:GENX_PROJECT_ROOT "logs"
        if (Test-Path `$logDir) {
            Get-ChildItem -Path `$logDir -Recurse -File | 
                Sort-Object LastWriteTime -Descending | 
                Select-Object -First 10 | 
                Format-Table Name, LastWriteTime, Length -AutoSize
        } else {
            Write-Host "No logs directory found" -ForegroundColor Yellow
        }
    }
    
    function genx-env {
        `$envPath = Join-Path `$env:GENX_PROJECT_ROOT ".env"
        if (Test-Path `$envPath) {
            if (Get-Command code -ErrorAction SilentlyContinue) {
                code `$envPath
            } else {
                notepad `$envPath
            }
        } else {
            Write-Host ".env file not found" -ForegroundColor Red
        }
    }
    
    function genx-backup-secrets {
        `$backupDir = Join-Path `$env:GENX_SECRETS_DIR "backups"
        `$backupFile = Join-Path `$backupDir "secrets_backup_`$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
        
        if (Test-Path `$env:GENX_SECRETS_DIR) {
            Compress-Archive -Path (Join-Path `$env:GENX_SECRETS_DIR "*") -DestinationPath `$backupFile -Force
            Write-Host "Secrets backed up to: `$backupFile" -ForegroundColor Green
        }
    }
    
    Write-Host "GenX_FX aliases loaded. Use 'genx-status' to check setup." -ForegroundColor Green
}
"@

$profilePath = $PROFILE.CurrentUserAllHosts
try {
    if (Test-Path $profilePath) {
        $existingProfile = Get-Content $profilePath -Raw -ErrorAction SilentlyContinue
        if ($existingProfile -and $existingProfile -notmatch "GenX_FX Development Environment") {
            Add-Content $profilePath "`n$profileContent" -Encoding UTF8
            Write-Host "✓ Added GenX_FX aliases to existing profile" -ForegroundColor Green
        } else {
            Write-Host "✓ GenX_FX aliases already in profile" -ForegroundColor Yellow
        }
    } else {
        $profileDir = Split-Path $profilePath -Parent
        if (-not (Test-Path $profileDir)) {
            New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
        }
        Set-Content $profilePath $profileContent -Encoding UTF8
        Write-Host "✓ Created PowerShell profile with GenX_FX aliases" -ForegroundColor Green
    }
} catch {
    Write-Warning "Could not modify PowerShell profile: $_"
    Write-Host "Manual profile setup required at: $profilePath" -ForegroundColor Yellow
}
#endregion

#region Summary
Write-Host "`n" + ("="*60) -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE" -ForegroundColor Cyan  
Write-Host ("="*60) -ForegroundColor Cyan

Write-Host @"

🎉 GenX_FX credential management setup complete!

📍 Key Locations:
  • Project Root: $PROJECT_ROOT
  • Secrets Dir:  $SECRETS_DIR  
  • SSH Key:      $env:GENX_SSH_KEY_PATH

📋 Next Steps:
  1. Edit .env file with your API keys:
     genx-env

  2. Add credentials to Windows Credential Manager:
     cmdkey /generic:GenX_FX_FXCM_API /user:fxcm-user /pass:YOUR_API_KEY
     cmdkey /generic:GenX_FX_Gemini_API /user:gemini-api /pass:YOUR_API_KEY

  3. Test SSH access:
     ssh -T git@github.com

  4. Install Python dependencies:
     pip install -r requirements.txt

  5. Use new aliases:
     genx-status           # Show environment status
     genx-secrets          # Open secrets directory
     genx-logs             # View recent logs
     genx-env              # Edit .env file
     genx-backup-secrets   # Backup your secrets

🔧 IDE Setup:
  • VS Code: Settings configured automatically
  • PyCharm/IntelliJ: See JETBRAINS_SETUP.md

🔐 Security Notes:
  • Secrets directory has restricted permissions
  • Environment variables set for current user
  • SSH keys should be protected (600 permissions)

Environment: $Environment
"@ -ForegroundColor Green

Write-Host "🚀 Your secure development environment is ready!" -ForegroundColor Cyan
#endregion