#!/bin/bash

# Docker Deployment Script for GenX FX Trading System
# Docker Hub: keamouyleng/genx_docker

set -e

IMAGE_NAME="keamouyleng/genx_docker"
TAG="latest"
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"

echo "🐳 Docker Deployment for GenX FX Trading System"
echo "==============================================="
echo "Docker Hub: $IMAGE_NAME"
echo "Tag: $TAG"
echo ""

# Function to check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed or not available"
        echo "Please install Docker first: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo "✅ Docker is available"
}

# Function to build Docker image
build_image() {
    echo "🔨 Building Docker image..."
    echo "   Image: $FULL_IMAGE_NAME"
    echo "   Dockerfile: Dockerfile"
    echo ""
    
    docker build -t $FULL_IMAGE_NAME .
    
    if [ $? -eq 0 ]; then
        echo "✅ Docker image built successfully"
    else
        echo "❌ Docker build failed"
        exit 1
    fi
}

# Function to test Docker image locally
test_image() {
    echo "🧪 Testing Docker image locally..."
    
    # Stop any existing test container
    docker stop genx-test 2>/dev/null || true
    docker rm genx-test 2>/dev/null || true
    
    # Run the container in background
    CONTAINER_ID=$(docker run -d -p 8000:8000 --name genx-test $FULL_IMAGE_NAME)
    
    if [ $? -eq 0 ]; then
        echo "✅ Container started successfully"
        
        # Wait a bit for the application to start
        echo "⏳ Waiting for application to start..."
        sleep 15
        
        # Test health endpoint
        if curl -f http://localhost:8000/health &> /dev/null; then
            echo "✅ Health check passed"
        else
            echo "⚠️  Health check failed, but continuing..."
        fi
        
        # Stop and remove test container
        docker stop $CONTAINER_ID
        docker rm $CONTAINER_ID
        echo "🧹 Test container cleaned up"
    else
        echo "❌ Failed to start test container"
        exit 1
    fi
}

# Function to push to Docker Hub
push_to_dockerhub() {
    echo "📤 Pushing to Docker Hub..."
    echo "   Repository: $IMAGE_NAME"
    echo "   Tag: $TAG"
    echo ""
    
    docker push $FULL_IMAGE_NAME
    
    if [ $? -eq 0 ]; then
        echo "✅ Image pushed to Docker Hub successfully"
    else
        echo "❌ Failed to push to Docker Hub"
        exit 1
    fi
}

# Function to run with Docker Compose
run_with_compose() {
    echo "🚀 Running with Docker Compose..."
    
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo "✅ Docker Compose started successfully"
    else
        echo "❌ Docker Compose failed"
        exit 1
    fi
}

# Function to show deployment info
show_deployment_info() {
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo "===================================="
    echo ""
    echo "📊 Docker Hub Image:"
    echo "   $FULL_IMAGE_NAME"
    echo ""
    echo "🔗 Pull and run:"
    echo "   docker pull $FULL_IMAGE_NAME"
    echo "   docker run -p 8000:8000 $FULL_IMAGE_NAME"
    echo ""
    echo "📋 Docker Compose:"
    echo "   docker-compose up -d"
    echo ""
    echo "🌐 Access your application:"
    echo "   http://localhost:8000"
    echo "   http://localhost:8000/health"
    echo "   http://localhost:8000/docs"
    echo ""
    echo "📈 Monitor containers:"
    echo "   docker ps"
    echo "   docker logs <container_id>"
}

# Function to show manual steps
show_manual_steps() {
    echo ""
    echo "📋 Manual Deployment Steps"
    echo "=========================="
    echo ""
    echo "1. Build image:"
    echo "   docker build -t $FULL_IMAGE_NAME ."
    echo ""
    echo "2. Test locally:"
    echo "   docker run -p 8000:8000 $FULL_IMAGE_NAME"
    echo ""
    echo "3. Push to Docker Hub:"
    echo "   docker push $FULL_IMAGE_NAME"
    echo ""
    echo "4. Run with Docker Compose:"
    echo "   docker-compose up -d"
    echo ""
    echo "5. Production deployment:"
    echo "   docker-compose -f docker-compose.production.yml up -d"
}

# Main execution
main() {
    echo "🔍 Checking prerequisites..."
    check_docker
    
    echo ""
    echo "Choose deployment method:"
    echo "1. Build and test locally"
    echo "2. Build, test, and push to Docker Hub"
    echo "3. Run with Docker Compose"
    echo "4. Full deployment (build + test + push + compose)"
    echo "5. Show manual steps"
    echo "0. Exit"
    echo ""
    read -p "Enter your choice (0-5): " choice
    
    case $choice in
        1)
            echo ""
            echo "🔄 Build and test locally"
            echo "========================="
            build_image
            test_image
            show_deployment_info
            ;;
        2)
            echo ""
            echo "🔄 Build, test, and push to Docker Hub"
            echo "====================================="
            build_image
            test_image
            push_to_dockerhub
            show_deployment_info
            ;;
        3)
            echo ""
            echo "🔄 Run with Docker Compose"
            echo "=========================="
            run_with_compose
            show_deployment_info
            ;;
        4)
            echo ""
            echo "🔄 Full deployment"
            echo "=================="
            build_image
            test_image
            push_to_dockerhub
            run_with_compose
            show_deployment_info
            ;;
        5)
            show_manual_steps
            ;;
        0)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please enter 0-5."
            exit 1
            ;;
    esac
}

# Run main function
main