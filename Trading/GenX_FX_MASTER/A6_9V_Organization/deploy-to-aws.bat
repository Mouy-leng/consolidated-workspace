@echo off
REM Quick AWS Deployment Script for GenX Trading Platform (Windows)
REM Optimized for AWS Free Tier

echo ========================================
echo   GenX FX - AWS Free Tier Deployment
echo ========================================
echo.

REM Check if AWS CLI is installed
aws --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: AWS CLI is not installed!
    echo Please install from: https://aws.amazon.com/cli/
    echo Then run: aws configure
    pause
    exit /b 1
)

REM Check if AWS credentials are configured
aws sts get-caller-identity >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: AWS credentials not configured!
    echo Please run: aws configure
    echo Enter your AWS Access Key ID and Secret Access Key
    pause
    exit /b 1
)

echo ✅ AWS CLI configured successfully!
echo.

REM Set deployment variables
set AWS_REGION=us-east-1
set STACK_NAME=genx-fx-free-tier
set KEY_PAIR_NAME=genx-fx-key

echo 🚀 Starting deployment...
echo Region: %AWS_REGION%
echo Stack: %STACK_NAME%
echo.

REM Create key pair if it doesn't exist
echo 🔑 Creating SSH key pair...
aws ec2 describe-key-pairs --key-names %KEY_PAIR_NAME% --region %AWS_REGION% >nul 2>&1
if %errorlevel% neq 0 (
    aws ec2 create-key-pair --key-name %KEY_PAIR_NAME% --region %AWS_REGION% --query "KeyMaterial" --output text > %KEY_PAIR_NAME%.pem
    echo ✅ Key pair created: %KEY_PAIR_NAME%.pem
) else (
    echo ✅ Key pair %KEY_PAIR_NAME% already exists
)

REM Deploy CloudFormation stack
echo 📦 Deploying CloudFormation stack...
aws cloudformation deploy ^
    --template-file deploy\aws-free-tier-deploy.yml ^
    --stack-name %STACK_NAME% ^
    --parameter-overrides KeyPairName=%KEY_PAIR_NAME% ^
    --capabilities CAPABILITY_IAM ^
    --region %AWS_REGION%

if %errorlevel% neq 0 (
    echo ❌ Deployment failed!
    pause
    exit /b 1
)

echo ✅ Deployment completed successfully!
echo.

REM Get deployment outputs
echo 📋 Getting deployment information...
for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --region %AWS_REGION% --query "Stacks[0].Outputs[?OutputKey==`PublicIP`].OutputValue" --output text') do set PUBLIC_IP=%%i
for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --region %AWS_REGION% --query "Stacks[0].Outputs[?OutputKey==`InstanceId`].OutputValue" --output text') do set INSTANCE_ID=%%i

echo.
echo ========================================
echo   🎉 DEPLOYMENT SUCCESSFUL!
echo ========================================
echo.
echo 🌐 Trading Platform URL: http://%PUBLIC_IP%:8000
echo 📊 Real-time Signals: http://%PUBLIC_IP%:8000/MT4_Signals.csv
echo 🖥️  Instance ID: %INSTANCE_ID%
echo 🔗 SSH Access: ssh -i %KEY_PAIR_NAME%.pem ec2-user@%PUBLIC_IP%
echo.
echo 📝 Next Steps:
echo 1. Wait 2-3 minutes for the application to fully start
echo 2. Visit http://%PUBLIC_IP%:8000 to access your trading platform
echo 3. Check logs: ssh -i %KEY_PAIR_NAME%.pem ec2-user@%PUBLIC_IP% "sudo docker logs genx-fx"
echo.
echo 💰 Estimated Monthly Cost: FREE (12 months) then $12-15/month
echo.

pause
