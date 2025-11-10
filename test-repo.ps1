# Test Git Repository Setup
# Verifies that the repository is properly configured and secure

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Git Repository Test & Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$errors = 0
$warnings = 0

# Test 1: Check if Git is initialized
Write-Host "[1/8] Checking Git initialization..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "  ✓ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "  ✗ Git repository not found" -ForegroundColor Red
    $errors++
}
Write-Host ""

# Test 2: Check Git config
Write-Host "[2/8] Checking Git configuration..." -ForegroundColor Yellow
$userName = git config user.name
$userEmail = git config user.email
if ($userName -and $userEmail) {
    Write-Host "  ✓ User: $userName <$userEmail>" -ForegroundColor Green
} else {
    Write-Host "  ✗ Git user not configured" -ForegroundColor Red
    $errors++
}
Write-Host ""

# Test 3: Check for commits
Write-Host "[3/8] Checking commits..." -ForegroundColor Yellow
$commitCount = (git log --oneline 2>&1 | Measure-Object -Line).Lines
if ($commitCount -gt 0) {
    Write-Host "  ✓ Found $commitCount commit(s)" -ForegroundColor Green
} else {
    Write-Host "  ✗ No commits found" -ForegroundColor Red
    $errors++
}
Write-Host ""

# Test 4: Check .gitignore
Write-Host "[4/8] Checking .gitignore..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore" -Raw
    $requiredPatterns = @(".env", "credentials/", "*.secret", "*.key")
    $missing = @()
    foreach ($pattern in $requiredPatterns) {
        if ($gitignoreContent -notlike "*$pattern*") {
            $missing += $pattern
        }
    }
    if ($missing.Count -eq 0) {
        Write-Host "  ✓ .gitignore properly configured" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Missing patterns: $($missing -join ', ')" -ForegroundColor Yellow
        $warnings++
    }
} else {
    Write-Host "  ✗ .gitignore not found" -ForegroundColor Red
    $errors++
}
Write-Host ""

# Test 5: Check for sensitive files in staging
Write-Host "[5/8] Checking for sensitive files..." -ForegroundColor Yellow
$sensitiveFiles = git ls-files | Where-Object { 
    $_ -like "*.env" -or 
    $_ -like "*credentials*" -or 
    $_ -like "*.key" -or 
    $_ -like "*.secret" -or
    $_ -like "*password*" 
}
if ($sensitiveFiles.Count -eq 0) {
    Write-Host "  ✓ No sensitive files in repository" -ForegroundColor Green
} else {
    Write-Host "  ✗ Sensitive files found:" -ForegroundColor Red
    $sensitiveFiles | ForEach-Object { Write-Host "    - $_" -ForegroundColor Red }
    $errors++
}
Write-Host ""

# Test 6: Check branch name
Write-Host "[6/8] Checking branch..." -ForegroundColor Yellow
$branch = git branch --show-current
if ($branch -eq "main") {
    Write-Host "  ✓ On main branch" -ForegroundColor Green
} else {
    Write-Host "  ⚠ On branch: $branch (expected: main)" -ForegroundColor Yellow
    $warnings++
}
Write-Host ""

# Test 7: Check for remote
Write-Host "[7/8] Checking remote repository..." -ForegroundColor Yellow
$remote = git remote -v
if ($remote) {
    Write-Host "  ℹ Remote configured:" -ForegroundColor Cyan
    $remote | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
} else {
    Write-Host "  ⚠ No remote repository configured" -ForegroundColor Yellow
    Write-Host "    Run: git remote add origin <url>" -ForegroundColor Gray
    $warnings++
}
Write-Host ""

# Test 8: Check repository size
Write-Host "[8/8] Checking repository size..." -ForegroundColor Yellow
$repoSize = (Get-ChildItem -Path .git -Recurse -ErrorAction SilentlyContinue | 
    Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "  ℹ Repository size: $([math]::Round($repoSize, 2)) MB" -ForegroundColor Cyan
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
if ($errors -eq 0 -and $warnings -eq 0) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
    exit 0
} elseif ($errors -eq 0) {
    Write-Host "✓ Tests passed with $warnings warning(s)" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "✗ Tests failed with $errors error(s) and $warnings warning(s)" -ForegroundColor Red
    exit 1
}

