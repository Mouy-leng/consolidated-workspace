# A6-9V Repository Environments

## Production Environment
- **Protection Rules**: 
  - Required reviewers: A6-9V team
  - Wait timer: 5 minutes
  - Restrict to main branch only
- **Secrets**: All production secrets
- **Variables**: Production configuration

## Staging Environment  
- **Protection Rules**:
  - Required reviewers: 1 team member
  - Restrict to staging branch
- **Secrets**: Staging-specific secrets
- **Variables**: Staging configuration

## Development Environment
- **Protection Rules**: None (open access)
- **Secrets**: Development secrets only
- **Variables**: Development configuration

## Setup Commands (using GitHub CLI)

```bash
# Create environments
gh api repos/:owner/:repo/environments/production --method PUT
gh api repos/:owner/:repo/environments/staging --method PUT  
gh api repos/:owner/:repo/environments/development --method PUT

# Set environment secrets (example)
gh secret set A6V9_API_KEY --env production
gh secret set A6V9_DEV_API_KEY --env development
```