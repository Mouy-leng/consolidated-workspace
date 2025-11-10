# Configure Trading Analysis System

param(
    [string]$ConfigType = "basic",
    [switch]$Interactive = $true,
    [switch]$AdvancedSetup = $false
)

Write-Host "⚙️  Configuring Trading Analysis System" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# Ensure we're in the right directory
if (-not (Test-Path "trading-analysis")) {
    Write-Host "❌ trading-analysis directory not found" -ForegroundColor Red
    Write-Host "Please run .\install-analysis-tools.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Create configuration directory if it doesn't exist
$configDir = "trading-analysis\config"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

Write-Host "`n📋 Configuration Setup:" -ForegroundColor Yellow

if ($Interactive) {
    Write-Host "`n🎯 Trading Analysis Preferences:" -ForegroundColor Cyan
    
    # Symbol preferences
    Write-Host "`nSelect your preferred currency pairs (comma-separated):" -ForegroundColor Yellow
    Write-Host "Examples: EURUSD,GBPUSD,USDJPY or leave blank for defaults" -ForegroundColor Gray
    $symbolInput = Read-Host "Currency pairs"
    
    if ($symbolInput) {
        $symbols = $symbolInput -split "," | ForEach-Object { $_.Trim().ToUpper() }
    }
    else {
        $symbols = @("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "USDCHF")
    }
    
    # Timeframe preferences
    Write-Host "`nSelect your preferred timeframes:" -ForegroundColor Yellow
    Write-Host "1. Scalping (1m, 5m)" -ForegroundColor Gray
    Write-Host "2. Day Trading (15m, 30m, 1h)" -ForegroundColor Gray
    Write-Host "3. Swing Trading (4h, 1d)" -ForegroundColor Gray
    Write-Host "4. All timeframes" -ForegroundColor Gray
    $timeframeChoice = Read-Host "Choice (1-4)"
    
    switch ($timeframeChoice) {
        "1" { $timeframes = @("1m", "5m") }
        "2" { $timeframes = @("15m", "30m", "1h") }
        "3" { $timeframes = @("4h", "1d") }
        default { $timeframes = @("1m", "5m", "15m", "30m", "1h", "4h", "1d") }
    }
    
    # Risk management
    Write-Host "`nRisk Management Settings:" -ForegroundColor Yellow
    $riskPerTrade = Read-Host "Risk per trade (% of capital, default 2)"
    if (-not $riskPerTrade) { $riskPerTrade = 2 }
    
    $initialCapital = Read-Host "Initial capital for backtesting (default 10000)"
    if (-not $initialCapital) { $initialCapital = 10000 }
    
    # Analysis preferences
    Write-Host "`nAnalysis Preferences:" -ForegroundColor Yellow
    $enablePatterns = Read-Host "Enable pattern recognition? (y/n, default y)"
    $enableSmartMoney = Read-Host "Enable smart money analysis? (y/n, default y)"
    $enableML = Read-Host "Enable machine learning models? (y/n, default y)"
    
    $patternsEnabled = ($enablePatterns -ne "n")
    $smartMoneyEnabled = ($enableSmartMoney -ne "n")
    $mlEnabled = ($enableML -ne "n")
}
else {
    # Use defaults for non-interactive mode
    $symbols = @("EURUSD", "GBPUSD", "USDJPY", "AUDUSD")
    $timeframes = @("15m", "1h", "4h", "1d")
    $riskPerTrade = 2
    $initialCapital = 10000
    $patternsEnabled = $true
    $smartMoneyEnabled = $true
    $mlEnabled = $true
}

# Create main configuration
$config = @{
    "analysis"      = @{
        "symbols"     = $symbols
        "timeframes"  = $timeframes
        "indicators"  = @{
            "rsi_period"       = 14
            "rsi_oversold"     = 30
            "rsi_overbought"   = 70
            "macd_fast"        = 12
            "macd_slow"        = 26
            "macd_signal"      = 9
            "bollinger_period" = 20
            "bollinger_std"    = 2
            "ma_periods"       = @(20, 50, 100, 200)
            "stoch_k_period"   = 14
            "stoch_d_period"   = 3
        }
        "patterns"    = @{
            "enabled"              = $patternsEnabled
            "min_bars"             = 5
            "max_bars"             = 50
            "sensitivity"          = 0.7
            "min_pattern_strength" = 0.5
        }
        "smart_money" = @{
            "enabled"                      = $smartMoneyEnabled
            "order_block_strength"         = 3
            "liquidity_threshold"          = 100
            "structure_break_confirmation" = 2
            "swing_lookback"               = 5
        }
        "ml_models"   = @{
            "enabled"             = $mlEnabled
            "prediction_horizon"  = 24
            "training_split"      = 0.8
            "validation_split"    = 0.1
            "test_split"          = 0.1
            "feature_engineering" = @{
                "technical_indicators" = $true
                "time_features"        = $true
                "volatility_features"  = $true
                "volume_features"      = $true
            }
        }
    }
    "backtesting"   = @{
        "initial_capital"    = [int]$initialCapital
        "risk_per_trade"     = [float]($riskPerTrade / 100)
        "max_open_trades"    = 3
        "commission"         = 0.0003
        "slippage"           = 0.0001
        "min_trade_duration" = 1
        "max_trade_duration" = 1440
    }
    "data_sources"  = @{
        "primary"           = "yahoo_finance"
        "backup"            = "mt5"
        "news"              = "reuters"
        "economic_calendar" = "investing.com"
        "cache_duration"    = 3600
    }
    "notifications" = @{
        "enabled"  = $false
        "telegram" = @{
            "enabled"   = $false
            "bot_token" = ""
            "chat_id"   = ""
        }
        "email"    = @{
            "enabled"     = $false
            "smtp_server" = ""
            "username"    = ""
            "password"    = ""
        }
    }
    "dashboard"     = @{
        "port"              = 8501
        "theme"             = "dark"
        "auto_refresh"      = 30
        "default_symbol"    = $symbols[0]
        "default_timeframe" = $timeframes[0]
    }
}

# Save configuration
$configJson = $config | ConvertTo-Json -Depth 10
$configJson | Out-File -FilePath "$configDir\analysis-config.json" -Encoding UTF8

Write-Host "`n✅ Configuration saved successfully!" -ForegroundColor Green

# Advanced setup
if ($AdvancedSetup -or ($Interactive -and (Read-Host "`nRun advanced setup? (y/n)") -eq "y")) {
    Write-Host "`n🔧 Advanced Configuration:" -ForegroundColor Cyan
    
    # API Keys setup
    Write-Host "`n🔑 API Keys Setup (optional but recommended):" -ForegroundColor Yellow
    Write-Host "You can add these later to the .env file" -ForegroundColor Gray
    
    $envContent = @"
# Trading Analysis Environment Variables
# Copy this to .env file and fill in your API keys

# Data Sources
YAHOO_FINANCE_API_KEY=your_yahoo_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
QUANDL_API_KEY=your_quandl_key_here

# News & Sentiment Analysis
NEWS_API_KEY=your_news_api_key_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here

# Machine Learning & AI
OPENAI_API_KEY=your_openai_key_here
HUGGINGFACE_API_KEY=your_huggingface_key_here

# Database (optional)
DB_CONNECTION_STRING=your_database_connection_here

# Notifications
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Email Notifications
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here

# MT5 Connection (if using MT5 data source)
MT5_LOGIN=$($env:MT5_LOGIN)
MT5_PASSWORD=$($env:MT5_PASSWORD)
MT5_SERVER=$($env:MT5_SERVER)
"@

    $envContent | Out-File -FilePath "trading-analysis\.env.example" -Encoding UTF8
    
    # Strategy configuration
    Write-Host "`n📈 Strategy Configuration:" -ForegroundColor Yellow
    
    $strategies = @{
        "rsi_strategy"         = @{
            "enabled"    = $true
            "parameters" = @{
                "rsi_period"        = 14
                "oversold"          = 30
                "overbought"        = 70
                "risk_reward_ratio" = 2.0
                "max_position_size" = 0.1
            }
        }
        "macd_strategy"        = @{
            "enabled"    = $true
            "parameters" = @{
                "fast_period"       = 12
                "slow_period"       = 26
                "signal_period"     = 9
                "risk_reward_ratio" = 2.5
                "max_position_size" = 0.1
            }
        }
        "ma_cross_strategy"    = @{
            "enabled"    = $true
            "parameters" = @{
                "fast_ma"           = 20
                "slow_ma"           = 50
                "risk_reward_ratio" = 3.0
                "max_position_size" = 0.08
            }
        }
        "smart_money_strategy" = @{
            "enabled"    = $smartMoneyEnabled
            "parameters" = @{
                "order_block_strength_min"     = 3
                "liquidity_zone_touches_min"   = 3
                "structure_break_confirmation" = 2
                "risk_reward_ratio"            = 4.0
                "max_position_size"            = 0.05
            }
        }
    }
    
    $strategiesJson = $strategies | ConvertTo-Json -Depth 10
    $strategiesJson | Out-File -FilePath "$configDir\strategies-config.json" -Encoding UTF8
    
    Write-Host "   ✅ Strategy configuration saved" -ForegroundColor Green
    
    # ML Model configuration
    if ($mlEnabled) {
        Write-Host "`n🤖 Machine Learning Configuration:" -ForegroundColor Yellow
        
        $mlConfig = @{
            "models"              = @{
                "random_forest" = @{
                    "enabled"           = $true
                    "n_estimators"      = 100
                    "max_depth"         = 10
                    "min_samples_split" = 5
                    "min_samples_leaf"  = 2
                }
                "xgboost"       = @{
                    "enabled"          = $true
                    "n_estimators"     = 100
                    "max_depth"        = 6
                    "learning_rate"    = 0.1
                    "subsample"        = 0.8
                    "colsample_bytree" = 0.8
                }
                "lstm"          = @{
                    "enabled"         = $true
                    "lookback_period" = 60
                    "epochs"          = 100
                    "batch_size"      = 32
                    "dropout_rate"    = 0.2
                    "learning_rate"   = 0.001
                }
            }
            "feature_engineering" = @{
                "technical_indicators" = $true
                "price_features"       = $true
                "volume_features"      = $true
                "time_features"        = $true
                "volatility_features"  = $true
                "lag_features"         = @(1, 2, 3, 5, 10)
                "rolling_windows"      = @(5, 10, 20, 50)
            }
            "training"            = @{
                "test_size"               = 0.2
                "validation_size"         = 0.1
                "cross_validation_folds"  = 5
                "early_stopping_patience" = 10
                "model_selection_metric"  = "r2_score"
            }
        }
        
        $mlConfigJson = $mlConfig | ConvertTo-Json -Depth 10
        $mlConfigJson | Out-File -FilePath "$configDir\ml-config.json" -Encoding UTF8
        
        Write-Host "   ✅ ML configuration saved" -ForegroundColor Green
    }
}

# Create startup script
$startupScript = @"
#!/usr/bin/env python3
# Trading Analysis System Startup

import sys
import os
sys.path.append(os.path.dirname(__file__))

from analysis_engine.core_analysis import TradingAnalysisEngine
from strategies.strategy_framework import BacktestEngine
from ml_models.ml_framework import TradingMLModels

print("🚀 Trading Analysis System Starting...")
print("Configuration loaded from: config/analysis-config.json")

# Initialize components
analysis_engine = TradingAnalysisEngine('config/analysis-config.json')
backtest_engine = BacktestEngine()
ml_models = TradingMLModels()

print("✅ All components initialized successfully!")
print("📊 Access the dashboard at: http://localhost:8501")
"@

$startupScript | Out-File -FilePath "trading-analysis\startup.py" -Encoding UTF8

# Create requirements file
$requirements = @"
# Trading Analysis System Requirements

# Core data and analysis
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.15.0
yfinance>=0.2.0
scipy>=1.11.0

# Machine Learning
scikit-learn>=1.3.0
tensorflow>=2.13.0
xgboost>=1.7.0

# Web Dashboard
streamlit>=1.25.0
dash>=2.12.0

# Technical Analysis
ta-lib>=0.4.0

# Utilities
requests>=2.31.0
python-dotenv>=1.0.0
beautifulsoup4>=4.12.0

# Development
jupyter>=1.0.0
"@

$requirements | Out-File -FilePath "trading-analysis\requirements.txt" -Encoding UTF8

Write-Host "`n📊 Configuration Summary:" -ForegroundColor Green
Write-Host "Symbols: $($symbols -join ', ')" -ForegroundColor Gray
Write-Host "Timeframes: $($timeframes -join ', ')" -ForegroundColor Gray
Write-Host "Risk per trade: $riskPerTrade%" -ForegroundColor Gray
Write-Host "Initial capital: $initialCapital" -ForegroundColor Gray
Write-Host "Pattern recognition: $(if($patternsEnabled){'Enabled'}else{'Disabled'})" -ForegroundColor Gray
Write-Host "Smart money analysis: $(if($smartMoneyEnabled){'Enabled'}else{'Disabled'})" -ForegroundColor Gray
Write-Host "ML models: $(if($mlEnabled){'Enabled'}else{'Disabled'})" -ForegroundColor Gray

Write-Host "`n📁 Files created:" -ForegroundColor Yellow
Write-Host "   📄 config/analysis-config.json - Main configuration" -ForegroundColor Gray
Write-Host "   📄 .env.example - Environment variables template" -ForegroundColor Gray
Write-Host "   📄 requirements.txt - Python dependencies" -ForegroundColor Gray
if ($AdvancedSetup -or $Interactive) {
    Write-Host "   📄 config/strategies-config.json - Strategy parameters" -ForegroundColor Gray
    if ($mlEnabled) {
        Write-Host "   📄 config/ml-config.json - ML model configuration" -ForegroundColor Gray
    }
}

Write-Host "`n🎯 Next Steps:" -ForegroundColor Green
Write-Host "1. Copy .env.example to .env and add your API keys (optional)" -ForegroundColor Cyan
Write-Host "2. Run: .\start-analysis.ps1 to launch the system" -ForegroundColor Cyan
Write-Host "3. Open http://localhost:8501 in your browser" -ForegroundColor Cyan
Write-Host "4. Start analyzing and developing strategies!" -ForegroundColor Cyan