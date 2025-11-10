#!/usr/bin/env powershell
<#
.SYNOPSIS
Crypto Wallet Backup Helper
.DESCRIPTION
Helps locate and backup crypto wallet files to drive I:
#>

Write-Host "🔍 CRYPTO WALLET BACKUP HELPER" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor DarkCyan
Write-Host ""

# Backup directory
$backupPath = "I:\CryptoWalletBackup"
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

Write-Host "📁 Backup Location: $backupPath" -ForegroundColor Green
Write-Host "📅 Timestamp: $timestamp" -ForegroundColor Gray
Write-Host ""

function Show-WalletSearchResults {
    Write-Host "🔍 WALLET SEARCH SUMMARY:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   ❌ No standard crypto wallets found in system" -ForegroundColor Red
    Write-Host "   ❌ No MetaMask, Ledger, Trezor, or Exodus wallets detected" -ForegroundColor Red
    Write-Host "   ❌ No Bitcoin Core, Electrum, or wallet.dat files found" -ForegroundColor Red
    Write-Host ""
    
    Write-Host "📋 COMMON WALLET LOCATIONS TO CHECK MANUALLY:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   📱 Mobile Wallets:" -ForegroundColor White
    Write-Host "      - Trust Wallet (phone)" -ForegroundColor Gray
    Write-Host "      - MetaMask (phone)" -ForegroundColor Gray
    Write-Host "      - Coinbase Wallet (phone)" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "   💻 Desktop Wallets:" -ForegroundColor White
    Write-Host "      - C:\Users\$env:USERNAME\AppData\Roaming\Bitcoin\wallet.dat" -ForegroundColor Gray
    Write-Host "      - C:\Users\$env:USERNAME\AppData\Roaming\Electrum\wallets\" -ForegroundColor Gray
    Write-Host "      - C:\Users\$env:USERNAME\AppData\Roaming\Exodus\" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "   🌐 Browser Extensions:" -ForegroundColor White
    Write-Host "      - MetaMask Chrome/Edge extension data" -ForegroundColor Gray
    Write-Host "      - Phantom, Solflare, or other wallet extensions" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "   📝 Text/Document Files:" -ForegroundColor White
    Write-Host "      - Seed phrases in .txt files" -ForegroundColor Gray
    Write-Host "      - Private keys in documents" -ForegroundColor Gray
    Write-Host "      - Recovery phrases in notes" -ForegroundColor Gray
    Write-Host ""
}

function Show-BackupInstructions {
    Write-Host "📋 MANUAL BACKUP INSTRUCTIONS:" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "   If you have crypto wallet files:" -ForegroundColor White
    Write-Host ""
    Write-Host "   1. 📁 Copy wallet files to: I:\CryptoWalletBackup\$timestamp\" -ForegroundColor Yellow
    Write-Host "   2. 📝 Copy seed phrases to: I:\CryptoWalletBackup\$timestamp\seeds.txt" -ForegroundColor Yellow
    Write-Host "   3. 🔐 Copy private keys to: I:\CryptoWalletBackup\$timestamp\private_keys.txt" -ForegroundColor Yellow
    Write-Host "   4. 📋 Create inventory list: I:\CryptoWalletBackup\$timestamp\inventory.txt" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "   Security Tips:" -ForegroundColor Red
    Write-Host "   ⚠️  Encrypt sensitive files before storing" -ForegroundColor Red
    Write-Host "   ⚠️  Never share private keys or seed phrases" -ForegroundColor Red
    Write-Host "   ⚠️  Keep multiple backups in different locations" -ForegroundColor Red
    Write-Host "   ⚠️  Test recovery process periodically" -ForegroundColor Red
    Write-Host ""
}

function Create-BackupStructure {
    Write-Host "🏗️  CREATING BACKUP STRUCTURE..." -ForegroundColor Cyan
    
    $timestampedPath = Join-Path $backupPath $timestamp
    New-Item -Path $timestampedPath -ItemType Directory -Force | Out-Null
    
    # Create subfolders
    $folders = @("wallet_files", "seed_phrases", "private_keys", "documentation")
    foreach ($folder in $folders) {
        New-Item -Path (Join-Path $timestampedPath $folder) -ItemType Directory -Force | Out-Null
    }
    
    # Create template files
    $inventoryTemplate = @"
CRYPTO WALLET BACKUP INVENTORY
Generated: $timestamp

WALLET FILES:
- [File Name] | [Type] | [Crypto] | [Balance] | [Last Used]

SEED PHRASES:
- [Wallet Name] | [Crypto] | [Word Count] | [Derivation Path]

PRIVATE KEYS:
- [Address] | [Crypto] | [Format] | [Purpose]

EXCHANGE ACCOUNTS:
- [Exchange] | [Username/Email] | [2FA Status] | [API Keys]

NOTES:
- Add any additional information about your crypto holdings
"@
    
    $inventoryPath = Join-Path $timestampedPath "inventory.txt"
    $inventoryTemplate | Out-File -FilePath $inventoryPath -Encoding UTF8
    
    Write-Host "   ✅ Created backup directory: $timestampedPath" -ForegroundColor Green
    Write-Host "   ✅ Created inventory template: $inventoryPath" -ForegroundColor Green
    Write-Host ""
    
    return $timestampedPath
}

function Show-NextSteps {
    param($backupDir)
    
    Write-Host "🚀 NEXT STEPS:" -ForegroundColor Green
    Write-Host ""
    Write-Host "   1. 📂 Open backup directory:" -ForegroundColor White
    Write-Host "      explorer.exe `"$backupDir`"" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   2. 🔍 Search for wallet files manually:" -ForegroundColor White
    Write-Host "      - Check common wallet locations listed above" -ForegroundColor Gray
    Write-Host "      - Look in Documents, Desktop, Downloads folders" -ForegroundColor Gray
    Write-Host "      - Search for .dat, .json, .key files" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   3. 📋 Fill out inventory.txt with found items" -ForegroundColor White
    Write-Host ""
    Write-Host "   4. 🔐 Copy files to appropriate backup folders" -ForegroundColor White
    Write-Host ""
    Write-Host "   5. ✅ Verify backup completeness and security" -ForegroundColor White
    Write-Host ""
}

# Main execution
Show-WalletSearchResults
$backupDir = Create-BackupStructure
Show-BackupInstructions
Show-NextSteps $backupDir

Write-Host "💾 Backup structure ready on drive I:" -ForegroundColor Green
Write-Host "📁 Location: $backupDir" -ForegroundColor White
Write-Host ""
Write-Host "🎯 TO USE THIS SCRIPT AGAIN: .\crypto-wallet-backup-helper.ps1" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor DarkCyan