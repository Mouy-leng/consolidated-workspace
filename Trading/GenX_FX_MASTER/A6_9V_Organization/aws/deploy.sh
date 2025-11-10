#!/bin/bash

# GenX_FX AWS Deployment Script
# This script deploys the GenX_FX trading system to AWS

set -e

echo "🚀 Deploying GenX_FX Trading System to AWS..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Load AWS configuration
load_config() {
    if [ -f "aws_config.json" ]; then
        print_status "Loading AWS configuration..."
        export S3_BUCKET=$(jq -r '.s3_bucket' aws_config.json)
        export DYNAMODB_TABLE=$(jq -r '.dynamodb_table' aws_config.json)
        export CLOUDWATCH_LOG_GROUP=$(jq -r '.cloudwatch_log_group' aws_config.json)
        export AWS_REGION=$(jq -r '.region' aws_config.json)
        print_success "Configuration loaded"
    else
        print_error "aws_config.json not found. Please run setup.sh first."
        exit 1
    fi
}

# Create deployment package
create_deployment_package() {
    print_status "Creating deployment package..."
    
    # Create temporary directory
    mkdir -p temp_deploy
    
    # Copy necessary files
    cp -r core/ temp_deploy/
    cp -r api/ temp_deploy/
    cp -r utils/ temp_deploy/
    cp -r config/ temp_deploy/
    cp requirements.txt temp_deploy/
    cp main.py temp_deploy/
    
    # Create deployment script
    cat > temp_deploy/deploy_script.sh << 'EOF'
#!/bin/bash
set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting GenX_FX trading system..."
python main.py
EOF
    
    chmod +x temp_deploy/deploy_script.sh
    
    # Create zip file
    cd temp_deploy
    zip -r ../genx-fx-deployment.zip .
    cd ..
    
    # Upload to S3
    print_status "Uploading deployment package to S3..."
    aws s3 cp genx-fx-deployment.zip s3://$S3_BUCKET/
    
    # Cleanup
    rm -rf temp_deploy genx-fx-deployment.zip
    
    print_success "Deployment package created and uploaded"
}

# Create EC2 instance
create_ec2_instance() {
    print_status "Creating EC2 instance..."
    
    # Get latest Amazon Linux 2 AMI
    AMI_ID=$(aws ec2 describe-images \
        --owners amazon \
        --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" "Name=state,Values=available" \
        --query "reverse(sort_by(Images, &CreationDate))[:1].ImageId" \
        --output text)
    
    print_status "Using AMI: $AMI_ID"
    
    # Create security group
    SG_NAME="genx-fx-trading-sg"
    SG_ID=$(aws ec2 create-security-group \
        --group-name $SG_NAME \
        --description "Security group for GenX_FX trading system" \
        --query 'GroupId' --output text)
    
    # Add security group rules
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0
    
    aws ec2 authorize-security-group-ingress \
        --group-id $SG_ID \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0
    
    # Create EC2 instance
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --count 1 \
        --instance-type t3.medium \
        --key-name genx-fx-key \
        --security-group-ids $SG_ID \
        --iam-instance-profile Name=GenXFXEC2Role \
        --user-data file://aws/user_data.sh \
        --query 'Instances[0].InstanceId' --output text)
    
    print_success "EC2 instance created: $INSTANCE_ID"
    
    # Wait for instance to be running
    print_status "Waiting for instance to be running..."
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID
    
    # Get public IP
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids $INSTANCE_ID \
        --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
    
    print_success "Instance is running at: $PUBLIC_IP"
    
    # Save instance info
    cat > instance_info.json << EOF
{
    "instance_id": "$INSTANCE_ID",
    "public_ip": "$PUBLIC_IP",
    "security_group_id": "$SG_ID"
}
EOF
}

# Create user data script
create_user_data() {
    cat > aws/user_data.sh << 'EOF'
#!/bin/bash
yum update -y
yum install -y python3 python3-pip git

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Download deployment package
aws s3 cp s3://$S3_BUCKET/genx-fx-deployment.zip /tmp/
cd /tmp
unzip genx-fx-deployment.zip

# Install dependencies and start application
chmod +x deploy_script.sh
./deploy_script.sh
EOF
}

# Deploy to ECS (alternative to EC2)
deploy_to_ecs() {
    print_status "Deploying to ECS..."
    
    # Create ECS cluster
    aws ecs create-cluster --cluster-name genx-fx-cluster
    
    # Create task definition
    cat > task-definition.json << EOF
{
    "family": "genx-fx-task",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "512",
    "memory": "1024",
    "executionRoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "genx-fx-container",
            "image": "python:3.9-slim",
            "essential": true,
            "portMappings": [
                {
                    "containerPort": 8000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {
                    "name": "AWS_REGION",
                    "value": "$AWS_REGION"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "$CLOUDWATCH_LOG_GROUP",
                    "awslogs-region": "$AWS_REGION",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]
}
EOF
    
    # Register task definition
    aws ecs register-task-definition --cli-input-json file://task-definition.json
    
    print_success "ECS deployment configuration created"
}

# Main deployment function
main() {
    print_status "Starting GenX_FX AWS deployment..."
    
    # Load configuration
    load_config
    
    # Create deployment package
    create_deployment_package
    
    # Create user data script
    create_user_data
    
    # Choose deployment method
    echo "Choose deployment method:"
    echo "1. EC2 Instance"
    echo "2. ECS Fargate"
    read -p "Enter choice (1 or 2): " choice
    
    case $choice in
        1)
            create_ec2_instance
            ;;
        2)
            deploy_to_ecs
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
    
    print_success "Deployment completed successfully!"
    print_status "Next steps:"
    echo "1. SSH into your instance (if EC2): ssh -i genx-fx-key.pem ec2-user@<PUBLIC_IP>"
    echo "2. Monitor logs in CloudWatch: $CLOUDWATCH_LOG_GROUP"
    echo "3. Check S3 bucket for data: $S3_BUCKET"
}

# Run main function
main "$@" 