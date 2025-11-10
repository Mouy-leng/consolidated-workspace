# PyCharm/IntelliJ Setup for GenX_FX

## Environment Setup
1. **Python Interpreter**: Set to ./venv/Scripts/python.exe
2. **Working Directory**: Set to project root
3. **Environment Variables** (in Run Configurations):
   - GENX_PROJECT_ROOT: C:\Users\lengk\GenX_FX_Remote
   - GENX_ENVIRONMENT: dev
   - GENX_SECRETS_DIR: C:\Users\lengk\.genx_fx_secrets

## Plugin Recommendations
- Python
- .env files support
- Docker
- GitToolBox
- Rainbow Brackets

## Run Configuration Template
1. Create new Python configuration
2. Set script path to your main script
3. Add environment variables above
4. Enable "Include parent environment variables"
5. Set .env file path to .env

## Database Integration
- Database URL: postgresql://genx_user:password@localhost:5432/genx_trading
- Redis URL: edis://localhost:6379

## Code Style
- Use Black formatter
- Enable import sorting (isort)
- Set line length to 88 characters
