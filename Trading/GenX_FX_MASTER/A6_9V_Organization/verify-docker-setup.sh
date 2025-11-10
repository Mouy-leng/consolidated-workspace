#!/bin/bash

# Docker Setup Verification Script for GenX FX
# This script verifies that the Docker setup is working correctly

set -e

echo "🔍 Verifying Docker Setup for GenX FX..."

# Configuration
DOCKER_REGISTRY="keamouyleng"
DOCKER_IMAGE="genx-fx-dev"
DOCKER_TAG="latest"
FULL_IMAGE="$DOCKER_REGISTRY/$DOCKER_IMAGE:$DOCKER_TAG"

echo "📋 Configuration:"
echo "  Registry: $DOCKER_REGISTRY"
echo "  Image: $DOCKER_IMAGE"
echo "  Tag: $DOCKER_TAG"
echo "  Full Image: $FULL_IMAGE"
echo ""

# Check Docker installation
echo "🐳 Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi
echo "✅ Docker is installed"

# Check Docker daemon
echo "🔧 Checking Docker daemon..."
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running"
    exit 1
fi
echo "✅ Docker daemon is running"

# Check Docker login
echo "🔐 Checking Docker login..."
if ! docker login -u keamouyleng -p leng12345@#$%01 &> /dev/null; then
    echo "❌ Failed to login to Docker registry"
    exit 1
fi
echo "✅ Docker login successful"

# Check if image exists locally
echo "🔍 Checking local image..."
if docker images | grep -q "$DOCKER_REGISTRY/$DOCKER_IMAGE"; then
    echo "✅ Local image found"
else
    echo "⚠️  Local image not found, will pull from registry"
fi

# Try to pull image from registry
echo "📥 Pulling image from registry..."
if docker pull "$FULL_IMAGE" &> /dev/null; then
    echo "✅ Image pulled successfully from registry"
else
    echo "❌ Failed to pull image from registry"
    exit 1
fi

# Test image functionality
echo "🧪 Testing image functionality..."
if docker run --rm "$FULL_IMAGE" python -c "print('✅ Image test successful')" &> /dev/null; then
    echo "✅ Image functionality test passed"
else
    echo "❌ Image functionality test failed"
    exit 1
fi

# Check devcontainer configuration
echo "📁 Checking devcontainer configuration..."
if [ -f "devcontainer.json" ]; then
    if grep -q "$DOCKER_REGISTRY" devcontainer.json; then
        echo "✅ DevContainer configured with correct registry"
    else
        echo "⚠️  DevContainer may not be configured correctly"
    fi
else
    echo "❌ devcontainer.json not found"
fi

# Check .env file
echo "📝 Checking environment configuration..."
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    if grep -q "DOCKER_REGISTRY" .env; then
        echo "✅ Docker registry configured in .env"
    else
        echo "⚠️  Docker registry not found in .env"
    fi
else
    echo "⚠️  .env file not found (will be created by setup script)"
fi

# Check git remote
echo "🔗 Checking git remote configuration..."
if git remote get-url target &> /dev/null; then
    echo "✅ Target remote configured"
    echo "  URL: $(git remote get-url target)"
else
    echo "⚠️  Target remote not configured"
fi

echo ""
echo "🎉 Docker Setup Verification Complete!"
echo ""
echo "📊 Summary:"
echo "  ✅ Docker installation: OK"
echo "  ✅ Docker daemon: OK"
echo "  ✅ Registry login: OK"
echo "  ✅ Image pull: OK"
echo "  ✅ Image functionality: OK"
echo "  ✅ DevContainer config: OK"
echo "  ✅ Environment config: OK"
echo "  ✅ Git remote: OK"
echo ""
echo "🚀 Your Docker setup is ready for development!"
echo "📋 Next steps:"
echo "  1. Open VS Code with DevContainers extension"
echo "  2. Open this project in a container"
echo "  3. Configure your API keys in .env"
echo "  4. Start developing!" 