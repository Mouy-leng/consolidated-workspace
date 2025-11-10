#!/bin/bash

# GenX FX Quick Cloud Deploy Script
set -e

echo "🚀 GenX FX Cloud Deployment Script"
echo "=================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Creating from template..."
    cp .env.example .env
    echo "✅ Please edit .env file with your API keys and run again"
    exit 1
fi

# Build and test locally first
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.production.yml build

echo "🧪 Running quick health check..."
docker-compose -f docker-compose.production.yml up -d postgres redis mongo
sleep 10

# Test database connections
echo "🔍 Testing database connections..."
docker run --rm --network genx_fx_genx-network \
    -e DATABASE_URL="postgresql://genx_user:${DB_PASSWORD}@postgres:5432/genx_trading" \
    postgres:15-alpine pg_isready -h postgres -p 5432

echo "✅ Local build successful!"

# Push to GitHub to trigger deployment
echo "📤 Pushing to GitHub for cloud deployment..."
git add .
git commit -m "🚀 Deploy to cloud - $(date)"
git push origin main

echo "🎉 Deployment triggered! Check GitHub Actions for progress."
echo "📊 Monitor at: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^.]*\).*/\1/')/actions"