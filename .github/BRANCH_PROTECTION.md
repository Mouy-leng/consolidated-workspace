# Branch Protection Rules

## Main Branch Protection

The `main` branch should be protected with the following rules:

### Required Settings:
- ✅ Require pull request reviews before merging
- ✅ Require approvals: 1
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Require conversation resolution before merging
- ✅ Do not allow bypassing the above settings
- ✅ Restrict who can push to matching branches (only maintainers)

### Status Checks Required:
- CI tests must pass
- Security checks must pass
- No secrets detected

### Setup Instructions:

1. Go to GitHub repository: Settings > Branches
2. Add rule for branch: `main`
3. Configure the above settings
4. Save changes

## Development Workflow

1. Create feature branch from `main`
2. Make changes and commit
3. Push to remote
4. Create Pull Request
5. Get approval
6. Merge to `main`

## Emergency Bypass

For emergency fixes, use the `hotfix/` branch pattern which can bypass some restrictions (use with caution).

