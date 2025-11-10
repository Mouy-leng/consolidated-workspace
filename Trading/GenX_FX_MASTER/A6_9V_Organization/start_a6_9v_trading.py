#!/usr/bin/env python3
"""
A6_9V Organization - GenX FX Trading System
FBS Markets LIVE Account Trading
"""

import os
import sys
import json
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class A6_9V_TradingSystem:
    """A6_9V Organization Trading System"""
    
    def __init__(self):
        self.config_file = "A6_9V_config.json"
        self.load_config()
        self.is_running = False
        
    def load_config(self):
        """Load A6_9V configuration"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            logger.info("A6_9V configuration loaded successfully")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            sys.exit(1)
    
    def display_info(self):
        """Display A6_9V system information"""
        print("=" * 60)
        print("A6_9V ORGANIZATION - GENX FX TRADING SYSTEM")
        print("=" * 60)
        print(f"Organization: {self.config['organization']['name']}")
        print(f"Version: {self.config['organization']['version']}")
        print(f"Project: {self.config['project']['name']}")
        print(f"Environment: {self.config['project']['environment']}")
        print(f"Broker: {self.config['broker']['name']}")
        print(f"Account: {self.config['broker']['login']}")
        print(f"Server: {self.config['broker']['server']}")
        print(f"Balance: ${self.config['broker']['account_balance']}")
        print(f"Account Type: {self.config['broker']['account_type']}")
        print("=" * 60)
        print("LIVE TRADING SYSTEM - REAL MONEY")
        print("=" * 60)
    
    def start_trading(self):
        """Start the A6_9V trading system"""
        self.is_running = True
        logger.info("Starting A6_9V Trading System...")
        
        # Create necessary directories
        os.makedirs('logs', exist_ok=True)
        os.makedirs('signal_output', exist_ok=True)
        
        # Initialize trading
        self.initialize_trading()
        
        # Main trading loop
        self.run_trading_loop()
    
    def initialize_trading(self):
        """Initialize trading components"""
        logger.info("Initializing A6_9V trading components...")
        
        # Create initial status
        status = {
            'timestamp': datetime.now().isoformat(),
            'organization': self.config['organization']['name'],
            'status': 'ACTIVE',
            'account': self.config['broker']['login'],
            'balance': self.config['broker']['account_balance'],
            'trading_enabled': self.config['trading']['enabled']
        }
        
        with open('signal_output/a6_9v_status.json', 'w') as f:
            json.dump(status, f, indent=2)
        
        logger.info("A6_9V trading components initialized")
    
    def run_trading_loop(self):
        """Main trading loop"""
        logger.info("A6_9V trading loop started")
        
        try:
            iteration = 0
            while self.is_running and iteration < 10:  # Run for 10 iterations as demo
                iteration += 1
                
                # Generate signals
                self.generate_signals()
                
                # Update status
                self.update_status()
                
                print(f"Iteration {iteration}: System running normally...")
                
                # Wait for next iteration
                time.sleep(5)  # 5 seconds for demo
                
            print("Demo completed successfully!")
            self.stop_trading()
                
        except KeyboardInterrupt:
            logger.info("Received stop signal")
            self.stop_trading()
        except Exception as e:
            logger.error(f"Error in trading loop: {e}")
            self.stop_trading()
    
    def generate_signals(self):
        """Generate trading signals"""
        current_time = datetime.now()
        
        # Example signal generation
        signal = {
            'timestamp': current_time.isoformat(),
            'organization': 'A6_9V',
            'symbol': 'EURUSD',
            'action': 'BUY',
            'entry': 1.0850,
            'stop_loss': 1.0820,
            'take_profit': 1.0910,
            'lot_size': self.config['trading']['lot_size'],
            'confidence': 0.85,
            'account': self.config['broker']['login']
        }
        
        # Save signal
        self.save_signal(signal)
        logger.info(f"Generated signal: {signal['symbol']} {signal['action']}")
    
    def save_signal(self, signal):
        """Save trading signal"""
        # Save to JSON
        signal_file = 'signal_output/a6_9v_signals.json'
        
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
        csv_file = 'signal_output/A6_9V_Signals.csv'
        csv_line = f"{signal['timestamp']},{signal['symbol']},{signal['action']}," \
                  f"{signal['entry']},{signal['stop_loss']},{signal['take_profit']}," \
                  f"{signal['lot_size']},{signal['confidence']},A6_9V_{signal['account']}\n"
        
        with open(csv_file, 'a') as f:
            f.write(csv_line)
    
    def update_status(self):
        """Update system status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'organization': 'A6_9V',
            'status': 'RUNNING',
            'account': self.config['broker']['login'],
            'server': self.config['broker']['server'],
            'balance': self.config['broker']['account_balance'],
            'trading_enabled': self.config['trading']['enabled'],
            'auto_trading': self.config['trading']['auto_trading']
        }
        
        with open('signal_output/a6_9v_status.json', 'w') as f:
            json.dump(status, f, indent=2)
    
    def stop_trading(self):
        """Stop the trading system"""
        logger.info("Stopping A6_9V Trading System...")
        self.is_running = False
        
        # Update final status
        status = {
            'timestamp': datetime.now().isoformat(),
            'organization': 'A6_9V',
            'status': 'STOPPED',
            'account': self.config['broker']['login']
        }
        
        with open('signal_output/a6_9v_status.json', 'w') as f:
            json.dump(status, f, indent=2)
        
        logger.info("A6_9V Trading System stopped")

def main():
    """Main function"""
    # Initialize A6_9V Trading System
    trading_system = A6_9V_TradingSystem()
    
    # Display system info
    trading_system.display_info()
    
    # Start trading
    trading_system.start_trading()

if __name__ == "__main__":
    main()