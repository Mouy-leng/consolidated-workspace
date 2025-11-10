# Push repository to GitHub
# This script will push the consolidated workspace to GitHub

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pushing to GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check SSH connection
Write-Host "Testing SSH connection..." -ForegroundColor Yellow
$sshTest = ssh -T git@github.com 2>&1
if ($sshTest -like "*successfully authenticated*" -or $sshTest -like "*Hi*") {
    Write-Host "✓ SSH connection successful" -ForegroundColor Green
} else {
    Write-Host "✗ SSH connection failed" -ForegroundColor Red
    Write-Host "  Error: $sshTest" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please add your SSH key to GitHub first:" -ForegroundColor Yellow
    Write-Host "  1. Go to: https://github.com/settings/keys" -ForegroundColor White
    Write-Host "  2. Click 'New SSH key'" -ForegroundColor White
    Write-Host "  3. Paste this key:" -ForegroundColor White
    Write-Host ""
    if (Test-Path "$env:USERPROFILE\.ssh\id_ed25519_github.pub") {
        Get-Content "$env:USERPROFILE\.ssh\id_ed25519_github.pub" | ForEach-Object { Write-Host "    $_" -ForegroundColor Cyan }
    }
    Write-Host ""
    exit 1
}

Write-Host ""

# Check remote
Write-Host "Checking remote configuration..." -ForegroundColor Yellow
$remote = git remote -v
if ($remote) {
    Write-Host "✓ Remote configured:" -ForegroundColor Green
    $remote | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
} else {
    Write-Host "✗ No remote configured" -ForegroundColor Red
    Write-Host "  Adding remote..." -ForegroundColor Yellow
    git remote add origin git@github.com:genxapitrading/consolidated-workspace.git
    Write-Host "  ✓ Remote added" -ForegroundColor Green
}

Write-Host ""

# Check for uncommitted changes
Write-Host "Checking repository status..." -ForegroundColor Yellow
$status = git status --short
if ($status) {
    Write-Host "⚠ Uncommitted changes found:" -ForegroundColor Yellow
    $status | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    Write-Host ""
    $commit = Read-Host "Commit these changes? (y/N)"
    if ($commit -eq 'y') {
        git add .
        git commit -m "Update: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        Write-Host "✓ Changes committed" -ForegroundColor Green
    }
} else {
    Write-Host "✓ Working tree clean" -ForegroundColor Green
}

Write-Host ""

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
try {
    git push -u origin main
    Write-Host ""
    Write-Host "✓ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository URL: https://github.com/genxapitrading/consolidated-workspace" -ForegroundColor Cyan
} catch {
    Write-Host "✗ Push failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Ensure SSH key is added to GitHub" -ForegroundColor White
    Write-Host "  2. Check repository exists on GitHub" -ForegroundColor White
    Write-Host "  3. Verify you have push permissions" -ForegroundColor White
    exit 1
}

Write-Host ""

