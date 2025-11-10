# A6-9V Git Configuration with Token Authentication
# Run when Git becomes available

git config --global credential.helper manager-core
git config --global user.name "A6-9V"
git config --global user.email "admin@a6-9v.dev"
git config --global init.defaultBranch main

# GitHub specific configuration
git config --global hub.protocol https
git config --global github.user "A6-9V"

Write-Host "✓ Git configured for A6-9V with token authentication" -ForegroundColor Green
