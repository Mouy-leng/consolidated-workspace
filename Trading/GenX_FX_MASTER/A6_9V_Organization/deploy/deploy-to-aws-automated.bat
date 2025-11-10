@echo off
echo 🚀 GenX FX - AWS Free Tier Deployment
echo =====================================

REM Configure AWS credentials (you'll need to provide access keys)
echo 📋 Configuring AWS CLI...
aws configure set default.region us-east-1
aws configure set default.output json

REM Create EC2 Key Pair if not exists
echo 🔑 Creating EC2 Key Pair...
aws ec2 create-key-pair --key-name genx-fx-key --query 'KeyMaterial' --output text > genx-fx-key.pem 2>nul

REM Deploy CloudFormation Stack
echo 🏗️ Deploying CloudFormation Stack...
aws cloudformation create-stack ^
    --stack-name genx-fx ^
    --template-body file://aws-free-tier-deploy.yml ^
    --parameters ParameterKey=KeyPairName,ParameterValue=genx-fx-key ^
    --capabilities CAPABILITY_IAM ^
    --region us-east-1

REM Wait for stack creation
echo ⏳ Waiting for stack creation to complete...
aws cloudformation wait stack-create-complete --stack-name genx-fx --region us-east-1

REM Get outputs
echo 📊 Getting deployment information...
aws cloudformation describe-stacks --stack-name genx-fx --query "Stacks[0].Outputs" --region us-east-1

echo ✅ AWS deployment initiated!
echo 📋 Check AWS Console: https://console.aws.amazon.com/cloudformation/
pause
