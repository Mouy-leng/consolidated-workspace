# XM Demo Trading Controller
# Integrates XM testing with existing FBS trading system

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("setup", "test", "compare", "status", "report")]
    [string]$Action = "status"
)

# Set console to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "🦊 $Title" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Gray
}

function Test-XMDemoSetup {
    Write-Header "XM DEMO SETUP STATUS"
    
    # Check if XM demo config exists
    $configPath = "xm_demo_config.json"
    if (Test-Path $configPath) {
        $config = Get-Content $configPath -Raw | ConvertFrom-Json
        Write-Host "✅ XM Demo Configuration Found" -ForegroundColor Green
        Write-Host "   📅 Setup Date: $($config.setup_date)" -ForegroundColor Gray
        Write-Host "   🔑 Demo Login: $($config.xm_demo.login)" -ForegroundColor Gray
        Write-Host "   💰 Demo Balance: $($config.xm_demo.balance)" -ForegroundColor Gray
        Write-Host "   📊 Leverage: $($config.xm_demo.leverage)" -ForegroundColor Gray
        return $true
    }
    else {
        Write-Host "❌ XM Demo Not Configured" -ForegroundColor Red
        Write-Host "   Run: .\xm-trading-controller.ps1 -Action setup" -ForegroundColor Yellow
        return $false
    }
}

function Start-XMDemoSetup {
    Write-Header "XM DEMO ACCOUNT SETUP"
    
    Write-Host "🎯 QUICK SETUP GUIDE:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1️⃣  VISIT XM DEMO REGISTRATION"
    Write-Host "   🌐 https://www.xm.com/register/demo" -ForegroundColor Blue
    Write-Host ""
    Write-Host "2️⃣  RECOMMENDED SETTINGS:"
    Write-Host "   ✅ Account Type: Standard Account" -ForegroundColor Green
    Write-Host "   ✅ Platform: MT4 (same as FBS for comparison)" -ForegroundColor Green
    Write-Host "   ✅ Leverage: 1:888 (high leverage)" -ForegroundColor Green
    Write-Host "   ✅ Base Currency: USD" -ForegroundColor Green
    Write-Host "   ✅ Demo Balance: $10,000" -ForegroundColor Green
    Write-Host ""
    Write-Host "3️⃣  AFTER REGISTRATION:"
    Write-Host "   📧 Check email for login details" -ForegroundColor Cyan
    Write-Host "   💾 Download MetaTrader 4" -ForegroundColor Cyan
    Write-Host "   🔑 Save login credentials" -ForegroundColor Cyan
    Write-Host ""
    
    $continue = Read-Host "Have you completed XM demo registration? (y/n)"
    if ($continue -eq 'y' -or $continue -eq 'yes') {
        Write-Host ""
        Write-Host "🚀 Starting XM demo configuration..." -ForegroundColor Green
        python xm-demo-setup.py
    }
    else {
        Write-Host "📋 Complete registration first, then run setup again" -ForegroundColor Yellow
    }
}

function Start-BrokerComparison {
    Write-Header "BROKER COMPARISON TESTING"
    
    # Check if both FBS and XM are configured
    $fbsRunning = Get-Process | Where-Object { $_.ProcessName -eq "python" -and $_.Id -eq 20264 }
    $xmConfigured = Test-Path "xm_demo_config.json"
    
    Write-Host "📊 SYSTEM STATUS:" -ForegroundColor Yellow
    if ($fbsRunning) {
        Write-Host "   ✅ FBS Trading System: RUNNING (PID: 20264)" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ FBS Trading System: NOT RUNNING" -ForegroundColor Red
    }
    
    if ($xmConfigured) {
        Write-Host "   ✅ XM Demo Account: CONFIGURED" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ XM Demo Account: NOT CONFIGURED" -ForegroundColor Red
        Write-Host "   Run: .\xm-trading-controller.ps1 -Action setup" -ForegroundColor Yellow
        return
    }
    
    if ($fbsRunning -and $xmConfigured) {
        Write-Host ""
        Write-Host "🎯 STARTING BROKER COMPARISON..." -ForegroundColor Green
        python xm-demo-setup.py
    }
    else {
        Write-Host ""
        Write-Host "⚠️  Please ensure both systems are ready before comparison" -ForegroundColor Yellow
    }
}

function Show-SystemStatus {
    Write-Header "TRADING SYSTEM STATUS"
    
    # FBS System Status
    Write-Host "📈 FBS LIVE TRADING:" -ForegroundColor Yellow
    $fbsProcess = Get-Process | Where-Object { $_.ProcessName -eq "python" -and $_.Id -eq 20264 }
    if ($fbsProcess) {
        $runtime = (Get-Date) - $fbsProcess.StartTime
        Write-Host "   ✅ Status: RUNNING" -ForegroundColor Green
        Write-Host "   🔍 PID: $($fbsProcess.Id)" -ForegroundColor Gray
        Write-Host "   ⏱️  Runtime: $($runtime.Hours)h $($runtime.Minutes)m" -ForegroundColor Gray
        Write-Host "   💰 Account: 241926287 ($47.79)" -ForegroundColor Gray
    }
    else {
        Write-Host "   ❌ Status: STOPPED" -ForegroundColor Red
        Write-Host "   🔧 Start with: python micro-account-trader.py" -ForegroundColor Yellow
    }
    
    Write-Host ""
    
    # XM Demo Status
    Write-Host "🦊 XM DEMO TRADING:" -ForegroundColor Yellow
    if (Test-Path "xm_demo_config.json") {
        $config = Get-Content "xm_demo_config.json" -Raw | ConvertFrom-Json
        Write-Host "   ✅ Status: CONFIGURED" -ForegroundColor Green
        Write-Host "   🔑 Demo Login: $($config.xm_demo.login)" -ForegroundColor Gray
        Write-Host "   💰 Demo Balance: $($config.xm_demo.balance)" -ForegroundColor Gray
        Write-Host "   📊 Leverage: $($config.xm_demo.leverage)" -ForegroundColor Gray
        
        # Check for test results
        if ($config.test_results.spreads -or $config.test_results.execution_time) {
            Write-Host "   📋 Test Results: AVAILABLE" -ForegroundColor Green
        }
        else {
            Write-Host "   📋 Test Results: NO TESTS RUN" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "   ❌ Status: NOT CONFIGURED" -ForegroundColor Red
        Write-Host "   🔧 Setup with: .\xm-trading-controller.ps1 -Action setup" -ForegroundColor Yellow
    }
    
    Write-Host ""
    
    # Device Status
    Write-Host "💾 DEVICE STATUS:" -ForegroundColor Yellow
    $usbDrive = Get-Volume | Where-Object { $_.DriveLetter -eq 'I' -and $_.FileSystemLabel -eq 'BLUEDIM' }
    if ($usbDrive) {
        $freeSpace = [math]::Round($usbDrive.SizeRemaining / 1GB, 2)
        $totalSpace = [math]::Round($usbDrive.Size / 1GB, 2)
        Write-Host "   ✅ USB Drive I: CONNECTED ($freeSpace GB free / $totalSpace GB)" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ USB Drive I: NOT DETECTED" -ForegroundColor Red
    }
    
    # Crypto Wallet Status
    Write-Host "   🔍 Crypto Wallets: SCANNING..." -ForegroundColor Gray
    $walletCount = 0
    
    # Quick check for MetaMask
    $metamaskPath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Local Extension Settings\nkbihfbeogaeaoehlefnkodbefgpgknn"
    if (Test-Path $metamaskPath) {
        Write-Host "   🦊 MetaMask: DETECTED" -ForegroundColor Green
        $walletCount++
    }
    
    if ($walletCount -eq 0) {
        Write-Host "   ❌ Crypto Wallets: NONE DETECTED" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # Broker Analysis Status
    Write-Host "🏆 BROKER ANALYSIS:" -ForegroundColor Yellow
    $brokerAnalysis = Get-ChildItem -Filter "broker_analysis_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($brokerAnalysis) {
        Write-Host "   ✅ Latest Analysis: $($brokerAnalysis.Name)" -ForegroundColor Green
        Write-Host "   📅 Date: $($brokerAnalysis.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor Gray
        Write-Host "   🥇 Top Recommendation: Interactive Brokers (91.3/100)" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ No broker analysis found" -ForegroundColor Red
    }
}

function Generate-ComparisonReport {
    Write-Header "GENERATING COMPARISON REPORT"
    
    if (Test-Path "xm_demo_config.json") {
        Write-Host "📊 Generating comprehensive broker comparison..." -ForegroundColor Green
        python xm-demo-setup.py
        
        # Also show recent files
        Write-Host ""
        Write-Host "📄 RECENT REPORTS:" -ForegroundColor Yellow
        
        $xmReports = Get-ChildItem -Filter "xm_fbs_comparison_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 3
        foreach ($report in $xmReports) {
            Write-Host "   📋 $($report.Name) - $($report.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor Gray
        }
        
        $brokerReports = Get-ChildItem -Filter "broker_analysis_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 3
        foreach ($report in $brokerReports) {
            Write-Host "   🏆 $($report.Name) - $($report.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "❌ XM demo not configured. Run setup first." -ForegroundColor Red
    }
}

function Show-QuickActions {
    Write-Host ""
    Write-Host "🚀 QUICK ACTIONS:" -ForegroundColor Cyan
    Write-Host "   1. Setup XM Demo:     .\xm-trading-controller.ps1 -Action setup" -ForegroundColor White
    Write-Host "   2. Test Comparison:   .\xm-trading-controller.ps1 -Action test" -ForegroundColor White
    Write-Host "   3. Generate Report:   .\xm-trading-controller.ps1 -Action report" -ForegroundColor White
    Write-Host "   4. Check Status:      .\xm-trading-controller.ps1 -Action status" -ForegroundColor White
    Write-Host "   5. Broker Analysis:   .\broker-dashboard.ps1" -ForegroundColor White
    Write-Host ""
}

# Main execution
switch ($Action) {
    "setup" {
        Start-XMDemoSetup
    }
    "test" {
        Start-BrokerComparison
    }
    "compare" {
        Start-BrokerComparison
    }
    "status" {
        Show-SystemStatus
        Show-QuickActions
    }
    "report" {
        Generate-ComparisonReport
    }
    default {
        Show-SystemStatus
        Show-QuickActions
    }
}