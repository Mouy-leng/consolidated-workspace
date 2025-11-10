#!/usr/bin/env powershell
<#
.SYNOPSIS
USDT & Crypto Wallet Detector
.DESCRIPTION
Scans system for crypto wallets and provides USDT detection capabilities
#>

function Show-CryptoHeader {
    Clear-Host
    Write-Host ""
    Write-Host "🔍 CRYPTO WALLET & USDT DETECTOR" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor DarkCyan
    Write-Host "💰 Scanning for crypto wallets and USDT ERC-20..." -ForegroundColor Yellow
    Write-Host ""
}

function Test-CryptoWallets {
    Write-Host "🔍 SCANNING CRYPTO WALLETS..." -ForegroundColor Cyan
    Write-Host ""
    
    $wallets = @()
    
    # Check MetaMask Chrome
    $metamaskChrome = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Local Extension Settings\nkbihfbeogaeaoehlefnkodbefgpgknn"
    if (Test-Path $metamaskChrome) {
        $wallets += [PSCustomObject]@{
            Type         = "MetaMask Chrome"
            Status       = "✅ DETECTED"
            Path         = $metamaskChrome
            USDT_Support = "Yes"
        }
        Write-Host "   🦊 MetaMask (Chrome): ✅ DETECTED" -ForegroundColor Green
    }
    else {
        Write-Host "   🦊 MetaMask (Chrome): ❌ NOT FOUND" -ForegroundColor Red
    }
    
    # Check MetaMask Edge
    $metamaskEdge = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Local Extension Settings\nkbihfbeogaeaoehlefnkodbefgpgknn"
    if (Test-Path $metamaskEdge) {
        $wallets += [PSCustomObject]@{
            Type         = "MetaMask Edge"
            Status       = "✅ DETECTED"
            Path         = $metamaskEdge
            USDT_Support = "Yes"
        }
        Write-Host "   🦊 MetaMask (Edge): ✅ DETECTED" -ForegroundColor Green
    }
    else {
        Write-Host "   🦊 MetaMask (Edge): ❌ NOT FOUND" -ForegroundColor Red
    }
    
    # Check Ledger Live
    $ledgerPath = "$env:APPDATA\Ledger Live"
    if (Test-Path $ledgerPath) {
        $wallets += [PSCustomObject]@{
            Type         = "Ledger Live"
            Status       = "✅ DETECTED"
            Path         = $ledgerPath
            USDT_Support = "Yes"
        }
        Write-Host "   🔐 Ledger Live: ✅ DETECTED" -ForegroundColor Green
    }
    else {
        Write-Host "   🔐 Ledger Live: ❌ NOT FOUND" -ForegroundColor Red
    }
    
    # Check Trezor Suite
    $trezorPath = "$env:APPDATA\TrezorSuite"
    if (Test-Path $trezorPath) {
        $wallets += [PSCustomObject]@{
            Type         = "Trezor Suite"
            Status       = "✅ DETECTED"
            Path         = $trezorPath
            USDT_Support = "Yes"
        }
        Write-Host "   🔐 Trezor Suite: ✅ DETECTED" -ForegroundColor Green
    }
    else {
        Write-Host "   🔐 Trezor Suite: ❌ NOT FOUND" -ForegroundColor Red
    }
    
    # Check Ethereum Keystore
    $keystorePath = "$env:APPDATA\Ethereum\keystore"
    if (Test-Path $keystorePath) {
        $keystoreFiles = Get-ChildItem $keystorePath -Filter "*.json" -ErrorAction SilentlyContinue
        if ($keystoreFiles) {
            $wallets += [PSCustomObject]@{
                Type         = "Ethereum Keystore"
                Status       = "✅ DETECTED ($($keystoreFiles.Count) files)"
                Path         = $keystorePath
                USDT_Support = "Yes"
            }
            Write-Host "   📁 Ethereum Keystore: ✅ DETECTED ($($keystoreFiles.Count) files)" -ForegroundColor Green
        }
    }
    else {
        Write-Host "   📁 Ethereum Keystore: ❌ NOT FOUND" -ForegroundColor Red
    }
    
    # Check for common wallet apps
    $commonWallets = @(
        @{Name = "Exodus"; Path = "$env:APPDATA\Exodus" },
        @{Name = "Atomic Wallet"; Path = "$env:APPDATA\atomic" },
        @{Name = "Electrum"; Path = "$env:APPDATA\Electrum" },
        @{Name = "Trust Wallet"; Path = "$env:LOCALAPPDATA\trust-wallet" }
    )
    
    foreach ($wallet in $commonWallets) {
        if (Test-Path $wallet.Path) {
            $wallets += [PSCustomObject]@{
                Type         = $wallet.Name
                Status       = "✅ DETECTED"
                Path         = $wallet.Path
                USDT_Support = "Possibly"
            }
            Write-Host "   💼 $($wallet.Name): ✅ DETECTED" -ForegroundColor Green
        }
        else {
            Write-Host "   💼 $($wallet.Name): ❌ NOT FOUND" -ForegroundColor Red
        }
    }
    
    return $wallets
}

function Show-USDTInfo {
    Write-Host ""
    Write-Host "💰 USDT ERC-20 INFORMATION" -ForegroundColor Yellow
    Write-Host "-" * 30 -ForegroundColor DarkYellow
    Write-Host "   Contract: 0xdAC17F958D2ee523a2206206994597C13D831ec7" -ForegroundColor White
    Write-Host "   Network: Ethereum Mainnet" -ForegroundColor White
    Write-Host "   Decimals: 6" -ForegroundColor White
    Write-Host "   Symbol: USDT" -ForegroundColor White
    Write-Host ""
}

function Show-TradingIntegration {
    Write-Host "🔗 TRADING SYSTEM INTEGRATION" -ForegroundColor Magenta
    Write-Host "-" * 35 -ForegroundColor DarkMagenta
    Write-Host "   ✅ Device Manager: Updated for crypto wallet detection" -ForegroundColor Green
    Write-Host "   ✅ Sync System: Ready for crypto wallet sync" -ForegroundColor Green
    Write-Host "   ⚠️  USDT Balance Check: Requires Etherscan API key" -ForegroundColor Yellow
    Write-Host "   📊 Current Account: $47.79 FBS Real Trading" -ForegroundColor White
    Write-Host ""
}

function Show-NextSteps {
    Write-Host "📋 NEXT STEPS FOR USDT INTEGRATION:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   1. 🔑 Get Etherscan API Key (free):" -ForegroundColor White
    Write-Host "      https://etherscan.io/apis" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   2. 📱 Add Your Wallet Addresses:" -ForegroundColor White
    Write-Host "      Edit usdt-balance-checker.ps1" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   3. 🔄 Run USDT Balance Check:" -ForegroundColor White
    Write-Host "      .\usdt-balance-checker.ps1 -Address 0x..." -ForegroundColor Gray
    Write-Host ""
    Write-Host "   4. 📊 Integration with Trading System:" -ForegroundColor White
    Write-Host "      Crypto balances will sync with device manager" -ForegroundColor Gray
    Write-Host ""
}

# Main execution
Show-CryptoHeader

$detectedWallets = Test-CryptoWallets

Write-Host ""
Write-Host "📊 SCAN SUMMARY:" -ForegroundColor Green
Write-Host "-" * 20 -ForegroundColor DarkGreen
Write-Host "   Total Wallets Detected: $($detectedWallets.Count)" -ForegroundColor White

if ($detectedWallets.Count -gt 0) {
    Write-Host ""
    Write-Host "📋 DETECTED WALLETS:" -ForegroundColor Cyan
    $detectedWallets | Format-Table Type, Status, USDT_Support -AutoSize
}

Show-USDTInfo
Show-TradingIntegration
Show-NextSteps

# Save results
$results = @{
    timestamp        = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    detected_wallets = $detectedWallets
    total_count      = $detectedWallets.Count
}

$results | ConvertTo-Json -Depth 3 | Out-File "crypto_wallet_scan.json" -Encoding UTF8

Write-Host "💾 Results saved to: crypto_wallet_scan.json" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 CRYPTO WALLET SCAN COMPLETE!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor DarkCyan