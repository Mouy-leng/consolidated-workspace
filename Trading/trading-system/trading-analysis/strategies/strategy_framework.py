"""
Strategy Development and Backtesting Framework
Provides tools for creating, testing, and optimizing trading strategies
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
import logging
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from enum import Enum

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class Trade:
    """Trade execution record"""
    symbol: str
    side: OrderSide
    quantity: float
    entry_price: float
    entry_time: datetime
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    commission: float = 0.0
    pnl: float = 0.0
    is_open: bool = True

@dataclass
class StrategyPerformance:
    """Strategy performance metrics"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    max_drawdown: float
    sharpe_ratio: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    max_consecutive_wins: int
    max_consecutive_losses: int

class TradingStrategy:
    """Base class for trading strategies"""
    
    def __init__(self, name: str, initial_capital: float = 10000):
        self.name = name
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.trades: List[Trade] = []
        self.open_trades: List[Trade] = []
        self.signals: List[Dict] = []
        self.logger = logging.getLogger(f"Strategy.{name}")
        
    def generate_signal(self, data: pd.DataFrame, current_time: datetime) -> Optional[Dict]:
        """Generate trading signal based on market data
        
        Should be implemented by subclasses
        Returns: Dict with 'action', 'symbol', 'quantity', 'price', etc.
        """
        raise NotImplementedError("Subclasses must implement generate_signal method")
    
    def calculate_position_size(self, signal: Dict, current_price: float, 
                              stop_loss: float, risk_per_trade: float = 0.02) -> float:
        """Calculate position size based on risk management"""
        risk_amount = self.current_capital * risk_per_trade
        price_diff = abs(current_price - stop_loss)
        
        if price_diff > 0:
            position_size = risk_amount / price_diff
            # Don't risk more than 10% of capital on single trade
            max_position = self.current_capital * 0.1 / current_price
            return min(position_size, max_position)
        
        return 0.0
    
    def execute_trade(self, signal: Dict, current_data: pd.Series) -> Optional[Trade]:
        """Execute trade based on signal"""
        try:
            symbol = signal.get('symbol', 'EURUSD')
            action = signal.get('action')
            price = signal.get('price', current_data['Close'])
            
            if action in ['BUY', 'SELL']:
                # Calculate position size
                stop_loss = signal.get('stop_loss', price * 0.99 if action == 'BUY' else price * 1.01)
                quantity = self.calculate_position_size(signal, price, stop_loss)
                
                if quantity > 0:
                    trade = Trade(
                        symbol=symbol,
                        side=OrderSide.BUY if action == 'BUY' else OrderSide.SELL,
                        quantity=quantity,
                        entry_price=price,
                        entry_time=current_data.name,
                        stop_loss=signal.get('stop_loss'),
                        take_profit=signal.get('take_profit'),
                        commission=quantity * price * 0.0003  # 0.03% commission
                    )
                    
                    self.open_trades.append(trade)
                    self.trades.append(trade)
                    self.current_capital -= trade.commission
                    
                    self.logger.info(f"Executed {action} trade: {quantity:.2f} {symbol} @ {price:.5f}")
                    return trade
                    
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
        
        return None
    
    def check_exit_conditions(self, trade: Trade, current_data: pd.Series) -> bool:
        """Check if trade should be closed"""
        current_price = current_data['Close']
        
        # Check stop loss
        if trade.stop_loss:
            if (trade.side == OrderSide.BUY and current_price <= trade.stop_loss) or \
               (trade.side == OrderSide.SELL and current_price >= trade.stop_loss):
                return True
        
        # Check take profit
        if trade.take_profit:
            if (trade.side == OrderSide.BUY and current_price >= trade.take_profit) or \
               (trade.side == OrderSide.SELL and current_price <= trade.take_profit):
                return True
        
        return False
    
    def close_trade(self, trade: Trade, exit_price: float, exit_time: datetime) -> None:
        """Close an open trade"""
        trade.exit_price = exit_price
        trade.exit_time = exit_time
        trade.is_open = False
        
        # Calculate P&L
        if trade.side == OrderSide.BUY:
            trade.pnl = (exit_price - trade.entry_price) * trade.quantity - trade.commission
        else:
            trade.pnl = (trade.entry_price - exit_price) * trade.quantity - trade.commission
        
        self.current_capital += trade.pnl
        
        # Remove from open trades
        if trade in self.open_trades:
            self.open_trades.remove(trade)
        
        self.logger.info(f"Closed trade: {trade.pnl:.2f} PnL")

class RSIStrategy(TradingStrategy):
    """RSI-based trading strategy"""
    
    def __init__(self, rsi_period: int = 14, oversold: int = 30, overbought: int = 70):
        super().__init__("RSI Strategy")
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
        
    def generate_signal(self, data: pd.DataFrame, current_time: datetime) -> Optional[Dict]:
        """Generate RSI-based signals"""
        if len(data) < self.rsi_period + 1:
            return None
        
        # Calculate RSI
        close_prices = data['Close']
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        previous_rsi = rsi.iloc[-2]
        current_price = close_prices.iloc[-1]
        
        # Generate signals
        if previous_rsi <= self.oversold and current_rsi > self.oversold:
            # RSI crosses above oversold - BUY signal
            return {
                'action': 'BUY',
                'symbol': 'EURUSD',
                'price': current_price,
                'stop_loss': current_price * 0.98,
                'take_profit': current_price * 1.04,
                'reason': f'RSI({current_rsi:.1f}) crossed above oversold({self.oversold})'
            }
        
        elif previous_rsi >= self.overbought and current_rsi < self.overbought:
            # RSI crosses below overbought - SELL signal
            return {
                'action': 'SELL',
                'symbol': 'EURUSD',
                'price': current_price,
                'stop_loss': current_price * 1.02,
                'take_profit': current_price * 0.96,
                'reason': f'RSI({current_rsi:.1f}) crossed below overbought({self.overbought})'
            }
        
        return None

class MACDStrategy(TradingStrategy):
    """MACD-based trading strategy"""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        super().__init__("MACD Strategy")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        
    def generate_signal(self, data: pd.DataFrame, current_time: datetime) -> Optional[Dict]:
        """Generate MACD-based signals"""
        if len(data) < self.slow_period + self.signal_period:
            return None
        
        # Calculate MACD
        close_prices = data['Close']
        ema_fast = close_prices.ewm(span=self.fast_period).mean()
        ema_slow = close_prices.ewm(span=self.slow_period).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.signal_period).mean()
        
        current_macd = macd_line.iloc[-1]
        current_signal = signal_line.iloc[-1]
        previous_macd = macd_line.iloc[-2]
        previous_signal = signal_line.iloc[-2]
        current_price = close_prices.iloc[-1]
        
        # MACD line crosses above signal line - BUY
        if previous_macd <= previous_signal and current_macd > current_signal:
            return {
                'action': 'BUY',
                'symbol': 'EURUSD',
                'price': current_price,
                'stop_loss': current_price * 0.985,
                'take_profit': current_price * 1.03,
                'reason': 'MACD bullish crossover'
            }
        
        # MACD line crosses below signal line - SELL
        elif previous_macd >= previous_signal and current_macd < current_signal:
            return {
                'action': 'SELL',
                'symbol': 'EURUSD',
                'price': current_price,
                'stop_loss': current_price * 1.015,
                'take_profit': current_price * 0.97,
                'reason': 'MACD bearish crossover'
            }
        
        return None

class MovingAverageCrossStrategy(TradingStrategy):
    """Moving Average Crossover Strategy"""
    
    def __init__(self, fast_ma: int = 20, slow_ma: int = 50):
        super().__init__("MA Cross Strategy")
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
        
    def generate_signal(self, data: pd.DataFrame, current_time: datetime) -> Optional[Dict]:
        """Generate MA crossover signals"""
        if len(data) < self.slow_ma + 1:
            return None
        
        close_prices = data['Close']
        fast_ma = close_prices.rolling(window=self.fast_ma).mean()
        slow_ma = close_prices.rolling(window=self.slow_ma).mean()
        
        current_fast = fast_ma.iloc[-1]
        current_slow = slow_ma.iloc[-1]
        previous_fast = fast_ma.iloc[-2]
        previous_slow = slow_ma.iloc[-2]
        current_price = close_prices.iloc[-1]
        
        # Fast MA crosses above slow MA - BUY
        if previous_fast <= previous_slow and current_fast > current_slow:
            return {
                'action': 'BUY',
                'symbol': 'EURUSD',
                'price': current_price,
                'stop_loss': current_price * 0.98,
                'take_profit': current_price * 1.04,
                'reason': f'MA({self.fast_ma}) crossed above MA({self.slow_ma})'
            }
        
        # Fast MA crosses below slow MA - SELL
        elif previous_fast >= previous_slow and current_fast < current_slow:
            return {
                'action': 'SELL',
                'symbol': 'EURUSD',
                'price': current_price,
                'stop_loss': current_price * 1.02,
                'take_profit': current_price * 0.96,
                'reason': f'MA({self.fast_ma}) crossed below MA({self.slow_ma})'
            }
        
        return None

class BacktestEngine:
    """Backtesting engine for trading strategies"""
    
    def __init__(self):
        self.logger = logging.getLogger("BacktestEngine")
        
    def run_backtest(self, strategy: TradingStrategy, data: pd.DataFrame, 
                    start_date: Optional[datetime] = None, 
                    end_date: Optional[datetime] = None) -> StrategyPerformance:
        """Run backtest on historical data"""
        
        # Filter data by date range if specified
        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]
        
        self.logger.info(f"Starting backtest for {strategy.name}")
        self.logger.info(f"Data range: {data.index[0]} to {data.index[-1]}")
        self.logger.info(f"Total bars: {len(data)}")
        
        # Reset strategy state
        strategy.current_capital = strategy.initial_capital
        strategy.trades = []
        strategy.open_trades = []
        strategy.signals = []
        
        # Run strategy on each bar
        for i in range(1, len(data)):
            current_data = data.iloc[i]
            historical_data = data.iloc[max(0, i-200):i+1]  # Last 200 bars for analysis
            
            # Check exit conditions for open trades
            for trade in strategy.open_trades.copy():
                if strategy.check_exit_conditions(trade, current_data):
                    strategy.close_trade(trade, current_data['Close'], current_data.name)
            
            # Generate new signals
            signal = strategy.generate_signal(historical_data, current_data.name)
            if signal:
                strategy.signals.append(signal)
                strategy.execute_trade(signal, current_data)
        
        # Close any remaining open trades at the end
        for trade in strategy.open_trades.copy():
            strategy.close_trade(trade, data.iloc[-1]['Close'], data.index[-1])
        
        # Calculate performance metrics
        performance = self._calculate_performance(strategy)
        
        self.logger.info(f"Backtest completed. Total trades: {performance.total_trades}")
        self.logger.info(f"Win rate: {performance.win_rate:.2%}")
        self.logger.info(f"Total PnL: {performance.total_pnl:.2f}")
        
        return performance
    
    def _calculate_performance(self, strategy: TradingStrategy) -> StrategyPerformance:
        """Calculate strategy performance metrics"""
        trades = [t for t in strategy.trades if not t.is_open]
        
        if not trades:
            return StrategyPerformance(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        # Basic metrics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.pnl > 0])
        losing_trades = len([t for t in trades if t.pnl < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        total_pnl = sum(t.pnl for t in trades)
        
        # Wins and losses
        wins = [t.pnl for t in trades if t.pnl > 0]
        losses = [t.pnl for t in trades if t.pnl < 0]
        
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0
        
        # Profit factor
        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Drawdown calculation
        equity_curve = [strategy.initial_capital]
        running_total = strategy.initial_capital
        
        for trade in trades:
            running_total += trade.pnl
            equity_curve.append(running_total)
        
        peak = equity_curve[0]
        max_drawdown = 0
        
        for equity in equity_curve[1:]:
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        # Sharpe ratio (simplified)
        if len(trades) > 1:
            returns = [t.pnl / strategy.initial_capital for t in trades]
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Consecutive wins/losses
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        
        for trade in trades:
            if trade.pnl > 0:
                consecutive_wins += 1
                consecutive_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
            else:
                consecutive_losses += 1
                consecutive_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        
        return StrategyPerformance(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            profit_factor=profit_factor,
            avg_win=avg_win,
            avg_loss=avg_loss,
            max_consecutive_wins=max_consecutive_wins,
            max_consecutive_losses=max_consecutive_losses
        )

if __name__ == "__main__":
    # Example usage
    print("Trading Strategy Framework initialized!")
    print("Available strategies:")
    print("- RSI Strategy")
    print("- MACD Strategy") 
    print("- Moving Average Cross Strategy")
    print("- Custom Strategy (base class)")