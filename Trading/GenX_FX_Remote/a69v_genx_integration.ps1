#!/usr/bin/env pwsh
<#
.SYNOPSIS
    A6-9V GenX Integration Script
.DESCRIPTION
    Integrates A6-9V organization identity into your existing GenX_FX development environment.
    Updates credentials, SSH configurations, and development tools to use A6-9V branding.
#>

param(
    [Parameter(HelpMessage="Skip interactive confirmations")]
    [switch]$Force,
    
    [Parameter(HelpMessage="Custom A6-9V email")]
    [string]$A69VEmail = "admin@a6-9v.dev"
)

# A6-9V Configuration
$A69V_CONFIG = @{
    OrgName = "A6-9V"
    Email = $A69VEmail
    Description = "A6-9V Development Organization"
    Username = "A6-9V"
    GitHubUsername = "A6-9V"  # This should match your actual GitHub username
}

$PROJECT_ROOT = $PWD.Path
$GENX_ENV_FILE = Join-Path $PROJECT_ROOT ".env"
$SECRETS_DIR = $env:GENX_SECRETS_DIR ?? (Join-Path $env:USERPROFILE ".genx_fx_secrets")

#region Utility Functions
function Write-Header {
    param([string]$Title)
    Write-Host "`n" + ("="*60) -ForegroundColor Magenta
    Write-Host "  A6-9V ❤ GenX_FX: $Title" -ForegroundColor Magenta
    Write-Host ("="*60) -ForegroundColor Magenta
}

function Write-Success { param([string]$Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Warning { param([string]$Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message) Write-Host "✗ $Message" -ForegroundColor Red }
function Write-Info { param([string]$Message) Write-Host "ℹ $Message" -ForegroundColor Blue }

function Confirm-Action {
    param([string]$Message, [string]$Default = "Y")
    
    if ($Force) { return $true }
    
    $choice = Read-Host "$Message [$Default/N]"
    return ($choice -eq "" -and $Default -eq "Y") -or ($choice -match "^[Yy]")
}
#endregion

#region SSH Configuration Update
function Update-SSHConfiguration {
    Write-Header "Updating SSH Configuration for A6-9V"
    
    $sshConfigPath = Join-Path $env:USERPROFILE ".ssh\config"
    
    if (-not (Test-Path $sshConfigPath)) {
        Write-Warning "SSH config file not found at: $sshConfigPath"
        return
    }
    
    try {
        $sshConfig = Get-Content $sshConfigPath -Raw
        
        # Create A6-9V specific SSH configuration
        $a69vSshConfig = @"
        
# A6-9V Organization SSH Configuration
Host github-a69v
    HostName github.com
    User git
    IdentityFile ~/.ssh/genx_fx_deploy
    IdentitiesOnly yes

# A6-9V GitLab Configuration
Host gitlab-a69v
    HostName gitlab.com
    User git
    IdentityFile ~/.ssh/genx_fx_deploy
    IdentitiesOnly yes

# A6-9V Gitpod Configuration
Host *.gitpod.io
    IdentityFile ~/.ssh/genx_fx_deploy
    IdentitiesOnly yes
    User gitpod
"@

        # Check if A6-9V config already exists
        if ($sshConfig -notmatch "A6-9V Organization SSH Configuration") {
            Add-Content -Path $sshConfigPath -Value $a69vSshConfig
            Write-Success "Added A6-9V SSH configuration"
        } else {
            Write-Info "A6-9V SSH configuration already exists"
        }
        
    } catch {
        Write-Error "Failed to update SSH configuration: $($_.Exception.Message)"
    }
}
#endregion

#region Environment Variables Update
function Update-EnvironmentVariables {
    Write-Header "Updating Environment Variables for A6-9V"
    
    # Update user environment variables
    $a69vEnvVars = @{
        "A69V_ORGANIZATION" = $A69V_CONFIG.OrgName
        "A69V_EMAIL" = $A69V_CONFIG.Email
        "A69V_GITHUB_USERNAME" = $A69V_CONFIG.GitHubUsername
        "GENX_A69V_INTEGRATION" = "enabled"
    }
    
    foreach ($envVar in $a69vEnvVars.GetEnumerator()) {
        try {
            [Environment]::SetEnvironmentVariable($envVar.Key, $envVar.Value, "User")
            Set-Item -Path "Env:$($envVar.Key)" -Value $envVar.Value -Force
            Write-Success "Set environment variable: $($envVar.Key)"
        } catch {
            Write-Warning "Failed to set environment variable: $($envVar.Key)"
        }
    }
    
    # Update .env file for the project
    if (Test-Path $GENX_ENV_FILE) {
        try {
            $envContent = Get-Content $GENX_ENV_FILE -Raw
            
            # Add A6-9V specific variables
            $a69vEnvSection = @"

# A6-9V Organization Configuration
A69V_ORGANIZATION=$($A69V_CONFIG.OrgName)
A69V_EMAIL=$($A69V_CONFIG.Email)
A69V_GITHUB_USERNAME=$($A69V_CONFIG.GitHubUsername)
A69V_INTEGRATION_DATE=$(Get-Date -Format 'yyyy-MM-dd')

# A6-9V API Keys (update with your actual keys)
A69V_API_KEY=your_a69v_api_key_here
A69V_JWT_SECRET=your_jwt_secret_here
A69V_ENCRYPTION_KEY=your_encryption_key_here
"@

            if ($envContent -notmatch "A6-9V Organization Configuration") {
                Add-Content -Path $GENX_ENV_FILE -Value $a69vEnvSection
                Write-Success "Added A6-9V configuration to .env file"
            } else {
                Write-Info "A6-9V configuration already exists in .env file"
            }
            
        } catch {
            Write-Error "Failed to update .env file: $($_.Exception.Message)"
        }
    }
}
#endregion

#region Credential Management Update
function Update-CredentialManagement {
    Write-Header "Updating Credential Management for A6-9V"
    
    # Create A6-9V credential entries
    $a69vCredentials = @{
        "A69V_GITHUB_TOKEN" = "A6-9V GitHub personal access token"
        "A69V_API_KEY" = "A6-9V main API key"
        "A69V_DATABASE_URL" = "A6-9V database connection string"
        "A69V_JWT_SECRET" = "A6-9V JWT signing secret"
    }
    
    Write-Info "Setting up A6-9V credential placeholders..."
    Write-Host "To add actual credentials, use these commands:" -ForegroundColor Cyan
    
    foreach ($cred in $a69vCredentials.GetEnumerator()) {
        Write-Host "  cmdkey /generic:$($cred.Key) /user:A6-9V /pass:YOUR_$($cred.Key)" -ForegroundColor Gray
        Write-Host "    # $($cred.Value)" -ForegroundColor DarkGray
    }
    
    # Create A6-9V secrets directory
    $a69vSecretsDir = Join-Path $SECRETS_DIR "a69v"
    if (-not (Test-Path $a69vSecretsDir)) {
        New-Item -ItemType Directory -Path $a69vSecretsDir -Force | Out-Null
        
        # Set restrictive permissions
        try {
            $acl = Get-Acl $a69vSecretsDir
            $acl.SetAccessRuleProtection($true, $false)
            $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($env:USERNAME, "FullControl", "Allow")
            $acl.SetAccessRule($accessRule)
            Set-Acl $a69vSecretsDir $acl
            Write-Success "Created secure A6-9V secrets directory"
        } catch {
            Write-Warning "Could not set permissions on A6-9V secrets directory"
        }
    }
    
    # Create credential management documentation
    $credDocumentation = @"
# A6-9V Credential Management

## Local Development Credentials

### Windows Credential Manager
Use these commands to store your A6-9V credentials securely:

```powershell
# Core A6-9V credentials
cmdkey /generic:A69V_GITHUB_TOKEN /user:A6-9V /pass:YOUR_GITHUB_TOKEN
cmdkey /generic:A69V_API_KEY /user:A6-9V /pass:YOUR_API_KEY
cmdkey /generic:A69V_DATABASE_URL /user:A6-9V /pass:YOUR_DATABASE_URL
cmdkey /generic:A69V_JWT_SECRET /user:A6-9V /pass:YOUR_JWT_SECRET

# Trading platform credentials
cmdkey /generic:A69V_FXCM_API /user:A6-9V /pass:YOUR_FXCM_API_KEY
cmdkey /generic:A69V_GEMINI_API /user:A6-9V /pass:YOUR_GEMINI_API_KEY
```

### Environment Variables
Update your .env file with A6-9V specific variables:

```env
A69V_ORGANIZATION=A6-9V
A69V_EMAIL=admin@a6-9v.dev
A69V_GITHUB_USERNAME=A6-9V
```

### Retrieve Credentials in Code
```python
import os
import subprocess

def get_a69v_credential(cred_name):
    '''Retrieve A6-9V credential from Windows Credential Manager'''
    try:
        result = subprocess.run(['cmdkey', f'/list:{cred_name}'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            # Extract credential (implement secure extraction logic)
            return "credential_value"
        return None
    except Exception:
        return None

# Usage
github_token = get_a69v_credential('A69V_GITHUB_TOKEN')
api_key = get_a69v_credential('A69V_API_KEY')
```

## Security Best Practices

1. **Never commit credentials to version control**
2. **Use environment-specific credentials**
3. **Rotate credentials regularly**
4. **Use least-privilege access**
5. **Monitor credential usage**

## Credential Rotation Schedule

- GitHub tokens: Every 90 days
- API keys: Every 60 days
- Database passwords: Every 30 days
- JWT secrets: Every 180 days

## Backup & Recovery

- Credentials are backed up securely in the A6-9V secrets directory
- Use `scripts/a69v_secrets.ps1` for credential management
- Maintain offline backup of critical credentials

---
Generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@

    Set-Content -Path (Join-Path $a69vSecretsDir "CREDENTIALS.md") -Value $credDocumentation
    Write-Success "Created A6-9V credentials documentation"
}
#endregion

#region GenX Integration Update
function Update-GenXIntegration {
    Write-Header "Integrating A6-9V with GenX_FX System"
    
    # Update PowerShell profile with A6-9V aliases
    $profilePath = $PROFILE.CurrentUserAllHosts
    $a69vProfileAddition = @"

# A6-9V GenX_FX Integration Aliases
function a69v-status {
    Write-Host "A6-9V GenX_FX Development Status:" -ForegroundColor Magenta
    Write-Host "Organization: `$env:A69V_ORGANIZATION"
    Write-Host "Email: `$env:A69V_EMAIL"  
    Write-Host "GitHub: `$env:A69V_GITHUB_USERNAME"
    
    if (`$env:GENX_PROJECT_ROOT) {
        Set-Location `$env:GENX_PROJECT_ROOT
        & "./genx.ps1" status
    }
}

function a69v-repo {
    param([string]`$Action = "status")
    if (Test-Path "./a69v_repo_manager.ps1") {
        & "./a69v_repo_manager.ps1" `$Action
    } else {
        Write-Host "A6-9V repository manager not found" -ForegroundColor Red
    }
}

function a69v-secrets {
    param([string]`$Action = "list")
    if (Test-Path "./scripts/a69v_secrets.ps1") {
        & "./scripts/a69v_secrets.ps1" `$Action
    } else {
        Write-Host "A6-9V secrets manager not found" -ForegroundColor Red
    }
}

function a69v-genx {
    if (`$env:GENX_PROJECT_ROOT) {
        Set-Location `$env:GENX_PROJECT_ROOT
        & "./genx.ps1" `$args
    } else {
        Write-Host "GenX project root not found" -ForegroundColor Red
    }
}

Write-Host "A6-9V GenX_FX aliases loaded. Use 'a69v-status' to check integration." -ForegroundColor Magenta
"@

    try {
        if (Test-Path $profilePath) {
            $profileContent = Get-Content $profilePath -Raw
            if ($profileContent -and $profileContent -notmatch "A6-9V GenX_FX Integration") {
                Add-Content $profilePath $a69vProfileAddition
                Write-Success "Added A6-9V aliases to PowerShell profile"
            } else {
                Write-Info "A6-9V aliases already in PowerShell profile"
            }
        } else {
            $profileDir = Split-Path $profilePath -Parent
            if (-not (Test-Path $profileDir)) {
                New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
            }
            Set-Content $profilePath $a69vProfileAddition -Encoding UTF8
            Write-Success "Created PowerShell profile with A6-9V aliases"
        }
    } catch {
        Write-Warning "Could not update PowerShell profile: $_"
    }
    
    # Update genx.ps1 to include A6-9V branding
    $genxPath = Join-Path $PROJECT_ROOT "genx.ps1"
    if (Test-Path $genxPath) {
        try {
            $genxContent = Get-Content $genxPath -Raw
            
            # Add A6-9V branding to the header
            $originalHeader = 'Write-Host "🎯 GenX_FX Remote Control Center v\$SCRIPT_VERSION" -ForegroundColor Magenta'
            $a69vHeader = 'Write-Host "🎯 A6-9V GenX_FX Remote Control Center v$SCRIPT_VERSION" -ForegroundColor Magenta
Write-Host "Organization: A6-9V | Email: admin@a6-9v.dev" -ForegroundColor Gray'
            
            if ($genxContent -match [regex]::Escape($originalHeader) -and $genxContent -notmatch "Organization: A6-9V") {
                $updatedContent = $genxContent -replace [regex]::Escape($originalHeader), $a69vHeader
                Set-Content -Path $genxPath -Value $updatedContent
                Write-Success "Updated genx.ps1 with A6-9V branding"
            } else {
                Write-Info "genx.ps1 already has A6-9V branding or couldn't be updated"
            }
            
        } catch {
            Write-Warning "Could not update genx.ps1: $($_.Exception.Message)"
        }
    }
}
#endregion

#region Documentation Update
function Update-Documentation {
    Write-Header "Updating Documentation for A6-9V"
    
    # Create A6-9V integration documentation
    $integrationDoc = @"
# A6-9V GenX_FX Integration Complete

## Overview
Your GenX_FX Remote trading system has been successfully integrated with the **A6-9V** development organization.

## What's Changed

### 🔧 Environment Configuration
- Environment variables updated with A6-9V identity
- SSH configuration enhanced for A6-9V repositories  
- Credential management configured for A6-9V organization
- PowerShell profile updated with A6-9V aliases

### 🎯 New Commands Available

#### A6-9V Specific Commands
```powershell
a69v-status          # Show A6-9V GenX integration status
a69v-repo status     # A6-9V repository management
a69v-secrets list    # A6-9V credential management  
a69v-genx dev        # Run GenX commands with A6-9V context
```

#### Repository Management
```powershell
./a69v_repo_manager.ps1 configure    # Configure Git for A6-9V
./a69v_repo_manager.ps1 security     # Set up repository security
./a69v_repo_manager.ps1 secrets      # Configure secrets management
./a69v_repo_manager.ps1 cleanup      # Clean up repositories
./a69v_repo_manager.ps1 fork <repo>  # Fork repository for A6-9V
```

### 🔐 Credential Management

#### Add A6-9V Credentials
```powershell
# Core credentials
cmdkey /generic:A69V_GITHUB_TOKEN /user:A6-9V /pass:YOUR_TOKEN
cmdkey /generic:A69V_API_KEY /user:A6-9V /pass:YOUR_API_KEY

# Trading credentials
cmdkey /generic:A69V_FXCM_API /user:A6-9V /pass:YOUR_FXCM_KEY
cmdkey /generic:A69V_GEMINI_API /user:A6-9V /pass:YOUR_GEMINI_KEY
```

#### Local Secrets Management
```powershell
./scripts/a69v_secrets.ps1 add API_KEY your_key_value
./scripts/a69v_secrets.ps1 list
./scripts/a69v_secrets.ps1 backup
```

### 🌐 Git Configuration
When Git becomes available, run:
```powershell
./a69v_repo_manager.ps1 configure
```

This will set:
- Username: A6-9V
- Email: admin@a6-9v.dev
- Default branch: main
- Security-focused settings
- A6-9V specific Git aliases

### 📁 Directory Structure
```
GenX_FX_Remote/
├── a69v_repo_manager.ps1     # A6-9V repository management
├── a69v_genx_integration.ps1 # This integration script
├── genx.ps1                  # Updated with A6-9V branding
├── config/                   # A6-9V configuration files
│   ├── SECRETS.md           # Secrets documentation
│   ├── ENVIRONMENTS.md      # Environment setup guide
│   └── CLEANUP_RECOMMENDATIONS.md
├── scripts/                  # A6-9V utility scripts
│   └── a69v_secrets.ps1     # Local secrets management
└── .github/                  # A6-9V security templates
    └── ISSUE_TEMPLATE/
        └── security.md       # Security issue template
```

### 🚀 Next Steps

1. **Install Git** (when available):
   ```powershell
   ./a69v_repo_manager.ps1 configure
   ```

2. **Add Your Credentials**:
   ```powershell
   ./scripts/a69v_secrets.ps1 add GITHUB_TOKEN your_token
   ```

3. **Update .env File**:
   ```powershell
   ./genx.ps1 env  # Edit with your A6-9V specific values
   ```

4. **Test Integration**:
   ```powershell
   a69v-status     # Check integration status
   ```

5. **Repository Cleanup** (when GitHub CLI available):
   ```powershell
   ./a69v_repo_manager.ps1 cleanup
   ```

## Environment Variables Set

```env
A69V_ORGANIZATION=A6-9V
A69V_EMAIL=admin@a6-9v.dev
A69V_GITHUB_USERNAME=A6-9V
GENX_A69V_INTEGRATION=enabled
```

## Security Features

- ✅ Secure credential storage via Windows Credential Manager
- ✅ A6-9V specific secrets directory with restricted permissions
- ✅ SSH configuration for A6-9V repositories
- ✅ Security issue templates
- ✅ Dependabot configuration for dependency updates

## Support

- **Organization**: A6-9V
- **Email**: admin@a6-9v.dev
- **Security**: security@a6-9v.dev

Your GenX_FX system is now fully integrated with A6-9V organization! 🎉

---
Integration completed on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@

    $docPath = Join-Path $PROJECT_ROOT "A69V_GENX_INTEGRATION_COMPLETE.md"
    Set-Content -Path $docPath -Value $integrationDoc
    Write-Success "Created A6-9V integration documentation"
    
    # Update main README if it exists
    $readmePath = Join-Path $PROJECT_ROOT "README.md"
    if (Test-Path $readmePath) {
        $a69vBadge = @"

## A6-9V Organization

[![A6-9V](https://img.shields.io/badge/Organization-A6--9V-magenta?style=flat-square)](https://github.com/A6-9V)
[![GenX_FX](https://img.shields.io/badge/Project-GenX__FX-blue?style=flat-square)](https://github.com/A6-9V/GenX_FX_Remote)

This repository is maintained by the **A6-9V** development organization.
"@

        try {
            $readmeContent = Get-Content $readmePath -Raw
            if ($readmeContent -notmatch "A6-9V Organization") {
                $updatedReadme = $readmeContent.Replace("# GenX_FX", "# GenX_FX$a69vBadge`n")
                Set-Content -Path $readmePath -Value $updatedReadme
                Write-Success "Updated README.md with A6-9V organization badge"
            }
        } catch {
            Write-Warning "Could not update README.md"
        }
    }
}
#endregion

#region Main Execution
Clear-Host
Write-Host "🎯 A6-9V GenX_FX Integration" -ForegroundColor Magenta
Write-Host "Integrating A6-9V organization identity into GenX_FX system" -ForegroundColor Gray

Write-Host "`n📋 Integration Plan:" -ForegroundColor Cyan
Write-Host "✓ Update SSH configuration for A6-9V repositories" -ForegroundColor Gray  
Write-Host "✓ Configure environment variables with A6-9V identity" -ForegroundColor Gray
Write-Host "✓ Set up A6-9V credential management" -ForegroundColor Gray
Write-Host "✓ Integrate A6-9V aliases into GenX system" -ForegroundColor Gray
Write-Host "✓ Update documentation and branding" -ForegroundColor Gray

if (Confirm-Action "Proceed with A6-9V GenX_FX integration?") {
    
    Update-SSHConfiguration
    Update-EnvironmentVariables  
    Update-CredentialManagement
    Update-GenXIntegration
    Update-Documentation
    
    Write-Header "Integration Complete!"
    
    Write-Host @"

🎉 A6-9V GenX_FX Integration Successful!

Your development environment now includes:
✅ A6-9V organization identity
✅ Enhanced credential management  
✅ Repository security templates
✅ Integrated command interface
✅ Comprehensive documentation

🚀 Quick Start:
  a69v-status              # Check integration status
  ./a69v_repo_manager.ps1  # Manage A6-9V repositories
  ./genx.ps1 status        # GenX with A6-9V branding

📖 Documentation: A69V_GENX_INTEGRATION_COMPLETE.md

When Git becomes available:
  ./a69v_repo_manager.ps1 configure

🔐 Next: Add your credentials using the generated scripts!
"@ -ForegroundColor Green

} else {
    Write-Info "Integration cancelled by user."
}

Write-Host "`n✨ A6-9V integration script completed!" -ForegroundColor Magenta
#endregion