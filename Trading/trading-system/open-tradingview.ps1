# TradingView Quick Access Script
# Opens TradingView with your credentials info

param(
    [string]$Symbol = "XAUUSD",
    [string]$Timeframe = "15",
    [switch]$Login = $false,
    [switch]$ShowCredentials = $false
)

Write-Host "🔥 TradingView Quick Access" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

# Credentials
$Email = "Lengkundee01@gmail.com"
$Password = "Leng1234@#$01"

if ($ShowCredentials) {
    Write-Host ""
    Write-Host "📧 Email: $Email" -ForegroundColor Cyan
    Write-Host "🔑 Password: $Password" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Copy these credentials to login manually" -ForegroundColor Gray
    return
}

# Chart URLs
$ChartUrls = @{
    "XAUUSD" = "https://www.tradingview.com/chart/?symbol=OANDA%3AXAUUSD&interval=$Timeframe"
    "EURUSD" = "https://www.tradingview.com/chart/?symbol=FX%3AEURUSD&interval=$Timeframe"
    "GBPUSD" = "https://www.tradingview.com/chart/?symbol=FX%3AGBPUSD&interval=$Timeframe"
    "USDJPY" = "https://www.tradingview.com/chart/?symbol=FX%3AUSDJPY&interval=$Timeframe"
    "USDCAD" = "https://www.tradingview.com/chart/?symbol=FX%3AUSDCAD&interval=$Timeframe"
    "AUDUSD" = "https://www.tradingview.com/chart/?symbol=FX%3AAUDUSD&interval=$Timeframe"
    "BTCUSD" = "https://www.tradingview.com/chart/?symbol=BINANCE%3ABTCUSDT&interval=$Timeframe"
}

if ($Login) {
    Write-Host "🌐 Opening TradingView login page..." -ForegroundColor Cyan
    Write-Host "📧 Email: $Email" -ForegroundColor Yellow
    Write-Host "🔑 Password: [Ready to copy]" -ForegroundColor Yellow
    
    # Copy email to clipboard
    Set-Clipboard -Value $Email
    Write-Host "✅ Email copied to clipboard!" -ForegroundColor Green
    
    Start-Process "https://www.tradingview.com/accounts/signin/"
    
    Write-Host ""
    Write-Host "💡 Login Steps:" -ForegroundColor Gray
    Write-Host "1. Email is already copied - just paste it" -ForegroundColor Gray
    Write-Host "2. Password: $Password" -ForegroundColor Gray
    Write-Host "3. Complete any 2FA if required" -ForegroundColor Gray
}
else {
    if ($ChartUrls.ContainsKey($Symbol.ToUpper())) {
        $url = $ChartUrls[$Symbol.ToUpper()]
        Write-Host "📈 Opening $Symbol chart (${Timeframe}min)..." -ForegroundColor Cyan
        Start-Process $url
    }
    else {
        Write-Host "❌ Symbol '$Symbol' not found" -ForegroundColor Red
        Write-Host "Available symbols:" -ForegroundColor Yellow
        $ChartUrls.Keys | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
    }
}

Write-Host ""
Write-Host "🎯 Quick Commands:" -ForegroundColor Yellow
Write-Host "  .\open-tradingview.ps1 -Login                     # Open login page" -ForegroundColor Gray
Write-Host "  .\open-tradingview.ps1 -Symbol EURUSD             # Open EURUSD chart" -ForegroundColor Gray
Write-Host "  .\open-tradingview.ps1 -Symbol XAUUSD -Timeframe 5 # Open XAUUSD 5min" -ForegroundColor Gray
Write-Host "  .\open-tradingview.ps1 -ShowCredentials           # Show login info" -ForegroundColor Gray