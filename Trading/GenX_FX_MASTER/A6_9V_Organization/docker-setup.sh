#!/bin/bash

# Docker Registry Configuration Script for GenX FX
# This script sets up Docker registry access and builds the image

set -e

echo "🚀 Setting up Docker Registry for GenX FX..."

# Docker Registry Configuration
DOCKER_REGISTRY="keamouyleng"
DOCKER_USERNAME="keamouyleng"
DOCKER_PASSWORD="leng12345@#$%01"
DOCKER_TOKEN="t_wZXJXn95IiS2n__skVnWsvmcVP8"
DOCKER_IMAGE="genx-fx-dev"
DOCKER_TAG="latest"

# Login to Docker Registry
echo "🔐 Logging into Docker Registry..."
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

# Build the Docker image
echo "🏗️ Building Docker image..."
docker build -t "$DOCKER_REGISTRY/$DOCKER_IMAGE:$DOCKER_TAG" .

# Tag the image
echo "🏷️ Tagging image..."
docker tag "$DOCKER_REGISTRY/$DOCKER_IMAGE:$DOCKER_TAG" "$DOCKER_REGISTRY/$DOCKER_IMAGE:latest"

# Push the image to registry
echo "📤 Pushing image to registry..."
docker push "$DOCKER_REGISTRY/$DOCKER_IMAGE:$DOCKER_TAG"
docker push "$DOCKER_REGISTRY/$DOCKER_IMAGE:latest"

echo "✅ Docker setup completed successfully!"
echo "📋 Image: $DOCKER_REGISTRY/$DOCKER_IMAGE:$DOCKER_TAG"
echo "🔗 Registry: $DOCKER_REGISTRY"

# Create .env file for local development (if not exists)
if [ ! -f .env ]; then
    echo "📝 Creating .env file for local development..."
    cat > .env << EOF
# Docker Registry Configuration
DOCKER_REGISTRY=$DOCKER_REGISTRY
DOCKER_USERNAME=$DOCKER_USERNAME
DOCKER_IMAGE=$DOCKER_IMAGE
DOCKER_TAG=$DOCKER_TAG

# GitHub Repository
GITHUB_REPO=https://github.com/Mouy-leng/GenX-EA_Script.git
GITHUB_BRANCH=main

# Development Environment
NODE_ENV=development
PYTHON_ENV=development

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Database Configuration
DATABASE_URL=sqlite:///./genx_fx.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/genx_fx.log

# Security
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET=your-jwt-secret-here-change-in-production

# External APIs (to be configured)
GEMINI_API_KEY=your-gemini-api-key
NEWSDATA_API_KEY=your-newsdata-key
ALPHAVANTAGE_API_KEY=your-alphavantage-key
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret
BYBIT_API_KEY=your-bybit-api-key
BYBIT_API_SECRET=your-bybit-api-secret
EOF
    echo "✅ .env file created successfully!"
else
    echo "ℹ️ .env file already exists, skipping creation"
fi

echo "🎉 Docker setup completed! You can now use the devcontainer." 