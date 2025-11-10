# Setup SSH Key for GitHub
# Email: genxapitrading@gmail.com

$sshKey = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICw9/G//98IiSdsfAyn2tYS0ip9rE5wB6UAV1iue4dFm genxapitrading@gmail.com"
$sshDir = "$env:USERPROFILE\.ssh"
$keyFile = "$sshDir\id_ed25519_github"

Write-Host "Setting up SSH key for GitHub..." -ForegroundColor Cyan

# Create .ssh directory if it doesn't exist
if (-not (Test-Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
    Write-Host "Created .ssh directory" -ForegroundColor Green
}

# Check if key already exists
if (Test-Path $keyFile) {
    Write-Host "SSH key already exists at $keyFile" -ForegroundColor Yellow
    $overwrite = Read-Host "Overwrite? (y/N)"
    if ($overwrite -ne 'y') {
        Write-Host "Skipping key creation" -ForegroundColor Yellow
        exit
    }
}

# Note: We can't create the private key from just the public key
# The user needs to have the private key file
Write-Host ""
Write-Host "IMPORTANT: This script sets up the public key." -ForegroundColor Yellow
Write-Host "You need to have the private key file to use SSH authentication." -ForegroundColor Yellow
Write-Host ""
Write-Host "Public key to add to GitHub:" -ForegroundColor Cyan
Write-Host $sshKey
Write-Host ""

# Add to SSH config
$sshConfig = "$sshDir\config"
$configEntry = @"

Host github.com
    HostName github.com
    User git
    IdentityFile $keyFile
    IdentitiesOnly yes
"@

if (Test-Path $sshConfig) {
    $content = Get-Content $sshConfig -Raw
    if ($content -notlike "*github.com*") {
        Add-Content -Path $sshConfig -Value $configEntry
        Write-Host "Added GitHub entry to SSH config" -ForegroundColor Green
    } else {
        Write-Host "GitHub entry already exists in SSH config" -ForegroundColor Yellow
    }
} else {
    Set-Content -Path $sshConfig -Value $configEntry
    Write-Host "Created SSH config file" -ForegroundColor Green
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Copy your private key to: $keyFile" -ForegroundColor White
Write-Host "2. Set permissions: icacls `"$keyFile`" /inheritance:r /grant:r `"$env:USERNAME:R`"" -ForegroundColor White
Write-Host "3. Add the public key to GitHub: Settings > SSH and GPG keys > New SSH key" -ForegroundColor White
Write-Host "4. Test connection: ssh -T git@github.com" -ForegroundColor White

