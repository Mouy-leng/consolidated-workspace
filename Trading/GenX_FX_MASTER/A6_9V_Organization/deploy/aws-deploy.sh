#!/bin/bash

# AWS Deployment Script for GenX Trading Platform
# This script automates the deployment of the GenX Trading Platform to AWS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="genx-trading-platform"
AWS_REGION="us-east-1"
ENVIRONMENT="production"
STACK_NAME="${ENVIRONMENT}-${PROJECT_NAME}"

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

# Function to check if AWS CLI is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    print_success "AWS CLI is installed"
}

# Function to check if AWS credentials are configured
check_aws_credentials() {
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials are not configured. Please run 'aws configure' first."
        exit 1
    fi
    print_success "AWS credentials are configured"
}

# Function to create ECR repository
create_ecr_repository() {
    local repo_name="$1"
    print_status "Creating ECR repository: $repo_name"
    
    if aws ecr describe-repositories --repository-names "$repo_name" --region "$AWS_REGION" &> /dev/null; then
        print_warning "ECR repository $repo_name already exists"
    else
        aws ecr create-repository --repository-name "$repo_name" --region "$AWS_REGION"
        print_success "ECR repository $repo_name created"
    fi
}

# Function to build and push Docker image
build_and_push_image() {
    local image_name="$1"
    local ecr_repo="$2"
    local account_id=$(aws sts get-caller-identity --query Account --output text)
    local ecr_uri="${account_id}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ecr_repo}"
    
    print_status "Building Docker image: $image_name"
    
    # Get ECR login token
    aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ecr_uri"
    
    # Build image
    docker build -f Dockerfile.production -t "$image_name" .
    
    # Tag image
    docker tag "$image_name:latest" "$ecr_uri:latest"
    
    # Push image
    docker push "$ecr_uri:latest"
    
    print_success "Docker image pushed to ECR: $ecr_uri:latest"
}

# Function to deploy CloudFormation stack
deploy_cloudformation_stack() {
    print_status "Deploying CloudFormation stack: $STACK_NAME"
    
    aws cloudformation deploy \
        --template-file deploy/aws-deployment.yml \
        --stack-name "$STACK_NAME" \
        --parameter-overrides \
            Environment="$ENVIRONMENT" \
        --capabilities CAPABILITY_IAM \
        --region "$AWS_REGION"
    
    print_success "CloudFormation stack deployed successfully"
}

# Function to get stack outputs
get_stack_outputs() {
    print_status "Getting stack outputs..."
    
    local alb_dns=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text)
    
    local db_endpoint=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
        --output text)
    
    local redis_endpoint=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`RedisEndpoint`].OutputValue' \
        --output text)
    
    print_success "Deployment completed successfully!"
    echo ""
    echo "=== Deployment Information ==="
    echo "Load Balancer DNS: $alb_dns"
    echo "Database Endpoint: $db_endpoint"
    echo "Redis Endpoint: $redis_endpoint"
    echo "Stack Name: $STACK_NAME"
    echo "Region: $AWS_REGION"
    echo ""
    echo "You can access your application at: http://$alb_dns"
}

# Function to set up environment variables in AWS Systems Manager
setup_environment_variables() {
    print_status "Setting up environment variables in AWS Systems Manager..."
    
    # List of environment variables to store
    declare -A env_vars=(
        ["DATABASE_URL"]="postgresql://genxadmin:$(aws secretsmanager get-secret-value --secret-id "${ENVIRONMENT}-genx-db-password" --region "$AWS_REGION" --query SecretString --output text | jq -r .password)@$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$AWS_REGION" --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' --output text):5432/genx"
        ["REDIS_URL"]="redis://$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$AWS_REGION" --query 'Stacks[0].Outputs[?OutputKey==`RedisEndpoint`].OutputValue' --output text):6379"
        ["SECRET_KEY"]="$(openssl rand -hex 32)"
        ["ENVIRONMENT"]="$ENVIRONMENT"
        ["LOG_LEVEL"]="INFO"
    )
    
    for key in "${!env_vars[@]}"; do
        print_status "Setting $key in Parameter Store"
        aws ssm put-parameter \
            --name "/genx/$ENVIRONMENT/$key" \
            --value "${env_vars[$key]}" \
            --type "SecureString" \
            --region "$AWS_REGION" \
            --overwrite
    done
    
    print_success "Environment variables configured in AWS Systems Manager"
}

# Function to create SSL certificate (if domain is provided)
create_ssl_certificate() {
    if [ -n "$DOMAIN_NAME" ]; then
        print_status "Creating SSL certificate for domain: $DOMAIN_NAME"
        
        # Request certificate
        local cert_arn=$(aws acm request-certificate \
            --domain-name "$DOMAIN_NAME" \
            --subject-alternative-names "*.$DOMAIN_NAME" \
            --validation-method DNS \
            --region "$AWS_REGION" \
            --query 'CertificateArn' \
            --output text)
        
        print_success "SSL certificate requested: $cert_arn"
        print_warning "Please complete DNS validation for the certificate"
    fi
}

# Function to update ECS service
update_ecs_service() {
    print_status "Updating ECS service..."
    
    local cluster_name=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`ECSClusterName`].OutputValue' \
        --output text)
    
    local service_name="${ENVIRONMENT}-genx-service"
    
    # Force new deployment
    aws ecs update-service \
        --cluster "$cluster_name" \
        --service "$service_name" \
        --force-new-deployment \
        --region "$AWS_REGION"
    
    print_success "ECS service updated"
}

# Function to monitor deployment
monitor_deployment() {
    print_status "Monitoring deployment..."
    
    local cluster_name=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`ECSClusterName`].OutputValue' \
        --output text)
    
    local service_name="${ENVIRONMENT}-genx-service"
    
    # Wait for service to be stable
    aws ecs wait services-stable \
        --cluster "$cluster_name" \
        --services "$service_name" \
        --region "$AWS_REGION"
    
    print_success "Deployment is stable"
}

# Main deployment function
main() {
    print_status "Starting AWS deployment for GenX Trading Platform"
    echo ""
    
    # Pre-deployment checks
    check_aws_cli
    check_aws_credentials
    
    # Create ECR repositories
    create_ecr_repository "genx-api"
    create_ecr_repository "genx-discord-bot"
    create_ecr_repository "genx-telegram-bot"
    
    # Build and push Docker images
    build_and_push_image "genx-api" "genx-api"
    build_and_push_image "genx-discord-bot" "genx-discord-bot"
    build_and_push_image "genx-telegram-bot" "genx-telegram-bot"
    
    # Deploy CloudFormation stack
    deploy_cloudformation_stack
    
    # Set up environment variables
    setup_environment_variables
    
    # Create SSL certificate (if domain provided)
    if [ -n "$DOMAIN_NAME" ]; then
        create_ssl_certificate
    fi
    
    # Update ECS service
    update_ecs_service
    
    # Monitor deployment
    monitor_deployment
    
    # Get deployment outputs
    get_stack_outputs
    
    print_success "AWS deployment completed successfully!"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --region)
            AWS_REGION="$2"
            shift 2
            ;;
        --environment)
            ENVIRONMENT="$2"
            STACK_NAME="${ENVIRONMENT}-${PROJECT_NAME}"
            shift 2
            ;;
        --domain)
            DOMAIN_NAME="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --region REGION     AWS region (default: us-east-1)"
            echo "  --environment ENV   Environment name (default: production)"
            echo "  --domain DOMAIN     Domain name for SSL certificate"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main 