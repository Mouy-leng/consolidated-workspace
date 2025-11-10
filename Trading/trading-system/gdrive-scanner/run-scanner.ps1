# Google Drive Payment Link Scanner Runner
# Runs the complete scanning and organization process

Write-Host "🔍 Google Drive Payment Link Scanner" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Install requirements
Write-Host "`n📦 Installing requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

# Setup authentication if needed
if (-not (Test-Path "credentials.json")) {
    Write-Host "`n🔐 Setting up Google Drive authentication..." -ForegroundColor Yellow
    python setup-gdrive-auth.py
    
    if (-not (Test-Path "credentials.json")) {
        Write-Host "❌ Please setup credentials.json first" -ForegroundColor Red
        exit 1
    }
}

# Run scanner
Write-Host "`n🔍 Scanning Google Drive for payment links..." -ForegroundColor Yellow
python payment-link-scanner.py

# Check if scan results exist
$scanFiles = Get-ChildItem -Name "payment_links_*.json"
if ($scanFiles.Count -eq 0) {
    Write-Host "❌ No scan results found" -ForegroundColor Red
    exit 1
}

# Organize links
Write-Host "`n🔗 Organizing payment links..." -ForegroundColor Yellow
python link-organizer.py

# Display completion message
Write-Host "`n✅ Scanning and organization completed!" -ForegroundColor Green
Write-Host "`n📁 Generated files:" -ForegroundColor Cyan
Get-ChildItem -Name "*payment_links*" | ForEach-Object {
    Write-Host "  • $_" -ForegroundColor White
}

Write-Host "`n📋 Next steps:" -ForegroundColor Yellow
Write-Host "1. Review the organized_payment_links_*.json file" -ForegroundColor White
Write-Host "2. Check the payment_links_report_*.txt for summary" -ForegroundColor White
Write-Host "3. Implement the recommendations provided" -ForegroundColor White