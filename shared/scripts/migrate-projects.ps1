# Migration Script: Move all projects from C: to E: drive
# This script consolidates all code projects into one workspace

param(
    [switch]$DryRun = $false,
    [switch]$SkipGit = $false
)

$ErrorActionPreference = "Continue"

# Source locations
$sources = @(
    @{
        Path = "C:\Users\lengk\GenX_FX_Remote"
        Dest = "projects\genx-fx-remote"
        IsGit = $true
        Description = "Main trading system"
    },
    @{
        Path = "C:\Users\lengk\trading-bot-a69v"
        Dest = "projects\trading-bot"
        IsGit = $true
        Description = "Autonomous trading bot"
    },
    @{
        Path = "C:\Users\lengk\AI_Trading_System"
        Dest = "projects\ai-trading-system"
        IsGit = $false
        Description = "AI trading system"
    },
    @{
        Path = "C:\Users\lengk\GenX_FX-1"
        Dest = "projects\genx-fx-1"
        IsGit = $false
        Description = "Trading system variant"
    },
    @{
        Path = "C:\Users\lengk\.config\trading-system\trading-analysis"
        Dest = "projects\trading-analysis"
        IsGit = $false
        Description = "Trading analysis tools"
    },
    @{
        Path = "C:\Users\lengk\.config\trading-system\trading-microservice"
        Dest = "projects\trading-microservice"
        IsGit = $false
        Description = "Trading microservices"
    },
    @{
        Path = "C:\Users\lengk\.config\trading-system\mt5-fbs-setup"
        Dest = "projects\mt5-integration"
        IsGit = $false
        Description = "MT5/FBS integration"
    }
)

# Target workspace
$workspaceRoot = "E:\Code\consolidated-workspace"
$projectsDir = Join-Path $workspaceRoot "projects"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project Migration Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Workspace: $workspaceRoot" -ForegroundColor Yellow
Write-Host "Mode: $(if ($DryRun) { 'DRY RUN' } else { 'LIVE' })" -ForegroundColor $(if ($DryRun) { 'Yellow' } else { 'Green' })
Write-Host ""

# Create projects directory
if (-not $DryRun) {
    New-Item -ItemType Directory -Path $projectsDir -Force | Out-Null
}

$migrated = @()
$skipped = @()
$errors = @()

foreach ($source in $sources) {
    $sourcePath = $source.Path
    $destPath = Join-Path $workspaceRoot $source.Dest
    
    Write-Host "Processing: $($source.Description)" -ForegroundColor Cyan
    Write-Host "  Source: $sourcePath" -ForegroundColor Gray
    Write-Host "  Dest: $destPath" -ForegroundColor Gray
    
    # Check if source exists
    if (-not (Test-Path $sourcePath)) {
        Write-Host "  ⚠ Source not found, skipping" -ForegroundColor Yellow
        $skipped += $source
        continue
    }
    
    # Check if destination already exists
    if (Test-Path $destPath) {
        Write-Host "  ⚠ Destination exists, skipping" -ForegroundColor Yellow
        $skipped += $source
        continue
    }
    
    if ($DryRun) {
        Write-Host "  [DRY RUN] Would copy to: $destPath" -ForegroundColor Yellow
        $migrated += $source
    } else {
        try {
            # Copy directory
            Write-Host "  Copying..." -ForegroundColor White
            Copy-Item -Path $sourcePath -Destination $destPath -Recurse -Force
            
            # Remove .git if SkipGit is set (for consolidation)
            if ($SkipGit -and $source.IsGit -and (Test-Path (Join-Path $destPath ".git"))) {
                Remove-Item -Path (Join-Path $destPath ".git") -Recurse -Force
                Write-Host "  Removed .git directory (consolidating into main repo)" -ForegroundColor Yellow
            }
            
            # Remove node_modules and other large dirs to save space
            $largeDirs = @("node_modules", "__pycache__", ".venv", "venv", "dist", "build")
            foreach ($dir in $largeDirs) {
                $dirPath = Join-Path $destPath $dir
                if (Test-Path $dirPath) {
                    Remove-Item -Path $dirPath -Recurse -Force -ErrorAction SilentlyContinue
                    Write-Host "  Removed $dir" -ForegroundColor Gray
                }
            }
            
            Write-Host "  ✓ Migrated successfully" -ForegroundColor Green
            $migrated += $source
        } catch {
            Write-Host "  ✗ Error: $_" -ForegroundColor Red
            $errors += @{Source = $source; Error = $_}
        }
    }
    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Migration Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Migrated: $($migrated.Count)" -ForegroundColor Green
Write-Host "Skipped: $($skipped.Count)" -ForegroundColor Yellow
Write-Host "Errors: $($errors.Count)" -ForegroundColor $(if ($errors.Count -eq 0) { 'Green' } else { 'Red' })

if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "Errors:" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "  - $($error.Source.Description): $($error.Error)" -ForegroundColor Red
    }
}

if ($DryRun) {
    Write-Host ""
    Write-Host "This was a DRY RUN. Run without -DryRun to perform actual migration." -ForegroundColor Yellow
}

