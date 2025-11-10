# Trading System Training Launcher

Write-Host "Trading System Training Platform" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

Write-Host "`nAvailable Training Modules:" -ForegroundColor Yellow
Write-Host "1. Complete Trading Course" -ForegroundColor White
Write-Host "2. Advanced Strategies" -ForegroundColor White  
Write-Host "3. Practice Scenarios" -ForegroundColor White
Write-Host "4. System Usage Training" -ForegroundColor White

$choice = Read-Host "`nSelect training module (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`nStarting Complete Trading Course..." -ForegroundColor Green
        python training/trading-trainer.py
    }
    "2" {
        Write-Host "`nStarting Advanced Strategies..." -ForegroundColor Green
        python training/modules/advanced-strategies.py
    }
    "3" {
        Write-Host "`nStarting Practice Scenarios..." -ForegroundColor Green
        python training/exercises/practice-scenarios.py
    }
    "4" {
        Write-Host "`nSystem Usage Training:" -ForegroundColor Green
        Write-Host "1. Run signal generator: python trading-signal-generator.py" -ForegroundColor White
        Write-Host "2. Run MT4 bot: python mt4-fbs-setup/mt4-trading-bot.py" -ForegroundColor White
        Write-Host "3. Check system status: python ci/ci-status.py" -ForegroundColor White
    }
    default {
        Write-Host "Invalid choice. Please select 1-4." -ForegroundColor Red
    }
}

Write-Host "`nTraining session complete!" -ForegroundColor Cyan