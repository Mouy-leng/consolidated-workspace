#!/usr/bin/env powershell
<#
.SYNOPSIS
Deep Crypto Wallet Search
.DESCRIPTION
Performs an exhaustive search for crypto wallet files across the entire system
#>

Write-Host "🕵️ DEEP CRYPTO WALLET SEARCH" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor DarkCyan
Write-Host "🔍 Searching entire system for crypto wallet files..." -ForegroundColor Yellow
Write-Host ""

$results = @()
$searchLocations = @()

function Search-CryptoFiles {
    param($path, $description)
    
    Write-Host "🔍 Searching: $description" -ForegroundColor Gray
    
    if (Test-Path $path) {
        try {
            # Search for wallet files
            $walletFiles = Get-ChildItem -Path $path -Recurse -Force -ErrorAction SilentlyContinue | Where-Object {
                $_.Name -match "(wallet|seed|mnemonic|private|crypto|bitcoin|ethereum|btc|eth)" -or
                $_.Extension -in @(".dat", ".wallet", ".key", ".json", ".txt", ".backup") -and
                $_.Name -match "(wallet|crypto|key|seed|mnemonic|private)"
            }
            
            foreach ($file in $walletFiles) {
                if ($file.Length -gt 0 -and $file.Length -lt 50MB) {
                    # Skip very large files
                    $results += [PSCustomObject]@{
                        Name     = $file.Name
                        Path     = $file.FullName
                        Size     = $file.Length
                        Modified = $file.LastWriteTime
                        Location = $description
                    }
                }
            }
        }
        catch {
            Write-Host "  ⚠️ Access denied: $path" -ForegroundColor Red
        }
    }
}

function Search-BrowserExtensions {
    Write-Host "🌐 Searching browser extensions..." -ForegroundColor Cyan
    
    # Chrome extensions
    $chromeExt = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Local Extension Settings"
    if (Test-Path $chromeExt) {
        $extensions = Get-ChildItem $chromeExt -ErrorAction SilentlyContinue
        foreach ($ext in $extensions) {
            if ($ext.Name -match "(nkbihfbeogaeaoehlefnkodbefgpgknn|fhbohimaelbohpjbbldcngcnapndodjp|bfnaelmomeimhlpmgjnjophhpkkoljpa)") {
                $walletType = switch ($ext.Name) {
                    "nkbihfbeogaeaoehlefnkodbefgpgknn" { "MetaMask" }
                    "fhbohimaelbohpjbbldcngcnapndodjp" { "Phantom" }
                    "bfnaelmomeimhlpmgjnjophhpkkoljpa" { "Solflare" }
                    default { "Unknown Wallet" }
                }
                
                $results += [PSCustomObject]@{
                    Name     = "$walletType Extension Data"
                    Path     = $ext.FullName
                    Size     = (Get-ChildItem $ext.FullName -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
                    Modified = $ext.LastWriteTime
                    Location = "Chrome Extension"
                }
            }
        }
    }
    
    # Edge extensions
    $edgeExt = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Local Extension Settings"
    if (Test-Path $edgeExt) {
        $extensions = Get-ChildItem $edgeExt -ErrorAction SilentlyContinue
        foreach ($ext in $extensions) {
            if ($ext.Name -match "(nkbihfbeogaeaoehlefnkodbefgpgknn|fhbohimaelbohpjbbldcngcnapndodjp)") {
                $results += [PSCustomObject]@{
                    Name     = "MetaMask Edge Extension"
                    Path     = $ext.FullName
                    Size     = (Get-ChildItem $ext.FullName -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
                    Modified = $ext.LastWriteTime
                    Location = "Edge Extension"
                }
            }
        }
    }
}

function Search-TextFiles {
    Write-Host "📝 Searching text files for seed phrases..." -ForegroundColor Cyan
    
    $textLocations = @(
        "$env:USERPROFILE\Desktop",
        "$env:USERPROFILE\Documents", 
        "$env:USERPROFILE\Downloads",
        "$env:USERPROFILE\OneDrive",
        "$env:USERPROFILE\Dropbox"
    )
    
    foreach ($location in $textLocations) {
        if (Test-Path $location) {
            try {
                $textFiles = Get-ChildItem -Path $location -Recurse -Include "*.txt", "*.doc*", "*.rtf" -ErrorAction SilentlyContinue
                foreach ($file in $textFiles) {
                    if ($file.Length -lt 10MB) {
                        # Only check smaller text files
                        try {
                            $content = Get-Content $file.FullName -TotalCount 50 -ErrorAction SilentlyContinue
                            if ($content -and ($content -join " ") -match "(seed phrase|mnemonic|private key|wallet|bitcoin|ethereum|recovery|backup)") {
                                $results += [PSCustomObject]@{
                                    Name     = $file.Name
                                    Path     = $file.FullName
                                    Size     = $file.Length
                                    Modified = $file.LastWriteTime
                                    Location = "Text File (potential seed/key)"
                                }
                            }
                        }
                        catch { }
                    }
                }
            }
            catch { }
        }
    }
}

# Main search execution
Write-Host "🔍 Starting comprehensive search..." -ForegroundColor Yellow

# Search common locations
Search-CryptoFiles "$env:APPDATA" "AppData Roaming"
Search-CryptoFiles "$env:LOCALAPPDATA" "AppData Local"
Search-CryptoFiles "$env:USERPROFILE\Desktop" "Desktop"
Search-CryptoFiles "$env:USERPROFILE\Documents" "Documents"
Search-CryptoFiles "$env:USERPROFILE\Downloads" "Downloads"

# Search specific wallet locations
$walletPaths = @(
    @{Path = "$env:APPDATA\Bitcoin"; Desc = "Bitcoin Core" },
    @{Path = "$env:APPDATA\Electrum"; Desc = "Electrum" },
    @{Path = "$env:APPDATA\Exodus"; Desc = "Exodus" },
    @{Path = "$env:APPDATA\atomic"; Desc = "Atomic Wallet" },
    @{Path = "$env:APPDATA\Ethereum"; Desc = "Ethereum" },
    @{Path = "$env:LOCALAPPDATA\Programs\Exodus"; Desc = "Exodus (Local)" },
    @{Path = "$env:LOCALAPPDATA\trust-wallet"; Desc = "Trust Wallet" }
)

foreach ($wallet in $walletPaths) {
    Search-CryptoFiles $wallet.Path $wallet.Desc
}

# Search browser extensions
Search-BrowserExtensions

# Search text files
Search-TextFiles

# Search USB drives and external storage
Write-Host "💾 Searching external drives..." -ForegroundColor Cyan
$drives = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DriveType -eq 2 -or $_.DriveType -eq 3 }
foreach ($drive in $drives) {
    if ($drive.DeviceID -ne "C:" -and (Test-Path $drive.DeviceID)) {
        Search-CryptoFiles $drive.DeviceID "External Drive ($($drive.DeviceID))"
    }
}

# Display results
Write-Host ""
Write-Host "📊 SEARCH RESULTS:" -ForegroundColor Green
Write-Host "-" * 50 -ForegroundColor DarkGreen

if ($results.Count -eq 0) {
    Write-Host "❌ No crypto wallet files found in deep search" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 SUGGESTIONS:" -ForegroundColor Yellow
    Write-Host "   1. Check if you have crypto wallets on mobile devices" -ForegroundColor White
    Write-Host "   2. Look for hardware wallets (Ledger, Trezor)" -ForegroundColor White
    Write-Host "   3. Check cloud storage (Google Drive, Dropbox, OneDrive)" -ForegroundColor White
    Write-Host "   4. Look for exchange account details (Binance, Coinbase, etc.)" -ForegroundColor White
    Write-Host "   5. Check for paper wallets or written seed phrases" -ForegroundColor White
}
else {
    Write-Host "✅ Found $($results.Count) potential crypto wallet files:" -ForegroundColor Green
    Write-Host ""
    
    $results | Sort-Object Modified -Descending | Format-Table -AutoSize -Wrap
    
    Write-Host ""
    Write-Host "🎯 NEXT STEPS:" -ForegroundColor Cyan
    Write-Host "   1. Review each file above carefully" -ForegroundColor White
    Write-Host "   2. Copy important files to I:\CryptoWalletBackup\2025-10-31_20-05-47\" -ForegroundColor White
    Write-Host "   3. Verify file contents before backing up" -ForegroundColor White
    Write-Host "   4. Update the inventory.txt file with details" -ForegroundColor White
}

# Save results
$searchResults = @{
    timestamp         = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    search_complete   = $true
    files_found       = $results.Count
    potential_wallets = $results
}

$searchResults | ConvertTo-Json -Depth 3 | Out-File "crypto_wallet_deep_search.json" -Encoding UTF8

Write-Host ""
Write-Host "💾 Deep search results saved to: crypto_wallet_deep_search.json" -ForegroundColor Green
Write-Host "🎉 DEEP SEARCH COMPLETE!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor DarkCyan