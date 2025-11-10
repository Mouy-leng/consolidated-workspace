# Trading Microservice

A production-ready microservice for trading system with Docker containerization and complete CI/CD pipeline.

## 🏗️ Architecture

- **Runtime**: Node.js 20
- **Framework**: Express.js
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions
- **Registry**: GitHub Container Registry (GHCR)

## 📋 Prerequisites

- Docker Desktop (for Windows)
- Node.js 20+ (for local development)
- Git
- kubectl (for Kubernetes deployments)
- GitHub account with access to A6-9V organization

## 🚀 Quick Start

### Local Development (Docker Compose)

1. **Start all services:**
   ```powershell
   docker-compose up -d
   ```

2. **View logs:**
   ```powershell
   docker-compose logs -f trading-microservice
   ```

3. **Stop services:**
   ```powershell
   docker-compose down
   ```

### Local Development (Node.js)

1. **Install dependencies:**
   ```powershell
   npm install
   ```

2. **Run in development mode:**
   ```powershell
   npm run dev
   ```

3. **Run tests:**
   ```powershell
   npm test
   ```

## 🔨 Building Docker Image

### Build locally:
```powershell
docker build -t trading-microservice .
```

### Run the container:
```powershell
docker run -p 3000:3000 -e NODE_ENV=production trading-microservice
```

## 🧪 Testing

### Run all tests:
```powershell
npm test
```

### Run with coverage:
```powershell
npm test -- --coverage
```

### Run linter:
```powershell
npm run lint
```

## 📦 API Endpoints

### Health & Status
- `GET /health` - Health check endpoint
- `GET /ready` - Readiness check endpoint
- `GET /api/v1/status` - API status

### Trading API
- `GET /api/v1/trades` - Get trading data

## 🚢 Deployment

### GitHub Actions CI/CD Pipeline

The pipeline automatically:
1. **Test**: Runs tests and linting on every PR and push
2. **Build**: Builds Docker image and pushes to GHCR
3. **Security**: Scans image with Trivy
4. **Deploy**: 
   - `develop` branch → Staging environment
   - `main` branch → Production environment

### Manual Deployment to Kubernetes

1. **Apply ConfigMap:**
   ```powershell
   kubectl apply -f k8s/configmap.yml
   ```

2. **Create secrets (replace with your values):**
   ```powershell
   kubectl create secret generic trading-secrets `
     --from-literal=db-host=your-db-host `
     --from-literal=db-name=trading_db `
     --from-literal=db-user=postgres `
     --from-literal=db-password=your-password
   ```

3. **Deploy application:**
   ```powershell
   kubectl apply -f k8s/deployment.yml
   ```

4. **Apply ingress:**
   ```powershell
   kubectl apply -f k8s/ingress.yml
   ```

5. **Check deployment status:**
   ```powershell
   kubectl get pods -l app=trading-microservice
   kubectl get svc trading-microservice
   ```

## 🔐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NODE_ENV` | Environment mode | `development` |
| `PORT` | Server port | `3000` |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_NAME` | Database name | `trading_db` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `LOG_LEVEL` | Logging level | `info` |

## 📊 Monitoring

### Health Checks
- **Liveness**: `http://localhost:3000/health`
- **Readiness**: `http://localhost:3000/ready`

### Kubernetes Metrics
```powershell
kubectl top pods -l app=trading-microservice
kubectl describe hpa trading-microservice-hpa
```

## 🔧 Troubleshooting

### Check container logs:
```powershell
docker logs trading-microservice
```

### Check Kubernetes pod logs:
```powershell
kubectl logs -l app=trading-microservice --tail=100 -f
```

### Restart deployment:
```powershell
kubectl rollout restart deployment/trading-microservice
```

### Check deployment history:
```powershell
kubectl rollout history deployment/trading-microservice
```

## 📁 Project Structure

```
trading-microservice/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # CI/CD pipeline
├── config/
│   └── config.js              # Application configuration
├── k8s/
│   ├── deployment.yml         # Kubernetes deployment
│   ├── configmap.yml          # Kubernetes config
│   └── ingress.yml            # Kubernetes ingress
├── src/
│   └── index.js               # Application entry point
├── tests/
│   └── app.test.js            # Test suite
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Docker image definition
├── package.json               # Node.js dependencies
└── README.md                  # This file
```

## 🛡️ Security Features

- Multi-stage Docker builds
- Non-root container user
- Security headers (Helmet.js)
- CORS protection
- Image security scanning with Trivy
- Secret management with Kubernetes Secrets
- Resource limits and quotas

## 🔄 CI/CD Workflow

1. **Push to `develop`** → Tests → Build → Deploy to Staging
2. **Push to `main`** → Tests → Build → Deploy to Production
3. **Pull Request** → Tests only (no deployment)

## 📝 Contributing

1. Create a feature branch from `develop`
2. Make your changes
3. Ensure tests pass: `npm test`
4. Create a Pull Request to `develop`
5. After review, merge to `develop` for staging deployment
6. Merge `develop` to `main` for production deployment

## 📄 License

MIT License - A6-9V Organization

## 🤝 Support

For issues and questions, please open an issue in the GitHub repository.

---

**Organization**: A6-9V  
**Created**: 2025  
**Maintained by**: A6-9V Team
