#!/usr/bin/env python3
"""
Fix GenX_FX to use PostgreSQL instead of SQLite
"""
import os
import re

def update_api_main():
    """Update api/main.py to use PostgreSQL"""
    api_file = "api/main.py"
    
    if not os.path.exists(api_file):
        print(f"Creating {api_file} with PostgreSQL support...")
        
        content = '''from fastapi import FastAPI
from sqlalchemy import create_engine, text
import os
from datetime import datetime

app = FastAPI(title="GenX FX API")

# PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://genx_user:genx_password@localhost:5432/genx_trading")
engine = create_engine(DATABASE_URL)

@app.get("/")
def root():
    return {"status": "GenX FX API", "database": "PostgreSQL", "timestamp": datetime.now().isoformat()}

@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@app.get("/signals")
def get_signals():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM trading_signals ORDER BY created_at DESC LIMIT 10"))
            signals = [dict(row._mapping) for row in result]
        return {"signals": signals}
    except Exception as e:
        return {"error": str(e)}
'''
        
        os.makedirs("api", exist_ok=True)
        with open(api_file, 'w') as f:
            f.write(content)
        print(f"Created {api_file}")
    else:
        print(f"{api_file} already exists")

def create_env_example():
    """Create .env.example with placeholders"""
    content = '''# GenX_FX Environment Variables Template
# Copy to .env and fill with your actual values

# Database
DATABASE_URL=postgresql://genx_user:genx_password@localhost:5432/genx_trading
POSTGRES_DB=genx_trading
POSTGRES_USER=genx_user
POSTGRES_PASSWORD=your_secure_password
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# AI Services
GEMINI_API_KEY=your_gemini_api_key

# Trading APIs
FXCM_USERNAME=your_fxcm_username
FXCM_PASSWORD=your_fxcm_password
BYBIT_API_KEY=your_bybit_key
BYBIT_API_SECRET=your_bybit_secret

# Notifications
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_USER_ID=your_telegram_user_id

# Docker
DOCKER_USERNAME=your_docker_username
DOCKER_PASSWORD=your_docker_password

# Security
JWT_SECRET_KEY=your_jwt_secret

# Trading Config
TRADING_ENABLED=false
TRADING_MODE=demo
RISK_LEVEL=medium
'''
    
    with open('.env.example', 'w') as f:
        f.write(content)
    print("Created .env.example")

def update_gitignore():
    """Update .gitignore to exclude secrets"""
    gitignore_content = '''# Environment files
.env
.env.local
.env.deployment
.env.production

# Credentials
*credentials*
*secrets*
GenX_FX_Master_Credentials.*
GenX_FX_Credentials_Backup.txt

# Logs
logs/
*.log

# Database
*.db
*.sqlite

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# Node
node_modules/
npm-debug.log*

# Docker
.dockerignore

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
'''
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("Updated .gitignore")

def create_makefile():
    """Create Makefile for easy commands"""
    content = '''# GenX_FX Makefile

.PHONY: help install dev api-start docker-build docker-up docker-down db-up db-migrate clean

help:
	@echo "GenX_FX Commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Start development server"
	@echo "  api-start   - Start API server"
	@echo "  docker-build- Build Docker image"
	@echo "  docker-up   - Start all services"
	@echo "  docker-down - Stop all services"
	@echo "  db-up       - Start database only"
	@echo "  db-migrate  - Run database migrations"
	@echo "  clean       - Clean up containers"

install:
	pip install -r requirements.txt

dev:
	python enhanced_trading.py

api-start:
	cd api && python main.py

docker-build:
	docker build -f Dockerfile.enhanced -t genx-enhanced .

docker-up:
	docker-compose -f docker-compose.production.yml up -d

docker-down:
	docker-compose -f docker-compose.production.yml down

db-up:
	docker-compose -f docker-compose.production.yml up -d postgres redis

db-migrate:
	python setup_database.py

clean:
	docker system prune -f
	docker volume prune -f
'''
    
    with open('Makefile', 'w') as f:
        f.write(content)
    print("Created Makefile")

if __name__ == "__main__":
    print("Fixing GenX_FX Database Configuration...")
    
    update_api_main()
    create_env_example()
    update_gitignore()
    create_makefile()
    
    print("\nDatabase fixes complete!")
    print("\nNext steps:")
    print("1. Run: emergency_revoke.bat")
    print("2. Run: make db-up")
    print("3. Run: make db-migrate")
    print("4. Run: make docker-up")