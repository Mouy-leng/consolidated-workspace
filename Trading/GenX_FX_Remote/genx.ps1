#!/usr/bin/env pwsh
<#
.SYNOPSIS
    GenX_FX Master Control Script
.DESCRIPTION
    Unified interface for managing the GenX_FX Remote trading system development environment.
    Provides high-quality code automation with IDE integration and secure credential management.
.PARAMETER Command
    The command to execute
.EXAMPLE
    .\genx.ps1 status
    .\genx.ps1 dev start
    .\genx.ps1 secrets setup
    .\genx.ps1 ide pycharm
#>

[CmdletBinding()]
param(
    [Parameter(Position=0, Mandatory=$false)]
    [ValidateSet(
        "status", "dev", "secrets", "ide", "ssh", "test", "deploy", 
        "backup", "clean", "logs", "env", "help"
    )]
    [string]$Command = "status",
    
    [Parameter(Position=1, Mandatory=$false)]
    [string]$SubCommand = "",
    
    [Parameter(HelpMessage="Additional parameters")]
    [string[]]$Args = @()
)

# Script metadata
$SCRIPT_VERSION = "1.0.0"
$PROJECT_NAME = "GenX_FX Remote"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = $SCRIPT_DIR

# Import environment if available
if ($env:GENX_PROJECT_ROOT) {
    $PROJECT_ROOT = $env:GENX_PROJECT_ROOT
}

# Set location to project root
Set-Location $PROJECT_ROOT

#region Utility Functions
function Write-Header {
    param([string]$Title)
    $border = "=" * 60
    Write-Host $border -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host $border -ForegroundColor Cyan
}

function Write-Success { param([string]$Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Warning { param([string]$Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message) Write-Host "✗ $Message" -ForegroundColor Red }
function Write-Info { param([string]$Message) Write-Host "ℹ $Message" -ForegroundColor Blue }

function Test-Command {
    param([string]$CommandName)
    return $null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

function Invoke-SafeCommand {
    param(
        [string]$Command,
        [string]$SuccessMessage = "",
        [string]$ErrorMessage = "Command failed"
    )
    
    try {
        Invoke-Expression $Command
        if ($LASTEXITCODE -eq 0 -and $SuccessMessage) {
            Write-Success $SuccessMessage
        }
        return $LASTEXITCODE -eq 0
    } catch {
        Write-Error "$ErrorMessage : $($_.Exception.Message)"
        return $false
    }
}
#endregion

#region Main Commands
function Show-Status {
    Write-Header "$PROJECT_NAME - Environment Status"
    
    Write-Host "`n🏠 Project Information:" -ForegroundColor Cyan
    Write-Host "  Version: $SCRIPT_VERSION"
    Write-Host "  Root: $PROJECT_ROOT"
    Write-Host "  Environment: $($env:GENX_ENVIRONMENT ?? 'Not Set')"
    
    Write-Host "`n🔐 Security:" -ForegroundColor Cyan
    $sshKey = Join-Path $env:USERPROFILE ".ssh\genx_fx_deploy"
    $secretsDir = $env:GENX_SECRETS_DIR
    
    if (Test-Path $sshKey) { Write-Success "SSH Key configured" } 
    else { Write-Warning "SSH Key not found" }
    
    if ($secretsDir -and (Test-Path $secretsDir)) { Write-Success "Secrets directory ready" }
    else { Write-Warning "Secrets directory not configured" }
    
    Write-Host "`n📁 Configuration Files:" -ForegroundColor Cyan
    $configs = @{
        ".env" = ".env"
        "requirements.txt" = "requirements.txt"
        "VS Code" = ".vscode\settings.json"
        "PyCharm" = ".idea\misc.xml"
    }
    
    foreach ($config in $configs.GetEnumerator()) {
        $path = Join-Path $PROJECT_ROOT $config.Value
        if (Test-Path $path) { Write-Success "$($config.Key) configured" }
        else { Write-Warning "$($config.Key) not found" }
    }
    
    Write-Host "`n🛠️ Tools:" -ForegroundColor Cyan
    $tools = @("python", "git", "code", "docker", "node")
    foreach ($tool in $tools) {
        if (Test-Command $tool) {
            try {
                $version = (& $tool --version 2>$null | Select-Object -First 1).Trim()
                Write-Success "$tool ($version)"
            } catch {
                Write-Success "$tool (installed)"
            }
        } else {
            Write-Warning "$tool not found"
        }
    }
    
    # Check if automation script is available
    if (& "$PROJECT_ROOT\genx_automation.ps1" status -ErrorAction SilentlyContinue) {
        Write-Host "`n📊 Recent automation logs available" -ForegroundColor Gray
    }
}

function Start-Dev {
    Write-Header "Starting Development Environment"
    
    # Check virtual environment
    $venvPath = Join-Path $PROJECT_ROOT "venv"
    if (-not (Test-Path $venvPath)) {
        Write-Info "Creating Python virtual environment..."
        Invoke-SafeCommand "python -m venv $venvPath" "Virtual environment created"
    }
    
    # Activate and install dependencies
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        Write-Info "Installing dependencies..."
        & $activateScript
        Invoke-SafeCommand "pip install -r requirements.txt" "Dependencies updated"
    }
    
    # Start services based on subcommand
    switch ($SubCommand) {
        "api" {
            Write-Info "Starting API server..."
            python api/main.py
        }
        "trading" {
            Write-Info "Starting trading engine..."
            python main.py
        }
        "ml" {
            Write-Info "Starting ML training..."
            python core/model_trainer.py
        }
        default {
            Write-Info "Development environment ready!"
            Write-Info "Available services:"
            Write-Host "  genx dev api     - Start API server" -ForegroundColor Gray
            Write-Host "  genx dev trading - Start trading engine" -ForegroundColor Gray  
            Write-Host "  genx dev ml      - Start ML training" -ForegroundColor Gray
        }
    }
}

function Manage-Secrets {
    Write-Header "Secret Management"
    
    switch ($SubCommand) {
        "setup" {
            Write-Info "Running credential setup..."
            & "$PROJECT_ROOT\setup_credentials.ps1" -Environment dev
        }
        "backup" {
            if ($env:GENX_SECRETS_DIR) {
                $backupFile = Join-Path $env:GENX_SECRETS_DIR "backups\secrets_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
                Write-Info "Creating secrets backup..."
                Compress-Archive -Path "$($env:GENX_SECRETS_DIR)\*" -DestinationPath $backupFile
                Write-Success "Backup created: $backupFile"
            } else {
                Write-Error "Secrets directory not configured"
            }
        }
        "open" {
            if ($env:GENX_SECRETS_DIR -and (Test-Path $env:GENX_SECRETS_DIR)) {
                explorer.exe $env:GENX_SECRETS_DIR
            } else {
                Write-Error "Secrets directory not found"
            }
        }
        default {
            if ($env:GENX_SECRETS_DIR) {
                Write-Info "Secrets directory: $env:GENX_SECRETS_DIR"
                Write-Info "Available commands:"
                Write-Host "  genx secrets setup  - Initial setup" -ForegroundColor Gray
                Write-Host "  genx secrets backup - Create backup" -ForegroundColor Gray
                Write-Host "  genx secrets open   - Open in explorer" -ForegroundColor Gray
            } else {
                Write-Warning "Secrets not configured. Run 'genx secrets setup'"
            }
        }
    }
}

function Manage-IDE {
    Write-Header "IDE Configuration"
    
    switch ($SubCommand) {
        "vscode" {
            Write-Info "Configuring VS Code..."
            & "$PROJECT_ROOT\genx_automation.ps1" setup -IDE vscode
            if (Test-Command "code") {
                code $PROJECT_ROOT
            }
        }
        "pycharm" {
            Write-Info "Configuring PyCharm..."
            & "$PROJECT_ROOT\genx_automation.ps1" setup -IDE pycharm
            Write-Info "See JETBRAINS_SETUP.md for manual configuration"
        }
        "intellij" {
            Write-Info "Configuring IntelliJ..."
            & "$PROJECT_ROOT\genx_automation.ps1" setup -IDE intellij  
            Write-Info "See JETBRAINS_SETUP.md for manual configuration"
        }
        default {
            Write-Info "Available IDEs:"
            Write-Host "  genx ide vscode   - Configure VS Code" -ForegroundColor Gray
            Write-Host "  genx ide pycharm  - Configure PyCharm" -ForegroundColor Gray
            Write-Host "  genx ide intellij - Configure IntelliJ" -ForegroundColor Gray
        }
    }
}

function Manage-SSH {
    Write-Header "SSH Configuration"
    
    $sshDir = Join-Path $env:USERPROFILE ".ssh"
    $keyPath = Join-Path $sshDir "genx_fx_deploy"
    
    switch ($SubCommand) {
        "status" {
            if (Test-Path $keyPath) {
                Write-Success "SSH key found: genx_fx_deploy"
                if (Test-Path "$keyPath.pub") {
                    $pubKey = Get-Content "$keyPath.pub" -Raw
                    Write-Info "Public key: $($pubKey.Trim())"
                }
            } else {
                Write-Warning "SSH key not found"
            }
            
            if (Test-Path (Join-Path $sshDir "config")) {
                Write-Success "SSH config found"
            } else {
                Write-Warning "SSH config not found"
            }
        }
        "test" {
            Write-Info "Testing SSH connection to GitHub..."
            ssh -T git@github.com
        }
        default {
            Manage-SSH -SubCommand "status"
            Write-Host "`nAvailable commands:" -ForegroundColor Gray
            Write-Host "  genx ssh status - Show SSH status" -ForegroundColor Gray
            Write-Host "  genx ssh test   - Test GitHub connection" -ForegroundColor Gray
        }
    }
}

function Run-Tests {
    Write-Header "Running Tests"
    
    $venvPython = Join-Path $PROJECT_ROOT "venv\Scripts\python.exe"
    $pythonCmd = if (Test-Path $venvPython) { $venvPython } else { "python" }
    
    switch ($SubCommand) {
        "unit" {
            & $pythonCmd -m pytest tests/unit/ -v
        }
        "integration" {
            & $pythonCmd -m pytest tests/integration/ -v
        }
        "coverage" {
            & $pythonCmd -m pytest --cov=core --cov-report=html tests/
        }
        default {
            & $pythonCmd -m pytest tests/ -v --tb=short
        }
    }
}

function Show-Logs {
    Write-Header "System Logs"
    
    $logDir = Join-Path $PROJECT_ROOT "logs"
    if (Test-Path $logDir) {
        $recentLogs = Get-ChildItem $logDir -File | Sort-Object LastWriteTime -Descending | Select-Object -First 10
        
        if ($recentLogs) {
            Write-Info "Recent log files:"
            $recentLogs | ForEach-Object {
                Write-Host "  $($_.Name) - $($_.LastWriteTime)" -ForegroundColor Gray
            }
            
            if ($SubCommand -eq "tail") {
                $latestLog = $recentLogs | Select-Object -First 1
                Write-Info "Tailing: $($latestLog.Name)"
                Get-Content $latestLog.FullName -Tail 20 -Wait
            }
        } else {
            Write-Info "No log files found"
        }
    } else {
        Write-Warning "Logs directory not found"
    }
}

function Edit-Environment {
    Write-Header "Environment Configuration"
    
    $envFile = Join-Path $PROJECT_ROOT ".env"
    if (Test-Path $envFile) {
        if (Test-Command "code") {
            code $envFile
        } else {
            notepad $envFile
        }
    } else {
        Write-Warning ".env file not found"
        $envExample = Join-Path $PROJECT_ROOT ".env.example"
        if (Test-Path $envExample) {
            Write-Info "Creating .env from template..."
            Copy-Item $envExample $envFile
            if (Test-Command "code") { code $envFile } else { notepad $envFile }
        }
    }
}

function Show-Help {
    Write-Header "$PROJECT_NAME - Command Reference"
    
    Write-Host @"

🚀 DEVELOPMENT COMMANDS:
  genx status              Show environment status
  genx dev [api|trading|ml] Start development services
  genx test [unit|integration] Run tests
  genx clean               Clean temporary files

🔐 SECURITY & CREDENTIALS:
  genx secrets setup       Initialize credential management
  genx secrets backup      Backup secrets securely
  genx secrets open        Open secrets directory
  genx ssh [status|test]   Manage SSH configuration

🛠️ IDE & TOOLS:
  genx ide [vscode|pycharm|intellij] Configure IDE
  genx env                 Edit environment variables
  genx logs [tail]         View system logs
  genx backup              Backup entire project

📚 EXAMPLES:
  genx dev api            # Start FastAPI server
  genx test unit          # Run unit tests only
  genx secrets setup      # First-time credential setup
  genx ide pycharm        # Configure PyCharm for GenX_FX
  genx ssh test          # Test GitHub SSH access

🔧 AUTOMATION:
All commands leverage high-quality automation scripts with:
- Secure credential management via Windows Credential Manager
- Cross-platform support (Windows/WSL/Linux)
- IDE integration (VS Code, PyCharm, IntelliJ)
- Comprehensive logging and monitoring

For advanced options, use the underlying automation scripts:
- setup_credentials.ps1  - Credential management
- genx_automation.ps1   - Full automation suite

"@ -ForegroundColor White
}
#endregion

#region Main Execution
Clear-Host
Write-Host "🎯 $PROJECT_NAME Control Center v$SCRIPT_VERSION" -ForegroundColor Magenta

# Execute command
switch ($Command) {
    "status" { Show-Status }
    "dev" { Start-Dev }
    "secrets" { Manage-Secrets }
    "ide" { Manage-IDE }
    "ssh" { Manage-SSH }
    "test" { Run-Tests }
    "logs" { Show-Logs }
    "env" { Edit-Environment }
    "backup" { & "$PROJECT_ROOT\genx_automation.ps1" backup }
    "clean" { & "$PROJECT_ROOT\genx_automation.ps1" clean }
    "help" { Show-Help }
    default { 
        Write-Error "Unknown command: $Command"
        Show-Help
    }
}

Write-Host "`n✨ Command completed successfully!" -ForegroundColor Green
#endregion