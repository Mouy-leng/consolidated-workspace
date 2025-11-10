# Start Trading Analysis System

param(
    [switch]$InstallDependencies = $false,
    [switch]$Dashboard = $true,
    [switch]$Background = $false,
    [int]$Port = 8501
)

Write-Host "🚀 Starting Trading Analysis & Training System" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Check if we're in the correct directory
if (-not (Test-Path "trading-analysis")) {
    Write-Host "❌ trading-analysis directory not found" -ForegroundColor Red
    Write-Host "Please run this script from the trading-system root directory" -ForegroundColor Yellow
    exit 1
}

# Install dependencies if requested
if ($InstallDependencies) {
    Write-Host "`n📦 Installing dependencies..." -ForegroundColor Yellow
    if (Test-Path "install-analysis-tools.ps1") {
        & ".\install-analysis-tools.ps1"
    }
    else {
        Write-Host "⚠️  install-analysis-tools.ps1 not found. Skipping dependency installation." -ForegroundColor Yellow
    }
}

# Set up environment variables
Write-Host "`n🔧 Setting up environment..." -ForegroundColor Yellow

# Add Python to path if not already there
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Host "⚠️  Python not found in PATH. Please install Python 3.8+ first." -ForegroundColor Yellow
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Cyan
}

# Check required Python packages
$requiredPackages = @("streamlit", "pandas", "numpy", "plotly", "yfinance")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    try {
        python -c "import $package" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $package installed" -ForegroundColor Green
        }
        else {
            $missingPackages += $package
        }
    }
    catch {
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "`n📦 Installing missing Python packages..." -ForegroundColor Yellow
    foreach ($package in $missingPackages) {
        Write-Host "   Installing $package..." -ForegroundColor Gray
        python -m pip install $package --quiet
    }
}

# Start the dashboard
if ($Dashboard) {
    Write-Host "`n📊 Starting Trading Analysis Dashboard..." -ForegroundColor Green
    Write-Host "Dashboard will be available at: http://localhost:$Port" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the dashboard" -ForegroundColor Yellow
    Write-Host ""
    
    try {
        Set-Location "trading-analysis"
        
        if ($Background) {
            # Start in background
            $job = Start-Job -ScriptBlock {
                param($DashboardPath, $Port)
                Set-Location $DashboardPath
                python -m streamlit run dashboard.py --server.port $Port --server.headless true
            } -ArgumentList (Get-Location), $Port
            
            Write-Host "✅ Dashboard started in background (Job ID: $($job.Id))" -ForegroundColor Green
            Write-Host "Use 'Stop-Job $($job.Id)' to stop the dashboard" -ForegroundColor Gray
            
            Set-Location ..
        }
        else {
            # Start in foreground
            python -m streamlit run dashboard.py --server.port $Port
        }
        
    }
    catch {
        Write-Host "❌ Failed to start dashboard: $_" -ForegroundColor Red
        Set-Location ..
    }
}

# Start analysis engine services
Write-Host "`n⚙️  Analysis Engine Status:" -ForegroundColor Yellow

# Check if MT5 is running
$mt5Process = Get-Process -Name "terminal64" -ErrorAction SilentlyContinue
if ($mt5Process) {
    Write-Host "   ✅ MT5 Terminal: Running" -ForegroundColor Green
}
else {
    Write-Host "   ⚠️  MT5 Terminal: Not running" -ForegroundColor Yellow
}

# Check if microservice is running
$nodeProcess = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcess) {
    Write-Host "   ✅ Trading Microservice: Running" -ForegroundColor Green
}
else {
    Write-Host "   ⚠️  Trading Microservice: Not running" -ForegroundColor Yellow
}

# Check analysis data directory
if (Test-Path "trading-analysis\data") {
    $dataFiles = Get-ChildItem "trading-analysis\data" -Recurse -File
    Write-Host "   📁 Data files: $($dataFiles.Count) files available" -ForegroundColor Green
}
else {
    Write-Host "   📁 Data directory: Empty (will be populated during analysis)" -ForegroundColor Gray
}

Write-Host "`n🎯 System Ready!" -ForegroundColor Green
Write-Host "Available features:" -ForegroundColor Yellow
Write-Host "   📊 Web Dashboard: http://localhost:$Port" -ForegroundColor Cyan
Write-Host "   📈 Technical Analysis: RSI, MACD, Bollinger Bands, etc." -ForegroundColor Cyan
Write-Host "   🔍 Pattern Recognition: Double tops/bottoms, triangles, flags" -ForegroundColor Cyan
Write-Host "   🧠 Smart Money Concepts: Order blocks, liquidity zones" -ForegroundColor Cyan
Write-Host "   📋 Strategy Backtesting: RSI, MACD, MA Cross strategies" -ForegroundColor Cyan
Write-Host "   💹 Real-time Data: Live forex and crypto prices" -ForegroundColor Cyan

Write-Host "`n📚 Quick Start Guide:" -ForegroundColor Yellow
Write-Host "   1. Open http://localhost:$Port in your browser" -ForegroundColor Gray
Write-Host "   2. Select a currency pair (EURUSD, GBPUSD, etc.)" -ForegroundColor Gray
Write-Host "   3. Choose time period and interval" -ForegroundColor Gray
Write-Host "   4. Click 'Load Data' to start analysis" -ForegroundColor Gray
Write-Host "   5. Explore technical indicators and patterns" -ForegroundColor Gray
Write-Host "   6. Test strategies with backtesting" -ForegroundColor Gray

if (-not $Background) {
    Write-Host "`nPress any key to continue..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}