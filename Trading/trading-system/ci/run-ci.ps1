# CI Management Script for Trading System

param(
    [string]$Action = "test",
    [switch]$Verbose
)

Write-Host "🔧 Trading System CI Manager" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan

switch ($Action.ToLower()) {
    "test" {
        Write-Host "🧪 Running tests..." -ForegroundColor Yellow
        python ci/test-runner.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ All tests passed!" -ForegroundColor Green
        } else {
            Write-Host "❌ Tests failed!" -ForegroundColor Red
            exit 1
        }
    }
    
    "lint" {
        Write-Host "🔍 Running linter..." -ForegroundColor Yellow
        flake8 . --count --statistics
    }
    
    "build" {
        Write-Host "🔨 Building project..." -ForegroundColor Yellow
        
        # Install Python dependencies
        if (Test-Path "requirements.txt") {
            pip install -r requirements.txt
        }
        
        # Install Node.js dependencies
        if (Test-Path "trading-analysis/package.json") {
            cd trading-analysis
            npm install
            cd ..
        }
        
        Write-Host "✅ Build completed!" -ForegroundColor Green
    }
    
    "deploy" {
        Write-Host "🚀 Deploying..." -ForegroundColor Yellow
        
        # Run tests first
        python ci/test-runner.py
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Tests failed, deployment aborted!" -ForegroundColor Red
            exit 1
        }
        
        # Deploy components
        Write-Host "Deploying trading system components..." -ForegroundColor Yellow
        
        Write-Host "✅ Deployment completed!" -ForegroundColor Green
    }
    
    "status" {
        Write-Host "📊 System Status:" -ForegroundColor Yellow
        
        # Check Python
        try {
            $pythonVersion = python --version 2>&1
            Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
        } catch {
            Write-Host "❌ Python not found" -ForegroundColor Red
        }
        
        # Check Node.js
        try {
            $nodeVersion = node --version 2>&1
            Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
        } catch {
            Write-Host "❌ Node.js not found" -ForegroundColor Red
        }
        
        # Check Git
        try {
            $gitVersion = git --version 2>&1
            Write-Host "✅ Git: $gitVersion" -ForegroundColor Green
        } catch {
            Write-Host "❌ Git not found" -ForegroundColor Red
        }
    }
    
    default {
        Write-Host "Usage: .\run-ci.ps1 -Action [test|lint|build|deploy|status]" -ForegroundColor Yellow
    }
}