# Deployment Guide

## 🚀 Complete Microservice Setup Summary

Your trading microservice is now fully configured with Docker and CI/CD pipeline!

## 📦 What's Been Created

### Application Files
- ✅ **src/index.js** - Express.js microservice with health checks
- ✅ **config/config.js** - Configuration management
- ✅ **tests/app.test.js** - Test suite with Jest
- ✅ **package.json** - Dependencies and scripts

### Docker Files
- ✅ **Dockerfile** - Multi-stage production build
- ✅ **docker-compose.yml** - Local development stack (PostgreSQL + Redis)
- ✅ **.dockerignore** - Optimize Docker builds

### Kubernetes Files (k8s/)
- ✅ **deployment.yml** - K8s deployment with autoscaling
- ✅ **configmap.yml** - Configuration management
- ✅ **ingress.yml** - External access configuration

### CI/CD Pipeline
- ✅ **.github/workflows/ci-cd.yml** - Complete GitHub Actions pipeline
  - Test stage (lint + tests)
  - Build stage (Docker + security scan)
  - Deploy to staging (develop branch)
  - Deploy to production (main branch)

### Documentation
- ✅ **README.md** - Complete project documentation
- ✅ **SETUP.md** - Step-by-step setup instructions
- ✅ **.env.example** - Environment template

## 🎯 Next Actions (In Order)

### 1. Test Locally (5 minutes)

```powershell
# Navigate to the project
cd trading-microservice

# Install dependencies
npm install

# Start Docker Compose stack
docker-compose up -d

# Check health
curl http://localhost:3000/health

# View logs
docker-compose logs -f trading-microservice
```

### 2. Push to GitHub (5 minutes)

```powershell
# Create repo on GitHub: https://github.com/organizations/A6-9V/repositories/new
# Name it: trading-microservice

# Add remote and push
git remote add origin https://github.com/A6-9V/trading-microservice.git
git add .
git commit -m "Initial setup: microservice with Docker and CI/CD"
git push -u origin develop
```

### 3. Configure GitHub Secrets (2 minutes)

Go to: `https://github.com/A6-9V/trading-microservice/settings/secrets/actions`

Add these secrets:
- `AWS_ACCESS_KEY_ID` (for deployment)
- `AWS_SECRET_ACCESS_KEY` (for deployment)

### 4. Verify CI/CD Pipeline (Automatic)

Once pushed, GitHub Actions will automatically:
1. ✅ Run tests
2. ✅ Build Docker image
3. ✅ Scan for vulnerabilities
4. ✅ Push to GitHub Container Registry
5. ✅ Deploy to staging (if on develop branch)

View pipeline: `https://github.com/A6-9V/trading-microservice/actions`

### 5. Deploy to Production

When ready for production:
```powershell
git checkout main
git merge develop
git push origin main
```

This triggers production deployment automatically.

## 🐳 Docker Commands Reference

### Local Development
```powershell
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# View logs
docker-compose logs -f

# Execute commands in container
docker-compose exec trading-microservice sh
```

### Build & Run Docker Image
```powershell
# Build image
docker build -t trading-microservice .

# Run container
docker run -p 3000:3000 `
  -e NODE_ENV=production `
  -e DB_HOST=host.docker.internal `
  trading-microservice

# Push to registry
docker tag trading-microservice ghcr.io/a6-9v/trading-microservice:latest
docker push ghcr.io/a6-9v/trading-microservice:latest
```

## ☸️ Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (EKS, GKE, AKS, or local)
- kubectl configured
- Docker image pushed to registry

### Deploy to K8s
```powershell
# Create namespace
kubectl create namespace trading

# Create secrets
kubectl create secret generic trading-secrets `
  --from-literal=db-host=YOUR_DB_HOST `
  --from-literal=db-name=trading_db `
  --from-literal=db-user=YOUR_USER `
  --from-literal=db-password=YOUR_PASSWORD `
  -n trading

# Create image pull secret for GHCR
kubectl create secret docker-registry ghcr-secret `
  --docker-server=ghcr.io `
  --docker-username=YOUR_GITHUB_USERNAME `
  --docker-password=YOUR_GITHUB_TOKEN `
  -n trading

# Deploy
kubectl apply -f k8s/configmap.yml -n trading
kubectl apply -f k8s/deployment.yml -n trading
kubectl apply -f k8s/ingress.yml -n trading
```

### Verify Deployment
```powershell
# Check pods
kubectl get pods -n trading -l app=trading-microservice

# Check service
kubectl get svc -n trading

# Check ingress
kubectl get ingress -n trading

# View logs
kubectl logs -f -l app=trading-microservice -n trading

# Port forward for testing
kubectl port-forward svc/trading-microservice 3000:80 -n trading
```

## 🔄 CI/CD Pipeline Details

### Workflow Triggers
- **Push to develop** → Deploy to Staging
- **Push to main** → Deploy to Production
- **Pull Request** → Run tests only

### Pipeline Stages

#### 1. Test Stage
- Checkout code
- Setup Node.js
- Install dependencies
- Run linter
- Run tests
- Upload coverage

#### 2. Build Stage
- Build Docker image (multi-arch)
- Push to GHCR
- Security scan with Trivy
- Upload security results

#### 3. Deploy Stage
- Configure cloud credentials
- Deploy to environment
- Health check
- Notification

### Customize Deployment

Edit `.github/workflows/ci-cd.yml`:

```yaml
# For SSH deployment
- name: Deploy to server
  run: |
    ssh deploy@your-server "
      docker pull ghcr.io/a6-9v/trading-microservice:latest &&
      docker-compose up -d
    "

# For Kubernetes
- name: Deploy to K8s
  run: |
    kubectl set image deployment/trading-microservice \
      trading-microservice=ghcr.io/a6-9v/trading-microservice:${{ github.sha }} \
      --namespace=production
```

## 📊 Monitoring & Observability

### Health Endpoints
- `GET /health` - Liveness probe (container is alive)
- `GET /ready` - Readiness probe (ready to accept traffic)

### Logs
```powershell
# Docker Compose
docker-compose logs -f trading-microservice

# Kubernetes
kubectl logs -f -l app=trading-microservice -n trading --tail=100
```

### Metrics (To Add)
Consider adding:
- Prometheus metrics endpoint
- Grafana dashboards
- Application Performance Monitoring (APM)
- Error tracking (Sentry, Rollbar)

## 🔒 Security Best Practices

✅ **Already Implemented:**
- Multi-stage Docker builds
- Non-root container user
- Security headers (Helmet.js)
- Secret management
- Image vulnerability scanning
- Resource limits

🎯 **Recommended Additions:**
- Rate limiting
- Input validation
- JWT authentication
- API key management
- Network policies (K8s)

## 🧪 Testing Strategy

### Current Tests
- Health endpoint tests
- API endpoint tests
- Error handling tests

### Recommended Tests to Add
```javascript
// Integration tests
describe('Database Integration', () => {
  // Test database connections
});

// Load tests
describe('Performance', () => {
  // Test under load
});

// E2E tests
describe('End-to-End', () => {
  // Full workflow tests
});
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Docker Build Fails
```powershell
# Clear Docker cache
docker system prune -a
docker-compose build --no-cache
```

#### 2. Health Check Fails
```powershell
# Check logs
docker logs trading-microservice

# Test endpoint
curl http://localhost:3000/health
```

#### 3. CI/CD Pipeline Fails
- Check GitHub Actions logs
- Verify secrets are configured
- Check Docker registry permissions
- Verify YAML syntax

#### 4. Kubernetes Pod Not Starting
```powershell
# Describe pod
kubectl describe pod <pod-name> -n trading

# Check events
kubectl get events -n trading --sort-by='.lastTimestamp'

# Check secrets
kubectl get secrets -n trading
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Express.js Guide](https://expressjs.com/en/guide/routing.html)
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)

## ✅ Deployment Checklist

Before going to production:

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Secrets properly managed
- [ ] Database migrations completed
- [ ] Monitoring setup
- [ ] Logging configured
- [ ] Backup strategy in place
- [ ] SSL/TLS certificates configured
- [ ] Load testing completed
- [ ] Security scan passed
- [ ] Documentation updated
- [ ] Team trained on deployment process

## 🎉 Success Criteria

Your deployment is successful when:
1. ✅ Health check returns 200 OK
2. ✅ Application logs show no errors
3. ✅ All pods are running (if using K8s)
4. ✅ API endpoints respond correctly
5. ✅ CI/CD pipeline completes successfully

---

**Organization**: A6-9V  
**Microservice**: Trading Microservice  
**Status**: Ready for Deployment 🚀
