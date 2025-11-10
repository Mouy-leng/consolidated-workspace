#!/usr/bin/env python3
"""
FBS Markets LIVE Account Trading System Launcher
Company: FBS Markets Inc. IO
Login: 104818081
Server: FBS-Demo
Server IP: 167.99.81.216:443
Password: Leng12345@#$01
Account Type: LIVE (with $25 deposit)
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fbs_live_trading.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class FBSLiveTradingSystem:
    """FBS Markets LIVE Account Trading System"""
    
    def __init__(self):
        self.is_running = False
        
        # FBS Markets LIVE Configuration
        self.fbs_config = {
            'company': 'FBS Markets Inc. IO',
            'login': '104818081',
            'password': 'Leng12345@#$01',
            'server': 'FBS-Demo',
            'server_ip': '167.99.81.216:443',
            'account_balance': 25.00,
            'account_currency': 'USD',
            'account_type': 'LIVE',
            'environment': 'LIVE'
        }
        
        # Trading settings for LIVE account
        self.trading_settings = {
            'enabled': True,
            'auto_trading': True,
            'lot_size': 0.01,
            'max_spread': 30,
            'risk_percentage': 1.0,  # Conservative for LIVE account
            'max_risk_per_trade': 1.0,
            'max_total_risk': 3.0,
            'min_confidence_threshold': 0.8,
            'max_concurrent_signals': 2
        }
        
        logger.info("FBS Markets LIVE Trading System initialized")
        logger.info(f"Company: {self.fbs_config['company']}")
        logger.info(f"Login: {self.fbs_config['login']}")
        logger.info(f"Server: {self.fbs_config['server']}")
        logger.info(f"Account Type: {self.fbs_config['account_type']}")
        logger.info(f"Account Balance: ${self.fbs_config['account_balance']}")
        logger.info(f"Risk per Trade: {self.trading_settings['risk_percentage']}%")
    
    async def start(self):
        """Start the FBS Markets LIVE trading system"""
        if self.is_running:
            logger.warning("LIVE trading system is already running")
            return
        
        self.is_running = True
        logger.info("Starting FBS Markets LIVE Trading System...")
        
        try:
            # Create signal output directory
            os.makedirs('signal_output', exist_ok=True)
            
            # Initialize trading components
            await self._initialize_trading_components()
            
            # Start main trading loop
            await self._run_trading_loop()
            
        except Exception as e:
            logger.error(f"Error starting LIVE trading system: {e}")
            await self.stop()
    
    async def _initialize_trading_components(self):
        """Initialize trading components"""
        logger.info("Initializing trading components...")
        
        # Create initial signal file
        signal_data = {
            'timestamp': datetime.now().isoformat(),
            'account_info': self.fbs_config,
            'trading_settings': self.trading_settings,
            'status': 'INITIALIZED',
            'signals': []
        }
        
        with open('signal_output/fbs_live_signals.json', 'w') as f:
            json.dump(signal_data, f, indent=2)
        
        logger.info("Trading components initialized successfully")
    
    async def _run_trading_loop(self):
        """Main trading loop for LIVE account"""
        logger.info("LIVE Trading loop started")
        
        while self.is_running:
            try:
                # Generate trading signals
                signals = await self._generate_live_signals()
                
                # Process signals
                if signals:
                    await self._process_signals(signals)
                
                # Update status
                await self._update_status()
                
                # Wait before next iteration
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in LIVE trading loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _generate_live_signals(self):
        """Generate trading signals for LIVE account"""
        # This would integrate with your AI signal generation
        # For now, we'll create a placeholder signal
        signals = []
        
        # Example signal generation (replace with actual AI logic)
        current_time = datetime.now()
        if current_time.second % 60 == 0:  # Generate signal every minute
            signal = {
                'timestamp': current_time.isoformat(),
                'symbol': 'EURUSD',
                'signal': 'BUY',
                'entry_price': 1.0850,
                'stop_loss': 1.0820,
                'take_profit': 1.0910,
                'confidence': 0.85,
                'risk_reward': 2.0,
                'lot_size': self.trading_settings['lot_size'],
                'account': self.fbs_config['login']
            }
            signals.append(signal)
            logger.info(f"Generated LIVE signal: {signal['symbol']} {signal['signal']}")
        
        return signals
    
    async def _process_signals(self, signals):
        """Process trading signals for LIVE account"""
        for signal in signals:
            try:
                # Save signal to file
                await self._save_signal(signal)
                
                # Log signal
                logger.info(f"Processing LIVE signal: {signal['symbol']} {signal['signal']} "
                           f"at {signal['entry_price']} (Confidence: {signal['confidence']})")
                
            except Exception as e:
                logger.error(f"Error processing signal: {e}")
    
    async def _save_signal(self, signal):
        """Save signal to output files"""
        # Save to JSON
        signal_file = 'signal_output/fbs_live_signals.json'
        if os.path.exists(signal_file):
            with open(signal_file, 'r') as f:
                data = json.load(f)
        else:
            data = {'signals': []}
        
        data['signals'].append(signal)
        data['last_update'] = datetime.now().isoformat()
        
        with open(signal_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Save to CSV for MT5
        csv_file = 'signal_output/MT5_Signals.csv'
        csv_line = f"{signal['timestamp']},{signal['symbol']},{signal['signal']}," \
                  f"{signal['entry_price']},{signal['stop_loss']},{signal['take_profit']}," \
                  f"{signal['lot_size']},{signal['confidence']},{signal['risk_reward']}," \
                  f"FBS_LIVE_{signal['account']}\n"
        
        with open(csv_file, 'a') as f:
            f.write(csv_line)
    
    async def _update_status(self):
        """Update system status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'is_running': self.is_running,
            'account': self.fbs_config,
            'trading_settings': self.trading_settings,
            'status': 'ACTIVE'
        }
        
        with open('signal_output/fbs_live_status.json', 'w') as f:
            json.dump(status, f, indent=2)
    
    async def stop(self):
        """Stop the LIVE trading system"""
        logger.info("Stopping FBS Markets LIVE Trading System...")
        self.is_running = False
        
        # Save final status
        await self._update_status()
        
        logger.info("LIVE Trading system stopped")

async def main():
    """Main function"""
    print("=" * 60)
    print("FBS MARKETS LIVE ACCOUNT TRADING SYSTEM")
    print("=" * 60)
    print(f"Company: FBS Markets Inc. IO")
    print(f"Login: 104818081")
    print(f"Server: FBS-Demo")
    print(f"Server IP: 167.99.81.216:443")
    print(f"Account Type: LIVE")
    print(f"Account Balance: $25.00")
    print(f"Risk per Trade: 1.0%")
    print(f"Max Total Risk: 3.0%")
    print("=" * 60)
    print("⚠️  LIVE ACCOUNT - REAL MONEY TRADING ⚠️")
    print("=" * 60)
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Initialize and start LIVE trading system
    trading_system = FBSLiveTradingSystem()
    
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
        logger.info("FBS Markets LIVE Trading System shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nLIVE Trading System shutdown complete")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
