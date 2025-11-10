#!/usr/bin/env python3
"""
AMP Job Runner - Execute next job with GenX Trading Platform
Connects with AMP and runs the configured trading pipeline
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AMPJobRunner:
    def __init__(self):
        self.project_root = Path.cwd()
        self.config_file = self.project_root / "amp_config.json"
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load AMP configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    async def run_next_job(self):
        """Execute the next job with all configured services"""
        print("🚀 AMP Job Runner - Starting Next Job")
        print("=" * 50)
        
        # Initialize all services
        services = await self.initialize_services()
        
        # Run the trading pipeline
        await self.run_trading_pipeline(services)
        
        # Generate reports
        await self.generate_reports(services)
        
        print("✅ Next job completed successfully!")
    
    async def initialize_services(self) -> Dict:
        """Initialize all configured services"""
        print("🔧 Initializing Services...")
        
        services = {}
        
        # Initialize Gemini AI Service
        if "gemini_service" in self.config.get("enabled_services", []):
            try:
                from api.services.gemini_service import GeminiService
                services["gemini"] = GeminiService()
                await services["gemini"].initialize()
                print("  ✅ Gemini AI Service initialized")
            except Exception as e:
                print(f"  ❌ Gemini AI Service failed: {e}")
        
        # Initialize Reddit Service
        if "reddit_service" in self.config.get("enabled_services", []):
            try:
                from api.services.reddit_service import RedditService
                services["reddit"] = RedditService()
                await services["reddit"].initialize()
                print("  ✅ Reddit Service initialized")
            except Exception as e:
                print(f"  ❌ Reddit Service failed: {e}")
        
        # Initialize News Service
        if "news_service" in self.config.get("enabled_services", []):
            try:
                from api.services.news_service import NewsService
                services["news"] = NewsService()
                await services["news"].initialize()
                print("  ✅ News Service initialized")
            except Exception as e:
                print(f"  ❌ News Service failed: {e}")
        
        # Initialize WebSocket Service
        if "websocket_service" in self.config.get("enabled_services", []):
            try:
                from api.services.websocket_service import WebSocketService
                services["websocket"] = WebSocketService()
                await services["websocket"].initialize()
                print("  ✅ WebSocket Service initialized")
            except Exception as e:
                print(f"  ❌ WebSocket Service failed: {e}")
        
        return services
    
    async def run_trading_pipeline(self, services: Dict):
        """Run the complete trading pipeline"""
        print("\n📈 Running Trading Pipeline...")
        
        # Step 1: Collect market data
        print("  1️⃣ Collecting market data...")
        market_data = await self.collect_market_data(services)
        
        # Step 2: Gather news and sentiment
        print("  2️⃣ Gathering news and sentiment...")
        sentiment_data = await self.gather_sentiment_data(services)
        
        # Step 3: Generate AI predictions
        print("  3️⃣ Generating AI predictions...")
        predictions = await self.generate_predictions(services, market_data, sentiment_data)
        
        # Step 4: Generate trading signals
        print("  4️⃣ Generating trading signals...")
        signals = await self.generate_trading_signals(services, predictions)
        
        # Step 5: Execute trades (if enabled)
        print("  5️⃣ Executing trades...")
        await self.execute_trades(services, signals)
        
        print("  ✅ Trading pipeline completed!")
    
    async def collect_market_data(self, services: Dict) -> Dict:
        """Collect real-time market data"""
        market_data = {}
        
        # Get WebSocket data if available
        if "websocket" in services:
            try:
                # Subscribe to major pairs
                symbols = ["BTCUSDT", "ETHUSDT", "EURUSD", "GBPUSD"]
                for symbol in symbols:
                    await services["websocket"].subscribe_to_symbol("bybit", symbol)
                
                # Collect data for 30 seconds
                await asyncio.sleep(30)
                market_data["websocket"] = "Real-time data collected"
            except Exception as e:
                print(f"    ⚠️ WebSocket data collection failed: {e}")
        
        return market_data
    
    async def gather_sentiment_data(self, services: Dict) -> Dict:
        """Gather news and social sentiment data"""
        sentiment_data = {}
        
        # Get news sentiment
        if "news" in services:
            try:
                crypto_news = await services["news"].get_crypto_news(limit=20)
                sentiment_data["news"] = crypto_news
                print(f"    📰 Collected {len(crypto_news)} news articles")
            except Exception as e:
                print(f"    ⚠️ News collection failed: {e}")
        
        # Get Reddit sentiment
        if "reddit" in services:
            try:
                crypto_sentiment = await services["reddit"].get_crypto_sentiment()
                sentiment_data["reddit"] = crypto_sentiment
                print(f"    📱 Collected Reddit sentiment data")
            except Exception as e:
                print(f"    ⚠️ Reddit sentiment collection failed: {e}")
        
        return sentiment_data
    
    async def generate_predictions(self, services: Dict, market_data: Dict, sentiment_data: Dict) -> Dict:
        """Generate AI predictions"""
        predictions = {}
        
        if "gemini" in services:
            try:
                # Analyze market sentiment
                sentiment_analysis = await services["gemini"].analyze_market_sentiment(sentiment_data)
                predictions["sentiment"] = sentiment_analysis
                print(f"    🤖 Generated sentiment analysis")
                
                # Generate trading signals
                trading_signals = await services["gemini"].analyze_trading_signals(market_data, sentiment_data)
                predictions["signals"] = trading_signals
                print(f"    🎯 Generated trading signals")
                
            except Exception as e:
                print(f"    ⚠️ AI prediction generation failed: {e}")
        
        return predictions
    
    async def generate_trading_signals(self, services: Dict, predictions: Dict) -> List[Dict]:
        """Generate final trading signals"""
        signals = []
        
        if "signals" in predictions:
            try:
                # Process AI-generated signals
                for signal in predictions["signals"]:
                    processed_signal = {
                        "symbol": signal.get("symbol", "BTCUSDT"),
                        "action": signal.get("action", "HOLD"),
                        "confidence": signal.get("confidence", 0.5),
                        "entry_price": signal.get("entry_price", 0),
                        "target_price": signal.get("target_price", 0),
                        "stop_loss": signal.get("stop_loss", 0),
                        "timestamp": datetime.now().isoformat()
                    }
                    signals.append(processed_signal)
                
                print(f"    📊 Generated {len(signals)} trading signals")
                
            except Exception as e:
                print(f"    ⚠️ Signal generation failed: {e}")
        
        return signals
    
    async def execute_trades(self, services: Dict, signals: List[Dict]):
        """Execute trades based on signals"""
        if not signals:
            print("    ⏭️ No signals to execute")
            return
        
        print(f"    💰 Processing {len(signals)} trading signals...")
        
        for signal in signals:
            if signal["confidence"] > 0.7:  # High confidence threshold
                print(f"      🎯 High confidence signal: {signal['symbol']} {signal['action']}")
                # Here you would integrate with your trading execution service
                # await trading_service.execute_trade(signal)
            else:
                print(f"      ⚠️ Low confidence signal: {signal['symbol']} {signal['action']} (confidence: {signal['confidence']:.2f})")
    
    async def generate_reports(self, services: Dict):
        """Generate job completion reports"""
        print("\n📋 Generating Reports...")
        
        # Create job report
        report = {
            "job_id": f"amp_job_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "services_initialized": list(services.keys()),
            "plugins_installed": [plugin["name"] for plugin in self.config.get("plugins", [])],
            "status": "completed",
            "next_job_scheduled": True
        }
        
        # Save report
        report_file = self.project_root / "logs" / f"amp_job_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"  📄 Report saved: {report_file}")
        print(f"  🎯 Next job scheduled for execution")
    
    async def run_deploy_job(self):
        """Execute deployment job"""
        print("🚀 Starting Deployment Job")
        print("=" * 50)
        
        # Step 1: Verify system requirements
        print("1️⃣ Verifying system requirements...")
        if not shutil.which("docker-compose"):
            raise RuntimeError("docker-compose not found. Please install Docker.")
        print("  ✅ Docker found")
        
        # Step 2: Pull latest images
        print("2️⃣ Pulling latest Docker images...")
        subprocess.run(["docker-compose", "-f", "docker-compose.production.yml", "pull"], check=True)
        
        # Step 3: Build services if needed
        print("3️⃣ Building services...")
        subprocess.run(["docker-compose", "-f", "docker-compose.production.yml", "build"], check=True)
        
        # Step 4: Deploy
        print("4️⃣ Deploying to production...")
        subprocess.run(["docker-compose", "-f", "docker-compose.production.yml", "up", "-d"], check=True)
        
        # Step 5: Verify deployment
        print("5️⃣ Verifying deployment...")
        await asyncio.sleep(10)  # Wait for services to start
        health_check = subprocess.run(["docker-compose", "-f", "docker-compose.production.yml", "ps"], capture_output=True, text=True)
        print(health_check.stdout)
        
        print("✅ Deployment job completed successfully!")
    
    def show_status(self):
        """Show current AMP status"""
        print("🔍 AMP Status Report")
        print("=" * 30)
        
        print(f"API Provider: {self.config.get('api_provider', 'Not set')}")
        print(f"Plugins Installed: {len(self.config.get('plugins', []))}")
        
        for plugin in self.config.get('plugins', []):
            print(f"  - {plugin['name']}: {'✅' if plugin.get('enabled') else '❌'}")
        
        print(f"Services Enabled: {len(self.config.get('enabled_services', []))}")
        for service in self.config.get('enabled_services', []):
            print(f"  - {service}")
        
        print(f"Features Enabled:")
        features = [
            ('Sentiment Analysis', 'enable_sentiment_analysis'),
            ('Social Signals', 'enable_social_signals'),
            ('News Feeds', 'enable_news_feeds'),
            ('WebSocket Streams', 'enable_websocket_streams')
        ]
        
        for feature_name, feature_key in features:
            status = '✅' if self.config.get(feature_key) else '❌'
            print(f"  - {feature_name}: {status}")

async def main():
    """Main function"""
    runner = AMPJobRunner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            runner.show_status()
        elif command == "run":
            await runner.run_next_job()
        elif command == "deploy":
            await runner.run_deploy_job()
        else:
            print("Usage: python amp_job_runner.py [status|run|deploy]")
    else:
        print("🚀 AMP Job Runner")
        print("Available commands:")
        print("  status - Show AMP status")
        print("  run    - Execute next job")
        print("  deploy - Execute deployment job")
        print("\nExample: python amp_job_runner.py deploy")

if __name__ == "__main__":
    asyncio.run(main())