# Download and Install MT4 from FBS
Write-Host "Downloading MT4 from FBS..." -ForegroundColor Yellow

# FBS MT4 download URL
$mt4Url = "https://download.mql5.com/cdn/web/fbs.inc/mt4/fbsmt4setup.exe"
$installerPath = "fbsmt4setup.exe"

try {
    # Download MT4 installer
    Write-Host "Downloading MT4 installer..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $mt4Url -OutFile $installerPath -UseBasicParsing
    Write-Host "MT4 installer downloaded successfully" -ForegroundColor Green
    
    # Run installer
    Write-Host "Starting MT4 installation..." -ForegroundColor Yellow
    Start-Process -FilePath $installerPath -Wait
    
    Write-Host "MT4 installation completed!" -ForegroundColor Green
    
    # Clean up
    Remove-Item $installerPath -ErrorAction SilentlyContinue
    
    # Find MT4 installation path
    $mt4Paths = @(
        "C:\Program Files\MetaTrader 4\terminal.exe",
        "C:\Program Files (x86)\MetaTrader 4\terminal.exe",
        "$env:LOCALAPPDATA\Programs\MetaTrader 4\terminal.exe"
    )
    
    $mt4Path = $null
    foreach ($path in $mt4Paths) {
        if (Test-Path $path) {
            $mt4Path = $path
            break
        }
    }
    
    if ($mt4Path) {
        Write-Host "MT4 found at: $mt4Path" -ForegroundColor Green
        
        # Create desktop shortcut
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\MT4 FBS Real.lnk")
        $Shortcut.TargetPath = $mt4Path
        $Shortcut.WorkingDirectory = Split-Path $mt4Path
        $Shortcut.IconLocation = "$mt4Path,0"
        $Shortcut.Description = "MetaTrader 4 - FBS Real Account"
        $Shortcut.Save()
        
        Write-Host "Desktop shortcut created" -ForegroundColor Green
    }
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please download manually from: https://www.fbs.com/download/metatrader4" -ForegroundColor Yellow
}

Write-Host "`nMT4 Setup Complete!" -ForegroundColor Cyan
Write-Host "Account Details:" -ForegroundColor Yellow
Write-Host "Login: 241926287" -ForegroundColor White
Write-Host "Server: FBS-Real-4" -ForegroundColor White
Write-Host "Company: FBS Markets Inc." -ForegroundColor White