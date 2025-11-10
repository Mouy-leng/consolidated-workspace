#!/usr/bin/env python3
"""
Autonomous Trading Bot - A6-9V Organization
Main execution entry point
"""
import asyncio
import logging
import os
import yaml
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

# Import trading modules
from exchange.connector import ExchangeConnector
from execution.order_manager import OrderManager
from strategies.momentum_strategy import MomentumStrategy

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class AutonomousTrader:
    """Autonomous trading system with self-executing strategies"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        
        # Components
        self.exchange = None
        self.order_manager = None
        self.strategy = None
        
        # State
        self.total_trades = 0
        self.successful_trades = 0
        self.daily_pnl = 0
        
    async def initialize(self):
        """Initialize trading system components"""
        logger.info("="*60)
        logger.info("Initializing Autonomous Trading Bot")
        logger.info(f"Organization: {os.getenv('ORGANIZATION', 'A6-9V')}")
        logger.info(f"User: {os.getenv('USER', 'mouy-leng')}")
        logger.info("="*60)
        
        # Initialize exchange connection
        exchange_config = {
            'exchange_id': self.config['exchange']['exchange_id'],
            'testnet': self.config['exchange']['testnet'],
            'api_key': os.getenv('BINANCE_API_KEY'),
            'api_secret': os.getenv('BINANCE_API_SECRET')
        }
        
        self.exchange = ExchangeConnector(exchange_config)
        connected = await self.exchange.initialize()
        
        if not connected:
            logger.error("Failed to connect to exchange. Check your API credentials.")
            return False
            
        # Initialize order manager
        self.order_manager = OrderManager(self.exchange)
        logger.info("Order manager initialized")
        
        # Initialize strategy
        strategy_config = {
            'symbol': self.config['trading']['symbol'],
            'timeframe': self.config['trading']['timeframe'],
            'lookback': self.config['strategy']['lookback'],
            'momentum_threshold': self.config['strategy']['momentum_threshold'],
            'risk_percentage': self.config['strategy']['risk_percentage'],
            'min_balance': self.config['strategy']['min_balance']
        }
        
        self.strategy = MomentumStrategy(strategy_config)
        logger.info(f"Strategy initialized: {self.strategy.name}")
        
        # Check initial balance
        balance = await self.exchange.get_balance(self.config['trading']['base_currency'])
        logger.info(f"Initial balance: {balance.get('free', 0)} {self.config['trading']['base_currency']}")
        
        logger.info("="*60)
        logger.info("Initialization complete!")
        logger.info("="*60)
        
        return True
        
    async def execute_autonomous_cycle(self):
        """Main autonomous execution loop"""
        analysis_interval = self.config['monitoring']['analysis_interval']
        
        while self.is_running:
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"Trading Cycle - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*60}")
                
                # Analyze market
                analysis = await self.strategy.analyze(self.exchange)
                signal = analysis.get('signal', 'HOLD')
                price = analysis.get('price', 0)
                
                logger.info(f"Signal: {signal} | Price: ${price:.2f}")
                logger.info(f"Momentum: {analysis.get('momentum', 0):.4f} | Price Change: {analysis.get('price_change', 0):.4f}")
                
                # Execute trading logic
                if signal != 'HOLD':
                    await self.execute_trade(signal, price)
                else:
                    logger.info("No trading signal, holding position")
                
                # Display statistics
                stats = self.order_manager.get_order_stats()
                logger.info(f"\nStats: Total={stats['total_orders']} | Active={stats['active_orders']} | Success Rate={stats['success_rate']*100:.1f}%")
                
                # Wait for next cycle
                logger.info(f"\nWaiting {analysis_interval} seconds until next analysis...")
                await asyncio.sleep(analysis_interval)
                
            except KeyboardInterrupt:
                logger.info("Received shutdown signal...")
                break
            except Exception as e:
                logger.error(f"Error in autonomous cycle: {e}", exc_info=True)
                await asyncio.sleep(10)
                
    async def execute_trade(self, signal: str, price: float):
        """Execute trade based on signal"""
        try:
            base_currency = self.config['trading']['base_currency']
            balance_info = await self.exchange.get_balance(base_currency)
            balance = balance_info.get('free', 0)
            
            logger.info(f"Available balance: {balance} {base_currency}")
            
            # Check if we can execute
            can_execute = await self.strategy.can_execute(signal, balance)
            
            if not can_execute:
                logger.info(f"Cannot execute {signal} signal at this time")
                return
                
            symbol = self.config['trading']['symbol']
            
            if signal == 'BUY':
                # Calculate position size
                amount = await self.strategy.calculate_position_size(balance, price)
                
                if amount <= 0:
                    logger.warning("Calculated amount is too small to trade")
                    return
                
                logger.info(f"Executing BUY: {amount} {symbol}")
                
                # Place order
                result = await self.order_manager.place_market_order(
                    symbol=symbol,
                    side='buy',
                    amount=amount,
                    metadata={'strategy': self.strategy.name, 'signal': signal}
                )
                
                if result['success']:
                    logger.info(f"✓ BUY order executed successfully! Order ID: {result['order_id']}")
                    self.strategy.update_position('BUY', price, amount)
                    self.total_trades += 1
                    self.successful_trades += 1
                else:
                    logger.error(f"✗ BUY order failed: {result.get('error')}")
                    
            elif signal == 'SELL':
                position = self.strategy.get_position_info()
                if not position:
                    logger.warning("No position to sell")
                    return
                    
                amount = position['amount']
                
                logger.info(f"Executing SELL: {amount} {symbol}")
                
                # Place order
                result = await self.order_manager.place_market_order(
                    symbol=symbol,
                    side='sell',
                    amount=amount,
                    metadata={'strategy': self.strategy.name, 'signal': signal}
                )
                
                if result['success']:
                    logger.info(f"✓ SELL order executed successfully! Order ID: {result['order_id']}")
                    self.strategy.update_position('SELL', price, amount)
                    self.total_trades += 1
                    self.successful_trades += 1
                else:
                    logger.error(f"✗ SELL order failed: {result.get('error')}")
                    
        except Exception as e:
            logger.error(f"Error executing trade: {e}", exc_info=True)
            
    async def start(self):
        """Start autonomous trading"""
        self.is_running = True
        
        if self.config['safety']['paper_trading']:
            logger.warning("\n⚠️  PAPER TRADING MODE - No real money will be used ⚠️\n")
        else:
            logger.warning("\n🔴 LIVE TRADING MODE - Real money at risk! 🔴\n")
            
        logger.info("Starting autonomous trading system...\n")
        await self.execute_autonomous_cycle()
        
    async def stop(self):
        """Stop autonomous trading"""
        self.is_running = False
        logger.info("Stopping autonomous trading system...")
        
        if self.exchange:
            await self.exchange.close()
            
        logger.info("Trading session summary:")
        logger.info(f"Total trades: {self.total_trades}")
        logger.info(f"Successful trades: {self.successful_trades}")
        logger.info("Shutdown complete")


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}


async def main():
    """Main entry point"""
    # Load configuration
    config = load_config()
    
    if not config:
        logger.error("Failed to load configuration. Exiting.")
        return
    
    # Create and initialize trader
    trader = AutonomousTrader(config)
    
    initialized = await trader.initialize()
    if not initialized:
        logger.error("Failed to initialize trader. Exiting.")
        return
    
    # Start trading
    try:
        await trader.start()
    except KeyboardInterrupt:
        logger.info("\nReceived interrupt signal")
    finally:
        await trader.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
