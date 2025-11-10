#!/bin/bash

# Fix API Service Issues
echo "🔧 Fixing API service configuration..."

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env
    echo "DB_PASSWORD=$(python -c 'import secrets; print(secrets.token_urlsafe(16))')" >> .env
    echo "MONGO_PASSWORD=$(python -c 'import secrets; print(secrets.token_urlsafe(16))')" >> .env
    echo "REDIS_PASSWORD=$(python -c 'import secrets; print(secrets.token_urlsafe(16))')" >> .env
    echo "GRAFANA_PASSWORD=$(python -c 'import secrets; print(secrets.token_urlsafe(16))')" >> .env
fi

# Stop any running containers
docker-compose -f docker-compose.production.yml down

# Remove old containers and images
docker container prune -f
docker image prune -f

# Start databases first
echo "🗄️ Starting databases..."
docker-compose -f docker-compose.production.yml up -d postgres mongo redis

# Wait for databases
echo "⏳ Waiting for databases to be ready..."
sleep 30

# Start API service
echo "🚀 Starting API service..."
docker-compose -f docker-compose.production.yml up -d api

# Check API health
echo "🏥 Checking API health..."
sleep 15
curl -f http://localhost:8000/health || echo "❌ API health check failed"

# Start remaining services
echo "🔄 Starting remaining services..."
docker-compose -f docker-compose.production.yml up -d

echo "✅ All services started!"
docker-compose -f docker-compose.production.yml ps