#!/bin/bash

# Exness EA Deployment Script for Google Cloud Run
set -e

echo "🚀 Deploying Exness MT4/MT5 EA to Google Cloud Run..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Load environment variables
load_env() {
    if [ -f ".env" ]; then
        print_status "Loading environment variables..."
        export $(cat .env | grep -v '^#' | xargs)
        print_success "Environment variables loaded"
    else
        print_error ".env file not found!"
        exit 1
    fi
}

# Build and deploy to Google Cloud Run
deploy_to_cloud_run() {
    print_status "Building and deploying to Google Cloud Run..."
    
    # Set project variables
    PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}
    SERVICE_NAME="genx-exness-ea"
    REGION=${GOOGLE_CLOUD_REGION:-"europe-west1"}

    if [ -z "$PROJECT_ID" ]; then
        print_error "Google Cloud project ID is not set."
        print_error "Please set the GOOGLE_CLOUD_PROJECT environment variable or run 'gcloud config set project YOUR_PROJECT_ID'"
        exit 1
    fi

    print_status "Project ID: $PROJECT_ID"
    print_status "Service Name: $SERVICE_NAME"
    print_status "Region: $REGION"
    
    # Build the container
    print_status "Building container..."
    gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME .
    
    # Deploy to Cloud Run
    print_status "Deploying to Cloud Run..."
    gcloud run deploy $SERVICE_NAME \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --set-env-vars "BROKER=exness,TRADING_MODE=live" \
        --memory 2Gi \
        --cpu 2 \
        --timeout 3600 \
        --concurrency 80
    
    print_success "Deployment completed!"
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    print_success "Service URL: $SERVICE_URL"
}

# Setup Exness EA configuration
setup_exness_config() {
    print_status "Setting up Exness EA configuration..."
    
    # Create Exness-specific config
    cat > config/exness_config.json << EOF
{
    "broker": "exness",
    "account_type": "real",
    "server": "Exness-Real",
    "symbols": ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"],
    "timeframes": ["M1", "M5", "M15", "H1", "H4", "D1"],
    "risk_percentage": 2.0,
    "max_positions": 5,
    "stop_loss_pips": 50,
    "take_profit_pips": 100,
    "ea_settings": {
        "magic_number": 123456,
        "slippage": 3,
        "retry_attempts": 3
    }
}
EOF
    
    print_success "Exness configuration created"
}

# Main deployment function
main() {
    print_status "Starting Exness EA deployment..."
    
    # Load environment variables
    load_env
    
    # Setup Exness configuration
    setup_exness_config
    
    # Deploy to Cloud Run
    deploy_to_cloud_run
    
    print_success "Exness EA deployment completed successfully!"
    print_status "Next steps:"
    echo "1. Monitor the service logs: gcloud logs tail --service=$SERVICE_NAME"
    echo "2. Check trading signals at: $SERVICE_URL/signals"
    echo "3. Monitor performance at: $SERVICE_URL/status"
}

# Run main function
main "$@" 