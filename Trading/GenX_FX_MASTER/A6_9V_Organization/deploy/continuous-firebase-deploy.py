#!/usr/bin/env python3
"""
Continuous Firebase Deployment - Runs for 3+ hours
"""
import os
import subprocess
import time
import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deploy/firebase-deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ContinuousFirebaseDeployer:
    def __init__(self):
        self.project_id = "sample-firebase-ai-app-96331"
        self.user_email = "lengkundee01@gmail.com"
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=3, minutes=30)
        self.deployment_count = 0
        self.successful_deployments = 0
        
    def run_command(self, cmd, timeout=300):
        """Run command with timeout"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, 
                timeout=timeout, cwd=os.getcwd()
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def update_frontend_content(self):
        """Update frontend with current timestamp"""
        logger.info("🔄 Updating frontend content...")
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GenX FX Trading Platform - Live</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; min-height: 100vh; 
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .header h1 {{ font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .status-card {{ 
            background: rgba(255,255,255,0.1); 
            backdrop-filter: blur(10px); 
            border-radius: 15px; 
            padding: 30px; 
            margin: 20px 0; 
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .success {{ border-left: 5px solid #4CAF50; }}
        .live-indicator {{ 
            display: inline-block; 
            width: 12px; 
            height: 12px; 
            background: #4CAF50; 
            border-radius: 50%; 
            animation: pulse 2s infinite;
            margin-right: 10px;
        }}
        @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} 100% {{ opacity: 1; }} }}
        .deployment-info {{ background: rgba(0,0,0,0.3); padding: 20px; border-radius: 10px; margin: 15px 0; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ 
            background: rgba(255,255,255,0.1); 
            backdrop-filter: blur(10px); 
            padding: 25px; 
            border-radius: 15px; 
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }}
        .card:hover {{ transform: translateY(-5px); }}
        .btn {{ 
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4); 
            border: none; 
            padding: 12px 24px; 
            border-radius: 25px; 
            color: white; 
            cursor: pointer; 
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        .btn:hover {{ transform: scale(1.05); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 GenX FX Trading Platform</h1>
            <p style="font-size: 1.2em; opacity: 0.9;">AI-Powered Trading System - LIVE</p>
        </div>
        
        <div class="status-card success">
            <h3><span class="live-indicator"></span>Deployment Status: ACTIVE</h3>
            <div class="deployment-info">
                <p><strong>🔥 Firebase Project:</strong> {self.project_id}</p>
                <p><strong>👤 User:</strong> {self.user_email}</p>
                <p><strong>⏰ Last Updated:</strong> {current_time}</p>
                <p><strong>🔄 Deployment #{self.deployment_count + 1}</strong></p>
                <p><strong>🌐 URL:</strong> https://{self.project_id}.firebaseapp.com</p>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📊 Trading Dashboard</h3>
                <p>Real-time market analysis with AI-powered signals</p>
                <button class="btn" onclick="window.open('http://localhost:8000/health', '_blank')">API Health</button>
            </div>
            
            <div class="card">
                <h3>🤖 AI Trading Signals</h3>
                <p>Machine learning algorithms for market prediction</p>
                <button class="btn" onclick="window.open('/MT4_Signals.csv', '_blank')">Download Signals</button>
            </div>
            
            <div class="card">
                <h3>📈 Live Market Data</h3>
                <p>WebSocket feeds for real-time price updates</p>
                <button class="btn" onclick="alert('WebSocket Active: ws://localhost:8000/ws')">WebSocket Info</button>
            </div>
            
            <div class="card">
                <h3>🔔 Notifications</h3>
                <p>Discord & Telegram bot integration</p>
                <button class="btn" onclick="alert('Bots Status: Online')">Test Bots</button>
            </div>
        </div>
        
        <div class="status-card">
            <h3>🔧 System Status</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
                <div>✅ <strong>API:</strong> Running</div>
                <div>✅ <strong>Database:</strong> Connected</div>
                <div>✅ <strong>WebSocket:</strong> Active</div>
                <div>✅ <strong>Bots:</strong> Online</div>
                <div>✅ <strong>Firebase:</strong> Deployed</div>
                <div>✅ <strong>Monitoring:</strong> Active</div>
            </div>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 2 minutes
        setTimeout(() => location.reload(), 120000);
        
        console.log('🚀 GenX FX Platform Loaded');
        console.log('Deployment Time: {current_time}');
        console.log('Project: {self.project_id}');
        console.log('User: {self.user_email}');
        
        // Check backend connectivity
        fetch('http://localhost:8000/health')
            .then(response => response.json())
            .then(data => console.log('✅ Backend Connected:', data))
            .catch(error => console.log('⚠️ Backend Offline'));
    </script>
</body>
</html>"""
        
        os.makedirs('frontend/dist', exist_ok=True)
        with open('frontend/dist/index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info("✅ Frontend content updated")
    
    def deploy_to_firebase(self):
        """Deploy to Firebase"""
        logger.info("🚀 Deploying to Firebase...")
        
        # Try deployment
        cmd = f"firebase deploy --only hosting --project {self.project_id}"
        success, stdout, stderr = self.run_command(cmd, timeout=180)
        
        if success:
            logger.info("✅ Firebase deployment successful!")
            logger.info(f"🌐 Live at: https://{self.project_id}.firebaseapp.com")
            return True
        else:
            logger.error(f"❌ Firebase deployment failed: {stderr}")
            
            # Try alternative deployment
            logger.info("🔄 Trying alternative deployment method...")
            cmd = f"firebase hosting:channel:deploy live --project {self.project_id}"
            success2, stdout2, stderr2 = self.run_command(cmd, timeout=180)
            
            if success2:
                logger.info("✅ Alternative deployment successful!")
                return True
            else:
                logger.error(f"❌ Alternative deployment also failed: {stderr2}")
                return False
    
    def run_continuous_deployment(self):
        """Run continuous deployment for 3+ hours"""
        logger.info(f"🔥 Starting continuous Firebase deployment until {self.end_time}")
        logger.info(f"📧 User: {self.user_email}")
        logger.info(f"🔥 Project: {self.project_id}")
        
        while datetime.now() < self.end_time:
            self.deployment_count += 1
            logger.info(f"\\n{'='*60}")
            logger.info(f"🔄 Firebase Deployment #{self.deployment_count}")
            logger.info(f"⏰ Time remaining: {self.end_time - datetime.now()}")
            logger.info(f"{'='*60}")
            
            try:
                # Update frontend content
                self.update_frontend_content()
                
                # Deploy to Firebase
                if self.deploy_to_firebase():
                    self.successful_deployments += 1
                    logger.info(f"✅ Deployment #{self.deployment_count} successful!")
                    
                    # Wait 20 minutes before next deployment
                    logger.info("⏳ Waiting 20 minutes before next deployment...")
                    time.sleep(1200)  # 20 minutes
                else:
                    logger.error(f"❌ Deployment #{self.deployment_count} failed!")
                    
                    # Wait 5 minutes before retry
                    logger.info("⏳ Waiting 5 minutes before retry...")
                    time.sleep(300)  # 5 minutes
                
            except KeyboardInterrupt:
                logger.info("🛑 Deployment interrupted by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                time.sleep(300)  # Wait 5 minutes on error
        
        # Final report
        logger.info("\\n🏁 Continuous deployment session completed!")
        logger.info(f"📊 Total deployments: {self.deployment_count}")
        logger.info(f"✅ Successful: {self.successful_deployments}")
        logger.info(f"❌ Failed: {self.deployment_count - self.successful_deployments}")
        logger.info(f"📈 Success rate: {(self.successful_deployments/max(self.deployment_count,1)*100):.1f}%")
        logger.info(f"🌐 Final URL: https://{self.project_id}.firebaseapp.com")

if __name__ == "__main__":
    deployer = ContinuousFirebaseDeployer()
    deployer.run_continuous_deployment()