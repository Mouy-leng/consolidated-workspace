# A6-9V Repository Secrets Configuration

## Required Secrets

### Production Environment
- **A6V9_API_KEY**: Main A6-9V API key for external services
- **A6V9_DATABASE_URL**: Database connection string
- **A6V9_JWT_SECRET**: JWT signing secret
- **A6V9_ENCRYPTION_KEY**: Data encryption key
- **DOCKER_HUB_TOKEN**: Docker Hub access token
- **CODECOV_TOKEN**: Code coverage reporting token

### Development Environment
- **A6V9_DEV_API_KEY**: Development API key
- **A6V9_DEV_DATABASE_URL**: Development database URL

## Environment Variables

### Production
- **NODE_ENV**: production
- **LOG_LEVEL**: info
- **A6V9_ENVIRONMENT**: production

### Staging
- **NODE_ENV**: staging
- **LOG_LEVEL**: debug
- **A6V9_ENVIRONMENT**: staging

### Development
- **NODE_ENV**: development
- **LOG_LEVEL**: debug
- **A6V9_ENVIRONMENT**: development

## Setup Instructions

1. In your repository, go to Settings > Secrets and variables > Actions
2. Add each secret with appropriate values
3. Configure environment-specific secrets in Environments section
4. Ensure branch protection rules are enabled for production

## Security Notes

- Never log secret values
- Use least-privilege access
- Rotate secrets regularly
- Monitor secret usage in workflows