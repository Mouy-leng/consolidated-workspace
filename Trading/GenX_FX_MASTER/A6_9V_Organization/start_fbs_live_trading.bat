@echo off
echo ========================================
echo FBS MARKETS LIVE ACCOUNT TRADING SYSTEM
echo ========================================
echo Company: FBS Markets Inc. IO
echo Login: 104818081
echo Server: FBS-Demo
echo Server IP: 167.99.81.216:443
echo Account Type: LIVE
echo Account Balance: $25.00
echo Risk per Trade: 1.0%%
echo Max Total Risk: 3.0%%
echo ========================================
echo.
echo ⚠️  LIVE ACCOUNT - REAL MONEY TRADING ⚠️
echo ========================================

echo.
echo [1/3] Creating directories...
if not exist "logs" mkdir logs
if not exist "signal_output" mkdir signal_output

echo.
echo [2/3] Starting LIVE trading system...
python fbs_live_trading_launcher.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to start LIVE trading system
    pause
    exit /b 1
)

echo.
echo [3/3] LIVE Trading System is running!
echo.
echo LIVE Trading System Status:
echo - FBS Markets Account: 104818081 (LIVE)
echo - Server: FBS-Demo (167.99.81.216:443)
echo - Auto Trading: ENABLED
echo - Account Balance: $25.00
echo - Risk Management: ACTIVE (1%% per trade)
echo - Signal Generation: ACTIVE
echo.
echo Press Ctrl+C to stop the LIVE system
echo ========================================

pause
