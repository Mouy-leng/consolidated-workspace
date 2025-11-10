# Download and Install MT5 from FBS
Write-Host "Downloading MT5 from FBS..." -ForegroundColor Yellow

# FBS MT5 download URL
$mt5Url = "https://download.mql5.com/cdn/web/fbs.inc/mt5/fbsmt5setup.exe"
$installerPath = "fbsmt5setup.exe"

try {
    # Download MT5 installer
    Invoke-WebRequest -Uri $mt5Url -OutFile $installerPath -UseBasicParsing
    Write-Host "MT5 installer downloaded successfully" -ForegroundColor Green
    
    # Run installer
    Write-Host "Starting MT5 installation..." -ForegroundColor Yellow
    Start-Process -FilePath $installerPath -Wait
    
    Write-Host "MT5 installation completed!" -ForegroundColor Green
    
    # Clean up
    Remove-Item $installerPath -ErrorAction SilentlyContinue
    
} catch {
    Write-Host "Error downloading MT5: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please download manually from: https://www.fbs.com/download/metatrader5" -ForegroundColor Yellow
}