#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Deploy GenX_FX Docker image to Azure Container Registry and Azure App Service

.DESCRIPTION
    This script builds a Docker image, pushes it to Azure Container Registry (ACR),
    and deploys it to Azure App Service or Azure Container Instances.

.PARAMETER ResourceGroup
    The Azure resource group name

.PARAMETER ACRName
    The Azure Container Registry name

.PARAMETER AppName
    The Azure App Service or Container Instance name

.PARAMETER Location
    Azure region (default: eastus)

.PARAMETER DeploymentType
    Deployment target: 'webapp' or 'aci' (default: webapp)

.EXAMPLE
    .\deploy-to-azure.ps1 -ResourceGroup "genxfx-rg" -ACRName "genxfxacr" -AppName "genxfx-app"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroup,
    
    [Parameter(Mandatory=$true)]
    [string]$ACRName,
    
    [Parameter(Mandatory=$true)]
    [string]$AppName,
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('webapp', 'aci')]
    [string]$DeploymentType = "webapp"
)

# Script configuration
$ErrorActionPreference = "Stop"
$ImageName = "genxfx"
$ImageTag = "latest"
$FullImageName = "${ACRName}.azurecr.io/${ImageName}:${ImageTag}"

Write-Host "🚀 GenX_FX Azure Deployment Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Azure CLI installation
Write-Host "📋 Step 1: Checking prerequisites..." -ForegroundColor Yellow
try {
    $azVersion = az --version
    Write-Host "✅ Azure CLI is installed" -ForegroundColor Green
} catch {
    Write-Error "❌ Azure CLI is not installed. Please install from: https://aka.ms/installazurecliwindows"
    exit 1
}

# Check Docker
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Error "❌ Docker is not installed. Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
}

# Step 2: Azure login check
Write-Host ""
Write-Host "📋 Step 2: Checking Azure login..." -ForegroundColor Yellow
$account = az account show 2>$null
if (-not $account) {
    Write-Host "⚠️  Not logged in to Azure. Initiating login..." -ForegroundColor Yellow
    az login
} else {
    Write-Host "✅ Already logged in to Azure" -ForegroundColor Green
    $accountInfo = $account | ConvertFrom-Json
    Write-Host "   Subscription: $($accountInfo.name)" -ForegroundColor Gray
}

# Step 3: Create or verify resource group
Write-Host ""
Write-Host "📋 Step 3: Setting up resource group..." -ForegroundColor Yellow
$rgExists = az group exists --name $ResourceGroup
if ($rgExists -eq "false") {
    Write-Host "Creating resource group: $ResourceGroup" -ForegroundColor Yellow
    az group create --name $ResourceGroup --location $Location
    Write-Host "✅ Resource group created" -ForegroundColor Green
} else {
    Write-Host "✅ Resource group already exists" -ForegroundColor Green
}

# Step 4: Create or verify Azure Container Registry
Write-Host ""
Write-Host "📋 Step 4: Setting up Azure Container Registry..." -ForegroundColor Yellow
$acrExists = az acr show --name $ACRName --resource-group $ResourceGroup 2>$null
if (-not $acrExists) {
    Write-Host "Creating Azure Container Registry: $ACRName" -ForegroundColor Yellow
    az acr create --resource-group $ResourceGroup --name $ACRName --sku Basic --location $Location
    Write-Host "✅ ACR created" -ForegroundColor Green
} else {
    Write-Host "✅ ACR already exists" -ForegroundColor Green
}

# Enable admin user for ACR
az acr update --name $ACRName --admin-enabled true

# Step 5: Build Docker image
Write-Host ""
Write-Host "📋 Step 5: Building Docker image..." -ForegroundColor Yellow
Write-Host "Building image: $FullImageName" -ForegroundColor Gray
docker build -t ${ImageName}:${ImageTag} .
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Docker build failed"
    exit 1
}
Write-Host "✅ Docker image built successfully" -ForegroundColor Green

# Step 6: Tag and push to ACR
Write-Host ""
Write-Host "📋 Step 6: Pushing image to Azure Container Registry..." -ForegroundColor Yellow
az acr login --name $ACRName

docker tag ${ImageName}:${ImageTag} $FullImageName
docker push $FullImageName
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Docker push failed"
    exit 1
}
Write-Host "✅ Image pushed to ACR successfully" -ForegroundColor Green

# Step 7: Deploy based on deployment type
Write-Host ""
Write-Host "📋 Step 7: Deploying to Azure..." -ForegroundColor Yellow

if ($DeploymentType -eq "webapp") {
    # Deploy to Azure App Service
    Write-Host "Deploying to Azure App Service: $AppName" -ForegroundColor Yellow
    
    # Create App Service Plan if it doesn't exist
    $planName = "${AppName}-plan"
    $planExists = az appservice plan show --name $planName --resource-group $ResourceGroup 2>$null
    if (-not $planExists) {
        az appservice plan create --name $planName --resource-group $ResourceGroup --is-linux --sku B1 --location $Location
    }
    
    # Create or update Web App
    $webAppExists = az webapp show --name $AppName --resource-group $ResourceGroup 2>$null
    if (-not $webAppExists) {
        az webapp create --resource-group $ResourceGroup --plan $planName --name $AppName --deployment-container-image-name $FullImageName
    } else {
        az webapp config container set --name $AppName --resource-group $ResourceGroup --docker-custom-image-name $FullImageName
    }
    
    # Configure ACR credentials
    $acrUsername = az acr credential show --name $ACRName --query username -o tsv
    $acrPassword = az acr credential show --name $ACRName --query "passwords[0].value" -o tsv
    
    az webapp config container set --name $AppName --resource-group $ResourceGroup `
        --docker-registry-server-url "https://${ACRName}.azurecr.io" `
        --docker-registry-server-user $acrUsername `
        --docker-registry-server-password $acrPassword
    
    # Configure app settings (add your environment variables here)
    az webapp config appsettings set --name $AppName --resource-group $ResourceGroup --settings `
        WEBSITES_PORT=8080 `
        PYTHONUNBUFFERED=1
    
    Write-Host "✅ Deployed to Azure App Service" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Application URL: https://${AppName}.azurewebsites.net" -ForegroundColor Cyan
    
} elseif ($DeploymentType -eq "aci") {
    # Deploy to Azure Container Instances
    Write-Host "Deploying to Azure Container Instances: $AppName" -ForegroundColor Yellow
    
    $acrUsername = az acr credential show --name $ACRName --query username -o tsv
    $acrPassword = az acr credential show --name $ACRName --query "passwords[0].value" -o tsv
    
    az container create --resource-group $ResourceGroup --name $AppName `
        --image $FullImageName `
        --cpu 1 --memory 1.5 `
        --registry-login-server "${ACRName}.azurecr.io" `
        --registry-username $acrUsername `
        --registry-password $acrPassword `
        --dns-name-label $AppName `
        --ports 8080 3000 `
        --location $Location
    
    Write-Host "✅ Deployed to Azure Container Instances" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Application URL: http://${AppName}.${Location}.azurecontainer.io:8080" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Configure environment variables in Azure Portal" -ForegroundColor Gray
Write-Host "   2. Set up custom domain (if needed)" -ForegroundColor Gray
Write-Host "   3. Configure SSL certificate" -ForegroundColor Gray
Write-Host "   4. Monitor application logs" -ForegroundColor Gray
Write-Host ""
Write-Host "📊 View logs:" -ForegroundColor Yellow
if ($DeploymentType -eq "webapp") {
    Write-Host "   az webapp log tail --name $AppName --resource-group $ResourceGroup" -ForegroundColor Gray
} else {
    Write-Host "   az container logs --name $AppName --resource-group $ResourceGroup" -ForegroundColor Gray
}
