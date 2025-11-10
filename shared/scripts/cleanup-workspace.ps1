# Workspace Cleanup Script
# Removes temporary files, caches, logs, and organizes the workspace

param(
    [switch]$DryRun = $false,
    [switch]$KeepLogs = $false
)

$ErrorActionPreference = "Continue"
$workspaceRoot = "E:\Code\consolidated-workspace"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Workspace Cleanup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Workspace: $workspaceRoot" -ForegroundColor Yellow
Write-Host "Mode: $(if ($DryRun) { 'DRY RUN' } else { 'LIVE' })" -ForegroundColor $(if ($DryRun) { 'Yellow' } else { 'Green' })
Write-Host ""

$removedCount = 0
$removedSize = 0

function Remove-ItemSafe {
    param([string]$Path, [string]$Type)
    
    if (Test-Path $Path) {
        $size = (Get-ChildItem $Path -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would remove: $Path ($([math]::Round($size / 1MB, 2)) MB)" -ForegroundColor Yellow
        } else {
            try {
                Remove-Item -Path $Path -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "  ✓ Removed: $Path ($([math]::Round($size / 1MB, 2)) MB)" -ForegroundColor Green
                $script:removedCount++
                $script:removedSize += $size
            } catch {
                Write-Host "  ✗ Error removing: $Path - $_" -ForegroundColor Red
            }
        }
    }
}

# 1. Remove log files
if (-not $KeepLogs) {
    Write-Host "[1/6] Removing log files..." -ForegroundColor Yellow
    $logFiles = Get-ChildItem -Path $workspaceRoot -Recurse -File -ErrorAction SilentlyContinue | 
        Where-Object { $_.Extension -eq ".log" -or $_.Name -like "*.log" }
    
    foreach ($log in $logFiles) {
        Remove-ItemSafe -Path $log.FullName -Type "Log"
    }
    Write-Host ""
}

# 2. Remove Python cache directories
Write-Host "[2/6] Removing Python cache directories..." -ForegroundColor Yellow
$cacheDirs = @("__pycache__", ".pytest_cache", ".mypy_cache")
foreach ($cacheDir in $cacheDirs) {
    $dirs = Get-ChildItem -Path $workspaceRoot -Recurse -Directory -ErrorAction SilentlyContinue | 
        Where-Object { $_.Name -eq $cacheDir }
    foreach ($dir in $dirs) {
        Remove-ItemSafe -Path $dir.FullName -Type "Cache"
    }
}
Write-Host ""

# 3. Remove temporary files
Write-Host "[3/6] Removing temporary files..." -ForegroundColor Yellow
$tempPatterns = @("*.tmp", "*.bak", "*.backup", "*~", ".DS_Store", "Thumbs.db")
foreach ($pattern in $tempPatterns) {
    $files = Get-ChildItem -Path $workspaceRoot -Recurse -File -ErrorAction SilentlyContinue | 
        Where-Object { $_.Name -like $pattern }
    foreach ($file in $files) {
        Remove-ItemSafe -Path $file.FullName -Type "Temp"
    }
}
Write-Host ""

# 4. Remove unusual directories (like Program Files in projects)
Write-Host "[4/6] Removing unusual directories..." -ForegroundColor Yellow
$unusualDirs = Get-ChildItem -Path $workspaceRoot -Recurse -Directory -ErrorAction SilentlyContinue | 
    Where-Object { $_.Name -eq "Program Files" -or $_.Name -like "*Adobe*" }
foreach ($dir in $unusualDirs) {
    Remove-ItemSafe -Path $dir.FullName -Type "Unusual"
}
Write-Host ""

# 5. Remove node_modules (can be reinstalled)
Write-Host "[5/6] Removing node_modules directories..." -ForegroundColor Yellow
$nodeModules = Get-ChildItem -Path $workspaceRoot -Recurse -Directory -ErrorAction SilentlyContinue | 
    Where-Object { $_.Name -eq "node_modules" }
foreach ($dir in $nodeModules) {
    Remove-ItemSafe -Path $dir.FullName -Type "NodeModules"
}
Write-Host ""

# 6. Remove virtual environments (can be recreated)
Write-Host "[6/6] Removing virtual environments..." -ForegroundColor Yellow
$venvDirs = Get-ChildItem -Path $workspaceRoot -Recurse -Directory -ErrorAction SilentlyContinue | 
    Where-Object { $_.Name -in @("venv", ".venv", "env", ".env") -and $_.Parent.Name -ne "consolidated-workspace" }
foreach ($dir in $venvDirs) {
    # Skip if it's actually a .env file location
    if ($dir.Name -eq ".env" -and (Test-Path (Join-Path $dir.FullName ".env"))) {
        continue
    }
    Remove-ItemSafe -Path $dir.FullName -Type "Venv"
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cleanup Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "This was a DRY RUN. No files were actually removed." -ForegroundColor Yellow
    Write-Host "Run without -DryRun to perform actual cleanup." -ForegroundColor Yellow
} else {
    Write-Host "Files/Directories removed: $removedCount" -ForegroundColor Green
    Write-Host "Space freed: $([math]::Round($removedSize / 1MB, 2)) MB" -ForegroundColor Green
}
Write-Host ""

