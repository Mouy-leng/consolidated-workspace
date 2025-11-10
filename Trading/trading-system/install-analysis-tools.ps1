# Trading Analysis & Training System Installation

param(
    [switch]$InstallPython = $true,
    [switch]$InstallNodePackages = $true,
    [switch]$InstallRPackages = $false,
    [switch]$Force = $false
)

Write-Host "🔧 Installing Trading Analysis & Training Framework" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green

# Create directory structure
$directories = @(
    "analysis-engine",
    "strategies", 
    "indicators",
    "patterns",
    "smart-money",
    "backtesting",
    "ml-models",
    "data\historical",
    "data\live",
    "data\processed",
    "reports\daily",
    "reports\weekly", 
    "reports\monthly",
    "tools",
    "config",
    "logs"
)

Write-Host "`n📁 Creating directory structure..." -ForegroundColor Yellow
foreach ($dir in $directories) {
    $fullPath = Join-Path "trading-analysis" $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        Write-Host "   ✅ Created: $dir" -ForegroundColor Green
    }
    else {
        Write-Host "   📁 Exists: $dir" -ForegroundColor Gray
    }
}

# Install Python dependencies if requested
if ($InstallPython) {
    Write-Host "`n🐍 Installing Python dependencies..." -ForegroundColor Yellow
    
    $pythonPackages = @(
        "pandas>=2.0.0",
        "numpy>=1.24.0", 
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "scikit-learn>=1.3.0",
        "tensorflow>=2.13.0",
        "yfinance>=0.2.0",
        "ta-lib>=0.4.0",
        "plotly>=5.15.0",
        "dash>=2.12.0",
        "streamlit>=1.25.0",
        "scipy>=1.11.0",
        "jupyter>=1.0.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "python-dotenv>=1.0.0"
    )
    
    try {
        # Check if pip is available
        $pipVersion = python -m pip --version 2>$null
        if ($pipVersion) {
            Write-Host "   ✅ Python pip detected: $($pipVersion.Split(' ')[1])" -ForegroundColor Green
            
            foreach ($package in $pythonPackages) {
                Write-Host "   📦 Installing $package..." -ForegroundColor Gray
                python -m pip install $package --quiet
            }
            Write-Host "   ✅ Python packages installed successfully" -ForegroundColor Green
        }
        else {
            Write-Host "   ⚠️  Python pip not found. Please install Python first." -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "   ❌ Failed to install Python packages" -ForegroundColor Red
    }
}

# Install Node.js packages if requested
if ($InstallNodePackages) {
    Write-Host "`n📦 Installing Node.js dependencies..." -ForegroundColor Yellow
    
    $nodePackages = @(
        "express",
        "socket.io",
        "axios",
        "moment",
        "lodash",
        "csv-parser",
        "json2csv",
        "chart.js",
        "d3",
        "ws",
        "node-cron",
        "winston",
        "dotenv"
    )
    
    try {
        # Check if npm is available
        $npmVersion = npm --version 2>$null
        if ($npmVersion) {
            Write-Host "   ✅ NPM detected: v$npmVersion" -ForegroundColor Green
            
            # Initialize package.json in analysis directory
            Set-Location "trading-analysis"
            if (-not (Test-Path "package.json")) {
                npm init -y | Out-Null
                Write-Host "   ✅ Initialized package.json" -ForegroundColor Green
            }
            
            foreach ($package in $nodePackages) {
                Write-Host "   📦 Installing $package..." -ForegroundColor Gray
                npm install $package --silent
            }
            
            Set-Location ..
            Write-Host "   ✅ Node.js packages installed successfully" -ForegroundColor Green
        }
        else {
            Write-Host "   ⚠️  NPM not found. Please install Node.js first." -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "   ❌ Failed to install Node.js packages" -ForegroundColor Red
    }
}

# Create configuration files
Write-Host "`n⚙️  Creating configuration files..." -ForegroundColor Yellow

$configContent = @"
{
  "analysis": {
    "timeframes": ["1m", "5m", "15m", "1h", "4h", "1d"],
    "symbols": ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "USDCHF"],
    "indicators": {
      "rsi_period": 14,
      "macd_fast": 12,
      "macd_slow": 26,
      "macd_signal": 9,
      "bollinger_period": 20,
      "bollinger_std": 2,
      "ma_periods": [20, 50, 100, 200]
    },
    "patterns": {
      "min_bars": 5,
      "max_bars": 50,
      "sensitivity": 0.7
    },
    "smart_money": {
      "order_block_strength": 3,
      "liquidity_threshold": 100,
      "structure_break_confirmation": 2
    }
  },
  "backtesting": {
    "initial_capital": 10000,
    "risk_per_trade": 0.02,
    "max_trades": 1000,
    "commission": 0.0003
  },
  "ml_models": {
    "prediction_horizon": 24,
    "training_split": 0.8,
    "validation_split": 0.1,
    "test_split": 0.1
  },
  "data_sources": {
    "primary": "mt5",
    "backup": "yahoo_finance",
    "news": "reuters",
    "economic_calendar": "investing.com"
  }
}
"@

$configContent | Out-File -FilePath "trading-analysis\config\analysis-config.json" -Encoding UTF8
Write-Host "   ✅ Created analysis-config.json" -ForegroundColor Green

# Create environment template
$envTemplate = @"
# Trading Analysis Environment Variables

# MT5 Connection
MT5_LOGIN=your_mt5_login
MT5_PASSWORD=your_mt5_password
MT5_SERVER=your_mt5_server

# Data Sources
YAHOO_FINANCE_API_KEY=your_yahoo_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
QUANDL_API_KEY=your_quandl_key

# News & Sentiment
NEWS_API_KEY=your_news_api_key
TWITTER_API_KEY=your_twitter_key
REDDIT_CLIENT_ID=your_reddit_id

# Machine Learning
OPENAI_API_KEY=your_openai_key
HUGGINGFACE_API_KEY=your_huggingface_key

# Database
DB_CONNECTION_STRING=your_db_connection

# Notifications
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id
EMAIL_SMTP_SERVER=your_smtp_server
EMAIL_USERNAME=your_email
EMAIL_PASSWORD=your_email_password
"@

$envTemplate | Out-File -FilePath "trading-analysis\.env.template" -Encoding UTF8
Write-Host "   ✅ Created .env.template" -ForegroundColor Green

Write-Host "`n🎉 Installation completed successfully!" -ForegroundColor Green
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Copy .env.template to .env and configure your API keys" -ForegroundColor Gray
Write-Host "   2. Run .\configure-analysis.ps1 to setup your preferences" -ForegroundColor Gray
Write-Host "   3. Run .\start-analysis.ps1 to begin analysis" -ForegroundColor Gray
Write-Host "   4. Access the web dashboard at http://localhost:8080" -ForegroundColor Gray