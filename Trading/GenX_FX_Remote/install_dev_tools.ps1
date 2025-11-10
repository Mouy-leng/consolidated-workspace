# Development Tools Installation Script

Write-Host "=== Development Tools Installation ===" -ForegroundColor Green
Write-Host "Installing missing development tools..." -ForegroundColor Yellow

# Check if Chocolatey is installed
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Chocolatey package manager..." -ForegroundColor Cyan
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    refreshenv
}

# Tools to install
$tools = @{
    "Visual Studio Code" = @{
        command = "code"
        chocoPackage = "vscode"
        url = "https://code.visualstudio.com/"
    }
    "Windows Terminal" = @{
        command = "wt"
        chocoPackage = "microsoft-windows-terminal"
        url = $null
    }
    "Docker Desktop" = @{
        command = "docker"
        chocoPackage = "docker-desktop"
        url = "https://www.docker.com/products/docker-desktop/"
    }
    "Postman" = @{
        command = "postman"
        chocoPackage = "postman"
        url = "https://www.postman.com/"
    }
}

Write-Host "`nChecking installed tools..." -ForegroundColor Cyan

# Check what's already installed
foreach ($toolName in $tools.Keys) {
    $tool = $tools[$toolName]
    $isInstalled = Get-Command $tool.command -ErrorAction SilentlyContinue
    
    if ($isInstalled) {
        Write-Host "✓ $toolName is already installed" -ForegroundColor Green
    } else {
        Write-Host "✗ $toolName is not installed" -ForegroundColor Yellow
        
        $install = Read-Host "Would you like to install $toolName? (y/N)"
        if ($install -eq 'y' -or $install -eq 'Y') {
            Write-Host "Installing $toolName..." -ForegroundColor Cyan
            
            try {
                choco install $tool.chocoPackage -y
                Write-Host "Successfully installed $toolName" -ForegroundColor Green
            }
            catch {
                Write-Host "Failed to install $toolName via Chocolatey: $_" -ForegroundColor Red
                if ($tool.url) {
                    Write-Host "Please download manually from: $($tool.url)" -ForegroundColor Yellow
                }
            }
        }
    }
}

# Install common development extensions for VS Code (if installed)
Write-Host "`nChecking VS Code..." -ForegroundColor Cyan
$vscode = Get-Command code -ErrorAction SilentlyContinue
if ($vscode) {
    Write-Host "VS Code found! Installing useful extensions..." -ForegroundColor Green
    
    $extensions = @(
        "ms-python.python",
        "ms-vscode.cpptools",
        "ms-vscode.powershell",
        "eamodio.gitlens",
        "bradlc.vscode-tailwindcss",
        "esbenp.prettier-vscode",
        "ms-vscode.vscode-typescript-next",
        "ms-vscode.vscode-json",
        "redhat.vscode-yaml",
        "ms-vscode-remote.remote-containers",
        "GitHub.copilot"
    )
    
    foreach ($extension in $extensions) {
        Write-Host "Installing extension: $extension" -ForegroundColor Cyan
        try {
            & code --install-extension $extension --force
        }
        catch {
            Write-Host "Warning: Could not install extension $extension" -ForegroundColor Yellow
        }
    }
}

# Configure Git (if not already configured)
Write-Host "`nConfiguring Git..." -ForegroundColor Cyan
$gitName = git config --global user.name 2>$null
$gitEmail = git config --global user.email 2>$null

if (-not $gitName) {
    $name = Read-Host "Enter your Git username"
    git config --global user.name "$name"
}

if (-not $gitEmail) {
    $email = Read-Host "Enter your Git email"
    git config --global user.email "$email"
}

# Set up useful Git aliases
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage "reset HEAD --"
git config --global alias.last "log -1 HEAD"
git config --global alias.visual "!gitk"

Write-Host "`n=== Development Tools Setup Complete ===" -ForegroundColor Green
Write-Host "Installed tools summary:" -ForegroundColor Cyan
Write-Host "✓ Cursor (AI Code Editor)" -ForegroundColor Green
Write-Host "✓ Git (Version Control)" -ForegroundColor Green  
Write-Host "✓ Node.js (JavaScript Runtime)" -ForegroundColor Green
Write-Host "✓ Python (Programming Language)" -ForegroundColor Green
Write-Host "✓ PowerShell 7" -ForegroundColor Green

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Run the setup_dev_machine.ps1 script as Administrator" -ForegroundColor White
Write-Host "2. Connect your 2.5 SATA drive and initialize it" -ForegroundColor White
Write-Host "3. Create your first project in C:\Dev\Projects\" -ForegroundColor White

Read-Host "Press Enter to exit"