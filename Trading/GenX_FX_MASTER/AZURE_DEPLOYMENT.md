# Azure Deployment Guide for GenX_FX

This guide explains how to deploy the GenX_FX Docker image to Azure using Azure Container Registry (ACR) and Azure services.

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Azure Account**: Active Azure subscription ([Create free account](https://azure.microsoft.com/free/))
2. **Azure CLI**: Installed on your machine ([Installation guide](https://aka.ms/installazurecliwindows))
3. **Docker Desktop**: Installed and running ([Download](https://www.docker.com/products/docker-desktop))
4. **PowerShell 7+**: Already available on your system

## 🚀 Quick Start Deployment

### Option 1: Using the Automated Script (Recommended)

The easiest way to deploy is using the provided PowerShell script:

```powershell
# Deploy to Azure App Service (recommended for production)
.\deploy-to-azure.ps1 `
    -ResourceGroup "genxfx-rg" `
    -ACRName "genxfxacr" `
    -AppName "genxfx-app" `
    -Location "eastus" `
    -DeploymentType "webapp"

# OR Deploy to Azure Container Instances (cheaper, for testing)
.\deploy-to-azure.ps1 `
    -ResourceGroup "genxfx-rg" `
    -ACRName "genxfxacr" `
    -AppName "genxfx-app" `
    -Location "eastus" `
    -DeploymentType "aci"
```

**Parameters:**
- `ResourceGroup`: Azure resource group name (will be created if doesn't exist)
- `ACRName`: Container registry name (must be globally unique, lowercase alphanumeric only)
- `AppName`: Application name (must be globally unique)
- `Location`: Azure region (e.g., eastus, westus2, westeurope)
- `DeploymentType`: Choose "webapp" (App Service) or "aci" (Container Instances)

### Option 2: Manual Step-by-Step Deployment

#### Step 1: Login to Azure
```powershell
az login
```

#### Step 2: Create Resource Group
```powershell
az group create --name genxfx-rg --location eastus
```

#### Step 3: Create Azure Container Registry
```powershell
# Create ACR
az acr create --resource-group genxfx-rg --name genxfxacr --sku Basic

# Enable admin user
az acr update --name genxfxacr --admin-enabled true
```

#### Step 4: Build and Push Docker Image
```powershell
# Build Docker image locally
docker build -t genxfx:latest .

# Login to ACR
az acr login --name genxfxacr

# Tag image for ACR
docker tag genxfx:latest genxfxacr.azurecr.io/genxfx:latest

# Push to ACR
docker push genxfxacr.azurecr.io/genxfx:latest
```

#### Step 5A: Deploy to Azure App Service
```powershell
# Create App Service Plan
az appservice plan create --name genxfx-plan --resource-group genxfx-rg --is-linux --sku B1

# Create Web App
az webapp create --resource-group genxfx-rg --plan genxfx-plan --name genxfx-app --deployment-container-image-name genxfxacr.azurecr.io/genxfx:latest

# Configure ACR credentials
$acrUsername = az acr credential show --name genxfxacr --query username -o tsv
$acrPassword = az acr credential show --name genxfxacr --query "passwords[0].value" -o tsv

az webapp config container set --name genxfx-app --resource-group genxfx-rg `
    --docker-registry-server-url "https://genxfxacr.azurecr.io" `
    --docker-registry-server-user $acrUsername `
    --docker-registry-server-password $acrPassword

# Configure app settings
az webapp config appsettings set --name genxfx-app --resource-group genxfx-rg --settings WEBSITES_PORT=8080

# Access your app at: https://genxfx-app.azurewebsites.net
```

#### Step 5B: Deploy to Azure Container Instances (Alternative)
```powershell
# Get ACR credentials
$acrUsername = az acr credential show --name genxfxacr --query username -o tsv
$acrPassword = az acr credential show --name genxfxacr --query "passwords[0].value" -o tsv

# Create container instance
az container create --resource-group genxfx-rg --name genxfx-app `
    --image genxfxacr.azurecr.io/genxfx:latest `
    --cpu 1 --memory 1.5 `
    --registry-login-server genxfxacr.azurecr.io `
    --registry-username $acrUsername `
    --registry-password $acrPassword `
    --dns-name-label genxfx-app `
    --ports 8080 3000

# Access your app at: http://genxfx-app.eastus.azurecontainer.io:8080
```

## 🔧 Configuration

### Environment Variables

Configure environment variables in Azure Portal or via CLI:

```powershell
# For App Service
az webapp config appsettings set --name genxfx-app --resource-group genxfx-rg --settings `
    PYTHONUNBUFFERED=1 `
    FIREBASE_API_KEY="{{FIREBASE_API_KEY}}" `
    FIREBASE_PROJECT_ID="{{FIREBASE_PROJECT_ID}}" `
    DATABASE_URL="{{DATABASE_URL}}"

# For Container Instances
az container create --resource-group genxfx-rg --name genxfx-app `
    --image genxfxacr.azurecr.io/genxfx:latest `
    --environment-variables PYTHONUNBUFFERED=1 FIREBASE_API_KEY="{{FIREBASE_API_KEY}}"
```

### Custom Domain and SSL

```powershell
# Add custom domain
az webapp config hostname add --webapp-name genxfx-app --resource-group genxfx-rg --hostname www.yourdomain.com

# Enable HTTPS
az webapp update --name genxfx-app --resource-group genxfx-rg --https-only true
```

## 📊 Monitoring and Logs

### View Application Logs

```powershell
# App Service - Stream logs
az webapp log tail --name genxfx-app --resource-group genxfx-rg

# App Service - Download logs
az webapp log download --name genxfx-app --resource-group genxfx-rg

# Container Instances - View logs
az container logs --name genxfx-app --resource-group genxfx-rg

# Container Instances - Follow logs
az container logs --name genxfx-app --resource-group genxfx-rg --follow
```

### Enable Application Insights

```powershell
# Create Application Insights
az monitor app-insights component create --app genxfx-insights --location eastus --resource-group genxfx-rg

# Get instrumentation key
$instrumentationKey = az monitor app-insights component show --app genxfx-insights --resource-group genxfx-rg --query instrumentationKey -o tsv

# Add to app settings
az webapp config appsettings set --name genxfx-app --resource-group genxfx-rg --settings APPINSIGHTS_INSTRUMENTATIONKEY=$instrumentationKey
```

## 🔄 Updating the Application

To deploy a new version:

```powershell
# Rebuild and push
docker build -t genxfx:latest .
docker tag genxfx:latest genxfxacr.azurecr.io/genxfx:latest
docker push genxfxacr.azurecr.io/genxfx:latest

# Restart the app (it will pull the latest image)
az webapp restart --name genxfx-app --resource-group genxfx-rg

# OR for Container Instances, recreate the container
az container restart --name genxfx-app --resource-group genxfx-rg
```

Or simply run the deployment script again:
```powershell
.\deploy-to-azure.ps1 -ResourceGroup "genxfx-rg" -ACRName "genxfxacr" -AppName "genxfx-app"
```

## 💰 Cost Estimation

### Azure App Service (B1 Basic Plan)
- ~$13.14/month
- 1 core, 1.75 GB RAM
- Custom domains and SSL included
- Good for production workloads

### Azure Container Instances
- Pay-per-second pricing
- ~$0.0125/hour for 1 vCPU, 1.5 GB RAM
- ~$9/month if running 24/7
- Good for development/testing

### Azure Container Registry (Basic)
- ~$5/month
- 10 GB storage included

**Total estimated cost: $18-28/month**

## 🧹 Cleanup Resources

To avoid charges, delete resources when not needed:

```powershell
# Delete entire resource group (removes everything)
az group delete --name genxfx-rg --yes --no-wait

# Or delete individual resources
az webapp delete --name genxfx-app --resource-group genxfx-rg
az container delete --name genxfx-app --resource-group genxfx-rg --yes
az acr delete --name genxfxacr --resource-group genxfx-rg --yes
```

## 🔒 Security Best Practices

1. **Use Managed Identities**: Instead of ACR admin credentials
   ```powershell
   az webapp identity assign --name genxfx-app --resource-group genxfx-rg
   ```

2. **Enable HTTPS Only**
   ```powershell
   az webapp update --name genxfx-app --resource-group genxfx-rg --https-only true
   ```

3. **Store Secrets in Key Vault**
   ```powershell
   az keyvault create --name genxfx-vault --resource-group genxfx-rg --location eastus
   ```

4. **Enable Diagnostic Logging**
   ```powershell
   az webapp log config --name genxfx-app --resource-group genxfx-rg --docker-container-logging filesystem
   ```

## 🆘 Troubleshooting

### Issue: ACR name already exists
- ACR names must be globally unique. Try a different name like `genxfxacr2025` or `a69vgenxfxacr`

### Issue: Docker build fails
- Check that Docker Desktop is running
- Verify Dockerfile syntax
- Check requirements.txt for invalid packages

### Issue: Application not accessible
- Check if the app is running: `az webapp show --name genxfx-app --resource-group genxfx-rg --query state`
- Verify port configuration (should be 8080)
- Check logs for errors

### Issue: Authentication errors
- Re-login: `az login`
- Check subscription: `az account list`
- Verify permissions on the subscription

## 📚 Additional Resources

- [Azure Container Registry Documentation](https://docs.microsoft.com/azure/container-registry/)
- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- [Azure Container Instances Documentation](https://docs.microsoft.com/azure/container-instances/)
- [Azure CLI Reference](https://docs.microsoft.com/cli/azure/)

## 📞 Support

For issues specific to:
- **GenX_FX Application**: Contact your development team
- **Azure Services**: [Azure Support](https://azure.microsoft.com/support/)
- **Docker**: [Docker Documentation](https://docs.docker.com/)
