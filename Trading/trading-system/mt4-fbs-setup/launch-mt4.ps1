# Launch MT4 with FBS Configuration

Write-Host "Launching MT4 FBS Real Account..." -ForegroundColor Cyan

# Find MT4 installation
$mt4Paths = @(
    "C:\Program Files\MetaTrader 4\terminal.exe",
    "C:\Program Files (x86)\MetaTrader 4\terminal.exe", 
    "$env:LOCALAPPDATA\Programs\MetaTrader 4\terminal.exe",
    "$env:APPDATA\MetaQuotes\Terminal\*\terminal.exe"
)

$mt4Path = $null
foreach ($path in $mt4Paths) {
    if (Test-Path $path) {
        $mt4Path = $path
        break
    }
}

if (-not $mt4Path) {
    # Try to find in common locations
    $searchPaths = Get-ChildItem -Path "C:\Program Files*" -Name "MetaTrader*" -Directory -ErrorAction SilentlyContinue
    foreach ($searchPath in $searchPaths) {
        $terminalPath = Join-Path $searchPath.FullName "terminal.exe"
        if (Test-Path $terminalPath) {
            $mt4Path = $terminalPath
            break
        }
    }
}

if ($mt4Path) {
    Write-Host "Found MT4 at: $mt4Path" -ForegroundColor Green
    
    # Launch MT4
    Start-Process -FilePath $mt4Path
    
    Write-Host "MT4 launched successfully!" -ForegroundColor Green
    Write-Host "`nFBS Account Details:" -ForegroundColor Yellow
    Write-Host "Login: 241926287" -ForegroundColor White
    Write-Host "Password: f0v/9iIH" -ForegroundColor White  
    Write-Host "Server: FBS-Real-4" -ForegroundColor White
    Write-Host "Server IP: 95.179.194.198:443" -ForegroundColor White
    Write-Host "Company: FBS Markets Inc." -ForegroundColor White
    
    Write-Host "`nNext Steps:" -ForegroundColor Cyan
    Write-Host "1. MT4 should open automatically" -ForegroundColor White
    Write-Host "2. Login with the credentials above" -ForegroundColor White
    Write-Host "3. Verify connection to FBS-Real-4 server" -ForegroundColor White
    Write-Host "4. Start trading or run the Python bot" -ForegroundColor White
    
} else {
    Write-Host "MT4 not found. Please install MT4 first." -ForegroundColor Red
    Write-Host "Download from: https://www.fbs.com/download/metatrader4" -ForegroundColor Yellow
}