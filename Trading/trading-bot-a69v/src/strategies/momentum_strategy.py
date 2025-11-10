"""
Momentum Trading Strategy
Simple strategy based on price momentum and volume
"""
import logging
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MomentumStrategy:
    """
    Simple momentum-based trading strategy
    Buys when price momentum is positive and volume increasing
    Sells when momentum turns negative
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.name = "Momentum Strategy"
        self.config = config
        self.symbol = config.get('symbol', 'BTC/USDT')
        self.timeframe = config.get('timeframe', '5m')
        self.lookback = config.get('lookback', 20)
        self.momentum_threshold = config.get('momentum_threshold', 0.001)  # 0.1%
        
        self.position = None
        self.entry_price = None
        self.last_signal = None
        
    async def analyze(self, exchange) -> Dict[str, Any]:
        """Analyze market and generate signals"""
        try:
            # Get OHLCV data
            ohlcv = await exchange.get_ohlcv(self.symbol, self.timeframe, self.lookback + 10)
            
            if len(ohlcv) < self.lookback:
                logger.warning(f"Insufficient data for analysis: {len(ohlcv)} candles")
                return {'signal': 'HOLD', 'reason': 'Insufficient data'}
            
            # Extract price and volume data
            closes = np.array([candle[4] for candle in ohlcv])  # Close prices
            volumes = np.array([candle[5] for candle in ohlcv])  # Volumes
            
            # Calculate momentum indicators
            current_price = closes[-1]
            prev_price = closes[-2]
            avg_price = np.mean(closes[-self.lookback:])
            
            # Price momentum
            price_change = (current_price - prev_price) / prev_price
            momentum = (current_price - avg_price) / avg_price
            
            # Volume analysis
            current_volume = volumes[-1]
            avg_volume = np.mean(volumes[-self.lookback:])
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Generate signal
            signal = self._generate_signal(momentum, price_change, volume_ratio)
            
            return {
                'signal': signal,
                'price': current_price,
                'momentum': momentum,
                'price_change': price_change,
                'volume_ratio': volume_ratio,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market: {e}", exc_info=True)
            return {'signal': 'HOLD', 'reason': f'Analysis error: {str(e)}'}
            
    def _generate_signal(self, momentum: float, price_change: float, volume_ratio: float) -> str:
        """Generate trading signal based on indicators"""
        
        # BUY conditions
        if (momentum > self.momentum_threshold and 
            price_change > 0 and 
            volume_ratio > 1.2):
            return 'BUY'
        
        # SELL conditions
        elif (momentum < -self.momentum_threshold or 
              price_change < -0.002):  # 0.2% drop
            return 'SELL'
        
        return 'HOLD'
        
    async def can_execute(self, signal: str, balance: float) -> bool:
        """Check if strategy can execute given signal"""
        
        if signal == 'BUY':
            # Check if we have no position and sufficient balance
            if self.position is None:
                min_balance = self.config.get('min_balance', 10)
                if balance >= min_balance:
                    return True
                else:
                    logger.warning(f"Insufficient balance for BUY: {balance} < {min_balance}")
            return False
            
        elif signal == 'SELL':
            # Check if we have an open position
            if self.position is not None:
                return True
            return False
            
        return False
        
    async def calculate_position_size(self, balance: float, price: float) -> float:
        """Calculate position size based on risk management"""
        
        # Use percentage of balance
        risk_percentage = self.config.get('risk_percentage', 0.1)  # 10% of balance
        position_value = balance * risk_percentage
        
        # Calculate amount
        amount = position_value / price
        
        # Round to exchange precision (usually 8 decimals for crypto)
        amount = round(amount, 8)
        
        logger.info(f"Calculated position size: {amount} @ {price} = ${position_value:.2f}")
        
        return amount
        
    def update_position(self, signal: str, price: float, amount: float):
        """Update position state"""
        if signal == 'BUY':
            self.position = {
                'side': 'LONG',
                'entry_price': price,
                'amount': amount,
                'entry_time': datetime.now()
            }
            self.entry_price = price
            logger.info(f"Position opened: LONG {amount} @ {price}")
            
        elif signal == 'SELL':
            if self.position:
                pnl = (price - self.entry_price) / self.entry_price
                logger.info(f"Position closed: PnL = {pnl*100:.2f}%")
                self.position = None
                self.entry_price = None
                
    def get_position_info(self) -> Optional[Dict]:
        """Get current position information"""
        return self.position
