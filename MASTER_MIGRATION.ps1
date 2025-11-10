# Master Migration Script
# Orchestrates the complete migration and consolidation process

param(
    [switch]$SkipCredentialCollection = $false,
    [switch]$SkipMigration = $false,
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Master Migration Script" -ForegroundColor Cyan
Write-Host "Consolidated Workspace Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$workspaceRoot = "E:\Code\consolidated-workspace"
Set-Location $workspaceRoot

# Step 1: Credential Collection
if (-not $SkipCredentialCollection) {
    Write-Host "[1/4] Collecting and auditing credentials..." -ForegroundColor Yellow
    try {
        .\collect-credentials.ps1
        Write-Host "✓ Credential collection complete" -ForegroundColor Green
    } catch {
        Write-Host "✗ Error in credential collection: $_" -ForegroundColor Red
    }
    Write-Host ""
} else {
    Write-Host "[1/4] Skipping credential collection" -ForegroundColor Gray
    Write-Host ""
}

# Step 2: Project Migration
if (-not $SkipMigration) {
    Write-Host "[2/4] Migrating projects..." -ForegroundColor Yellow
    try {
        if ($DryRun) {
            .\migrate-projects.ps1 -DryRun
        } else {
            .\migrate-projects.ps1
        }
        Write-Host "✓ Project migration complete" -ForegroundColor Green
    } catch {
        Write-Host "✗ Error in project migration: $_" -ForegroundColor Red
    }
    Write-Host ""
} else {
    Write-Host "[2/4] Skipping project migration" -ForegroundColor Gray
    Write-Host ""
}

# Step 3: SSH Key Setup (Informational)
Write-Host "[3/4] SSH Key Setup" -ForegroundColor Yellow
Write-Host "Run .\setup-ssh-key.ps1 to configure GitHub SSH authentication" -ForegroundColor Cyan
Write-Host ""

# Step 4: Git Initialization
Write-Host "[4/4] Git Repository Status" -ForegroundColor Yellow
if (Test-Path ".git") {
    $gitStatus = git status --short 2>$null
    if ($gitStatus) {
        Write-Host "Repository has uncommitted changes" -ForegroundColor Yellow
        Write-Host "Run 'git add .' and 'git commit' to save changes" -ForegroundColor Cyan
    } else {
        Write-Host "✓ Repository is clean" -ForegroundColor Green
    }
} else {
    Write-Host "Git repository not initialized" -ForegroundColor Yellow
    Write-Host "Run 'git init' to initialize" -ForegroundColor Cyan
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Migration Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Workspace: $workspaceRoot" -ForegroundColor White
Write-Host "Mode: $(if ($DryRun) { 'DRY RUN' } else { 'LIVE' })" -ForegroundColor $(if ($DryRun) { 'Yellow' } else { 'Green' })
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Review CREDENTIALS_AUDIT.md" -ForegroundColor White
Write-Host "2. Run .\setup-ssh-key.ps1 to configure GitHub" -ForegroundColor White
Write-Host "3. Review migrated projects in projects/ directory" -ForegroundColor White
Write-Host "4. Initialize/commit to git repository" -ForegroundColor White
Write-Host "5. Test all projects to ensure they work" -ForegroundColor White
Write-Host "6. Clean up C: drive after verification" -ForegroundColor White
Write-Host ""

if ($DryRun) {
    Write-Host "⚠️  This was a DRY RUN. Run without -DryRun to perform actual operations." -ForegroundColor Yellow
}

