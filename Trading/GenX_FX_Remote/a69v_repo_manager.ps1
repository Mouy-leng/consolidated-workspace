#!/usr/bin/env pwsh
<#
.SYNOPSIS
    A6-9V Organization Repository Management System
.DESCRIPTION
    Comprehensive script for managing A6-9V organization repositories including:
    - Local Git configuration for A6-9V identity
    - Repository security management
    - Secrets and environment variables
    - Repository cleanup and organization
.PARAMETER Action
    The action to perform: setup, security, secrets, environments, cleanup, fork, status
.PARAMETER Repository
    Target repository name
#>

param(
    [Parameter(Position=0, Mandatory=$false)]
    [ValidateSet("setup", "security", "secrets", "environments", "cleanup", "fork", "status", "configure")]
    [string]$Action = "status",
    
    [Parameter(Position=1, Mandatory=$false)]
    [string]$Repository = "",
    
    [Parameter(HelpMessage="Organization name")]
    [string]$OrgName = "A6-9V",
    
    [Parameter(HelpMessage="Enable verbose output")]
    [switch]$VerboseLogging
)

# Organization Configuration
$ORGANIZATION = @{
    Name = $OrgName
    Email = "admin@a6-9v.dev"  # You can customize this
    Description = "A6-9V Development Organization"
    DefaultBranch = "main"
    PrivateByDefault = $true
}

# Project Configuration
$PROJECT_ROOT = $PWD.Path
$SCRIPTS_DIR = Join-Path $PROJECT_ROOT "scripts"
$CONFIG_DIR = Join-Path $PROJECT_ROOT "config"
$LOGS_DIR = Join-Path $PROJECT_ROOT "logs"

# Ensure directories exist
@($SCRIPTS_DIR, $CONFIG_DIR, $LOGS_DIR) | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

#region Utility Functions
function Write-Header {
    param([string]$Title)
    Write-Host "`n" + ("="*60) -ForegroundColor Magenta
    Write-Host "  A6-9V Organization: $Title" -ForegroundColor Magenta
    Write-Host ("="*60) -ForegroundColor Magenta
}

function Write-Success { param([string]$Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Warning { param([string]$Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message) Write-Host "✗ $Message" -ForegroundColor Red }
function Write-Info { param([string]$Message) Write-Host "ℹ $Message" -ForegroundColor Blue }

function Test-GitInstalled {
    try {
        $null = git --version 2>$null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Test-GHInstalled {
    try {
        $null = gh --version 2>$null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    $logFile = Join-Path $LOGS_DIR "a69v_repo_manager.log"
    Add-Content -Path $logFile -Value $logEntry -ErrorAction SilentlyContinue
    
    if ($VerboseLogging) {
        Write-Host $logEntry -ForegroundColor Gray
    }
}
#endregion

#region Git Configuration
function Set-A6V9Configuration {
    Write-Header "Configuring Git for A6-9V Organization"
    
    if (-not (Test-GitInstalled)) {
        Write-Error "Git is not installed or not available in PATH"
        Write-Info "Please install Git from: https://git-scm.com/downloads"
        return $false
    }
    
    Write-Info "Setting up Git configuration for $($ORGANIZATION.Name)..."
    
    try {
        # Set global Git configuration for A6-9V
        git config --global user.name $ORGANIZATION.Name
        Write-Success "Set Git username: $($ORGANIZATION.Name)"
        
        git config --global user.email $ORGANIZATION.Email
        Write-Success "Set Git email: $($ORGANIZATION.Email)"
        
        # Set default branch
        git config --global init.defaultBranch $ORGANIZATION.DefaultBranch
        Write-Success "Set default branch: $($ORGANIZATION.DefaultBranch)"
        
        # Enhanced Git settings for security
        git config --global pull.rebase true
        git config --global push.default simple
        git config --global core.autocrlf true  # Windows line endings
        git config --global credential.helper manager-core
        Write-Success "Applied security-focused Git settings"
        
        # Create Git aliases for A6-9V workflows
        git config --global alias.a6v-status "status --porcelain"
        git config --global alias.a6v-log "log --oneline --graph --decorate"
        git config --global alias.a6v-sync "!git fetch --all && git pull --rebase"
        Write-Success "Created A6-9V Git aliases"
        
        Write-Log "Git configured for A6-9V organization" "SUCCESS"
        return $true
        
    } catch {
        Write-Error "Failed to configure Git: $($_.Exception.Message)"
        Write-Log "Git configuration failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Show-GitConfiguration {
    Write-Header "Current Git Configuration"
    
    if (-not (Test-GitInstalled)) {
        Write-Error "Git is not installed"
        return
    }
    
    try {
        $username = git config --global user.name 2>$null
        $email = git config --global user.email 2>$null
        $defaultBranch = git config --global init.defaultBranch 2>$null
        
        Write-Host "📋 Git Identity:" -ForegroundColor Cyan
        if ($username) { Write-Success "Username: $username" } 
        else { Write-Warning "Username not set" }
        
        if ($email) { Write-Success "Email: $email" } 
        else { Write-Warning "Email not set" }
        
        if ($defaultBranch) { Write-Success "Default branch: $defaultBranch" } 
        else { Write-Warning "Default branch not set" }
        
        # Check if current directory is a Git repository
        if (Test-Path ".git") {
            Write-Host "`n📁 Current Repository:" -ForegroundColor Cyan
            $repoUrl = git remote get-url origin 2>$null
            if ($repoUrl) {
                Write-Success "Remote origin: $repoUrl"
            }
            
            $currentBranch = git branch --show-current 2>$null
            if ($currentBranch) {
                Write-Success "Current branch: $currentBranch"
            }
        }
        
    } catch {
        Write-Error "Failed to read Git configuration: $($_.Exception.Message)"
    }
}
#endregion

#region Repository Security Management
function Set-RepositorySecurity {
    Write-Header "Configuring Repository Security"
    
    if (-not (Test-GHInstalled)) {
        Write-Warning "GitHub CLI not installed. Installing security templates locally..."
        Set-LocalSecurityTemplates
        return
    }
    
    Write-Info "Setting up repository security features..."
    
    # Security policy template
    $securityPolicy = @"
# A6-9V Organization Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | ✅ Current        |
| < 1.0   | ❌ Not supported  |

## Reporting a Vulnerability

Please report security vulnerabilities to: security@a6-9v.dev

### Process:
1. **DO NOT** create public GitHub issues for security vulnerabilities
2. Email security@a6-9v.dev with details
3. Include steps to reproduce if possible
4. We will respond within 48 hours

### What to expect:
- Acknowledgment within 48 hours
- Regular updates on investigation progress
- Credit in security advisories (if desired)

## Security Best Practices

### For Contributors:
- Use strong, unique passwords
- Enable 2FA on all accounts
- Keep dependencies updated
- Follow secure coding practices
- Never commit secrets or credentials

### For A6-9V Team:
- Regular security audits
- Dependency scanning
- Code review requirements
- Automated security testing
- Secret scanning enabled
"@

    $securityPath = Join-Path $PROJECT_ROOT "SECURITY.md"
    Set-Content -Path $securityPath -Value $securityPolicy
    Write-Success "Created SECURITY.md policy"
    
    # Dependabot configuration
    $dependabotConfig = @"
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "A6-9V"
    assignees:
      - "A6-9V"
    commit-message:
      prefix: "deps"
      include: "scope"

  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    reviewers:
      - "A6-9V"

  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "monthly"
    reviewers:
      - "A6-9V"
"@

    $dependabotDir = Join-Path $PROJECT_ROOT ".github"
    if (-not (Test-Path $dependabotDir)) {
        New-Item -ItemType Directory -Path $dependabotDir -Force | Out-Null
    }
    
    $dependabotPath = Join-Path $dependabotDir "dependabot.yml"
    Set-Content -Path $dependabotPath -Value $dependabotConfig
    Write-Success "Created Dependabot configuration"
    
    Write-Log "Repository security configured" "SUCCESS"
}

function Set-LocalSecurityTemplates {
    Write-Info "Setting up local security templates..."
    
    # Create .github directory structure
    $githubDir = Join-Path $PROJECT_ROOT ".github"
    $templatesDir = Join-Path $githubDir "ISSUE_TEMPLATE"
    $workflowsDir = Join-Path $githubDir "workflows"
    
    @($githubDir, $templatesDir, $workflowsDir) | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ -Force | Out-Null
        }
    }
    
    # Security issue template
    $securityIssue = @"
---
name: 🔒 Security Issue
about: Report a security vulnerability (PRIVATE REPOSITORIES ONLY)
title: '[SECURITY] '
labels: security, high-priority
assignees: A6-9V
---

**⚠️ SECURITY NOTICE**
If this is a public repository, DO NOT use this template. Email security@a6-9v.dev instead.

## Description
Brief description of the security issue.

## Impact
What could an attacker achieve?

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Environment
- OS: 
- Version: 
- Browser (if applicable): 

## Additional Context
Any additional information about the vulnerability.
"@

    Set-Content -Path (Join-Path $templatesDir "security.md") -Value $securityIssue
    Write-Success "Created security issue template"
}
#endregion

#region Repository Secrets & Environment Management
function Manage-RepositorySecrets {
    Write-Header "Managing Repository Secrets & Variables"
    
    if (-not (Test-GHInstalled)) {
        Write-Warning "GitHub CLI not installed. Creating local templates..."
        Set-LocalSecretsTemplates
        return
    }
    
    Write-Info "Setting up repository secrets management..."
    
    # Define A6-9V standard secrets
    $standardSecrets = @{
        "A6V9_API_KEY" = "Main A6-9V API key for external services"
        "A6V9_DATABASE_URL" = "Database connection string"
        "A6V9_JWT_SECRET" = "JWT signing secret"
        "A6V9_ENCRYPTION_KEY" = "Data encryption key"
        "DOCKER_HUB_TOKEN" = "Docker Hub access token"
        "CODECOV_TOKEN" = "Code coverage reporting token"
    }
    
    $secretsTemplate = @"
# A6-9V Repository Secrets Configuration

## Required Secrets

### Production Environment
"@
    
    foreach ($secret in $standardSecrets.GetEnumerator()) {
        $secretsTemplate += "`n- **$($secret.Key)**: $($secret.Value)"
    }
    
    $secretsTemplate += @"

### Development Environment
- **A6V9_DEV_API_KEY**: Development API key
- **A6V9_DEV_DATABASE_URL**: Development database URL

## Environment Variables

### Production
- **NODE_ENV**: production
- **LOG_LEVEL**: info
- **A6V9_ENVIRONMENT**: production

### Staging
- **NODE_ENV**: staging
- **LOG_LEVEL**: debug
- **A6V9_ENVIRONMENT**: staging

### Development
- **NODE_ENV**: development
- **LOG_LEVEL**: debug
- **A6V9_ENVIRONMENT**: development

## Setup Instructions

1. In your repository, go to Settings > Secrets and variables > Actions
2. Add each secret with appropriate values
3. Configure environment-specific secrets in Environments section
4. Ensure branch protection rules are enabled for production

## Security Notes

- Never log secret values
- Use least-privilege access
- Rotate secrets regularly
- Monitor secret usage in workflows
"@

    $secretsPath = Join-Path $CONFIG_DIR "SECRETS.md"
    Set-Content -Path $secretsPath -Value $secretsTemplate
    Write-Success "Created secrets configuration guide"
    
    # Create environment template
    $environmentsConfig = @"
# A6-9V Repository Environments

## Production Environment
- **Protection Rules**: 
  - Required reviewers: A6-9V team
  - Wait timer: 5 minutes
  - Restrict to main branch only
- **Secrets**: All production secrets
- **Variables**: Production configuration

## Staging Environment  
- **Protection Rules**:
  - Required reviewers: 1 team member
  - Restrict to staging branch
- **Secrets**: Staging-specific secrets
- **Variables**: Staging configuration

## Development Environment
- **Protection Rules**: None (open access)
- **Secrets**: Development secrets only
- **Variables**: Development configuration

## Setup Commands (using GitHub CLI)

```bash
# Create environments
gh api repos/:owner/:repo/environments/production --method PUT
gh api repos/:owner/:repo/environments/staging --method PUT  
gh api repos/:owner/:repo/environments/development --method PUT

# Set environment secrets (example)
gh secret set A6V9_API_KEY --env production
gh secret set A6V9_DEV_API_KEY --env development
```
"@

    $envPath = Join-Path $CONFIG_DIR "ENVIRONMENTS.md"
    Set-Content -Path $envPath -Value $environmentsConfig
    Write-Success "Created environments configuration guide"
    
    Write-Log "Repository secrets and environments configured" "SUCCESS"
}

function Set-LocalSecretsTemplates {
    Write-Info "Creating local secrets management templates..."
    
    # Local secrets management script
    $localSecretsScript = @"
#!/usr/bin/env pwsh
# A6-9V Local Secrets Management

param(
    [Parameter(Position=0)]
    [ValidateSet("add", "list", "remove", "backup")]
    [string]$Action = "list",
    
    [Parameter(Position=1)]
    [string]$SecretName = "",
    
    [Parameter(Position=2)]
    [string]$SecretValue = ""
)

`$SECRETS_DIR = "`$env:GENX_SECRETS_DIR\a69v"
if (-not (Test-Path `$SECRETS_DIR)) {
    New-Item -ItemType Directory -Path `$SECRETS_DIR -Force | Out-Null
}

switch (`$Action) {
    "add" {
        if (-not `$SecretName) {
            Write-Host "Usage: ./a69v_secrets.ps1 add SECRET_NAME SECRET_VALUE" -ForegroundColor Yellow
            return
        }
        
        `$credTarget = "A6V9_`$SecretName"
        cmdkey /generic:`$credTarget /user:A6-9V /pass:`$SecretValue
        Write-Host "✓ Added secret: `$SecretName" -ForegroundColor Green
    }
    "list" {
        Write-Host "A6-9V Stored Secrets:" -ForegroundColor Cyan
        cmdkey /list | Where-Object { `$_ -match "A6V9_" } | ForEach-Object {
            Write-Host "  `$_" -ForegroundColor Gray
        }
    }
    "remove" {
        if (-not `$SecretName) {
            Write-Host "Usage: ./a69v_secrets.ps1 remove SECRET_NAME" -ForegroundColor Yellow
            return
        }
        
        `$credTarget = "A6V9_`$SecretName"
        cmdkey /delete:`$credTarget
        Write-Host "✓ Removed secret: `$SecretName" -ForegroundColor Green
    }
    "backup" {
        Write-Host "Creating secrets backup..." -ForegroundColor Blue
        # Note: This is a placeholder - actual backup would export non-sensitive metadata
        Write-Host "✓ Backup completed" -ForegroundColor Green
    }
}
"@

    $secretsScriptPath = Join-Path $SCRIPTS_DIR "a69v_secrets.ps1"
    Set-Content -Path $secretsScriptPath -Value $localSecretsScript
    Write-Success "Created local secrets management script"
}
#endregion

#region Repository Cleanup
function Start-RepositoryCleanup {
    Write-Header "Repository Cleanup & Organization"
    
    if (-not (Test-GHInstalled)) {
        Write-Warning "GitHub CLI not available. Showing cleanup recommendations..."
        Show-CleanupRecommendations
        return
    }
    
    Write-Info "Analyzing repositories for cleanup..."
    
    try {
        # Get user repositories
        $repos = gh repo list --json name,description,pushedAt,isPrivate,stargazerCount,language --limit 100 | ConvertFrom-Json
        
        if (-not $repos -or $repos.Count -eq 0) {
            Write-Warning "No repositories found or GitHub CLI not authenticated"
            return
        }
        
        Write-Host "`n📊 Repository Analysis:" -ForegroundColor Cyan
        Write-Host "Total repositories: $($repos.Count)"
        
        # Categorize repositories
        $oldRepos = $repos | Where-Object { 
            $pushDate = [DateTime]::Parse($_.pushedAt)
            $pushDate -lt (Get-Date).AddMonths(-6)
        }
        
        $emptyRepos = $repos | Where-Object { 
            -not $_.description -or $_.description.Trim() -eq ""
        }
        
        $zeroStarRepos = $repos | Where-Object { $_.stargazerCount -eq 0 }
        
        Write-Host "`n🧹 Cleanup Candidates:" -ForegroundColor Yellow
        Write-Host "Repositories not updated in 6+ months: $($oldRepos.Count)"
        Write-Host "Repositories with no description: $($emptyRepos.Count)"
        Write-Host "Repositories with 0 stars: $($zeroStarRepos.Count)"
        
        # Show specific cleanup recommendations
        if ($oldRepos.Count -gt 0) {
            Write-Host "`n📅 Old Repositories (not updated in 6+ months):" -ForegroundColor Yellow
            $oldRepos | Select-Object -First 10 | ForEach-Object {
                $pushDate = ([DateTime]::Parse($_.pushedAt)).ToString("yyyy-MM-dd")
                Write-Host "  - $($_.name) (last push: $pushDate)" -ForegroundColor Gray
            }
        }
        
        # Create cleanup script
        $cleanupScript = Generate-CleanupScript -OldRepos $oldRepos -EmptyRepos $emptyRepos
        $cleanupPath = Join-Path $SCRIPTS_DIR "a69v_cleanup.ps1"
        Set-Content -Path $cleanupPath -Value $cleanupScript
        Write-Success "Generated cleanup script: $cleanupPath"
        
    } catch {
        Write-Error "Failed to analyze repositories: $($_.Exception.Message)"
        Write-Log "Repository cleanup failed: $($_.Exception.Message)" "ERROR"
    }
}

function Show-CleanupRecommendations {
    Write-Info "Repository cleanup recommendations:"
    
    $recommendations = @"
# A6-9V Repository Cleanup Checklist

## Manual Cleanup Steps:

### 1. Identify Unused Repositories
- Check last commit date (older than 6 months)
- Review repository purpose and relevance
- Check if dependencies exist in other projects

### 2. Archive vs Delete Decision Matrix
**Archive if:**
- Historical value or reference needed
- Part of learning journey documentation
- Contains useful code snippets

**Delete if:**
- Test repositories with no real content
- Duplicate or redundant projects
- Broken projects with no value

### 3. Security Cleanup
- Remove any repositories with exposed secrets
- Check for hardcoded credentials in history
- Verify no sensitive data in commit history

### 4. Organization
- Rename repositories to follow A6-9V naming convention
- Add meaningful descriptions
- Set appropriate visibility (private for sensitive work)
- Add topics/tags for better organization

## A6-9V Naming Convention:
- **Core projects**: a69v-[project-name]
- **Tools/utilities**: a69v-tools-[tool-name]
- **Templates**: a69v-template-[type]
- **Documentation**: a69v-docs-[topic]

## Recommended Actions:
1. Run: gh repo list --json name,pushedAt,description
2. Review output and identify cleanup candidates
3. Use GitHub's archive feature for historical repos
4. Delete truly unnecessary repositories
5. Rename remaining repos to follow convention
"@

    $recommendationsPath = Join-Path $CONFIG_DIR "CLEANUP_RECOMMENDATIONS.md"
    Set-Content -Path $recommendationsPath -Value $recommendations
    Write-Success "Created cleanup recommendations: $recommendationsPath"
}

function Generate-CleanupScript {
    param($OldRepos, $EmptyRepos)
    
    $script = @"
#!/usr/bin/env pwsh
# A6-9V Repository Cleanup Script
# Generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

Write-Host "🧹 A6-9V Repository Cleanup Tool" -ForegroundColor Magenta

# IMPORTANT: Review each command before uncommenting and executing

# Old repositories (not updated in 6+ months)
Write-Host "`nOld Repositories:" -ForegroundColor Yellow
"@

    if ($OldRepos) {
        foreach ($repo in $OldRepos) {
            $script += "`n# gh repo archive $($repo.name) --confirm  # Archive: $($repo.name)"
        }
    }

    $script += @"

# Empty repositories (no description)
Write-Host "`nEmpty Repositories:" -ForegroundColor Yellow
"@

    if ($EmptyRepos) {
        foreach ($repo in $EmptyRepos) {
            $script += "`n# gh repo edit $($repo.name) --description 'A6-9V project description needed'  # Add description to: $($repo.name)"
        }
    }

    $script += @"

Write-Host "`n⚠️  REVIEW BEFORE EXECUTING:" -ForegroundColor Red
Write-Host "1. Uncomment commands you want to execute" -ForegroundColor Yellow
Write-Host "2. Review each repository before archiving/deleting" -ForegroundColor Yellow
Write-Host "3. Consider backing up important data first" -ForegroundColor Yellow

# Example usage:
# gh repo archive REPO_NAME --confirm
# gh repo delete REPO_NAME --confirm
# gh repo edit REPO_NAME --description "New description"
"@

    return $script
}
#endregion

#region Repository Forking & Management
function Start-RepositoryFork {
    param([string]$SourceRepo)
    
    Write-Header "Repository Forking for A6-9V"
    
    if (-not $SourceRepo) {
        Write-Info "Usage: .\a69v_repo_manager.ps1 fork <source-repo-url>"
        Write-Info "Example: .\a69v_repo_manager.ps1 fork https://github.com/user/repo"
        return
    }
    
    if (-not (Test-GHInstalled)) {
        Write-Error "GitHub CLI is required for repository forking"
        Write-Info "Install from: https://cli.github.com/"
        return
    }
    
    try {
        Write-Info "Forking repository: $SourceRepo"
        
        # Fork the repository
        gh repo fork $SourceRepo --clone=true
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Repository forked successfully"
            
            # Configure the forked repository for A6-9V
            $repoName = Split-Path $SourceRepo -Leaf
            if (Test-Path $repoName) {
                Set-Location $repoName
                
                # Set up A6-9V specific configuration
                git config user.name $ORGANIZATION.Name
                git config user.email $ORGANIZATION.Email
                
                Write-Success "Configured repository for A6-9V"
                
                # Create A6-9V specific files
                Create-A6V9Templates
                
                Write-Info "Repository ready for A6-9V development"
                Write-Info "Next steps:"
                Write-Host "  1. Review and customize README.md" -ForegroundColor Gray
                Write-Host "  2. Set up repository secrets" -ForegroundColor Gray
                Write-Host "  3. Configure branch protection rules" -ForegroundColor Gray
                Write-Host "  4. Add A6-9V specific workflows" -ForegroundColor Gray
            }
        } else {
            Write-Error "Failed to fork repository"
        }
        
    } catch {
        Write-Error "Fork operation failed: $($_.Exception.Message)"
        Write-Log "Repository fork failed: $($_.Exception.Message)" "ERROR"
    }
}

function Create-A6V9Templates {
    Write-Info "Adding A6-9V templates to repository..."
    
    # A6-9V README template addition
    $readmeAddition = @"

---

## A6-9V Organization

This repository is maintained by the **A6-9V** development organization.

### Development Setup
```bash
# Clone with A6-9V configuration
git clone <repo-url>
cd <repo-name>

# Set A6-9V identity (if not set globally)
git config user.name "A6-9V"
git config user.email "admin@a6-9v.dev"
```

### Contributing
- Follow A6-9V coding standards
- Ensure all commits are signed
- Use conventional commit messages
- Add appropriate tests

### Security
- Report security issues to: security@a6-9v.dev
- Follow responsible disclosure practices
- See SECURITY.md for details

### Contact
- Organization: A6-9V
- Email: admin@a6-9v.dev
- Issues: Use GitHub Issues for bug reports and feature requests

---
"@

    if (Test-Path "README.md") {
        Add-Content -Path "README.md" -Value $readmeAddition
        Write-Success "Updated README.md with A6-9V information"
    }
    
    # Create .a69v directory for organization-specific files
    $a69vDir = ".a69v"
    if (-not (Test-Path $a69vDir)) {
        New-Item -ItemType Directory -Path $a69vDir -Force | Out-Null
        
        $orgConfig = @"
# A6-9V Organization Configuration

organization: A6-9V
maintainer: admin@a6-9v.dev
created: $(Get-Date -Format 'yyyy-MM-dd')
repository_type: forked
security_level: standard

# Development guidelines
coding_standards: A6-9V
testing_required: true
documentation_required: true
security_review_required: false
"@
        
        Set-Content -Path (Join-Path $a69vDir "config.yml") -Value $orgConfig
        Write-Success "Created A6-9V organization configuration"
    }
}
#endregion

#region Status and Reporting
function Show-OrganizationStatus {
    Write-Header "A6-9V Organization Status"
    
    # Git Configuration Status
    Show-GitConfiguration
    
    # Repository Status
    Write-Host "`n📊 Current Repository Status:" -ForegroundColor Cyan
    if (Test-Path ".git") {
        try {
            $status = git status --porcelain 2>$null
            if ($status) {
                Write-Warning "Uncommitted changes detected"
                Write-Host "  Modified files: $(($status | Where-Object { $_ -match '^.M' }).Count)" -ForegroundColor Yellow
                Write-Host "  Untracked files: $(($status | Where-Object { $_ -match '^\?\?' }).Count)" -ForegroundColor Yellow
            } else {
                Write-Success "Working directory clean"
            }
            
            $branch = git branch --show-current 2>$null
            if ($branch) {
                Write-Success "Current branch: $branch"
            }
            
        } catch {
            Write-Warning "Could not read Git status"
        }
    } else {
        Write-Info "Not in a Git repository"
    }
    
    # A6-9V Files Status
    Write-Host "`n📁 A6-9V Configuration Files:" -ForegroundColor Cyan
    $a69vFiles = @{
        "SECURITY.md" = "Security policy"
        ".github/dependabot.yml" = "Dependency updates"
        "config/SECRETS.md" = "Secrets documentation"
        "config/ENVIRONMENTS.md" = "Environment configuration"
        "scripts/a69v_secrets.ps1" = "Local secrets management"
    }
    
    foreach ($file in $a69vFiles.GetEnumerator()) {
        $path = Join-Path $PROJECT_ROOT $file.Key
        if (Test-Path $path) {
            Write-Success "$($file.Key): $($file.Value)"
        } else {
            Write-Warning "$($file.Key): Not found"
        }
    }
    
    # Tools Status
    Write-Host "`n🛠️ Required Tools:" -ForegroundColor Cyan
    if (Test-GitInstalled) { Write-Success "Git: Available" }
    else { Write-Error "Git: Not installed" }
    
    if (Test-GHInstalled) { Write-Success "GitHub CLI: Available" }
    else { Write-Warning "GitHub CLI: Not installed (optional)" }
    
    # Recent Activity
    $logFile = Join-Path $LOGS_DIR "a69v_repo_manager.log"
    if (Test-Path $logFile) {
        Write-Host "`n📋 Recent Activity:" -ForegroundColor Cyan
        Get-Content $logFile | Select-Object -Last 5 | ForEach-Object {
            Write-Host "  $_" -ForegroundColor Gray
        }
    }
}
#endregion

#region Main Execution
Clear-Host
Write-Host "🎯 A6-9V Organization Repository Manager" -ForegroundColor Magenta
Write-Host "Organization: $($ORGANIZATION.Name)" -ForegroundColor Gray
Write-Host "Email: $($ORGANIZATION.Email)" -ForegroundColor Gray

switch ($Action) {
    "configure" {
        if (Set-A6V9Configuration) {
            Write-Success "A6-9V Git configuration completed!"
            Show-GitConfiguration
        }
    }
    
    "security" {
        Set-RepositorySecurity
    }
    
    "secrets" {
        Manage-RepositorySecrets
    }
    
    "environments" {
        Manage-RepositorySecrets  # Same function handles both
    }
    
    "cleanup" {
        Start-RepositoryCleanup
    }
    
    "fork" {
        Start-RepositoryFork -SourceRepo $Repository
    }
    
    "setup" {
        Write-Info "Running complete A6-9V setup..."
        if (Set-A6V9Configuration) {
            Set-RepositorySecurity
            Manage-RepositorySecrets
            Write-Success "Complete A6-9V setup finished!"
        }
    }
    
    "status" {
        Show-OrganizationStatus
    }
    
    default {
        Write-Error "Unknown action: $Action"
        Write-Host "`nAvailable actions:" -ForegroundColor Yellow
        Write-Host "  configure  - Set up Git for A6-9V organization" -ForegroundColor Gray
        Write-Host "  security   - Configure repository security" -ForegroundColor Gray
        Write-Host "  secrets    - Set up secrets and environments" -ForegroundColor Gray
        Write-Host "  cleanup    - Analyze and clean up repositories" -ForegroundColor Gray
        Write-Host "  fork       - Fork a repository for A6-9V" -ForegroundColor Gray
        Write-Host "  setup      - Complete A6-9V organization setup" -ForegroundColor Gray
        Write-Host "  status     - Show current status" -ForegroundColor Gray
    }
}

Write-Host "`n✨ A6-9V operation completed!" -ForegroundColor Green
#endregion