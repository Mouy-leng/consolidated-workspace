# 🐳 Docker Deployment Guide for GenX FX Trading System

## 📋 Overview
This guide covers deploying the GenX FX Trading System using Docker containers.

## 🔗 Docker Hub Repository
- **Repository**: `keamouyleng/genx_docker`
- **Latest Tag**: `latest`
- **Full Image**: `keamouyleng/genx_docker:latest`

## 🚀 Quick Start

### 1. Pull and Run
```bash
# Pull the latest image
docker pull keamouyleng/genx_docker:latest

# Run the container
docker run -p 8000:8000 keamouyleng/genx_docker:latest
```

### 2. Build Locally
```bash
# Build the image
docker build -t keamouyleng/genx_docker:latest .

# Run locally
docker run -p 8000:8000 keamouyleng/genx_docker:latest
```

### 3. Use Deployment Script
```bash
# Run the automated deployment script
./deploy_docker.sh
```

## 📦 Docker Compose

### Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production
```bash
# Start production stack
docker-compose -f docker-compose.production.yml up -d

# Monitor services
docker-compose -f docker-compose.production.yml ps
```

## 🏗️ Architecture

### Multi-Stage Build
1. **Frontend Stage** (Node.js 18 Alpine)
   - Builds React frontend with Vite
   - Installs npm dependencies
   - Creates optimized build

2. **Backend Stage** (Python 3.11 Slim)
   - Installs Python dependencies
   - Copies backend source code
   - Prepares production environment

3. **Production Stage** (Python 3.11 Slim)
   - Combines frontend and backend
   - Runs FastAPI application
   - Exposes port 8000

### Services
- **API**: FastAPI backend (Port 8000)
- **Redis**: Caching and job queue (Port 6379)
- **PostgreSQL**: Database (Port 5432)
- **Celery**: Background task processing
- **Flower**: Task monitoring (Port 5555)
- **Nginx**: Reverse proxy (Port 80/443)

## 🔧 Configuration

### Environment Variables
Create `.env` file for local development:
```bash
# Database
DATABASE_URL=postgresql://genx_user:password@localhost:5432/genx_fx

# Redis
REDIS_URL=redis://localhost:6379

# API Keys (optional)
GEMINI_API_KEY=your_gemini_key
REDDIT_CLIENT_ID=your_reddit_client_id
NEWSDATA_API_KEY=your_news_api_key

# Application
NODE_ENV=production
PYTHON_VERSION=3.11
PORT=8000
```

### Production Environment
Create `.env.production` for production deployment:
```bash
# Database
POSTGRES_PASSWORD=secure_password

# Application
NODE_ENV=production
PYTHON_VERSION=3.11
PORT=8000
```

## 📊 Monitoring

### Health Checks
- **API Health**: `http://localhost:8000/health`
- **API Documentation**: `http://localhost:8000/docs`
- **Flower Dashboard**: `http://localhost:5555`

### Container Monitoring
```bash
# View running containers
docker ps

# View container logs
docker logs <container_id>

# Monitor resource usage
docker stats
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   
   # Stop conflicting service
   docker stop <container_id>
   ```

2. **Build Failures**
   ```bash
   # Clean Docker cache
   docker system prune -a
   
   # Rebuild without cache
   docker build --no-cache -t keamouyleng/genx_docker:latest .
   ```

3. **Database Connection Issues**
   ```bash
   # Check database container
   docker-compose logs postgres
   
   # Restart database
   docker-compose restart postgres
   ```

### Debug Commands
```bash
# Enter container shell
docker exec -it <container_id> /bin/bash

# View container environment
docker exec <container_id> env

# Check application logs
docker logs -f <container_id>
```

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale API service
docker-compose up -d --scale api=3

# Load balancer configuration
# Update nginx.conf for multiple API instances
```

### Resource Limits
```bash
# Set memory and CPU limits
docker run -m 1g --cpus=1 -p 8000:8000 keamouyleng/genx_docker:latest
```

## 🔐 Security

### Best Practices
- ✅ Non-root user in container
- ✅ Health checks enabled
- ✅ Resource limits configured
- ✅ Environment variables for secrets
- ✅ Network isolation with Docker Compose

### Security Scanning
```bash
# Scan image for vulnerabilities
docker scan keamouyleng/genx_docker:latest

# Update base images regularly
docker pull node:18-alpine
docker pull python:3.11-slim
```

## 📝 Deployment Checklist

### Pre-Deployment
- [ ] Docker installed and running
- [ ] Environment variables configured
- [ ] Ports available (8000, 5432, 6379)
- [ ] Database initialized
- [ ] SSL certificates ready (production)

### Deployment
- [ ] Image built successfully
- [ ] Health checks passing
- [ ] All services running
- [ ] Logs showing no errors
- [ ] API endpoints responding

### Post-Deployment
- [ ] Monitor application performance
- [ ] Set up logging aggregation
- [ ] Configure backups
- [ ] Set up monitoring alerts
- [ ] Document deployment

## 🎯 Success Indicators

- ✅ Container starts without errors
- ✅ Health endpoint returns 200 OK
- ✅ API documentation accessible
- ✅ Database connections working
- ✅ Background tasks processing
- ✅ Frontend loading correctly

## 📞 Support

### Useful Commands
```bash
# Quick status check
./deploy_docker.sh

# View all containers
docker ps -a

# Clean up unused resources
docker system prune

# View Docker Hub image info
docker inspect keamouyleng/genx_docker:latest
```

### Documentation
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**🎉 Your GenX FX Trading System is ready for Docker deployment!**