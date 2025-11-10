# Create GitHub Repository and Push
# This script helps create the repository on GitHub and push the code

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Create GitHub Repository" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if GitHub CLI is available
$ghAvailable = Get-Command gh -ErrorAction SilentlyContinue

if ($ghAvailable) {
    Write-Host "GitHub CLI found. Creating repository..." -ForegroundColor Yellow
    
    # Check if logged in
    $ghAuth = gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Not logged in to GitHub CLI. Please login:" -ForegroundColor Yellow
        Write-Host "  gh auth login" -ForegroundColor White
        exit 1
    }
    
    # Create repository
    Write-Host "Creating repository: consolidated-workspace" -ForegroundColor Cyan
    gh repo create consolidated-workspace --private --description "Consolidated workspace for all trading system projects" --source=. --remote=origin --push 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✓ Repository created and code pushed!" -ForegroundColor Green
        Write-Host "Repository URL: https://github.com/genxapitrading/consolidated-workspace" -ForegroundColor Cyan
    } else {
        Write-Host "✗ Failed to create repository via CLI" -ForegroundColor Red
        Write-Host "Please create it manually on GitHub" -ForegroundColor Yellow
    }
} else {
    Write-Host "GitHub CLI not found. Please create repository manually:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Go to: https://github.com/new" -ForegroundColor White
    Write-Host "2. Repository name: consolidated-workspace" -ForegroundColor White
    Write-Host "3. Description: Consolidated workspace for all trading system projects" -ForegroundColor White
    Write-Host "4. Visibility: Private (recommended)" -ForegroundColor White
    Write-Host "5. DO NOT initialize with README, .gitignore, or license" -ForegroundColor White
    Write-Host "6. Click 'Create repository'" -ForegroundColor White
    Write-Host ""
    Write-Host "After creating, run: .\push-to-github.ps1" -ForegroundColor Cyan
    
    Start-Process "https://github.com/new"
}

Write-Host ""

