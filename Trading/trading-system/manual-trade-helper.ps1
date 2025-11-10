# Manual Trade Execution Helper
# Provides step-by-step guidance for placing trades

param(
    [string]$Action = "BUY",
    [decimal]$Entry = 0,
    [decimal]$StopLoss = 0,
    [decimal]$TakeProfit = 0,
    [decimal]$RiskPercent = 2,
    [string]$Symbol = "XAUUSD"
)

Write-Host "📊 MANUAL TRADE EXECUTION HELPER" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

if ($Entry -eq 0) {
    Write-Host "🎯 Usage Example:" -ForegroundColor Yellow
    Write-Host "   .\manual-trade-helper.ps1 -Action BUY -Entry 2650.50 -StopLoss 2635.00 -TakeProfit 2680.50" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🔍 Or run without parameters for current market analysis:" -ForegroundColor Yellow
    Write-Host "   .\manual-trade-helper.ps1" -ForegroundColor Gray
    Write-Host ""
    
    # Generate current signals
    Write-Host "🚀 Generating current market signals..." -ForegroundColor Cyan
    python trading-signal-generator.py
    return
}

Write-Host "📋 TRADE SETUP ANALYSIS" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

# Calculate trade metrics
$riskAmount = 1000 * ($RiskPercent / 100)  # Assuming $1000 account
$pipValue = [Math]::Abs($Entry - $StopLoss)
$rewardAmount = [Math]::Abs($TakeProfit - $Entry)
$riskRewardRatio = if ($pipValue -gt 0) { $rewardAmount / $pipValue } else { 0 }

Write-Host "📊 Trade Details:" -ForegroundColor White
Write-Host "   Symbol: $Symbol" -ForegroundColor Gray
Write-Host "   Action: $Action" -ForegroundColor Gray
Write-Host "   Entry: $Entry" -ForegroundColor Gray
Write-Host "   Stop Loss: $StopLoss" -ForegroundColor Gray
Write-Host "   Take Profit: $TakeProfit" -ForegroundColor Gray
Write-Host ""

Write-Host "💰 Risk Management:" -ForegroundColor White
Write-Host "   Risk Amount: $($riskAmount.ToString('F2'))" -ForegroundColor Gray
Write-Host "   Risk Distance: $($pipValue.ToString('F2'))" -ForegroundColor Gray
Write-Host "   Reward Distance: $($rewardAmount.ToString('F2'))" -ForegroundColor Gray
Write-Host "   Risk/Reward Ratio: 1:$($riskRewardRatio.ToString('F1'))" -ForegroundColor Gray
Write-Host ""

# Risk assessment
if ($riskRewardRatio -lt 1.5) {
    Write-Host "⚠️  WARNING: Risk/Reward ratio is below 1.5:1" -ForegroundColor Red
}
elseif ($riskRewardRatio -ge 2.0) {
    Write-Host "✅ GOOD: Risk/Reward ratio is 2:1 or better" -ForegroundColor Green
}
else {
    Write-Host "⚠️  ACCEPTABLE: Risk/Reward ratio is adequate" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📱 STEP-BY-STEP EXECUTION IN MT5:" -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Yellow
Write-Host ""

Write-Host "1️⃣ Open MT5 Terminal" -ForegroundColor Cyan
Write-Host "   • Ensure you're logged into account 40933270" -ForegroundColor Gray
Write-Host "   • Verify connection to FBS-Real server" -ForegroundColor Gray
Write-Host ""

Write-Host "2️⃣ Find $Symbol in Market Watch" -ForegroundColor Cyan
Write-Host "   • Right-click Market Watch → Symbols" -ForegroundColor Gray
Write-Host "   • Search for '$Symbol'" -ForegroundColor Gray
Write-Host "   • Add to Market Watch if not visible" -ForegroundColor Gray
Write-Host ""

Write-Host "3️⃣ Open New Order" -ForegroundColor Cyan
Write-Host "   • Right-click on $Symbol → Trading → New Order" -ForegroundColor Gray
Write-Host "   • Or press F9 key" -ForegroundColor Gray
Write-Host ""

Write-Host "4️⃣ Configure Order Parameters" -ForegroundColor Cyan
Write-Host "   • Symbol: $Symbol" -ForegroundColor Gray
Write-Host "   • Volume: Calculate based on risk (use position size calculator)" -ForegroundColor Gray
Write-Host "   • Type: Market Execution" -ForegroundColor Gray
Write-Host "   • Action: $Action" -ForegroundColor Gray
Write-Host ""

Write-Host "5️⃣ Set Stop Loss and Take Profit" -ForegroundColor Cyan
Write-Host "   • Stop Loss: $StopLoss" -ForegroundColor Gray
Write-Host "   • Take Profit: $TakeProfit" -ForegroundColor Gray
Write-Host ""

Write-Host "6️⃣ Final Verification" -ForegroundColor Cyan
Write-Host "   • Double-check all parameters" -ForegroundColor Gray
Write-Host "   • Verify position size matches risk tolerance" -ForegroundColor Gray
Write-Host "   • Confirm Stop Loss and Take Profit levels" -ForegroundColor Gray
Write-Host ""

Write-Host "7️⃣ Execute Trade" -ForegroundColor Cyan
Write-Host "   • Click 'Buy by Market' or 'Sell by Market'" -ForegroundColor Gray
Write-Host "   • Confirm execution" -ForegroundColor Gray
Write-Host ""

Write-Host "📊 POST-EXECUTION MONITORING:" -ForegroundColor Yellow
Write-Host "==============================" -ForegroundColor Yellow
Write-Host ""

Write-Host "📱 Monitor Position:" -ForegroundColor Cyan
Write-Host "   • Check 'Trade' tab for open positions" -ForegroundColor Gray
Write-Host "   • Monitor P&L in real-time" -ForegroundColor Gray
Write-Host "   • Watch for news events that might affect the trade" -ForegroundColor Gray
Write-Host ""

Write-Host "🎯 Exit Strategy:" -ForegroundColor Cyan
Write-Host "   • Let stops and targets work automatically" -ForegroundColor Gray
Write-Host "   • Consider partial profits at 1:1 risk/reward" -ForegroundColor Gray
Write-Host "   • Trail stop loss in profitable trades" -ForegroundColor Gray
Write-Host ""

Write-Host "⚠️  RISK WARNINGS:" -ForegroundColor Red
Write-Host "==================" -ForegroundColor Red
Write-Host "🚨 LIVE ACCOUNT: This is real money trading" -ForegroundColor Red
Write-Host "🚨 MAXIMUM RISK: Do not exceed 2% per trade" -ForegroundColor Red
Write-Host "🚨 STOP LOSS: Always use stop loss protection" -ForegroundColor Red
Write-Host "🚨 EMOTION CONTROL: Stick to your plan" -ForegroundColor Red
Write-Host ""

Write-Host "🎓 LEARNING OPPORTUNITY:" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host "📚 After the trade:" -ForegroundColor Cyan
Write-Host "   • Document the trade in your journal" -ForegroundColor Gray
Write-Host "   • Analyze what worked and what didn't" -ForegroundColor Gray
Write-Host "   • Review the pattern/setup quality" -ForegroundColor Gray
Write-Host "   • Plan improvements for next trades" -ForegroundColor Gray