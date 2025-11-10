#!/bin/bash

# GitHub Secrets and Variables Setup for AMP System
# This script will configure all necessary secrets and variables

set -e

echo "🔐 Setting up GitHub Secrets and Variables for AMP System"
echo "========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if GitHub CLI is authenticated
check_gh_auth() {
    if gh auth status &> /dev/null; then
        print_success "GitHub CLI is authenticated"
        gh auth status
        return 0
    else
        print_warning "GitHub CLI not authenticated"
        return 1
    fi
}

# Get repository info
get_repo_info() {
    if [ -d ".git" ]; then
        REPO_URL=$(git remote get-url origin)
        if [[ $REPO_URL == *"github.com"* ]]; then
            REPO_NAME=$(echo $REPO_URL | sed 's/.*github\.com[:/]\([^/]*\/[^/]*\)\.git.*/\1/')
            print_success "Repository: $REPO_NAME"
            return 0
        fi
    fi
    print_error "Not a GitHub repository or remote not configured"
    return 1
}

# Setup Docker Hub secrets
setup_docker_secrets() {
    print_status "Setting up Docker Hub secrets..."
    
    # Docker Hub credentials (you'll need to provide these)
    echo ""
    echo "🐳 Docker Hub Configuration"
    echo "=========================="
    echo "Please provide your Docker Hub credentials:"
    echo ""
    echo "1. Go to: https://hub.docker.com/settings/security"
    echo "2. Create an access token"
    echo "3. Use your Docker Hub username and the access token"
    echo ""
    
    read -p "Docker Hub Username: " DOCKER_USERNAME
    read -s -p "Docker Hub Access Token: " DOCKER_PASSWORD
    echo ""
    
    if [ -n "$DOCKER_USERNAME" ] && [ -n "$DOCKER_PASSWORD" ]; then
        gh secret set DOCKER_USERNAME --body "$DOCKER_USERNAME"
        gh secret set DOCKER_PASSWORD --body "$DOCKER_PASSWORD"
        print_success "Docker Hub secrets configured"
    else
        print_warning "Docker Hub secrets not configured (skipped)"
    fi
}

# Setup AMP Token secret
setup_amp_secret() {
    print_status "Setting up AMP Token secret..."
    
    AMP_TOKEN="sgamp_user_01K1B28JVS8XWZQ3CEWJP8E5GN_97969aa27077d9e44e82ad554b337f2bda14a5e3eccf15165b1a09c24872495e"
    
    gh secret set AMP_TOKEN --body "$AMP_TOKEN"
    print_success "AMP Token secret configured"
}

# Setup AWS secrets
setup_aws_secrets() {
    print_status "Setting up AWS secrets..."
    
    echo ""
    echo "☁️ AWS Configuration"
    echo "==================="
    echo "Please provide your AWS credentials:"
    echo ""
    echo "1. Go to: https://console.aws.amazon.com"
    echo "2. Login: genxapitrading@gmail.com / Leng12345@#$01"
    echo "3. Click 'keamouyleng' → 'Security credentials'"
    echo "4. Create access key for CLI"
    echo ""
    
    read -p "AWS Access Key ID: " AWS_ACCESS_KEY_ID
    read -s -p "AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
    echo ""
    
    if [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
        gh secret set AWS_ACCESS_KEY_ID --body "$AWS_ACCESS_KEY_ID"
        gh secret set AWS_SECRET_ACCESS_KEY --body "$AWS_SECRET_ACCESS_KEY"
        print_success "AWS secrets configured"
    else
        print_warning "AWS secrets not configured (skipped)"
    fi
}

# Setup trading platform secrets
setup_trading_secrets() {
    print_status "Setting up trading platform secrets..."
    
    echo ""
    echo "📈 Trading Platform Configuration"
    echo "================================"
    echo "Please provide your FXCM API credentials:"
    echo ""
    echo "1. Go to: https://www.fxcm.com/markets/forex-trading-demo/"
    echo "2. Create a demo account"
    echo "3. Get your API credentials"
    echo ""
    
    read -p "FXCM API Key: " FXCM_API_KEY
    read -s -p "FXCM Secret Key: " FXCM_SECRET_KEY
    echo ""
    
    if [ -n "$FXCM_API_KEY" ] && [ -n "$FXCM_SECRET_KEY" ]; then
        gh secret set FXCM_API_KEY --body "$FXCM_API_KEY"
        gh secret set FXCM_SECRET_KEY --body "$FXCM_SECRET_KEY"
        print_success "FXCM secrets configured"
    else
        print_warning "FXCM secrets not configured (skipped)"
    fi
}

# Setup AI/ML API secrets
setup_ai_secrets() {
    print_status "Setting up AI/ML API secrets..."
    
    echo ""
    echo "🤖 AI/ML API Configuration"
    echo "=========================="
    echo "Please provide your AI API credentials:"
    echo ""
    echo "1. Gemini API: https://makersuite.google.com/app/apikey"
    echo "2. OpenAI API: https://platform.openai.com/api-keys"
    echo ""
    
    read -p "Gemini API Key: " GEMINI_API_KEY
    read -p "OpenAI API Key: " OPENAI_API_KEY
    
    if [ -n "$GEMINI_API_KEY" ]; then
        gh secret set GEMINI_API_KEY --body "$GEMINI_API_KEY"
        print_success "Gemini API key configured"
    fi
    
    if [ -n "$OPENAI_API_KEY" ]; then
        gh secret set OPENAI_API_KEY --body "$OPENAI_API_KEY"
        print_success "OpenAI API key configured"
    fi
    
    if [ -z "$GEMINI_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
        print_warning "AI API secrets not configured (skipped)"
    fi
}

# Setup database secrets
setup_database_secrets() {
    print_status "Setting up database secrets..."
    
    # Generate secure passwords
    POSTGRES_PASSWORD=$(openssl rand -base64 32)
    REDIS_PASSWORD=$(openssl rand -base64 32)
    
    gh secret set POSTGRES_PASSWORD --body "$POSTGRES_PASSWORD"
    gh secret set REDIS_PASSWORD --body "$REDIS_PASSWORD"
    
    print_success "Database secrets configured"
    print_warning "Generated passwords saved to GitHub secrets"
}

# Setup GitHub variables
setup_github_variables() {
    print_status "Setting up GitHub variables..."
    
    # Set repository variables
    gh variable set AMP_ENV --body "production"
    gh variable set DOCKER_IMAGE --body "keamouyleng/genx-fx"
    gh variable set AWS_REGION --body "us-east-1"
    gh variable set EC2_INSTANCE_TYPE --body "t2.micro"
    
    print_success "GitHub variables configured"
}

# Show current secrets
show_current_secrets() {
    print_status "Current GitHub secrets:"
    gh secret list
    echo ""
    
    print_status "Current GitHub variables:"
    gh variable list
    echo ""
}

# Create secrets summary
create_secrets_summary() {
    cat > GITHUB_SECRETS_SUMMARY.md << 'EOF'
# GitHub Secrets and Variables Summary

## 🔐 Required Secrets

### Docker Hub
- `DOCKER_USERNAME` - Your Docker Hub username
- `DOCKER_PASSWORD` - Your Docker Hub access token

### AWS
- `AWS_ACCESS_KEY_ID` - AWS access key for deployment
- `AWS_SECRET_ACCESS_KEY` - AWS secret key for deployment

### AMP System
- `AMP_TOKEN` - Your AMP authentication token

### Trading Platform (FXCM)
- `FXCM_API_KEY` - FXCM API key for trading
- `FXCM_SECRET_KEY` - FXCM secret key for trading

### AI/ML APIs
- `GEMINI_API_KEY` - Google Gemini API key
- `OPENAI_API_KEY` - OpenAI API key

### Database
- `POSTGRES_PASSWORD` - PostgreSQL database password
- `REDIS_PASSWORD` - Redis cache password

## 📊 Repository Variables

- `AMP_ENV` - Environment (production)
- `DOCKER_IMAGE` - Docker image name
- `AWS_REGION` - AWS region for deployment
- `EC2_INSTANCE_TYPE` - EC2 instance type

## 🚀 How to Set Secrets Manually

If the automated setup doesn't work, you can set secrets manually:

1. Go to your GitHub repository
2. Click "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret" for each secret above
4. Add the name and value for each secret

## 🔗 Useful Links

- [Docker Hub Access Tokens](https://hub.docker.com/settings/security)
- [AWS Console](https://console.aws.amazon.com)
- [FXCM Demo Account](https://www.fxcm.com/markets/forex-trading-demo/)
- [Gemini API](https://makersuite.google.com/app/apikey)
- [OpenAI API](https://platform.openai.com/api-keys)
EOF

    print_success "Secrets summary created: GITHUB_SECRETS_SUMMARY.md"
}

# Main function
main() {
    print_status "Starting GitHub secrets and variables setup..."
    
    # Check GitHub CLI authentication
    if ! check_gh_auth; then
        print_error "Please authenticate with GitHub first:"
        echo "gh auth login"
        exit 1
    fi
    
    # Get repository info
    if ! get_repo_info; then
        print_error "Please ensure you're in a GitHub repository"
        exit 1
    fi
    
    echo ""
    echo "🎯 Setting up secrets for repository: $REPO_NAME"
    echo ""
    
    # Setup all secrets
    setup_amp_secret
    setup_docker_secrets
    setup_aws_secrets
    setup_trading_secrets
    setup_ai_secrets
    setup_database_secrets
    setup_github_variables
    
    # Show current configuration
    show_current_secrets
    
    # Create summary
    create_secrets_summary
    
    echo ""
    print_success "GitHub secrets and variables setup complete!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Review the configured secrets above"
    echo "2. Check GITHUB_SECRETS_SUMMARY.md for details"
    echo "3. Trigger a GitHub Actions workflow to test"
    echo "4. Deploy to AWS using: ./aws/amp-deploy.sh"
    echo ""
}

# Run main function
main "$@"