# Agent 3: Set up monitoring and logging
import os
import json

def setup_monitoring():
    # Create logging configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default"
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "logs/app.log",
                "level": "DEBUG",
                "formatter": "default"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file"]
        }
    }
    
    os.makedirs('logs', exist_ok=True)
    
    with open('logging.json', 'w') as f:
        json.dump(logging_config, f, indent=2)
    
    # Create health check endpoint
    health_check = '''
import time
import psutil
from datetime import datetime

def get_system_health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": time.time(),
        "memory_usage": psutil.virtual_memory().percent,
        "cpu_usage": psutil.cpu_percent(),
        "disk_usage": psutil.disk_usage('/').percent
    }
'''
    
    with open('api/health_monitor.py', 'w') as f:
        f.write(health_check)
    
    # Create monitoring dashboard config
    dashboard_config = {
        "dashboard": {
            "title": "GenX-FX Monitoring",
            "panels": [
                {"title": "API Response Time", "type": "graph"},
                {"title": "Error Rate", "type": "stat"},
                {"title": "Active Users", "type": "gauge"},
                {"title": "System Resources", "type": "table"}
            ]
        }
    }
    
    with open('monitoring-dashboard.json', 'w') as f:
        json.dump(dashboard_config, f, indent=2)
    
    print("Agent 3: Monitoring and logging configured")
    print("Files created: logging.json, api/health_monitor.py, monitoring-dashboard.json")

if __name__ == "__main__":
    setup_monitoring()