#!/usr/bin/env pwsh
<#
.SYNOPSIS
    GenX_FX Development Automation & Cross-Platform Setup
.DESCRIPTION
    Comprehensive automation script for GenX_FX development environment including
    IDE integration, cross-platform support, and development workflow automation.
.PARAMETER Task
    Specific task to run (setup, dev, test, deploy, status)
.PARAMETER IDE
    IDE to configure (vscode, pycharm, intellij, all)
.PARAMETER Platform  
    Target platform (windows, linux, wsl, all)
#>

param(
    [Parameter(Position=0, HelpMessage="Task to execute")]
    [ValidateSet("setup", "dev", "test", "deploy", "status", "clean", "backup")]
    [string]$Task = "status",
    
    [Parameter(HelpMessage="IDE to configure")]
    [ValidateSet("vscode", "pycharm", "intellij", "all")]
    [string]$IDE = "all",
    
    [Parameter(HelpMessage="Target platform")]
    [ValidateSet("windows", "linux", "wsl", "all")]  
    [string]$Platform = "all",
    
    [Parameter(HelpMessage="Enable verbose output")]
    [switch]$VerboseOutput
)

# Import environment variables
if ($env:GENX_PROJECT_ROOT) {
    Set-Location $env:GENX_PROJECT_ROOT
}

$PROJECT_ROOT = $PWD.Path
$SECRETS_DIR = $env:GENX_SECRETS_DIR ?? (Join-Path $env:USERPROFILE ".genx_fx_secrets")
$LOG_DIR = Join-Path $PROJECT_ROOT "logs"

# Ensure log directory exists
if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
}

# Logging function
function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "SUCCESS")]
        [string]$Level = "INFO",
        [string]$LogFile = (Join-Path $LOG_DIR "genx_automation.log")
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Console output with colors
    $color = switch ($Level) {
        "SUCCESS" { "Green" }
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        default { "White" }
    }
    
    Write-Host $logEntry -ForegroundColor $color
    
    # File output
    try {
        Add-Content -Path $LogFile -Value $logEntry -ErrorAction SilentlyContinue
    } catch {
        # Silent fail for logging issues
    }
}

#region Core Functions
function Test-Dependencies {
    Write-Log "Checking dependencies..." "INFO"
    
    $dependencies = @{
        "Python" = @{
            Command = "python --version"
            Required = $true
        }
        "Git" = @{
            Command = "git --version" 
            Required = $true
        }
        "Node.js" = @{
            Command = "node --version"
            Required = $false
        }
        "Docker" = @{
            Command = "docker --version"
            Required = $false
        }
        "VS Code" = @{
            Command = "code --version"
            Required = $false
        }
    }
    
    $results = @{}
    
    foreach ($dep in $dependencies.Keys) {
        try {
            $output = Invoke-Expression $dependencies[$dep].Command 2>$null
            if ($LASTEXITCODE -eq 0) {
                $results[$dep] = @{Status = "✓"; Version = $output.Split("`n")[0]}
                Write-Log "$dep found: $($output.Split("`n")[0])" "SUCCESS"
            } else {
                throw "Command failed"
            }
        } catch {
            $results[$dep] = @{Status = "✗"; Version = "Not found"}
            $level = if ($dependencies[$dep].Required) { "ERROR" } else { "WARN" }
            Write-Log "$dep not found" $level
        }
    }
    
    return $results
}

function Setup-CrossPlatform {
    Write-Log "Setting up cross-platform environment..." "INFO"
    
    # Check for WSL
    try {
        $wslDistros = wsl --list --quiet 2>$null
        if ($LASTEXITCODE -eq 0 -and $wslDistros) {
            Write-Log "WSL detected. Configuring cross-platform support..." "SUCCESS"
            
            # Create shared project symlink in WSL
            $wslProjectPath = "/mnt/c/Users/$env:USERNAME/GenX_FX_Remote"
            $wslHomePath = wsl echo '${HOME}'
            
            wsl ln -sf $wslProjectPath "$wslHomePath/genx_fx" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Log "Created WSL project symlink: ~/genx_fx" "SUCCESS"
            }
            
            # Copy SSH keys to WSL
            $wslSshDir = "$wslHomePath/.ssh"
            wsl mkdir -p $wslSshDir 2>$null
            wsl cp /mnt/c/Users/$env:USERNAME/.ssh/config $wslSshDir/ 2>$null
            wsl cp /mnt/c/Users/$env:USERNAME/.ssh/genx_fx_deploy* $wslSshDir/ 2>$null
            wsl chmod 600 $wslSshDir/genx_fx_deploy* 2>$null
            
            Write-Log "SSH configuration synced to WSL" "SUCCESS"
            
            # Create WSL environment setup script
            $wslSetupScript = @"
#!/bin/bash
# GenX_FX WSL Environment Setup

export GENX_PROJECT_ROOT=/mnt/c/Users/$env:USERNAME/GenX_FX_Remote
export GENX_ENVIRONMENT=dev
export GENX_WSL_MODE=true

# Add to .bashrc if not already present
if ! grep -q "GENX_PROJECT_ROOT" ~/.bashrc; then
    echo "# GenX_FX Environment" >> ~/.bashrc
    echo "export GENX_PROJECT_ROOT=/mnt/c/Users/$env:USERNAME/GenX_FX_Remote" >> ~/.bashrc  
    echo "export GENX_ENVIRONMENT=dev" >> ~/.bashrc
    echo "export GENX_WSL_MODE=true" >> ~/.bashrc
    echo "cd ~/genx_fx" >> ~/.bashrc
fi

# Install Python dependencies in WSL if needed
if command -v python3 >/dev/null 2>&1; then
    cd ~/genx_fx
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt --user
    fi
fi

echo "WSL environment setup complete"
"@
            
            $wslSetupPath = Join-Path $PROJECT_ROOT "setup_wsl_env.sh"
            Set-Content -Path $wslSetupPath -Value $wslSetupScript
            
            # Execute WSL setup
            wsl bash $wslSetupPath.Replace('\', '/').Replace('C:', '/mnt/c')
            
            Write-Log "WSL environment configured" "SUCCESS"
        } else {
            Write-Log "WSL not available. Skipping WSL setup." "WARN"
        }
    } catch {
        Write-Log "Error setting up WSL: $($_.Exception.Message)" "ERROR"
    }
}

function Setup-IDEIntegration {
    param([string]$TargetIDE = "all")
    
    Write-Log "Setting up IDE integration for: $TargetIDE" "INFO"
    
    if ($TargetIDE -eq "vscode" -or $TargetIDE -eq "all") {
        Setup-VSCode
    }
    
    if ($TargetIDE -eq "pycharm" -or $TargetIDE -eq "all") {
        Setup-PyCharm
    }
    
    if ($TargetIDE -eq "intellij" -or $TargetIDE -eq "all") {
        Setup-IntelliJ
    }
}

function Setup-VSCode {
    Write-Log "Configuring VS Code..." "INFO"
    
    $vscodeDir = Join-Path $PROJECT_ROOT ".vscode"
    New-Item -ItemType Directory -Path $vscodeDir -Force | Out-Null
    
    # Enhanced VS Code settings
    $settings = @{
        "python.defaultInterpreterPath" = "./venv/Scripts/python.exe"
        "python.terminal.activateEnvironment" = $true
        "python.envFile" = "`${workspaceFolder}/.env"
        "python.analysis.autoImportCompletions" = $true
        "python.analysis.typeCheckingMode" = "basic"
        "python.linting.enabled" = $true
        "python.linting.flake8Enabled" = $true
        "python.formatting.provider" = "black"
        "python.formatting.blackArgs" = @("--line-length=88")
        "python.sortImports.args" = @("--profile", "black")
        "files.exclude" = @{
            "**/__pycache__" = $true
            "**/.pytest_cache" = $true
            "**/node_modules" = $true
            "**/*.pyc" = $true
            "**/.env" = $false
        }
        "terminal.integrated.env.windows" = @{
            "GENX_PROJECT_ROOT" = "`${workspaceFolder}"
            "GENX_ENVIRONMENT" = "dev"
        }
        "git.autofetch" = $true
        "git.enableSmartCommit" = $true
        "editor.formatOnSave" = $true
        "editor.codeActionsOnSave" = @{
            "source.organizeImports" = $true
        }
    } | ConvertTo-Json -Depth 10
    
    Set-Content -Path (Join-Path $vscodeDir "settings.json") -Value $settings
    
    # Launch configuration
    $launchConfig = @{
        "version" = "0.2.0"
        "configurations" = @(
            @{
                "name" = "GenX_FX Main"
                "type" = "python" 
                "request" = "launch"
                "program" = "`${workspaceFolder}/main.py"
                "console" = "integratedTerminal"
                "envFile" = "`${workspaceFolder}/.env"
                "cwd" = "`${workspaceFolder}"
            },
            @{
                "name" = "GenX_FX API Server"
                "type" = "python"
                "request" = "launch" 
                "program" = "`${workspaceFolder}/api/main.py"
                "console" = "integratedTerminal"
                "envFile" = "`${workspaceFolder}/.env"
            },
            @{
                "name" = "GenX_FX Tests"
                "type" = "python"
                "request" = "launch"
                "module" = "pytest"
                "args" = @("tests/", "-v")
                "envFile" = "`${workspaceFolder}/.env"
            }
        )
    } | ConvertTo-Json -Depth 10
    
    Set-Content -Path (Join-Path $vscodeDir "launch.json") -Value $launchConfig
    
    # Extensions recommendations
    $extensions = @{
        "recommendations" = @(
            "ms-python.python",
            "ms-python.flake8", 
            "ms-python.black-formatter",
            "ms-python.isort",
            "ms-vscode.vscode-typescript-next",
            "ms-vscode-remote.remote-wsl",
            "ms-azuretools.vscode-docker",
            "eamodio.gitlens",
            "bradlc.vscode-tailwindcss",
            "ms-vscode.powershell"
        )
    } | ConvertTo-Json -Depth 10
    
    Set-Content -Path (Join-Path $vscodeDir "extensions.json") -Value $extensions
    
    Write-Log "VS Code configuration complete" "SUCCESS"
}

function Setup-PyCharm {
    Write-Log "Setting up PyCharm configuration..." "INFO"
    
    # Create PyCharm project configuration
    $pycharmDir = Join-Path $PROJECT_ROOT ".idea"
    
    if (Test-Path $pycharmDir) {
        # Update existing configuration
        $miscXml = @"
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectRootManager" version="2" project-jdk-name="Python 3.11 (GenX_FX_Remote)" project-jdk-type="Python SDK" />
  <component name="PyCharmProfessionalAdvertiser">
    <option name="shown" value="true" />
  </component>
</project>
"@
        Set-Content -Path (Join-Path $pycharmDir "misc.xml") -Value $miscXml
        
        # Run configuration template
        $runConfigDir = Join-Path $pycharmDir "runConfigurations"
        New-Item -ItemType Directory -Path $runConfigDir -Force | Out-Null
        
        $mainRunConfig = @"
<component name="ProjectRunConfigurationManager">
  <configuration default="false" name="GenX_FX_Main" type="PythonConfigurationType" factoryName="Python" singleton="false">
    <module name="GenX_FX_Remote" />
    <option name="INTERPRETER_OPTIONS" value="" />
    <option name="PARENT_ENVS" value="true" />
    <envs>
      <env name="GENX_ENVIRONMENT" value="dev" />
      <env name="GENX_PROJECT_ROOT" value="$PROJECT_ROOT" />
    </envs>
    <option name="SDK_HOME" value="" />
    <option name="WORKING_DIRECTORY" value="$PROJECT_ROOT" />
    <option name="IS_MODULE_SDK" value="true" />
    <option name="ADD_CONTENT_ROOTS" value="true" />
    <option name="ADD_SOURCE_ROOTS" value="true" />
    <option name="SCRIPT_NAME" value="$PROJECT_ROOT\main.py" />
    <option name="PARAMETERS" value="" />
    <option name="SHOW_COMMAND_LINE" value="false" />
    <option name="EMULATE_TERMINAL" value="false" />
    <option name="MODULE_MODE" value="false" />
    <option name="REDIRECT_INPUT" value="false" />
    <option name="INPUT_FILE" value="" />
    <method v="2" />
  </configuration>
</component>
"@
        Set-Content -Path (Join-Path $runConfigDir "GenX_FX_Main.xml") -Value $mainRunConfig
        
        Write-Log "PyCharm configuration updated" "SUCCESS"
    } else {
        Write-Log "PyCharm project not detected. Manual setup required." "WARN"
        Write-Log "See JETBRAINS_SETUP.md for instructions" "INFO"
    }
}

function Setup-IntelliJ {
    Setup-PyCharm  # Same configuration works for IntelliJ with Python plugin
}

function Start-DevEnvironment {
    Write-Log "Starting development environment..." "INFO"
    
    # Check if virtual environment exists
    $venvPath = Join-Path $PROJECT_ROOT "venv"
    if (-not (Test-Path $venvPath)) {
        Write-Log "Creating Python virtual environment..." "INFO"
        python -m venv $venvPath
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Virtual environment created" "SUCCESS"
        } else {
            Write-Log "Failed to create virtual environment" "ERROR"
            return
        }
    }
    
    # Activate virtual environment and install dependencies
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        Write-Log "Installing Python dependencies..." "INFO"
        & $activateScript
        pip install -r requirements.txt --upgrade
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Dependencies installed successfully" "SUCCESS"
        } else {
            Write-Log "Some dependencies may have failed to install" "WARN"
        }
    }
    
    # Start development services
    Write-Log "Development environment ready!" "SUCCESS"
    Write-Log "Available commands:" "INFO"
    Write-Log "  genx-status    - Check environment status" "INFO"
    Write-Log "  genx-logs      - View recent logs" "INFO"
    Write-Log "  genx-secrets   - Open secrets directory" "INFO"
    Write-Log "  genx-env       - Edit environment file" "INFO"
}

function Show-Status {
    Write-Log "GenX_FX Development Environment Status" "INFO"
    
    # Environment info
    Write-Host "`n📍 Environment Information:" -ForegroundColor Cyan
    Write-Host "  Project Root: $PROJECT_ROOT"
    Write-Host "  Environment: $($env:GENX_ENVIRONMENT ?? 'Not Set')"
    Write-Host "  Secrets Dir: $($env:GENX_SECRETS_DIR ?? 'Not Set')"
    Write-Host "  SSH Key: $($env:GENX_SSH_KEY_PATH ?? 'Not Set')"
    
    # File checks
    Write-Host "`n📄 Configuration Files:" -ForegroundColor Cyan
    $configs = @{
        ".env" = Join-Path $PROJECT_ROOT ".env"
        "requirements.txt" = Join-Path $PROJECT_ROOT "requirements.txt" 
        "SSH Config" = Join-Path $env:USERPROFILE ".ssh\config"
        "SSH Key" = Join-Path $env:USERPROFILE ".ssh\genx_fx_deploy"
    }
    
    foreach ($config in $configs.GetEnumerator()) {
        $status = if (Test-Path $config.Value) { "✓" } else { "✗" }
        $color = if (Test-Path $config.Value) { "Green" } else { "Red" }
        Write-Host "  $($config.Key): $status" -ForegroundColor $color
    }
    
    # Dependencies
    Write-Host "`n🛠️ Dependencies:" -ForegroundColor Cyan
    Test-Dependencies | Out-Null
    
    # Recent logs
    Write-Host "`n📋 Recent Activity:" -ForegroundColor Cyan
    $logFile = Join-Path $LOG_DIR "genx_automation.log"
    if (Test-Path $logFile) {
        Get-Content $logFile | Select-Object -Last 5 | ForEach-Object {
            Write-Host "  $_" -ForegroundColor Gray
        }
    } else {
        Write-Host "  No recent activity" -ForegroundColor Gray
    }
}

function Backup-Project {
    Write-Log "Creating project backup..." "INFO"
    
    $backupDir = Join-Path $SECRETS_DIR "backups"
    $backupName = "genx_fx_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
    $backupPath = Join-Path $backupDir $backupName
    
    # Files to exclude from backup
    $excludePatterns = @(
        "venv\*",
        "node_modules\*", 
        "__pycache__\*",
        ".git\*",
        "*.pyc",
        "logs\*.log"
    )
    
    try {
        $sourceFiles = Get-ChildItem -Path $PROJECT_ROOT -Recurse | 
            Where-Object { 
                $file = $_
                -not ($excludePatterns | Where-Object { $file.FullName -like "*$_*" })
            }
            
        $sourceFiles | Compress-Archive -DestinationPath $backupPath -Force
        Write-Log "Project backed up to: $backupPath" "SUCCESS"
    } catch {
        Write-Log "Backup failed: $($_.Exception.Message)" "ERROR"
    }
}
#endregion

#region Main Execution
Write-Host "🚀 GenX_FX Development Automation" -ForegroundColor Cyan
Write-Host "Task: $Task | IDE: $IDE | Platform: $Platform" -ForegroundColor Gray

switch ($Task) {
    "setup" {
        Write-Log "Running full setup..." "INFO"
        Test-Dependencies | Out-Null
        Setup-CrossPlatform
        Setup-IDEIntegration -TargetIDE $IDE
        Write-Log "Setup complete!" "SUCCESS"
    }
    
    "dev" {
        Start-DevEnvironment
    }
    
    "status" {
        Show-Status
    }
    
    "backup" {
        Backup-Project
    }
    
    "test" {
        Write-Log "Running tests..." "INFO"
        $venvPython = Join-Path $PROJECT_ROOT "venv\Scripts\python.exe"
        if (Test-Path $venvPython) {
            & $venvPython -m pytest tests/ -v --tb=short
        } else {
            python -m pytest tests/ -v --tb=short
        }
    }
    
    "clean" {
        Write-Log "Cleaning temporary files..." "INFO"
        $cleanPatterns = @("**\__pycache__", "**\*.pyc", "**\.pytest_cache")
        foreach ($pattern in $cleanPatterns) {
            Get-ChildItem -Path $PROJECT_ROOT -Recurse -Force | 
                Where-Object { $_.FullName -like $pattern } | 
                Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        }
        Write-Log "Cleanup complete" "SUCCESS"
    }
    
    default {
        Write-Log "Unknown task: $Task" "ERROR"
        Write-Host "Available tasks: setup, dev, test, deploy, status, clean, backup" -ForegroundColor Yellow
    }
}
#endregion

Write-Host "`n✨ Task completed!" -ForegroundColor Green