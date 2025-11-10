# Agent 2: Deploy to chosen platform (Vercel)
import subprocess
import json

def deploy_to_vercel():
    # Create vercel.json configuration
    vercel_config = {
        "version": 2,
        "builds": [
            {"src": "api/main.py", "use": "@vercel/python"},
            {"src": "dist/**", "use": "@vercel/static"}
        ],
        "routes": [
            {"src": "/api/(.*)", "dest": "/api/main.py"},
            {"src": "/(.*)", "dest": "/dist/$1"}
        ],
        "env": {
            "NODE_ENV": "production"
        }
    }
    
    with open('vercel.json', 'w') as f:
        json.dump(vercel_config, f, indent=2)
    
    # Create requirements.txt for Vercel
    requirements = [
        'fastapi==0.104.1',
        'uvicorn==0.24.0',
        'sqlite3'
    ]
    
    with open('requirements-vercel.txt', 'w') as f:
        for req in requirements:
            f.write(f'{req}\n')
    
    print("Agent 2: Vercel deployment configured")
    print("Files created: vercel.json, requirements-vercel.txt")
    print("Run: vercel --prod")

def deploy_to_railway():
    # Create railway.json
    railway_config = {
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "uvicorn api.main:app --host 0.0.0.0 --port $PORT"
        }
    }
    
    with open('railway.json', 'w') as f:
        json.dump(railway_config, f, indent=2)
    
    print("Agent 2: Railway deployment configured")
    print("File created: railway.json")

if __name__ == "__main__":
    deploy_to_vercel()
    deploy_to_railway()