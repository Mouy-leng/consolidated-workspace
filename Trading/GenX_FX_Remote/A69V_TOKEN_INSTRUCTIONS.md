# A6-9V GitHub Token Usage Instructions

## Token Information
- **Organization**: A6-9V
- **Token**: Stored securely in environment variables
- **Type**: GitHub Personal Access Token
- **Created**: 2025-10-13 14:42:44

## Environment Variables Set
- A69V_GITHUB_TOKEN - A6-9V specific GitHub token
- Added to .env file for project use

## Usage Examples

### GitHub CLI Operations
```powershell
# The token is automatically configured for GitHub CLI operations
gh repo list --limit 10
gh repo create A6-9V/new-repo --private
```

### Git Operations
```powershell  
# Configure Git with token authentication
.\setup_git_auth.ps1

# Clone repositories
git clone https://github.com/A6-9V/repository-name.git

# Push changes (token handles authentication)
git push origin main
```

### Repository Management
```powershell
# Use A6-9V repository manager with token
.\a69v_repo_manager.ps1 configure
.\a69v_repo_manager.ps1 cleanup
.\a69v_repo_manager.ps1 fork https://github.com/user/repo
```

### Token Helper Script
```powershell
# Test token access
.\scripts\a69v_token_helper.ps1

# Or import functions
Import-Module .\scripts\a69v_token_helper.ps1
Test-A69VTokenAccess
```

## Security Notes
- Token is stored in user environment variables
- Token metadata stored in secure directory with restricted permissions
- Token is not committed to version control (.gitignore configured)
- Use token only for A6-9V organization operations

## Next Steps
1. Test token access: .\scripts\a69v_token_helper.ps1
2. Configure Git authentication: .\setup_git_auth.ps1
3. Run repository operations: .\a69v_repo_manager.ps1 cleanup
4. Commit A6-9V work: .\execute_a69v_commit.ps1

## Token Scopes
This token should have the following GitHub scopes:
- epo - Full repository access
- workflow - GitHub Actions workflows
- dmin:repo_hook - Repository webhooks
- delete_repo - Delete repositories (for cleanup)
- dmin:org - Organization administration (if needed)

---
Generated: 2025-10-13 14:42:44
Organization: A6-9V
