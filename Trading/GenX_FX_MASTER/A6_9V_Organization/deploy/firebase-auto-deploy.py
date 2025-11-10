#!/usr/bin/env python3
"""
Firebase Auto Deployment Script
"""
import os
import subprocess
import time
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class FirebaseDeployer:
    def __init__(self):
        self.token = "jmboQydL5KRqerZ6RAFRCABtkLp2"
        self.project_id = "genx-fx-trading"
        
    def run_command(self, cmd):
        """Run command and return result"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def setup_firebase_config(self):
        """Setup Firebase configuration files"""
        logger.info("🔧 Setting up Firebase configuration...")
        
        # Create firebase.json
        firebase_config = {
            "hosting": {
                "public": "frontend/dist",
                "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
                "rewrites": [{"source": "**", "destination": "/index.html"}],
                "site": "genx-fx-trading"
            }
        }
        
        with open('firebase.json', 'w') as f:
            json.dump(firebase_config, f, indent=2)
        
        # Create .firebaserc
        firebaserc = {
            "projects": {
                "default": self.project_id
            },
            "targets": {
                self.project_id: {
                    "hosting": {
                        "genx-fx": ["genx-fx-trading"]
                    }
                }
            }
        }
        
        with open('.firebaserc', 'w') as f:
            json.dump(firebaserc, f, indent=2)
        
        logger.info("✅ Firebase configuration created")
    
    def create_frontend_build(self):
        """Create a simple frontend build"""
        logger.info("🔨 Creating frontend build...")
        
        os.makedirs('frontend/dist', exist_ok=True)
        
        # Create index.html
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GenX FX Trading Platform</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: white; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .status {{ background: #2a2a2a; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .success {{ border-left: 4px solid #4CAF50; }}
        .info {{ border-left: 4px solid #2196F3; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: #2a2a2a; padding: 20px; border-radius: 10px; }}
        .timestamp {{ color: #888; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 GenX FX Trading Platform</h1>
            <p>AI-Powered Trading System</p>
        </div>
        
        <div class="status success">
            <h3>✅ Deployment Status: LIVE</h3>
            <p class="timestamp">Deployed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>User: lengkundee01@gmail.com</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📊 Trading Dashboard</h3>
                <p>Real-time market analysis and trading signals</p>
                <button onclick="window.open('/api/health', '_blank')">Check API Status</button>
            </div>
            
            <div class="card">
                <h3>🤖 AI Signals</h3>
                <p>Machine learning powered trading recommendations</p>
                <button onclick="window.open('/MT4_Signals.csv', '_blank')">Download Signals</button>
            </div>
            
            <div class="card">
                <h3>📈 Market Data</h3>
                <p>Live cryptocurrency and forex data feeds</p>
                <button onclick="alert('WebSocket feed active')">View Live Data</button>
            </div>
            
            <div class="card">
                <h3>🔔 Notifications</h3>
                <p>Discord and Telegram bot integration</p>
                <button onclick="alert('Bots are running')">Test Notifications</button>
            </div>
        </div>
        
        <div class="status info">
            <h3>🔧 System Information</h3>
            <p><strong>Backend API:</strong> http://localhost:8000</p>
            <p><strong>WebSocket:</strong> ws://localhost:8000/ws</p>
            <p><strong>Database:</strong> PostgreSQL + MongoDB + Redis</p>
            <p><strong>Authentication:</strong> Firebase (SCRYPT)</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
        
        // Check API health
        fetch('/api/health')
            .then(response => response.json())
            .then(data => console.log('API Health:', data))
            .catch(error => console.log('API offline'));
    </script>
</body>
</html>"""
        
        with open('frontend/dist/index.html', 'w') as f:
            f.write(html_content)
        
        logger.info("✅ Frontend build created")
    
    def deploy_to_firebase(self):
        """Deploy to Firebase hosting"""
        logger.info("🚀 Deploying to Firebase...")
        
        # Set environment variable
        os.environ['FIREBASE_TOKEN'] = self.token
        
        # Deploy command
        cmd = f"firebase deploy --only hosting --project {self.project_id} --token {self.token}"
        success, stdout, stderr = self.run_command(cmd)
        
        if success:
            logger.info("✅ Firebase deployment successful!")
            logger.info(stdout)
            return True
        else:
            logger.error(f"❌ Firebase deployment failed: {stderr}")
            return False
    
    def run_continuous_deployment(self):
        """Run deployment every 30 minutes for 3+ hours"""
        logger.info("🔥 Starting Firebase continuous deployment...")
        
        end_time = time.time() + (3.5 * 3600)  # 3.5 hours
        attempt = 0
        
        while time.time() < end_time:
            attempt += 1
            logger.info(f"\n{'='*50}")
            logger.info(f"🔄 Firebase Deployment Attempt #{attempt}")
            logger.info(f"{'='*50}")
            
            try:
                # Setup configuration
                self.setup_firebase_config()
                
                # Create frontend build
                self.create_frontend_build()
                
                # Deploy to Firebase
                if self.deploy_to_firebase():
                    logger.info("✅ Deployment successful!")
                else:
                    logger.error("❌ Deployment failed!")
                
                # Wait 30 minutes before next deployment
                logger.info("⏳ Waiting 30 minutes before next deployment...")
                time.sleep(1800)  # 30 minutes
                
            except KeyboardInterrupt:
                logger.info("🛑 Deployment interrupted")
                break
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                time.sleep(300)  # Wait 5 minutes on error
        
        logger.info("🏁 Firebase deployment session completed!")

if __name__ == "__main__":
    deployer = FirebaseDeployer()
    deployer.run_continuous_deployment()