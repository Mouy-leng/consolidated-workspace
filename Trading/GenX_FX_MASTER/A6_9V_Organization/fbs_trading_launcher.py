#!/usr/bin/env python3
"""
FBS Markets GenX FX Trading System Launcher
Company: FBS Markets Inc. IO
Login: 104818081
Server: FBS-Demo
Server IP: 167.99.81.216:443
Password: Leng12345@#$01
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.trading_engine import TradingEngine
from core.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fbs_trading.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class FBSMarketsTradingSystem:
    """FBS Markets Trading System"""
    
    def __init__(self):
        self.trading_engine = None
        self.is_running = False
        
        # FBS Markets Configuration
        self.fbs_config = {
            'company': 'FBS Markets Inc. IO',
            'login': '104818081',
            'password': 'Leng12345@#$01',
            'server': 'FBS-Demo',
            'server_ip': '167.99.81.216:443',
            'account_balance': 25.00,
            'account_currency': 'USD',
            'account_type': 'DEMO'
        }
        
        logger.info("FBS Markets Trading System initialized")
        logger.info(f"Company: {self.fbs_config['company']}")
        logger.info(f"Login: {self.fbs_config['login']}")
        logger.info(f"Server: {self.fbs_config['server']}")
        logger.info(f"Account Balance: ${self.fbs_config['account_balance']}")
    
    async def start(self):
        """Start the FBS Markets trading system"""
        if self.is_running:
            logger.warning("Trading system is already running")
            return
        
        self.is_running = True
        logger.info("Starting FBS Markets Trading System...")
        
        try:
            # Initialize trading engine
            self.trading_engine = TradingEngine()
            
            # Update configuration with FBS Markets settings
            config.update({
                'fbs_markets': self.fbs_config,
                'trading': {
                    **config.get('trading', {}),
                    'enabled': True,
                    'auto_trading': True,
                    'account_balance': self.fbs_config['account_balance']
                }
            })
            
            # Start trading engine
            await self.trading_engine.start()
            
        except Exception as e:
            logger.error(f"Error starting trading system: {e}")
            await self.stop()
    
    async def stop(self):
        """Stop the trading system"""
        logger.info("Stopping FBS Markets Trading System...")
        self.is_running = False
        
        if self.trading_engine:
            await self.trading_engine.stop()
        
        logger.info("Trading system stopped")
    
    def get_status(self):
        """Get system status"""
        return {
            'is_running': self.is_running,
            'fbs_config': self.fbs_config,
            'trading_engine_status': self.trading_engine.is_running if self.trading_engine else False,
            'performance_report': self.trading_engine.get_performance_report() if self.trading_engine else {}
        }

async def main():
    """Main function"""
    print("=" * 50)
    print("FBS Markets GenX FX Trading System")
    print("=" * 50)
    print(f"Company: FBS Markets Inc. IO")
    print(f"Login: 104818081")
    print(f"Server: FBS-Demo")
    print(f"Server IP: 167.99.81.216:443")
    print(f"Account Balance: $25.00")
    print("=" * 50)
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Initialize and start trading system
    trading_system = FBSMarketsTradingSystem()
    
    try:
        await trading_system.start()
        
        # Keep running until interrupted
        while trading_system.is_running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await trading_system.stop()
        logger.info("FBS Markets Trading System shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
