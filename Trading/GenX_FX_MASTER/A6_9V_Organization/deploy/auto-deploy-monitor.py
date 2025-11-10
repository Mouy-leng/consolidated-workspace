#!/usr/bin/env python3
"""
GenX FX Auto Deployment Monitor
Runs continuous deployment attempts for 3+ hours
"""
import os
import time
import subprocess
import json
import logging
from datetime import datetime, timedelta
import requests
import secrets

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deploy/deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoDeploymentManager:
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=3, minutes=30)  # 3.5 hours
        self.deployment_attempts = 0
        self.successful_deployments = 0
        self.failed_deployments = 0
        
    def generate_env_file(self):
        """Generate secure .env file"""
        logger.info("🔐 Generating secure environment configuration...")
        
        env_content = f"""# Auto-generated secure configuration - {datetime.now()}
DATABASE_URL=postgresql://genx_user:{secrets.token_urlsafe(16)}@localhost:5432/genx_trading
MONGODB_URL=mongodb://localhost:27017/genx_trading
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY={secrets.token_urlsafe(32)}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Passwords
DB_PASSWORD={secrets.token_urlsafe(16)}
MONGO_PASSWORD={secrets.token_urlsafe(16)}
REDIS_PASSWORD={secrets.token_urlsafe(16)}
GRAFANA_PASSWORD={secrets.token_urlsafe(16)}

# AI API Configuration (placeholder - replace with real keys)
API_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

# Trading API Keys (placeholder - replace with real keys)
BYBIT_API_KEY=your-bybit-api-key
BYBIT_API_SECRET=your-bybit-api-secret

# Bot Tokens (placeholder - replace with real keys)
DISCORD_TOKEN=your-discord-bot-token
TELEGRAM_TOKEN=your-telegram-bot-token

# News API Keys (placeholder - replace with real keys)
NEWSDATA_API_KEY=your-newsdata-api-key-here
ALPHAVANTAGE_API_KEY=your-alphavantage-api-key-here
NEWSAPI_ORG_KEY=your-newsapi-org-key-here
FINNHUB_API_KEY=your-finnhub-api-key-here
FMP_API_KEY=your-fmp-api-key-here

# Reddit API Configuration (placeholder - replace with real keys)
REDDIT_CLIENT_ID=your-reddit-client-id-here
REDDIT_CLIENT_SECRET=your-reddit-client-secret-here
REDDIT_USERNAME=your-reddit-username-here
REDDIT_PASSWORD=your-reddit-password-here
REDDIT_USER_AGENT=GenX-Trading-Bot/1.0

# Logging
LOG_LEVEL=INFO

# Trading Configuration
DEFAULT_SYMBOL=BTCUSDT
MAX_POSITION_SIZE=0.1
RISK_PERCENTAGE=0.02

# Features
ENABLE_NEWS_ANALYSIS=true
ENABLE_REDDIT_ANALYSIS=true
ENABLE_WEBSOCKET_FEED=true
NEWS_REFRESH_INTERVAL=300
REDDIT_REFRESH_INTERVAL=600
SENTIMENT_THRESHOLD=0.6
WEBSOCKET_RECONNECT_INTERVAL=5
MAX_WEBSOCKET_RETRIES=10
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        logger.info("✅ Environment file generated")
    
    def run_command(self, command, timeout=300):
        """Run shell command with timeout"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=os.getcwd()
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Command timed out: {command}")
            return False, "", "Command timed out"
        except Exception as e:
            logger.error(f"❌ Command failed: {e}")
            return False, "", str(e)
    
    def cleanup_docker(self):
        """Clean up Docker containers and images"""
        logger.info("🧹 Cleaning up Docker environment...")
        
        commands = [
            "docker-compose -f docker-compose.production.yml down --remove-orphans",
            "docker container prune -f",
            "docker image prune -f",
            "docker volume prune -f",
            "docker network prune -f"
        ]
        
        for cmd in commands:
            success, stdout, stderr = self.run_command(cmd, timeout=60)
            if not success:
                logger.warning(f"⚠️ Cleanup command failed: {cmd}")
    
    def deploy_local(self):
        """Deploy locally with Docker Compose"""
        logger.info("🚀 Starting local deployment...")
        
        # Build images
        logger.info("🔨 Building Docker images...")
        success, stdout, stderr = self.run_command(
            "docker-compose -f docker-compose.production.yml build --no-cache", 
            timeout=600
        )
        
        if not success:
            logger.error(f"❌ Build failed: {stderr}")
            return False
        
        # Start databases first
        logger.info("🗄️ Starting databases...")
        success, stdout, stderr = self.run_command(
            "docker-compose -f docker-compose.production.yml up -d postgres mongo redis",
            timeout=120
        )
        
        if not success:
            logger.error(f"❌ Database startup failed: {stderr}")
            return False
        
        # Wait for databases
        logger.info("⏳ Waiting for databases to initialize...")
        time.sleep(45)
        
        # Start API service
        logger.info("🌐 Starting API service...")
        success, stdout, stderr = self.run_command(
            "docker-compose -f docker-compose.production.yml up -d api",
            timeout=120
        )
        
        if not success:
            logger.error(f"❌ API startup failed: {stderr}")
            return False
        
        # Wait for API
        time.sleep(30)
        
        # Health check
        logger.info("🏥 Performing health check...")
        for attempt in range(5):
            try:
                response = requests.get("http://localhost:8000/health", timeout=10)
                if response.status_code == 200:
                    logger.info("✅ API health check passed")
                    break
            except:
                logger.info(f"⏳ Health check attempt {attempt + 1}/5 failed, retrying...")
                time.sleep(10)
        else:
            logger.warning("⚠️ API health check failed, continuing anyway...")
        
        # Start remaining services
        logger.info("🔄 Starting remaining services...")
        success, stdout, stderr = self.run_command(
            "docker-compose -f docker-compose.production.yml up -d",
            timeout=180
        )
        
        if not success:
            logger.error(f"❌ Full deployment failed: {stderr}")
            return False
        
        # Final status check
        success, stdout, stderr = self.run_command(
            "docker-compose -f docker-compose.production.yml ps",
            timeout=30
        )
        
        logger.info("📊 Deployment status:")
        logger.info(stdout)
        
        return True
    
    def check_deployment_status(self):
        """Check current deployment status"""
        success, stdout, stderr = self.run_command(
            "docker-compose -f docker-compose.production.yml ps --format json",
            timeout=30
        )
        
        if not success:
            return {"status": "failed", "services": []}
        
        try:
            services = []
            for line in stdout.strip().split('\n'):
                if line.strip():
                    service_info = json.loads(line)
                    services.append({
                        "name": service_info.get("Service", "unknown"),
                        "state": service_info.get("State", "unknown"),
                        "status": service_info.get("Status", "unknown")
                    })
            
            running_services = [s for s in services if "running" in s["state"].lower()]
            return {
                "status": "running" if len(running_services) > 0 else "stopped",
                "services": services,
                "running_count": len(running_services),
                "total_count": len(services)
            }
        except:
            return {"status": "unknown", "services": []}
    
    def trigger_cloud_deployment(self):
        """Trigger cloud deployment via git push"""
        logger.info("☁️ Triggering cloud deployment...")
        
        # Add and commit changes
        commands = [
            "git add .",
            f"git commit -m '🚀 Auto-deployment attempt #{self.deployment_attempts} - {datetime.now()}'",
            "git push origin main"
        ]
        
        for cmd in commands:
            success, stdout, stderr = self.run_command(cmd, timeout=60)
            if not success and "nothing to commit" not in stderr:
                logger.warning(f"⚠️ Git command failed: {cmd} - {stderr}")
                return False
        
        logger.info("✅ Cloud deployment triggered")
        return True
    
    def save_deployment_report(self):
        """Save deployment report"""
        report = {
            "session_start": self.start_time.isoformat(),
            "session_end": datetime.now().isoformat(),
            "total_attempts": self.deployment_attempts,
            "successful_deployments": self.successful_deployments,
            "failed_deployments": self.failed_deployments,
            "success_rate": (self.successful_deployments / max(self.deployment_attempts, 1)) * 100,
            "final_status": self.check_deployment_status()
        }
        
        with open(f'deploy/deployment_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Final Report: {self.successful_deployments}/{self.deployment_attempts} successful deployments")
        return report
    
    def run_continuous_deployment(self):
        """Main deployment loop"""
        logger.info(f"🚀 Starting auto-deployment session until {self.end_time}")
        
        # Initial setup
        self.generate_env_file()
        
        while datetime.now() < self.end_time:
            self.deployment_attempts += 1
            logger.info(f"\n{'='*50}")
            logger.info(f"🔄 Deployment Attempt #{self.deployment_attempts}")
            logger.info(f"⏰ Time remaining: {self.end_time - datetime.now()}")
            logger.info(f"{'='*50}")
            
            try:
                # Cleanup before deployment
                self.cleanup_docker()
                time.sleep(10)
                
                # Deploy locally
                if self.deploy_local():
                    self.successful_deployments += 1
                    logger.info("✅ Local deployment successful!")
                    
                    # Trigger cloud deployment
                    self.trigger_cloud_deployment()
                    
                    # Monitor for 15 minutes before next attempt
                    logger.info("📊 Monitoring deployment for 15 minutes...")
                    for i in range(15):
                        status = self.check_deployment_status()
                        logger.info(f"Status: {status['running_count']}/{status['total_count']} services running")
                        time.sleep(60)  # Wait 1 minute
                        
                        if datetime.now() >= self.end_time:
                            break
                else:
                    self.failed_deployments += 1
                    logger.error("❌ Local deployment failed!")
                    
                    # Wait 5 minutes before retry
                    logger.info("⏳ Waiting 5 minutes before retry...")
                    time.sleep(300)
                
            except KeyboardInterrupt:
                logger.info("🛑 Deployment interrupted by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                self.failed_deployments += 1
                time.sleep(300)  # Wait 5 minutes on error
        
        # Final report
        logger.info("\n🏁 Auto-deployment session completed!")
        report = self.save_deployment_report()
        return report

if __name__ == "__main__":
    manager = AutoDeploymentManager()
    manager.run_continuous_deployment()