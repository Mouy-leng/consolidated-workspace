# Fix SSH Key Format
# Ensures the SSH key is in correct OpenSSH format

$sshDir = "$env:USERPROFILE\.ssh"
$privateKey = "$sshDir\id_ed25519_github"
$publicKey = "$sshDir\id_ed25519_github.pub"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SSH Key Format Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if key exists
if (Test-Path $publicKey) {
    Write-Host "Current key found. Checking format..." -ForegroundColor Yellow
    $currentKey = (Get-Content $publicKey -Raw).Trim()
    $parts = $currentKey -split '\s+'
    
    if ($parts.Count -eq 3 -and $parts[0] -eq 'ssh-ed25519') {
        Write-Host "✓ Key format is correct" -ForegroundColor Green
        Write-Host ""
        Write-Host "Key to copy:" -ForegroundColor Cyan
        Write-Host $currentKey -ForegroundColor White
        Write-Host ""
        $currentKey | Set-Clipboard
        Write-Host "✓ Key copied to clipboard" -ForegroundColor Green
    } else {
        Write-Host "⚠ Key format issue detected. Regenerating..." -ForegroundColor Yellow
        Remove-Item $privateKey, $publicKey -Force -ErrorAction SilentlyContinue
    }
}

# Generate new key if needed
if (-not (Test-Path $privateKey)) {
    Write-Host "Generating new SSH key pair..." -ForegroundColor Yellow
    
    # Generate key with proper format
    ssh-keygen -t ed25519 -C "genxapitrading@gmail.com" -f $privateKey -N '""' -q
    
    if (Test-Path $publicKey) {
        $newKey = (Get-Content $publicKey -Raw).Trim()
        Write-Host "✓ New key generated" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your SSH Public Key (copy this):" -ForegroundColor Cyan
        Write-Host $newKey -ForegroundColor White
        Write-Host ""
        $newKey | Set-Clipboard
        Write-Host "✓ Key copied to clipboard" -ForegroundColor Green
        
        # Set permissions
        icacls $privateKey /inheritance:r /grant "${env:USERNAME}:R" 2>&1 | Out-Null
        Write-Host "✓ Permissions set" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Go to: https://github.com/settings/keys" -ForegroundColor White
Write-Host "  2. Click 'New SSH key'" -ForegroundColor White
Write-Host "  3. Title: 'Consolidated Workspace'" -ForegroundColor White
Write-Host "  4. Key type: Authentication Key" -ForegroundColor White
Write-Host "  5. Paste the key (already in clipboard)" -ForegroundColor White
Write-Host "  6. Click 'Add SSH key'" -ForegroundColor White
Write-Host ""

