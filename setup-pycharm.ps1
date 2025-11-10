# Setup PyCharm for consolidated workspace
# Configures PyCharm project settings and build configurations

$projectPath = "E:\Code\consolidated-workspace"
$ideaPath = Join-Path $projectPath ".idea"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PyCharm Project Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ensure .idea directory exists
if (-not (Test-Path $ideaPath)) {
    New-Item -ItemType Directory -Path $ideaPath -Force | Out-Null
    Write-Host "Created .idea directory" -ForegroundColor Green
}

# Create run configurations
$runConfigsPath = Join-Path $ideaPath "runConfigurations"
if (-not (Test-Path $runConfigsPath)) {
    New-Item -ItemType Directory -Path $runConfigsPath -Force | Out-Null
}

# Create requirements.txt if it doesn't exist
$requirementsPath = Join-Path $projectPath "requirements.txt"
if (-not (Test-Path $requirementsPath)) {
    $requirements = @"
# Consolidated Workspace Requirements
# Python packages for all projects

# Core dependencies
python-dotenv>=1.0.0
pyyaml>=6.0

# Trading system dependencies
ccxt>=4.0.0
pandas>=2.0.0
numpy>=1.24.0

# API and web
fastapi>=0.100.0
uvicorn>=0.23.0
requests>=2.31.0

# Data processing
python-dateutil>=2.8.0

# Development tools
pytest>=7.4.0
black>=23.0.0
flake8>=6.0.0
"@
    Set-Content -Path $requirementsPath -Value $requirements
    Write-Host "Created requirements.txt" -ForegroundColor Green
}

# Create .python-version file
$pythonVersionPath = Join-Path $projectPath ".python-version"
if (-not (Test-Path $pythonVersionPath)) {
    Set-Content -Path $pythonVersionPath -Value "3.11"
    Write-Host "Created .python-version" -ForegroundColor Green
}

# Create pyproject.toml for modern Python project management
$pyprojectPath = Join-Path $projectPath "pyproject.toml"
if (-not (Test-Path $pyprojectPath)) {
    $pyproject = @"
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "consolidated-workspace"
version = "1.0.0"
description = "Consolidated workspace for all trading system projects"
requires-python = ">=3.9"
dependencies = [
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0",
    "ccxt>=4.0.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
]

[tool.black]
line-length = 100
target-version = ['py39', 'py310', 'py311']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
"@
    Set-Content -Path $pyprojectPath -Value $pyproject
    Write-Host "Created pyproject.toml" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run: .\start-pycharm.ps1" -ForegroundColor White
Write-Host "2. In PyCharm: File > Settings > Project > Python Interpreter" -ForegroundColor White
Write-Host "3. Select or create a virtual environment" -ForegroundColor White
Write-Host "4. Install requirements: pip install -r requirements.txt" -ForegroundColor White
Write-Host ""

