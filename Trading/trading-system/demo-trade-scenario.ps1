# Demo Trading Scenario
# Shows how a trade would be executed step-by-step

Write-Host "🎯 DEMO TRADE EXECUTION SCENARIO" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Simulate a trading signal
$DemoSignal = @{
    Symbol     = "XAUUSD"
    Action     = "BUY"
    Entry      = 2650.50
    StopLoss   = 2635.00
    TakeProfit = 2680.50
    Reason     = "RSI Oversold + MACD Bullish Crossover"
    Confidence = "HIGH"
    RiskReward = "1:2"
    Timestamp  = Get-Date
}

Write-Host "📊 GENERATED SIGNAL:" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host "Symbol: $($DemoSignal.Symbol)" -ForegroundColor White
Write-Host "Action: $($DemoSignal.Action)" -ForegroundColor Green
Write-Host "Entry Price: $($DemoSignal.Entry)" -ForegroundColor White
Write-Host "Stop Loss: $($DemoSignal.StopLoss)" -ForegroundColor Red
Write-Host "Take Profit: $($DemoSignal.TakeProfit)" -ForegroundColor Green
Write-Host "Setup: $($DemoSignal.Reason)" -ForegroundColor White
Write-Host "Confidence: $($DemoSignal.Confidence)" -ForegroundColor Yellow
Write-Host "Risk/Reward: $($DemoSignal.RiskReward)" -ForegroundColor White
Write-Host "Time: $($DemoSignal.Timestamp.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Gray
Write-Host ""

Write-Host "💰 RISK CALCULATION:" -ForegroundColor Yellow
$AccountBalance = 1000  # Example balance
$RiskPercent = 2
$RiskAmount = $AccountBalance * ($RiskPercent / 100)
$RiskDistance = $DemoSignal.Entry - $DemoSignal.StopLoss
$PositionSize = $RiskAmount / $RiskDistance

Write-Host "Account Balance: $AccountBalance" -ForegroundColor White
Write-Host "Risk Percentage: $RiskPercent%" -ForegroundColor White
Write-Host "Risk Amount: $($RiskAmount.ToString('F2'))" -ForegroundColor White
Write-Host "Risk Distance: $($RiskDistance.ToString('F2'))" -ForegroundColor White
Write-Host "Suggested Position Size: $($PositionSize.ToString('F2'))" -ForegroundColor White
Write-Host ""

Write-Host "🎯 EXECUTION STEPS FOR MT5:" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host "1. Open MT5 Terminal (Account: 40933270)" -ForegroundColor White
Write-Host "2. Find XAUUSD in Market Watch" -ForegroundColor White
Write-Host "3. Right-click → Trading → New Order (or F9)" -ForegroundColor White
Write-Host "4. Set parameters:" -ForegroundColor White
Write-Host "   • Type: Market Execution" -ForegroundColor Gray
Write-Host "   • Action: BUY" -ForegroundColor Gray
Write-Host "   • Volume: $($PositionSize.ToString('F2')) lots" -ForegroundColor Gray
Write-Host "   • Stop Loss: $($DemoSignal.StopLoss)" -ForegroundColor Gray
Write-Host "   • Take Profit: $($DemoSignal.TakeProfit)" -ForegroundColor Gray
Write-Host "5. Click 'Buy by Market'" -ForegroundColor White
Write-Host "6. Confirm execution" -ForegroundColor White
Write-Host ""

Write-Host "📈 EXPECTED OUTCOMES:" -ForegroundColor Green
Write-Host "====================" -ForegroundColor Green
$WinAmount = ($DemoSignal.TakeProfit - $DemoSignal.Entry) * $PositionSize
$LossAmount = ($DemoSignal.Entry - $DemoSignal.StopLoss) * $PositionSize

Write-Host "If Take Profit hit: +$($WinAmount.ToString('F2'))" -ForegroundColor Green
Write-Host "If Stop Loss hit: -$($LossAmount.ToString('F2'))" -ForegroundColor Red
Write-Host "Risk/Reward maintained: 1:2" -ForegroundColor Yellow
Write-Host ""

Write-Host "⚠️  SAFETY REMINDERS:" -ForegroundColor Red
Write-Host "=====================" -ForegroundColor Red
Write-Host "🚨 This is a DEMONSTRATION only" -ForegroundColor Red
Write-Host "🚨 Always verify signals manually" -ForegroundColor Red
Write-Host "🚨 Never risk more than 2% per trade" -ForegroundColor Red
Write-Host "🚨 Use stop losses on every trade" -ForegroundColor Red
Write-Host "🚨 Paper trade first if unsure" -ForegroundColor Red
Write-Host ""

Write-Host "🎓 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "==============" -ForegroundColor Cyan
Write-Host "1. Review the signal quality and market conditions" -ForegroundColor White
Write-Host "2. Confirm the setup matches your trading plan" -ForegroundColor White
Write-Host "3. Check economic calendar for news events" -ForegroundColor White
Write-Host "4. Execute manually if all conditions are met" -ForegroundColor White
Write-Host "5. Document the trade for learning purposes" -ForegroundColor White