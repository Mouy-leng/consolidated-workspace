# Organize workspace structure
# Creates proper directory structure and moves projects

$workspaceRoot = "E:\Code\consolidated-workspace"

Write-Host "Organizing workspace structure..." -ForegroundColor Cyan

# Create standard directories if they don't exist
$standardDirs = @(
    "projects",
    "shared",
    "shared\config",
    "shared\scripts",
    "shared\docs"
)

foreach ($dir in $standardDirs) {
    $fullPath = Join-Path $workspaceRoot $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "Created: $dir" -ForegroundColor Green
    }
}

# Move migration scripts to shared/scripts
$scripts = @(
    "migrate-projects.ps1",
    "collect-credentials.ps1",
    "setup-ssh-key.ps1",
    "cleanup-workspace.ps1",
    "organize-structure.ps1"
)

$sharedScripts = Join-Path $workspaceRoot "shared\scripts"
foreach ($script in $scripts) {
    $source = Join-Path $workspaceRoot $script
    $dest = Join-Path $sharedScripts $script
    if ((Test-Path $source) -and (-not (Test-Path $dest))) {
        Move-Item -Path $source -Destination $dest -Force
        Write-Host "Moved $script to shared/scripts" -ForegroundColor Yellow
    }
}

Write-Host "`nWorkspace structure organized!" -ForegroundColor Green

