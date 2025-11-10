# MT5 FBS Complete Setup Script
# Automates the entire MT5 FBS setup process

param(
    [string]$AccountType = "demo",
    [string]$Login = "",
    [string]$Password = "",
    [string]$Server = "FBS-Demo"
)

Write-Host "🏦 MT5 FBS Complete Setup" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Installing Python..." -ForegroundColor Red
    # Download and install Python
    $pythonUrl = "https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe"
    $pythonInstaller = "python-installer.exe"
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
    Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
    Remove-Item $pythonInstaller
}

# Install required packages
Write-Host "`n📦 Installing required packages..." -ForegroundColor Yellow
pip install MetaTrader5 pandas requests

# Step 1: FBS Account Setup
Write-Host "`n🏦 Step 1: FBS Account Setup" -ForegroundColor Cyan
python fbs-account-setup.py

# Step 2: Download and Install MT5
Write-Host "`n📥 Step 2: MT5 Installation" -ForegroundColor Cyan

if (-not $Login -or -not $Password) {
    $Login = Read-Host "Enter FBS Login"
    $Password = Read-Host "Enter FBS Password" -AsSecureString
    $Password = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password))
}

# Create environment variables for credentials
$env:FBS_LOGIN = $Login
$env:FBS_PASSWORD = $Password
$env:FBS_SERVER = $Server

# Run MT5 installer
python fbs-mt5-installer.py

# Step 3: Configure MT5 API
Write-Host "`n⚙️ Step 3: MT5 API Configuration" -ForegroundColor Cyan

# Test MT5 connection
Write-Host "🔌 Testing MT5 connection..." -ForegroundColor Yellow
python mt5-api-connector.py

# Step 4: Setup Trading Environment
Write-Host "`n📊 Step 4: Trading Environment Setup" -ForegroundColor Cyan

# Create trading workspace directory
$tradingDir = "$env:USERPROFILE\Documents\MT5-FBS-Trading"
New-Item -ItemType Directory -Force -Path $tradingDir | Out-Null

# Copy configuration files
Copy-Item "*.json" -Destination $tradingDir -ErrorAction SilentlyContinue
Copy-Item "*.ini" -Destination $tradingDir -ErrorAction SilentlyContinue

Write-Host "✅ Trading workspace created: $tradingDir" -ForegroundColor Green

# Step 5: Create shortcuts and startup scripts
Write-Host "`n🔗 Step 5: Creating Shortcuts" -ForegroundColor Cyan

# Create desktop shortcut for MT5
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\MT5 FBS.lnk")
$Shortcut.TargetPath = "C:\Program Files\MetaTrader 5\terminal64.exe"
$Shortcut.Arguments = "/config:$tradingDir\mt5_fbs_config.ini"
$Shortcut.WorkingDirectory = "C:\Program Files\MetaTrader 5"
$Shortcut.IconLocation = "C:\Program Files\MetaTrader 5\terminal64.exe,0"
$Shortcut.Description = "MT5 with FBS Configuration"
$Shortcut.Save()

Write-Host "✅ Desktop shortcut created" -ForegroundColor Green

# Create startup batch file
$startupScript = @"
@echo off
title MT5 FBS Trading Terminal
echo 🚀 Starting MT5 with FBS Configuration
echo =====================================
cd /d "C:\Program Files\MetaTrader 5"
start "" "terminal64.exe" /config:"$tradingDir\mt5_fbs_config.ini"
echo ✅ MT5 Started Successfully
echo 📊 Account: $Login
echo 🏦 Server: $Server
echo.
echo Press any key to close this window...
pause > nul
"@

$startupScript | Out-File -FilePath "$tradingDir\Start-MT5-FBS.bat" -Encoding ASCII

# Step 6: Final verification
Write-Host "`n✅ Setup Verification" -ForegroundColor Cyan

$setupComplete = $true

# Check MT5 installation
if (Test-Path "C:\Program Files\MetaTrader 5\terminal64.exe") {
    Write-Host "✅ MT5 installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ MT5 installation not found" -ForegroundColor Red
    $setupComplete = $false
}

# Check configuration files
if (Test-Path "$tradingDir\mt5_fbs_config.ini") {
    Write-Host "✅ Configuration files created" -ForegroundColor Green
} else {
    Write-Host "❌ Configuration files missing" -ForegroundColor Red
    $setupComplete = $false
}

# Display final results
Write-Host "`n🎉 MT5 FBS Setup Results" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

if ($setupComplete) {
    Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
    
    Write-Host "`n📋 What's been set up:" -ForegroundColor Yellow
    Write-Host "• MT5 Terminal installed" -ForegroundColor White
    Write-Host "• FBS server configuration" -ForegroundColor White
    Write-Host "• Python MT5 API connector" -ForegroundColor White
    Write-Host "• Trading workspace created" -ForegroundColor White
    Write-Host "• Desktop shortcut created" -ForegroundColor White
    
    Write-Host "`n🚀 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Double-click 'MT5 FBS' shortcut on desktop" -ForegroundColor White
    Write-Host "2. Login with your FBS credentials" -ForegroundColor White
    Write-Host "3. Start trading or run demo tests" -ForegroundColor White
    Write-Host "4. Use Python scripts for automated trading" -ForegroundColor White
    
    Write-Host "`n📁 Files location: $tradingDir" -ForegroundColor Cyan
    
} else {
    Write-Host "❌ Setup completed with errors" -ForegroundColor Red
    Write-Host "Please check the error messages above and retry" -ForegroundColor Yellow
}

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")