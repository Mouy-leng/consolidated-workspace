# Setup Instructions

## Quick Setup Guide

### 1. Initialize the Project

Navigate to the microservice directory:
```powershell
cd trading-microservice
```

### 2. Install Dependencies

```powershell
npm install
```

### 3. Create Environment File

Copy the example environment file:
```powershell
Copy-Item .env.example .env
```

Edit `.env` with your actual configuration values.

### 4. Test Locally with Docker Compose

Start all services:
```powershell
docker-compose up -d
```

Check health:
```powershell
curl http://localhost:3000/health
```

View logs:
```powershell
docker-compose logs -f
```

### 5. Run Tests

```powershell
npm test
```

### 6. Setup GitHub Repository (for CI/CD)

Create a new repository on GitHub under A6-9V organization:
```powershell
# Add remote (replace with your repo URL)
git remote add origin https://github.com/A6-9V/trading-microservice.git

# Initial commit
git add .
git commit -m "Initial microservice setup with Docker and CI/CD"

# Push both branches
git push -u origin develop
git checkout main
git merge develop
git push -u origin main
```

### 7. Configure GitHub Secrets

In your GitHub repository, go to Settings > Secrets and add:

- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
- Any other deployment secrets needed

### 8. Deploy to Kubernetes (if using K8s)

```powershell
# Create namespace (optional)
kubectl create namespace trading

# Create secrets
kubectl create secret generic trading-secrets `
  --from-literal=db-host=YOUR_DB_HOST `
  --from-literal=db-name=trading_db `
  --from-literal=db-user=YOUR_DB_USER `
  --from-literal=db-password=YOUR_DB_PASSWORD `
  -n trading

# Apply configurations
kubectl apply -f k8s/configmap.yml -n trading
kubectl apply -f k8s/deployment.yml -n trading
kubectl apply -f k8s/ingress.yml -n trading

# Verify deployment
kubectl get pods -n trading
kubectl get svc -n trading
```

## Next Steps

1. **Customize the application** - Modify `src/index.js` to implement your trading logic
2. **Add more tests** - Expand `tests/app.test.js` with comprehensive test coverage
3. **Configure monitoring** - Set up Prometheus/Grafana for metrics
4. **Add logging** - Integrate structured logging (e.g., Winston, Pino)
5. **Database migrations** - Add database schema management
6. **API documentation** - Add Swagger/OpenAPI documentation

## Troubleshooting

### Docker Issues
```powershell
# Rebuild without cache
docker-compose build --no-cache

# Check Docker logs
docker-compose logs -f trading-microservice

# Reset everything
docker-compose down -v
docker-compose up -d --build
```

### Git Issues
```powershell
# Check current branch
git branch

# Check remote
git remote -v

# Pull latest
git pull origin develop
```

### Kubernetes Issues
```powershell
# Check pod status
kubectl get pods -n trading -o wide

# Describe pod for errors
kubectl describe pod <pod-name> -n trading

# Check logs
kubectl logs -f <pod-name> -n trading

# Delete and recreate
kubectl delete -f k8s/deployment.yml -n trading
kubectl apply -f k8s/deployment.yml -n trading
```

## Support

For issues, contact the A6-9V team or create an issue in the GitHub repository.
