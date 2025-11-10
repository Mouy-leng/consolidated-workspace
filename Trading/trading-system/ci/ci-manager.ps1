# Simple CI Manager for Trading System

param([string]$Action = "status")

Write-Host "Trading System CI Manager" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

if ($Action -eq "status") {
    Write-Host "System Status:" -ForegroundColor Yellow
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "Python: Not found" -ForegroundColor Red
    }
    
    # Check Node.js
    try {
        $nodeVersion = node --version 2>&1
        Write-Host "Node.js: $nodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "Node.js: Not found" -ForegroundColor Red
    }
    
    # Run status check
    python ci/ci-status.py
}
elseif ($Action -eq "test") {
    Write-Host "Running tests..." -ForegroundColor Yellow
    python ci/simple-test.py
}
else {
    Write-Host "Usage: .\ci-manager.ps1 [status|test]" -ForegroundColor Yellow
}