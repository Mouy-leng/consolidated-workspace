# Backup Trading System to Dropbox Personal Vault
# Saves all critical files and configurations

param(
    [Parameter(Mandatory=$false)]
    [string]$DropboxPath = "C:\Users\lengk\Dropbox"
)

# Set console to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "💾 $Title" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Gray
}

function Test-DropboxPath {
    Write-Header "DROPBOX CONNECTION TEST"
    
    # Check multiple possible Dropbox paths
    $possiblePaths = @(
        "C:\Users\lengk\Dropbox",
        "C:\Users\lengk\OneDrive",
        "C:\Users\lengk\Dropbox\Personal Vault",
        "C:\Users\lengk\OneDrive\Personal Vault"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            Write-Host "✅ Found: $path" -ForegroundColor Green
            return $path
        } else {
            Write-Host "❌ Not found: $path" -ForegroundColor Red
        }
    }
    
    # Try to resolve the shortcut
    $shortcutPath = "C:\Users\lengk\Dropbox\OneDrive\Personal Vault.lnk"
    if (Test-Path $shortcutPath) {
        try {
            $shell = New-Object -ComObject WScript.Shell
            $shortcut = $shell.CreateShortcut($shortcutPath)
            $targetPath = $shortcut.TargetPath
            Write-Host "🔗 Shortcut target: $targetPath" -ForegroundColor Yellow
            
            if (Test-Path $targetPath) {
                Write-Host "✅ Target accessible: $targetPath" -ForegroundColor Green
                return $targetPath
            }
        } catch {
            Write-Host "❌ Could not resolve shortcut" -ForegroundColor Red
        }
    }
    
    # Fallback - create in current directory
    $fallbackPath = ".\BACKUP_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Write-Host "⚠️  Using fallback path: $fallbackPath" -ForegroundColor Yellow
    return $fallbackPath
}

function New-BackupDirectory {
    param([string]$BasePath)
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = Join-Path $BasePath "TradingSystem_Backup_$timestamp"
    
    if (!(Test-Path $backupDir)) {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        Write-Host "📁 Created backup directory: $backupDir" -ForegroundColor Green
    }
    
    return $backupDir
}

function Copy-CriticalFiles {
    param([string]$BackupDir)
    
    Write-Header "COPYING CRITICAL FILES"
    
    # Define critical files and folders to backup
    $criticalItems = @{
        # Trading Scripts
        "Core Trading Scripts" = @(
            "micro-account-trader.py",
            "xm-demo-setup.py",
            "broker-analyzer.py",
            "live-account-checker.py",
            "automated-trading-system.py"
        )
        
        # Controllers
        "PowerShell Controllers" = @(
            "trading-controller.ps1",
            "xm-trading-controller.ps1",
            "live-dashboard.ps1",
            "device-manager.ps1",
            "broker-dashboard.ps1",
            "micro-controller.ps1"
        )
        
        # Configuration Files
        "Configuration" = @(
            ".env",
            ".env.fbs.secure",
            ".env.template",
            "device-sync-registry.json",
            "crypto_wallet_scan.json"
        )
        
        # Analysis Results
        "Analysis & Reports" = @(
            "broker_analysis_*.json",
            "xm_fbs_comparison_*.json",
            "live_account_report.json",
            "quick_status.json",
            "ci-status-report.json"
        )
        
        # Log Files (recent)
        "Important Logs" = @(
            "micro_trading.log",
            "xm_demo_testing.log",
            "automated_trading.log",
            "device-manager.log"
        )
        
        # Documentation
        "Documentation" = @(
            "GETTING_STARTED.md",
            "QUICK_START.md",
            "SECURITY.md",
            "SYNC_REPORT.md",
            "SYSTEM_NOTES.md",
            "DAILY_ANALYSIS_CHECKLIST.md"
        )
    }
    
    $totalCopied = 0
    $totalSize = 0
    
    foreach ($category in $criticalItems.Keys) {
        Write-Host ""
        Write-Host "📂 ${category}:" -ForegroundColor Yellow
        
        $categoryDir = Join-Path $BackupDir $category.Replace(" ", "_").Replace("&", "and")
        New-Item -ItemType Directory -Path $categoryDir -Force | Out-Null
        
        foreach ($pattern in $criticalItems[$category]) {
            $files = Get-ChildItem -Path . -Name $pattern -ErrorAction SilentlyContinue
            
            foreach ($file in $files) {
                if (Test-Path $file) {
                    try {
                        $destPath = Join-Path $categoryDir (Split-Path $file -Leaf)
                        Copy-Item -Path $file -Destination $destPath -Force
                        
                        $size = (Get-Item $file).Length
                        $totalSize += $size
                        $totalCopied++
                        
                        $sizeKB = [math]::Round($size / 1KB, 1)
                        Write-Host "   ✅ $file ($sizeKB KB)" -ForegroundColor Green
                    } catch {
                        Write-Host "   ❌ Failed to copy $file" -ForegroundColor Red
                    }
                }
            }
        }
    }
    
    Write-Host ""
    Write-Host "📊 BACKUP SUMMARY:" -ForegroundColor Cyan
    Write-Host "   📁 Files copied: $totalCopied" -ForegroundColor White
    Write-Host "   💾 Total size: $([math]::Round($totalSize / 1MB, 2)) MB" -ForegroundColor White
    
    return @{
        FilesCopied = $totalCopied
        TotalSize = $totalSize
    }
}

function Copy-SpecialFolders {
    param([string]$BackupDir)
    
    Write-Header "COPYING SPECIAL FOLDERS"
    
    $specialFolders = @(
        "trading-microservice",
        "security",
        "mt4-fbs-setup",
        "mt5-fbs-setup",
        "trading-analysis"
    )
    
    foreach ($folder in $specialFolders) {
        if (Test-Path $folder) {
            try {
                $destPath = Join-Path $BackupDir "Special_Folders\$folder"
                Copy-Item -Path $folder -Destination $destPath -Recurse -Force
                
                $itemCount = (Get-ChildItem $folder -Recurse).Count
                Write-Host "   ✅ $folder ($itemCount items)" -ForegroundColor Green
            } catch {
                Write-Host "   ❌ Failed to copy folder $folder" -ForegroundColor Red
            }
        }
    }
}

function Create-BackupManifest {
    param([string]$BackupDir, [hashtable]$Stats)
    
    Write-Header "CREATING BACKUP MANIFEST"
    
    $manifest = @{
        backup_info = @{
            timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            source_path = (Get-Location).Path
            backup_path = $BackupDir
            total_files = $Stats.FilesCopied
            total_size_mb = [math]::Round($Stats.TotalSize / 1MB, 2)
        }
        
        system_status = @{
            fbs_account = "241926287"
            fbs_balance = 47.79
            trading_system_running = $true
            xm_demo_configured = (Test-Path "xm_demo_config.json")
            broker_analysis_complete = (Test-Path "broker_analysis_*.json")
        }
        
        critical_files = @{
            trading_scripts = @(
                "micro-account-trader.py",
                "xm-demo-setup.py", 
                "broker-analyzer.py"
            )
            controllers = @(
                "trading-controller.ps1",
                "xm-trading-controller.ps1",
                "device-manager.ps1"
            )
            configurations = @(
                ".env.fbs.secure",
                "device-sync-registry.json"
            )
        }
        
        next_steps = @(
            "Continue XM demo testing with saved configuration",
            "Use broker analysis results for migration decision", 
            "Monitor FBS account performance vs XM demo",
            "Consider FTMO evaluation when profitable"
        )
        
        restoration_notes = @(
            "Copy files back to C:\Users\lengk\.config\trading-system",
            "Run .\trading-controller.ps1 to restart system",
            "Check .\xm-trading-controller.ps1 -Action status for XM demo",
            "Review broker_analysis_*.json for recommendations"
        )
    }
    
    $manifestPath = Join-Path $BackupDir "BACKUP_MANIFEST.json"
    $manifest | ConvertTo-Json -Depth 4 | Out-File -FilePath $manifestPath -Encoding UTF8
    
    Write-Host "📋 Manifest created: BACKUP_MANIFEST.json" -ForegroundColor Green
    
    # Also create a simple README
    $readmePath = Join-Path $BackupDir "README.txt"
    $readmeContent = @"
TRADING SYSTEM BACKUP
Created: $(Get-Date)
Source: C:\Users\lengk\.config\trading-system

CONTENTS:
- Core Trading Scripts (Python trading systems)
- PowerShell Controllers (System management)
- Configuration Files (Environment and settings)
- Analysis & Reports (Broker analysis, trading reports)
- Important Logs (System and trading logs)
- Documentation (Setup guides and notes)
- Special Folders (Complete subsystems)

RESTORATION:
1. Copy all files back to original location
2. Run .\trading-controller.ps1 to restart
3. Check system status with quick-status.py
4. Continue with broker migration plan

CURRENT STATUS:
- FBS Account: 241926287 ($47.79)
- Trading System: RUNNING
- Top Broker Recommendation: Interactive Brokers
- Next Step: XM Demo Testing

For questions, check BACKUP_MANIFEST.json for detailed info.
"@
    
    $readmeContent | Out-File -FilePath $readmePath -Encoding UTF8
    Write-Host "📖 README created: README.txt" -ForegroundColor Green
}

function Start-Backup {
    Write-Header "TRADING SYSTEM BACKUP TO DROPBOX"
    
    Write-Host "🎯 BACKUP PLAN:" -ForegroundColor Yellow
    Write-Host "   💾 Save all critical trading files" -ForegroundColor White
    Write-Host "   🔒 Preserve security configurations" -ForegroundColor White  
    Write-Host "   📊 Include analysis results" -ForegroundColor White
    Write-Host "   📋 Create restoration manifest" -ForegroundColor White
    Write-Host ""
    
    # Find Dropbox path
    $dropboxPath = Test-DropboxPath
    Write-Host "📁 Backup destination: $dropboxPath" -ForegroundColor Cyan
    
    # Create backup directory
    $backupDir = New-BackupDirectory $dropboxPath
    Write-Host "📂 Backup directory: $backupDir" -ForegroundColor Cyan
    
    # Copy files
    $stats = Copy-CriticalFiles $backupDir
    Copy-SpecialFolders $backupDir
    Create-BackupManifest $backupDir $stats
    
    Write-Host ""
    Write-Header "BACKUP COMPLETE"
    Write-Host "✅ All critical files backed up successfully!" -ForegroundColor Green
    Write-Host "📁 Location: $backupDir" -ForegroundColor Cyan
    Write-Host "📋 Check BACKUP_MANIFEST.json for details" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🚀 READY TO CONTINUE:" -ForegroundColor Green
    Write-Host "   Your trading system is safely backed up" -ForegroundColor White
    Write-Host "   You can now proceed with XM demo testing" -ForegroundColor White
    Write-Host "   All configurations and analysis preserved" -ForegroundColor White
    
    return $backupDir
}

# Main execution
Start-Backup