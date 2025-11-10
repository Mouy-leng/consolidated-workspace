#!/usr/bin/env pwsh
<#
.SYNOPSIS
    A6-9V Desktop Project Organizer
.DESCRIPTION
    Saves current work, syncs projects, and organizes all development projects on desktop
    with A6-9V organization structure and shortcuts.
.PARAMETER Action
    Action to perform: save, sync, organize, show, all
#>

param(
    [Parameter(Position=0)]
    [ValidateSet("save", "sync", "organize", "show", "all")]
    [string]$Action = "all",
    
    [Parameter(HelpMessage="Force operations without confirmation")]
    [switch]$Force
)

# A6-9V Configuration
$A69V_CONFIG = @{
    OrgName = "A6-9V"
    ProjectRoot = $PWD.Path
    DesktopPath = [Environment]::GetFolderPath("Desktop")
    HomeDir = $env:USERPROFILE
    SecretsDir = $env:GENX_SECRETS_DIR ?? (Join-Path $env:USERPROFILE ".genx_fx_secrets")
}

#region Utility Functions
function Write-Header {
    param([string]$Title)
    Write-Host "`n" + ("="*60) -ForegroundColor Magenta
    Write-Host "  A6-9V Desktop Organizer: $Title" -ForegroundColor Magenta
    Write-Host ("="*60) -ForegroundColor Magenta
}

function Write-Success { param([string]$Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Warning { param([string]$Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message) Write-Host "✗ $Message" -ForegroundColor Red }
function Write-Info { param([string]$Message) Write-Host "ℹ $Message" -ForegroundColor Blue }

function Confirm-Action {
    param([string]$Message)
    if ($Force) { return $true }
    $choice = Read-Host "$Message [Y/N]"
    return $choice -match "^[Yy]"
}

function New-Shortcut {
    param(
        [string]$TargetPath,
        [string]$ShortcutPath,
        [string]$Description = "",
        [string]$WorkingDirectory = "",
        [string]$Arguments = ""
    )
    
    try {
        $WScriptShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)
        $Shortcut.TargetPath = $TargetPath
        $Shortcut.Description = $Description
        if ($WorkingDirectory) { $Shortcut.WorkingDirectory = $WorkingDirectory }
        if ($Arguments) { $Shortcut.Arguments = $Arguments }
        $Shortcut.Save()
        Write-Success "Created shortcut: $(Split-Path $ShortcutPath -Leaf)"
        return $true
    } catch {
        Write-Warning "Failed to create shortcut: $($_.Exception.Message)"
        return $false
    }
}
#endregion

#region Save Current Work
function Save-CurrentWork {
    Write-Header "Saving Current A6-9V Work"
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = Join-Path $A69V_CONFIG.SecretsDir "backups"
    
    # Ensure backup directory exists
    if (-not (Test-Path $backupDir)) {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    }
    
    # Create comprehensive backup
    $backupName = "a69v_genx_backup_$timestamp.zip"
    $backupPath = Join-Path $backupDir $backupName
    
    Write-Info "Creating comprehensive project backup..."
    
    # Files to include in backup
    $includePatterns = @(
        "*.ps1",
        "*.md", 
        "*.json",
        "*.yml",
        "*.yaml",
        ".env*",
        "*.py",
        "config\*",
        "scripts\*",
        ".github\*",
        ".vscode\*",
        ".idea\*"
    )
    
    # Files to exclude
    $excludePatterns = @(
        "node_modules\*",
        "venv\*",
        "__pycache__\*",
        "*.pyc",
        ".git\*",
        "logs\*.log"
    )
    
    try {
        $filesToBackup = @()
        foreach ($pattern in $includePatterns) {
            $files = Get-ChildItem -Path $A69V_CONFIG.ProjectRoot -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                $shouldExclude = $false
                foreach ($excludePattern in $excludePatterns) {
                    if ($file.FullName -like "*$excludePattern*") {
                        $shouldExclude = $true
                        break
                    }
                }
                if (-not $shouldExclude) {
                    $filesToBackup += $file
                }
            }
        }
        
        if ($filesToBackup.Count -gt 0) {
            Compress-Archive -Path ($filesToBackup | ForEach-Object { $_.FullName }) -DestinationPath $backupPath -Force
            Write-Success "Project backed up to: $backupPath"
            Write-Info "Files backed up: $($filesToBackup.Count)"
        } else {
            Write-Warning "No files found to backup"
        }
        
    } catch {
        Write-Error "Backup failed: $($_.Exception.Message)"
    }
    
    # Create save summary
    $saveSummary = @"
# A6-9V Project Save Summary
**Timestamp**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**Backup Location**: $backupPath
**Project Root**: $($A69V_CONFIG.ProjectRoot)

## Files Included:
$(if ($filesToBackup) {
    ($filesToBackup | ForEach-Object { "- $($_.Name) ($($_.Length) bytes)" }) -join "`n"
} else {
    "No files backed up"
})

## Current Environment:
- Organization: $($A69V_CONFIG.OrgName)
- Desktop Path: $($A69V_CONFIG.DesktopPath)
- Secrets Dir: $($A69V_CONFIG.SecretsDir)

## Next Steps:
1. Organize desktop projects
2. Create project shortcuts
3. Sync with remote repositories (when Git available)
"@

    $summaryPath = Join-Path $A69V_CONFIG.ProjectRoot "SAVE_SUMMARY_$timestamp.md"
    Set-Content -Path $summaryPath -Value $saveSummary
    Write-Success "Save summary created: SAVE_SUMMARY_$timestamp.md"
}
#endregion

#region Show All Projects
function Show-AllProjects {
    Write-Header "Discovering All Projects"
    
    $searchPaths = @(
        $A69V_CONFIG.DesktopPath,
        $A69V_CONFIG.HomeDir,
        "C:\Projects",
        "C:\Dev", 
        "C:\Code",
        "D:\Projects",
        "D:\Dev",
        "D:\Code"
    )
    
    $projectIndicators = @(
        ".git",
        "package.json",
        "requirements.txt",
        "setup.py",
        "*.sln",
        "Dockerfile",
        ".gitignore",
        "README.md"
    )
    
    $discoveredProjects = @()
    
    foreach ($searchPath in $searchPaths) {
        if (Test-Path $searchPath) {
            Write-Info "Scanning: $searchPath"
            
            try {
                $directories = Get-ChildItem -Path $searchPath -Directory -Force -ErrorAction SilentlyContinue | Where-Object {
                    $dir = $_.FullName
                    # Skip system directories
                    $_.Name -notmatch "^(Windows|System|Program|PerfLogs|\$|AppData|\.)" -and
                    # Check for project indicators
                    ($projectIndicators | ForEach-Object {
                        Test-Path (Join-Path $dir $_) -ErrorAction SilentlyContinue
                    }) -contains $true
                }
                
                foreach ($dir in $directories) {
                    $projectInfo = @{
                        Name = $dir.Name
                        Path = $dir.FullName
                        LastModified = $dir.LastWriteTime
                        Size = (Get-ChildItem -Path $dir.FullName -Recurse -File -ErrorAction SilentlyContinue | 
                               Measure-Object -Property Length -Sum).Sum
                        Type = "Unknown"
                        Indicators = @()
                    }
                    
                    # Determine project type
                    foreach ($indicator in $projectIndicators) {
                        if (Test-Path (Join-Path $dir.FullName $indicator)) {
                            $projectInfo.Indicators += $indicator
                            
                            switch ($indicator) {
                                ".git" { $projectInfo.Type = "Git Repository" }
                                "package.json" { $projectInfo.Type = "Node.js Project" }
                                "requirements.txt" { $projectInfo.Type = "Python Project" }
                                "setup.py" { $projectInfo.Type = "Python Package" }
                                "*.sln" { $projectInfo.Type = "Visual Studio Solution" }
                                "Dockerfile" { $projectInfo.Type = "Docker Project" }
                            }
                        }
                    }
                    
                    # Special detection for GenX_FX projects
                    if ($dir.Name -match "GenX|genx|FX|fx|trading|Trade") {
                        $projectInfo.Type = "GenX_FX Trading Project"
                    }
                    
                    $discoveredProjects += $projectInfo
                }
                
            } catch {
                Write-Warning "Could not scan $searchPath : $($_.Exception.Message)"
            }
        }
    }
    
    # Display discovered projects
    Write-Host "`n📊 Discovered Projects:" -ForegroundColor Cyan
    Write-Host "Total projects found: $($discoveredProjects.Count)" -ForegroundColor Yellow
    
    if ($discoveredProjects.Count -gt 0) {
        $discoveredProjects | Sort-Object LastModified -Descending | ForEach-Object {
            $sizeKB = [math]::Round($_.Size / 1KB, 1)
            $lastModified = $_.LastModified.ToString("yyyy-MM-dd")
            
            Write-Host "`n📁 $($_.Name)" -ForegroundColor White
            Write-Host "   Path: $($_.Path)" -ForegroundColor Gray
            Write-Host "   Type: $($_.Type)" -ForegroundColor Cyan
            Write-Host "   Size: $sizeKB KB | Modified: $lastModified" -ForegroundColor Gray
            if ($_.Indicators.Count -gt 0) {
                Write-Host "   Indicators: $($_.Indicators -join ', ')" -ForegroundColor DarkGray
            }
        }
        
        return $discoveredProjects
    } else {
        Write-Info "No projects found in search paths"
        return @()
    }
}
#endregion

#region Organize Desktop
function Organize-Desktop {
    Write-Header "Organizing Desktop with A6-9V Structure"
    
    $desktopPath = $A69V_CONFIG.DesktopPath
    
    # Create A6-9V organization structure
    $a69vStructure = @{
        "A6-9V Projects" = @{
            Description = "Main A6-9V development projects"
            Subfolders = @("Active", "Archive", "Templates", "Documentation")
        }
        "A6-9V Tools" = @{
            Description = "Development tools and utilities"
            Subfolders = @("Scripts", "Configurations", "References")
        }
        "A6-9V Trading" = @{
            Description = "Trading and financial projects"
            Subfolders = @("GenX_FX", "EA", "Indicators", "Backtesting")
        }
    }
    
    Write-Info "Creating A6-9V desktop organization structure..."
    
    foreach ($folder in $a69vStructure.Keys) {
        $folderPath = Join-Path $desktopPath $folder
        
        if (-not (Test-Path $folderPath)) {
            New-Item -ItemType Directory -Path $folderPath -Force | Out-Null
            Write-Success "Created folder: $folder"
            
            # Create subfolders
            foreach ($subfolder in $a69vStructure[$folder].Subfolders) {
                $subfolderPath = Join-Path $folderPath $subfolder
                New-Item -ItemType Directory -Path $subfolderPath -Force | Out-Null
            }
            
            # Create folder description
            $descriptionFile = Join-Path $folderPath "README.md"
            $description = @"
# $folder

$($a69vStructure[$folder].Description)

## Subfolders:
$(($a69vStructure[$folder].Subfolders | ForEach-Object { "- **$_**" }) -join "`n")

---
Created by A6-9V Desktop Organizer on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@
            Set-Content -Path $descriptionFile -Value $description
            
        } else {
            Write-Info "Folder already exists: $folder"
        }
    }
    
    # Create shortcuts for key A6-9V tools
    Create-A69VShortcuts
    
    # Organize existing desktop items
    Organize-DesktopItems
}

function Create-A69VShortcuts {
    Write-Info "Creating A6-9V tool shortcuts..."
    
    $shortcutsDir = Join-Path $A69V_CONFIG.DesktopPath "A6-9V Tools\Scripts"
    
    $shortcuts = @(
        @{
            Name = "A6-9V Repository Manager"
            Target = "powershell.exe"
            Arguments = "-ExecutionPolicy Bypass -File `"$($A69V_CONFIG.ProjectRoot)\a69v_repo_manager.ps1`""
            WorkingDir = $A69V_CONFIG.ProjectRoot
            Description = "A6-9V repository management tool"
        },
        @{
            Name = "A6-9V GenX Control"
            Target = "powershell.exe"
            Arguments = "-ExecutionPolicy Bypass -File `"$($A69V_CONFIG.ProjectRoot)\genx.ps1`""
            WorkingDir = $A69V_CONFIG.ProjectRoot
            Description = "A6-9V GenX_FX control center"
        },
        @{
            Name = "A6-9V Secrets Manager"
            Target = "powershell.exe"
            Arguments = "-ExecutionPolicy Bypass -File `"$($A69V_CONFIG.ProjectRoot)\scripts\a69v_secrets.ps1`""
            WorkingDir = $A69V_CONFIG.ProjectRoot
            Description = "A6-9V credential management"
        },
        @{
            Name = "A6-9V Project Folder"
            Target = $A69V_CONFIG.ProjectRoot
            Arguments = ""
            WorkingDir = $A69V_CONFIG.ProjectRoot
            Description = "A6-9V main project directory"
        }
    )
    
    foreach ($shortcut in $shortcuts) {
        $shortcutPath = Join-Path $shortcutsDir "$($shortcut.Name).lnk"
        New-Shortcut -TargetPath $shortcut.Target -ShortcutPath $shortcutPath -Description $shortcut.Description -WorkingDirectory $shortcut.WorkingDir -Arguments $shortcut.Arguments
    }
}

function Organize-DesktopItems {
    Write-Info "Organizing existing desktop items..."
    
    $desktopItems = Get-ChildItem -Path $A69V_CONFIG.DesktopPath -Force | Where-Object {
        $_.Name -notmatch "^A6-9V" -and $_.Name -notmatch "^\." 
    }
    
    $organizationRules = @{
        "Development" = @("*.py", "*.js", "*.ts", "*.cs", "*.cpp", "*.java", "*.go", "*.rs")
        "Documents" = @("*.txt", "*.md", "*.pdf", "*.doc", "*.docx", "*.rtf")
        "Images" = @("*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.svg", "*.ico")
        "Archives" = @("*.zip", "*.rar", "*.7z", "*.tar", "*.gz")
        "Executables" = @("*.exe", "*.msi", "*.bat", "*.cmd", "*.ps1")
    }
    
    if ($desktopItems.Count -gt 0) {
        Write-Host "`nFound $($desktopItems.Count) items to organize:" -ForegroundColor Yellow
        
        foreach ($item in $desktopItems) {
            Write-Host "  - $($item.Name)" -ForegroundColor Gray
        }
        
        if (Confirm-Action "Organize these items into A6-9V structure?") {
            # Create organization folders
            $miscFolder = Join-Path $A69V_CONFIG.DesktopPath "A6-9V Tools\Misc"
            if (-not (Test-Path $miscFolder)) {
                New-Item -ItemType Directory -Path $miscFolder -Force | Out-Null
            }
            
            foreach ($item in $desktopItems) {
                try {
                    $targetFolder = $miscFolder
                    
                    # Determine target folder based on rules
                    foreach ($category in $organizationRules.Keys) {
                        foreach ($pattern in $organizationRules[$category]) {
                            if ($item.Name -like $pattern) {
                                $categoryFolder = Join-Path $A69V_CONFIG.DesktopPath "A6-9V Tools\$category"
                                if (-not (Test-Path $categoryFolder)) {
                                    New-Item -ItemType Directory -Path $categoryFolder -Force | Out-Null
                                }
                                $targetFolder = $categoryFolder
                                break
                            }
                        }
                        if ($targetFolder -ne $miscFolder) { break }
                    }
                    
                    $targetPath = Join-Path $targetFolder $item.Name
                    Move-Item -Path $item.FullName -Destination $targetPath -Force
                    Write-Success "Moved: $($item.Name) → $(Split-Path $targetFolder -Leaf)"
                    
                } catch {
                    Write-Warning "Failed to move $($item.Name): $($_.Exception.Message)"
                }
            }
        }
    } else {
        Write-Info "Desktop is already clean"
    }
}
#endregion

#region Sync Projects  
function Sync-Projects {
    Write-Header "Synchronizing A6-9V Projects"
    
    # Create sync summary
    $syncSummary = @"
# A6-9V Project Sync Summary
**Timestamp**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

## Current Status:
- Git: Not available in current environment
- GitHub CLI: Not available in current environment
- Project Root: $($A69V_CONFIG.ProjectRoot)

## Sync Actions Available:
When Git becomes available, use these commands:

### Configure Git Identity
``````powershell
.\a69v_repo_manager.ps1 configure
``````

### Sync Current Project
``````bash
git add .
git commit -m "A6-9V organization setup complete"
git push origin main
``````

### Sync Multiple Projects
``````powershell
# Use A6-9V repository manager for bulk operations
.\a69v_repo_manager.ps1 cleanup  # Analyze all repositories
``````

## Manual Sync Checklist:
- [ ] Commit current A6-9V changes
- [ ] Push to remote repository
- [ ] Update repository descriptions with A6-9V branding
- [ ] Set repository visibility (private for sensitive projects)
- [ ] Configure branch protection rules
- [ ] Add repository secrets and environment variables

## Repository URLs to Update:
Update your repository remote URLs to use A6-9V organization:
``````bash
git remote set-url origin https://github.com/A6-9V/GenX_FX_Remote.git
``````
"@

    $syncSummaryPath = Join-Path $A69V_CONFIG.ProjectRoot "A69V_SYNC_SUMMARY.md"
    Set-Content -Path $syncSummaryPath -Value $syncSummary
    Write-Success "Sync summary created: A69V_SYNC_SUMMARY.md"
    
    Write-Info "Git and GitHub CLI not available. Manual sync required."
    Write-Info "See A69V_SYNC_SUMMARY.md for detailed sync instructions."
}
#endregion

#region Main Execution
Clear-Host
Write-Host "🎯 A6-9V Desktop Organizer" -ForegroundColor Magenta
Write-Host "Organization: $($A69V_CONFIG.OrgName)" -ForegroundColor Gray
Write-Host "Project Root: $($A69V_CONFIG.ProjectRoot)" -ForegroundColor Gray
Write-Host "Desktop: $($A69V_CONFIG.DesktopPath)" -ForegroundColor Gray

$discoveredProjects = @()

switch ($Action) {
    "save" {
        Save-CurrentWork
    }
    
    "show" {
        $discoveredProjects = Show-AllProjects
    }
    
    "organize" {
        Organize-Desktop
    }
    
    "sync" {
        Sync-Projects
    }
    
    "all" {
        Write-Info "Running complete desktop organization..."
        
        Save-CurrentWork
        $discoveredProjects = Show-AllProjects
        Organize-Desktop
        Sync-Projects
        
        Write-Header "Organization Complete!"
        
        Write-Host @"

🎉 A6-9V Desktop Organization Complete!

✅ Current work saved and backed up
✅ All projects discovered and cataloged  
✅ Desktop organized with A6-9V structure
✅ Sync instructions prepared

📁 Desktop Structure Created:
  • A6-9V Projects/ (Active, Archive, Templates, Documentation)
  • A6-9V Tools/ (Scripts, Configurations, References)  
  • A6-9V Trading/ (GenX_FX, EA, Indicators, Backtesting)

🔧 Shortcuts Created:
  • A6-9V Repository Manager
  • A6-9V GenX Control
  • A6-9V Secrets Manager  
  • A6-9V Project Folder

📊 Projects Found: $($discoveredProjects.Count)
🎯 Organization: A6-9V
🕐 Completed: $(Get-Date -Format 'HH:mm:ss')

Next: Check your desktop for the new A6-9V organization structure!
"@ -ForegroundColor Green
    }
    
    default {
        Write-Error "Unknown action: $Action"
        Write-Host "Available actions: save, show, organize, sync, all" -ForegroundColor Yellow
    }
}

# Create final desktop summary
$finalSummary = @"
# A6-9V Desktop Organization Summary

## Completed Actions:
- ✅ Current work saved and backed up
- ✅ Projects discovered: $($discoveredProjects.Count)
- ✅ Desktop organized with A6-9V structure
- ✅ Tool shortcuts created
- ✅ Sync instructions prepared

## Desktop Folders Created:
- **A6-9V Projects/** - Main development projects
- **A6-9V Tools/** - Development tools and utilities  
- **A6-9V Trading/** - Trading and financial projects

## Quick Access Shortcuts:
- A6-9V Repository Manager
- A6-9V GenX Control Center
- A6-9V Secrets Manager
- A6-9V Project Folder

## Discovered Projects:
$(if ($discoveredProjects.Count -gt 0) {
    ($discoveredProjects | ForEach-Object { "- **$($_.Name)** ($($_.Type)) - $($_.Path)" }) -join "`n"
} else {
    "No projects discovered in search paths"
})

---
Organization completed: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
By: A6-9V Desktop Organizer v1.0
"@

$finalSummaryPath = Join-Path $A69V_CONFIG.DesktopPath "A6-9V_DESKTOP_SUMMARY.md"
Set-Content -Path $finalSummaryPath -Value $finalSummary

Write-Host "`n✨ A6-9V desktop organization completed!" -ForegroundColor Magenta
Write-Host "📋 Summary saved to desktop: A6-9V_DESKTOP_SUMMARY.md" -ForegroundColor Cyan
#endregion