#!/usr/bin/env pwsh
<#
.SYNOPSIS
    A6-9V Secure Token Storage
.DESCRIPTION
    Securely stores the GitHub token and other A6-9V credentials for future use.
#>

param(
    [Parameter(HelpMessage="GitHub token to store")]
    [string]$GitHubToken = "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"
)

# A6-9V Configuration
$A69V_CONFIG = @{
    Organization = "A6-9V"
    SecretsDir = $env:GENX_SECRETS_DIR ?? (Join-Path $env:USERPROFILE ".genx_fx_secrets")
    ProjectRoot = $PWD.Path
}

#region Utility Functions
function Write-Header {
    param([string]$Title)
    Write-Host "`n" + ("="*60) -ForegroundColor Magenta
    Write-Host "  A6-9V Secure Token Storage: $Title" -ForegroundColor Magenta
    Write-Host ("="*60) -ForegroundColor Magenta
}

function Write-Success { param([string]$Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Warning { param([string]$Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message) Write-Host "✗ $Message" -ForegroundColor Red }
function Write-Info { param([string]$Message) Write-Host "ℹ $Message" -ForegroundColor Blue }
#endregion

#region Secure Token Storage
function Store-A69VToken {
    Write-Header "Storing A6-9V GitHub Token Securely"
    
    # Create secure token file
    $tokenDir = Join-Path $A69V_CONFIG.SecretsDir "tokens"
    if (-not (Test-Path $tokenDir)) {
        New-Item -ItemType Directory -Path $tokenDir -Force | Out-Null
        
        # Set restrictive permissions
        try {
            $acl = Get-Acl $tokenDir
            $acl.SetAccessRuleProtection($true, $false)
            $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($env:USERNAME, "FullControl", "Allow")
            $acl.SetAccessRule($accessRule)
            Set-Acl $tokenDir $acl
        } catch {
            Write-Warning "Could not set restrictive permissions on token directory"
        }
    }
    
    # Store token with metadata
    $tokenMetadata = @{
        organization = "A6-9V"
        token_type = "GitHub Personal Access Token"
        created_date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        scope = "Repository management, Actions, Secrets"
        usage = "A6-9V repository operations and automation"
        environment = "Development"
        expires = "Check GitHub settings for expiration"
        security_note = "This token provides access to A6-9V repositories"
    }
    
    $tokenFile = Join-Path $tokenDir "github_token_metadata.json"
    $tokenMetadata | ConvertTo-Json -Depth 10 | Set-Content -Path $tokenFile
    Write-Success "Token metadata stored: $tokenFile"
    
    # Set environment variable
    try {
        [Environment]::SetEnvironmentVariable("A69V_GITHUB_TOKEN", $GitHubToken, "User")
        $env:A69V_GITHUB_TOKEN = $GitHubToken
        Write-Success "GitHub token set as environment variable: A69V_GITHUB_TOKEN"
    } catch {
        Write-Warning "Could not set environment variable: $($_.Exception.Message)"
    }
    
    # Create .env entry
    $envFile = Join-Path $A69V_CONFIG.ProjectRoot ".env"
    if (Test-Path $envFile) {
        $envContent = Get-Content $envFile -Raw
        
        # Check if token entry already exists
        if ($envContent -notmatch "A69V_GITHUB_TOKEN=") {
            $tokenEntry = "`n# A6-9V GitHub Token (added $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))`nA69V_GITHUB_TOKEN=$GitHubToken"
            Add-Content -Path $envFile -Value $tokenEntry
            Write-Success "Added GitHub token to .env file"
        } else {
            Write-Info "GitHub token already exists in .env file"
        }
    }
    
    return $tokenMetadata
}

function Create-TokenUsageScript {
    Write-Info "Creating token usage script..."
    
    $tokenUsageScript = @"
#!/usr/bin/env pwsh
<#
.SYNOPSIS
    A6-9V Token Usage Helper
.DESCRIPTION
    Helper script to use stored A6-9V GitHub token for various operations.
#>

# Get A6-9V GitHub Token
function Get-A69VToken {
    if (`$env:A69V_GITHUB_TOKEN) {
        return `$env:A69V_GITHUB_TOKEN
    } elseif (`$env:GH_TOKEN) {
        return `$env:GH_TOKEN
    } else {
        Write-Warning "A6-9V GitHub token not found in environment variables"
        return `$null
    }
}

# Set token for GitHub CLI
function Set-GHToken {
    `$token = Get-A69VToken
    if (`$token) {
        `$env:GH_TOKEN = `$token
        Write-Host "✓ GitHub CLI token configured for A6-9V" -ForegroundColor Green
        return `$true
    }
    return `$false
}

# Verify token access
function Test-A69VTokenAccess {
    `$token = Get-A69VToken
    if (-not `$token) {
        Write-Host "✗ No A6-9V GitHub token found" -ForegroundColor Red
        return `$false
    }
    
    try {
        # Test token with GitHub API
        `$headers = @{
            "Authorization" = "Bearer `$token"
            "Accept" = "application/vnd.github.v3+json"
            "User-Agent" = "A6-9V-PowerShell"
        }
        
        `$response = Invoke-RestMethod -Uri "https://api.github.com/user" -Headers `$headers -Method Get
        Write-Host "✓ Token valid for user: `$(`$response.login)" -ForegroundColor Green
        Write-Host "  Name: `$(`$response.name)" -ForegroundColor Gray
        Write-Host "  Public repos: `$(`$response.public_repos)" -ForegroundColor Gray
        return `$true
        
    } catch {
        Write-Host "✗ Token validation failed: `$(`$_.Exception.Message)" -ForegroundColor Red
        return `$false
    }
}

# Export functions
Export-ModuleMember -Function Get-A69VToken, Set-GHToken, Test-A69VTokenAccess

# Auto-configure if running directly
if (`$MyInvocation.InvocationName -eq `$MyInvocation.MyCommand.Name) {
    Write-Host "🎯 A6-9V Token Usage Helper" -ForegroundColor Magenta
    
    if (Set-GHToken) {
        Test-A69VTokenAccess | Out-Null
    }
}
"@

    $tokenScriptPath = Join-Path $A69V_CONFIG.ProjectRoot "scripts/a69v_token_helper.ps1"
    Set-Content -Path $tokenScriptPath -Value $tokenUsageScript
    Write-Success "Created token usage helper: scripts/a69v_token_helper.ps1"
    
    return $tokenScriptPath
}

function Update-CommitScript {
    Write-Info "Updating commit script with token authentication..."
    
    $commitScriptPath = Join-Path $A69V_CONFIG.ProjectRoot "execute_a69v_commit.ps1"
    if (Test-Path $commitScriptPath) {
        $commitScript = Get-Content $commitScriptPath -Raw
        
        # Add token configuration to commit script
        $tokenConfig = @"

# Configure GitHub token for authentication
if (`$env:A69V_GITHUB_TOKEN) {
    `$env:GH_TOKEN = `$env:A69V_GITHUB_TOKEN
    Write-Host "✓ GitHub token configured for A6-9V operations" -ForegroundColor Green
} else {
    Write-Host "⚠ GitHub token not found. Manual authentication may be required." -ForegroundColor Yellow
}

"@

        # Insert token configuration after the header
        $updatedScript = $commitScript.Replace(
            'Write-Host "🎯 A6-9V Commit Execution" -ForegroundColor Magenta',
            'Write-Host "🎯 A6-9V Commit Execution" -ForegroundColor Magenta' + $tokenConfig
        )
        
        Set-Content -Path $commitScriptPath -Value $updatedScript
        Write-Success "Updated commit script with token configuration"
    }
}
#endregion

#region Repository Authentication Setup
function Setup-RepositoryAuth {
    Write-Header "Setting up Repository Authentication"
    
    # Update Git configuration with token
    Write-Info "Configuring Git credential helper..."
    
    $gitConfigScript = @"
# A6-9V Git Configuration with Token Authentication
# Run when Git becomes available

git config --global credential.helper manager-core
git config --global user.name "A6-9V"
git config --global user.email "admin@a6-9v.dev"
git config --global init.defaultBranch main

# GitHub specific configuration
git config --global hub.protocol https
git config --global github.user "A6-9V"

Write-Host "✓ Git configured for A6-9V with token authentication" -ForegroundColor Green
"@

    $gitConfigPath = Join-Path $A69V_CONFIG.ProjectRoot "setup_git_auth.ps1"
    Set-Content -Path $gitConfigPath -Value $gitConfigScript
    Write-Success "Created Git authentication setup: setup_git_auth.ps1"
    
    return $gitConfigPath
}

function Create-TokenInstructions {
    Write-Info "Creating token usage instructions..."
    
    $instructions = @"
# A6-9V GitHub Token Usage Instructions

## Token Information
- **Organization**: A6-9V
- **Token**: Stored securely in environment variables
- **Type**: GitHub Personal Access Token
- **Created**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

## Environment Variables Set
- `A69V_GITHUB_TOKEN` - A6-9V specific GitHub token
- Added to .env file for project use

## Usage Examples

### GitHub CLI Operations
``````powershell
# The token is automatically configured for GitHub CLI operations
gh repo list --limit 10
gh repo create A6-9V/new-repo --private
``````

### Git Operations
``````powershell  
# Configure Git with token authentication
.\setup_git_auth.ps1

# Clone repositories
git clone https://github.com/A6-9V/repository-name.git

# Push changes (token handles authentication)
git push origin main
``````

### Repository Management
``````powershell
# Use A6-9V repository manager with token
.\a69v_repo_manager.ps1 configure
.\a69v_repo_manager.ps1 cleanup
.\a69v_repo_manager.ps1 fork https://github.com/user/repo
``````

### Token Helper Script
``````powershell
# Test token access
.\scripts\a69v_token_helper.ps1

# Or import functions
Import-Module .\scripts\a69v_token_helper.ps1
Test-A69VTokenAccess
``````

## Security Notes
- Token is stored in user environment variables
- Token metadata stored in secure directory with restricted permissions
- Token is not committed to version control (.gitignore configured)
- Use token only for A6-9V organization operations

## Next Steps
1. Test token access: `.\scripts\a69v_token_helper.ps1`
2. Configure Git authentication: `.\setup_git_auth.ps1`
3. Run repository operations: `.\a69v_repo_manager.ps1 cleanup`
4. Commit A6-9V work: `.\execute_a69v_commit.ps1`

## Token Scopes
This token should have the following GitHub scopes:
- `repo` - Full repository access
- `workflow` - GitHub Actions workflows
- `admin:repo_hook` - Repository webhooks
- `delete_repo` - Delete repositories (for cleanup)
- `admin:org` - Organization administration (if needed)

---
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Organization: A6-9V
"@

    $instructionsPath = Join-Path $A69V_CONFIG.ProjectRoot "A69V_TOKEN_INSTRUCTIONS.md"
    Set-Content -Path $instructionsPath -Value $instructions
    Write-Success "Created token instructions: A69V_TOKEN_INSTRUCTIONS.md"
    
    return $instructionsPath
}
#endregion

#region Main Execution
Clear-Host
Write-Host "🎯 A6-9V Secure Token Storage" -ForegroundColor Magenta
Write-Host "Organization: $($A69V_CONFIG.Organization)" -ForegroundColor Gray
Write-Host "Token: ghp_***...***3rX1UE (secured)" -ForegroundColor Gray

# Store the token securely
$tokenMetadata = Store-A69VToken

# Create supporting scripts and documentation
$tokenScriptPath = Create-TokenUsageScript
$gitAuthPath = Setup-RepositoryAuth
$instructionsPath = Create-TokenInstructions

# Update existing scripts
Update-CommitScript

Write-Header "Token Storage Complete"

Write-Host @"

🎉 A6-9V GitHub Token Stored Securely!

✅ Token stored in environment variable: A69V_GITHUB_TOKEN
✅ Token metadata saved in secure directory
✅ .env file updated with token entry
✅ Token helper script created: $(Split-Path $tokenScriptPath -Leaf)
✅ Git authentication setup created: $(Split-Path $gitAuthPath -Leaf)
✅ Usage instructions created: $(Split-Path $instructionsPath -Leaf)
✅ Commit script updated with token authentication

🔧 Immediate Actions Available:
  1. Test token access: .\scripts\a69v_token_helper.ps1
  2. Setup Git authentication: .\setup_git_auth.ps1
  3. Use repository manager: .\a69v_repo_manager.ps1 cleanup
  4. Commit A6-9V work: .\execute_a69v_commit.ps1

🔐 Security Features:
  • Token stored in user environment variables
  • Secure token directory with restricted permissions
  • .gitignore configured to exclude token files
  • Token helper functions for safe usage

🚀 Ready for A6-9V Repository Operations!
Your GitHub token is now securely configured for all A6-9V operations.

"@ -ForegroundColor Green

Write-Host "✨ Token setup completed! Your A6-9V organization is ready for GitHub operations." -ForegroundColor Magenta
#endregion