@echo off
echo ========================================
echo FBS Markets GenX FX Trading System
echo ========================================
echo Company: FBS Markets Inc. IO
echo Login: 104818081
echo Server: FBS-Demo
echo Server IP: 167.99.81.216:443
echo Account Balance: $25.00
echo ========================================

echo.
echo [1/5] Updating credentials...
python credentials_master_list.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to update credentials
    pause
    exit /b 1
)

echo.
echo [2/5] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [3/5] Setting up environment...
copy "deploy\fbs-markets-config.env" ".env"
if %errorlevel% neq 0 (
    echo ERROR: Failed to setup environment
    pause
    exit /b 1
)

echo.
echo [4/5] Starting trading system...
python main.py --config config.yaml --env .env
if %errorlevel% neq 0 (
    echo ERROR: Failed to start trading system
    pause
    exit /b 1
)

echo.
echo [5/5] System is running!
echo.
echo Trading System Status:
echo - FBS Markets Account: 104818081
echo - Server: FBS-Demo (167.99.81.216:443)
echo - Auto Trading: ENABLED
echo - Account Balance: $25.00
echo - Risk Management: ACTIVE
echo.
echo Press Ctrl+C to stop the system
echo ========================================

pause
