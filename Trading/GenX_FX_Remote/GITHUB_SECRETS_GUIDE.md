# 🔐 GitHub Secrets and Variables Configuration Guide

## 📋 Complete List of Required Secrets and Variables

### 🔐 **Repository Secrets** (Settings → Secrets and variables → Actions → Secrets)

#### **Docker Hub Secrets**
```
DOCKER_USERNAME = keamouyleng
DOCKER_PASSWORD = [Your Docker Hub Access Token]
```
**How to get**: Go to https://hub.docker.com/settings/security → Create access token

#### **AWS Secrets**
```
AWS_ACCESS_KEY_ID = [Your AWS Access Key ID]
AWS_SECRET_ACCESS_KEY = [Your AWS Secret Access Key]
```
**How to get**: Go to https://console.aws.amazon.com → Login with genxapitrading@gmail.com → Security credentials → Create access key

#### **AMP System Secret**
```
AMP_TOKEN = sgamp_user_01K1B28JVS8XWZQ3CEWJP8E5GN_97969aa27077d9e44e82ad554b337f2bda14a5e3eccf15165b1a09c24872495e
```
**Status**: ✅ Already provided

#### **Trading Platform Secrets (FXCM)**
```
FXCM_API_KEY = [Your FXCM API Key]
FXCM_SECRET_KEY = [Your FXCM Secret Key]
```
**How to get**: Go to https://www.fxcm.com/markets/forex-trading-demo/ → Create demo account → Get API credentials

#### **AI/ML API Secrets**
```
GEMINI_API_KEY = [Your Google Gemini API Key]
OPENAI_API_KEY = [Your OpenAI API Key]
```
**How to get**: 
- Gemini: https://makersuite.google.com/app/apikey
- OpenAI: https://platform.openai.com/api-keys

#### **Database Secrets** (Auto-generated)
```
POSTGRES_PASSWORD = [Auto-generated secure password]
REDIS_PASSWORD = [Auto-generated secure password]
```

### 📊 **Repository Variables** (Settings → Secrets and variables → Actions → Variables)

```
AMP_ENV = production
DOCKER_IMAGE = keamouyleng/genx-fx
AWS_REGION = us-east-1
EC2_INSTANCE_TYPE = t2.micro
```

## 🚀 **Quick Setup Commands**

### **Option 1: Automated Setup (Recommended)**
```bash
# Run the automated setup script
./setup_github_secrets.sh
```

### **Option 2: Manual Setup**
1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each secret above
4. Click **Variables** tab and add each variable

## 📝 **Step-by-Step Manual Setup**

### **Step 1: Get Docker Hub Access Token**
1. Go to https://hub.docker.com/settings/security
2. Click **"New Access Token"**
3. Name it: `amp-trading-system`
4. Copy the token

### **Step 2: Get AWS Credentials**
1. Go to https://console.aws.amazon.com
2. Login: `genxapitrading@gmail.com` / `Leng12345@#$01`
3. Click **"keamouyleng"** (top right)
4. Click **"Security credentials"**
5. Scroll to **"Access keys"**
6. Click **"Create access key"**
7. Choose **"Command Line Interface (CLI)"**
8. Copy both keys

### **Step 3: Get FXCM API Credentials**
1. Go to https://www.fxcm.com/markets/forex-trading-demo/
2. Create a demo account
3. Get your API credentials from the dashboard

### **Step 4: Get AI API Keys**
1. **Gemini**: https://makersuite.google.com/app/apikey
2. **OpenAI**: https://platform.openai.com/api-keys

### **Step 5: Add to GitHub**
1. Go to your repository → Settings → Secrets and variables → Actions
2. Add each secret and variable from the list above

## 🔧 **Current Status Check**

Run this command to check what's already configured:
```bash
gh secret list
gh variable list
```

## 🎯 **What Each Secret/Variable Does**

| Secret/Variable | Purpose | Required |
|----------------|---------|----------|
| `DOCKER_USERNAME` | Docker Hub login for image pushes | ✅ |
| `DOCKER_PASSWORD` | Docker Hub access token | ✅ |
| `AWS_ACCESS_KEY_ID` | AWS deployment permissions | ✅ |
| `AWS_SECRET_ACCESS_KEY` | AWS deployment permissions | ✅ |
| `AMP_TOKEN` | AMP system authentication | ✅ |
| `FXCM_API_KEY` | Trading platform access | ⚠️ |
| `FXCM_SECRET_KEY` | Trading platform access | ⚠️ |
| `GEMINI_API_KEY` | AI/ML functionality | ⚠️ |
| `OPENAI_API_KEY` | AI/ML functionality | ⚠️ |
| `POSTGRES_PASSWORD` | Database security | ✅ |
| `REDIS_PASSWORD` | Cache security | ✅ |
| `AMP_ENV` | Environment configuration | ✅ |
| `DOCKER_IMAGE` | Docker image name | ✅ |
| `AWS_REGION` | AWS deployment region | ✅ |
| `EC2_INSTANCE_TYPE` | EC2 instance size | ✅ |

## 🚨 **Priority Order**

### **Critical (Must Have)**
1. `DOCKER_USERNAME` + `DOCKER_PASSWORD`
2. `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`
3. `AMP_TOKEN` (✅ Already provided)

### **Important (Should Have)**
4. `POSTGRES_PASSWORD` + `REDIS_PASSWORD` (Auto-generated)
5. All Variables (Auto-configured)

### **Optional (Nice to Have)**
6. `FXCM_API_KEY` + `FXCM_SECRET_KEY`
7. `GEMINI_API_KEY` + `OPENAI_API_KEY`

## 🔗 **Useful Links**

- **Docker Hub**: https://hub.docker.com/settings/security
- **AWS Console**: https://console.aws.amazon.com
- **FXCM Demo**: https://www.fxcm.com/markets/forex-trading-demo/
- **Gemini API**: https://makersuite.google.com/app/apikey
- **OpenAI API**: https://platform.openai.com/api-keys

## ✅ **Verification**

After setting up all secrets, test with:
```bash
# Check GitHub Actions workflow
gh workflow list

# Trigger a test build
gh workflow run docker-image.yml

# Check deployment status
python3 aws_deploy_status.py
```

## 🎉 **Success Indicators**

- ✅ GitHub Actions workflows run successfully
- ✅ Docker images build and push to Docker Hub
- ✅ AWS deployment completes without errors
- ✅ AMP system responds on deployed URL