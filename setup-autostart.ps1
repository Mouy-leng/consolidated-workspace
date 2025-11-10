# Setup PyCharm to auto-start with this project
# Creates a Windows startup shortcut

$projectPath = "E:\Code\consolidated-workspace"
$startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$shortcutPath = Join-Path $startupPath "PyCharm - Consolidated Workspace.lnk"
$targetPath = Join-Path $projectPath "start-pycharm.bat"

Write-Host "Setting up PyCharm auto-start..." -ForegroundColor Cyan

# Create shortcut using COM object
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $targetPath
$Shortcut.WorkingDirectory = $projectPath
$Shortcut.Description = "Auto-start PyCharm with Consolidated Workspace"
$Shortcut.Save()

Write-Host "✓ Created startup shortcut: $shortcutPath" -ForegroundColor Green
Write-Host ""
Write-Host "PyCharm will now start automatically when Windows starts." -ForegroundColor Yellow
Write-Host "To disable: Delete the shortcut from Startup folder" -ForegroundColor Gray
Write-Host ""

