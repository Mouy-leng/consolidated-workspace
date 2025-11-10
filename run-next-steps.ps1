# Run Next Steps - Automated Setup
# Completes remaining setup tasks

param(
    [switch]$SkipSSH = $false,
    [switch]$SkipVenv = $false,
    [switch]$SkipMigration = $false
)

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running Next Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: SSH Key Setup
if (-not $SkipSSH) {
    Write-Host "[1/4] Setting up SSH key for GitHub..." -ForegroundColor Yellow
    
    $sshDir = "$env:USERPROFILE\.ssh"
    $privateKey = "$sshDir\id_ed25519_github"
    $publicKey = "$sshDir\id_ed25519_github.pub"
    $knownPublicKey = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICw9/G//98IiSdsfAyn2tYS0ip9rE5wB6UAV1iue4dFm genxapitrading@gmail.com"
    
    # Check if private key exists
    if (-not (Test-Path $privateKey)) {
        Write-Host "  Creating SSH key pair..." -ForegroundColor Cyan
        ssh-keygen -t ed25519 -C "genxapitrading@gmail.com" -f $privateKey -N '""' -q
        Write-Host "  ✓ SSH key pair created" -ForegroundColor Green
    } else {
        Write-Host "  ✓ SSH key already exists" -ForegroundColor Green
    }
    
    # Verify public key matches
    if (Test-Path $publicKey) {
        $currentKey = Get-Content $publicKey -Raw
        if ($currentKey.Trim() -eq $knownPublicKey.Trim()) {
            Write-Host "  ✓ Public key matches expected key" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ Public key differs from expected" -ForegroundColor Yellow
            Write-Host "  Current: $currentKey" -ForegroundColor Gray
        }
    }
    
    # Set up SSH config
    $sshConfig = "$sshDir\config"
    $configEntry = @"

Host github.com
    HostName github.com
    User git
    IdentityFile $privateKey
    IdentitiesOnly yes
"@
    
    if (Test-Path $sshConfig) {
        $content = Get-Content $sshConfig -Raw
        if ($content -notlike "*github.com*") {
            Add-Content -Path $sshConfig -Value $configEntry
            Write-Host "  ✓ Added GitHub to SSH config" -ForegroundColor Green
        }
    } else {
        Set-Content -Path $sshConfig -Value $configEntry
        Write-Host "  ✓ Created SSH config" -ForegroundColor Green
    }
    
    # Set permissions
    if (Test-Path $privateKey) {
        icacls $privateKey /inheritance:r /grant:r "$env:USERNAME:R" 2>&1 | Out-Null
        Write-Host "  ✓ Set key permissions" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "  📋 Next: Add public key to GitHub" -ForegroundColor Cyan
    Write-Host "    1. Go to: https://github.com/settings/keys" -ForegroundColor White
    Write-Host "    2. Click 'New SSH key'" -ForegroundColor White
    Write-Host "    3. Copy the public key below:" -ForegroundColor White
    if (Test-Path $publicKey) {
        Write-Host ""
        Get-Content $publicKey | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
        Write-Host ""
    }
    Write-Host ""
} else {
    Write-Host "[1/4] Skipping SSH setup" -ForegroundColor Gray
    Write-Host ""
}

# Step 2: Create Python Virtual Environment
if (-not $SkipVenv) {
    Write-Host "[2/4] Creating Python virtual environment..." -ForegroundColor Yellow
    
    $venvPath = ".venv"
    if (-not (Test-Path $venvPath)) {
        python -m venv $venvPath
        Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
        
        # Activate and install requirements
        & "$venvPath\Scripts\Activate.ps1"
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "  ✓ Virtual environment already exists" -ForegroundColor Green
    }
    Write-Host ""
} else {
    Write-Host "[2/4] Skipping virtual environment setup" -ForegroundColor Gray
    Write-Host ""
}

# Step 3: Test SSH Connection
Write-Host "[3/4] Testing SSH connection to GitHub..." -ForegroundColor Yellow
$sshTest = ssh -T git@github.com 2>&1
if ($sshTest -like "*successfully authenticated*" -or $sshTest -like "*Hi*") {
    Write-Host "  ✓ SSH connection successful" -ForegroundColor Green
    $sshWorking = $true
} else {
    Write-Host "  ⚠ SSH connection test:" -ForegroundColor Yellow
    Write-Host "    $sshTest" -ForegroundColor Gray
    Write-Host "  Note: Add the public key to GitHub first" -ForegroundColor Yellow
    $sshWorking = $false
}
Write-Host ""

# Step 4: Set up GitHub Remote
Write-Host "[4/4] Setting up GitHub remote..." -ForegroundColor Yellow
$remote = git remote -v
if ($remote) {
    Write-Host "  ✓ Remote already configured:" -ForegroundColor Green
    $remote | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
} else {
    Write-Host "  Adding remote repository..." -ForegroundColor Cyan
    git remote add origin git@github.com:genxapitrading/consolidated-workspace.git
    Write-Host "  ✓ Remote added" -ForegroundColor Green
    Write-Host ""
    Write-Host "  📋 Ready to push! Run:" -ForegroundColor Cyan
    Write-Host "     git push -u origin main" -ForegroundColor White
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Completed:" -ForegroundColor Green
if (-not $SkipSSH) { Write-Host "  • SSH key setup" -ForegroundColor White }
if (-not $SkipVenv) { Write-Host "  • Python virtual environment" -ForegroundColor White }
Write-Host "  • GitHub remote configuration" -ForegroundColor White
Write-Host ""
Write-Host "📋 Remaining:" -ForegroundColor Yellow
if (-not $sshWorking) {
    Write-Host "  1. Add SSH public key to GitHub" -ForegroundColor White
    Write-Host "     https://github.com/settings/keys" -ForegroundColor Gray
}
Write-Host "  2. Push to GitHub: git push -u origin main" -ForegroundColor White
if ($SkipMigration) {
    Write-Host "  3. Migrate projects: .\shared\scripts\migrate-projects.ps1" -ForegroundColor White
}
Write-Host ""

