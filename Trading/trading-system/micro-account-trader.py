#!/usr/bin/env python3
"""
Micro Account Automated Trading System
Optimized for small account balances ($47.79)
"""

import time
import json
import logging
import datetime
from typing import Dict, List, Any, Optional
import yfinance as yf
import pandas as pd
import numpy as np
import sys

class MicroAccountTrader:
    def __init__(self):
        # Account settings
        self.account_id = "241926287"
        self.server = "FBS-Real-4"
        self.balance = 47.79
        
        # Conservative risk management for micro account
        self.max_risk_percent = 1.5  # 1.5% max risk per trade
        self.min_lot_size = 0.01     # Minimum micro lot
        self.max_lot_size = 0.02     # Maximum lot for small account
        self.max_trades = 2          # Maximum 2 concurrent trades
        
        # Trading symbols optimized for small accounts
        self.symbols = [
            'EURUSD=X',  # Major pair - good spreads
            'GBPUSD=X',  # Major pair - good volatility
            'USDJPY=X',  # Major pair - stable
            'GC=F',      # Gold - good for trending
            'AUDUSD=X'   # Minor pair - good range
        ]
        
        self.symbol_map = {
            'EURUSD=X': 'EURUSD',
            'GBPUSD=X': 'GBPUSD', 
            'USDJPY=X': 'USDJPY',
            'GC=F': 'XAUUSD',
            'AUDUSD=X': 'AUDUSD'
        }
        
        # Tracking
        self.active_trades = []
        self.trade_history = []
        self.daily_profit = 0.0
        
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging"""
        # Ensure console uses UTF-8 on Windows to avoid UnicodeEncodeError for emoji
        try:
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

        # Configure handlers explicitly using sys.stdout for stream handler
        file_handler = logging.FileHandler('micro_trading.log', encoding='utf-8')
        stream_handler = logging.StreamHandler(stream=sys.stdout)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[file_handler, stream_handler]
        )

        self.logger = logging.getLogger(__name__)
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                              stop_loss: float) -> float:
        """Calculate position size based on risk management"""
        
        # Maximum risk amount
        max_risk = self.balance * (self.max_risk_percent / 100)
        
        # Calculate pip difference
        if 'JPY' in symbol:
            pip_value = 0.01
            pip_cost = 0.10  # $0.10 per pip for 0.01 lot
        elif symbol == 'XAUUSD':
            pip_value = 0.10
            pip_cost = 0.01  # $0.01 per 0.1 pip for 0.01 lot
        else:
            pip_value = 0.0001
            pip_cost = 0.10  # $0.10 per pip for 0.01 lot
            
        # Calculate pips to stop loss
        pips_to_sl = abs(entry_price - stop_loss) / pip_value
        
        # Calculate lot size
        if pips_to_sl > 0:
            lot_size = max_risk / (pips_to_sl * pip_cost)
            lot_size = min(lot_size, self.max_lot_size)
            lot_size = max(lot_size, self.min_lot_size)
        else:
            lot_size = self.min_lot_size
            
        return round(lot_size, 2)
    
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """Get current market data for symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="5m")
            
            if data.empty:
                return None
                
            current_price = data['Close'].iloc[-1]
            high = data['High'].iloc[-20:].max()
            low = data['Low'].iloc[-20:].min()
            
            # Calculate simple moving averages
            sma_10 = data['Close'].iloc[-10:].mean()
            sma_20 = data['Close'].iloc[-20:].mean()
            
            # Calculate RSI
            rsi = self.calculate_rsi(data['Close'])
            
            return {
                'price': current_price,
                'high_20': high,
                'low_20': low,
                'sma_10': sma_10,
                'sma_20': sma_20,
                'rsi': rsi,
                'volume': data['Volume'].iloc[-1] if 'Volume' in data else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting market data for {symbol}: {e}")
            return None
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        except:
            return 50.0
    
    def analyze_signal(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        """Analyze trading signal for micro account"""
        
        price = market_data['price']
        sma_10 = market_data['sma_10']
        sma_20 = market_data['sma_20']
        rsi = market_data['rsi']
        high_20 = market_data['high_20']
        low_20 = market_data['low_20']
        
        signal = None
        
        # Conservative signals for small account
        
        # Bullish signal: Price above SMA10, SMA10 > SMA20, RSI oversold recovery
        if (price > sma_10 and sma_10 > sma_20 and 
            30 < rsi < 45 and price > low_20 * 1.001):
            
            stop_loss = low_20 * 0.999  # Tight stop loss
            take_profit = price + (price - stop_loss) * 2  # 1:2 RR
            
            signal = {
                'type': 'BUY',
                'entry': price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': 0.7
            }
            
        # Bearish signal: Price below SMA10, SMA10 < SMA20, RSI overbought decline
        elif (price < sma_10 and sma_10 < sma_20 and 
              55 < rsi < 70 and price < high_20 * 0.999):
            
            stop_loss = high_20 * 1.001  # Tight stop loss
            take_profit = price - (stop_loss - price) * 2  # 1:2 RR
            
            signal = {
                'type': 'SELL',
                'entry': price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': 0.7
            }
        
        return signal
    
    def simulate_trade(self, symbol: str, signal: Dict) -> Dict:
        """Simulate trade execution for micro account"""
        
        clean_symbol = self.symbol_map.get(symbol, symbol)
        lot_size = self.calculate_position_size(
            clean_symbol, signal['entry'], signal['stop_loss']
        )
        
        # Calculate potential profit/loss
        if signal['type'] == 'BUY':
            potential_profit = (signal['take_profit'] - signal['entry']) * lot_size * 10
            potential_loss = (signal['entry'] - signal['stop_loss']) * lot_size * 10
        else:
            potential_profit = (signal['entry'] - signal['take_profit']) * lot_size * 10
            potential_loss = (signal['stop_loss'] - signal['entry']) * lot_size * 10
        
        trade = {
            'id': len(self.trade_history) + 1,
            'symbol': clean_symbol,
            'type': signal['type'],
            'entry_price': signal['entry'],
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit'],
            'lot_size': lot_size,
            'potential_profit': round(potential_profit, 2),
            'potential_loss': round(potential_loss, 2),
            'timestamp': datetime.datetime.now().isoformat(),
            'status': 'SIMULATED',
            'confidence': signal['confidence']
        }
        
        return trade
    
    def monitor_positions(self) -> None:
        """Monitor active positions"""
        if not self.active_trades:
            return
            
        for trade in self.active_trades[:]:
            symbol = trade['symbol']
            market_data = self.get_market_data(symbol + '=X' if symbol != 'XAUUSD' else 'GC=F')
            
            if not market_data:
                continue
                
            current_price = market_data['price']
            
            # Check for TP/SL
            if trade['type'] == 'BUY':
                if current_price >= trade['take_profit']:
                    self.close_trade(trade, current_price, 'TP')
                elif current_price <= trade['stop_loss']:
                    self.close_trade(trade, current_price, 'SL')
            else:
                if current_price <= trade['take_profit']:
                    self.close_trade(trade, current_price, 'TP')
                elif current_price >= trade['stop_loss']:
                    self.close_trade(trade, current_price, 'SL')
    
    def close_trade(self, trade: Dict, exit_price: float, reason: str) -> None:
        """Close trade and calculate profit/loss"""
        
        if trade['type'] == 'BUY':
            profit = (exit_price - trade['entry_price']) * trade['lot_size'] * 10
        else:
            profit = (trade['entry_price'] - exit_price) * trade['lot_size'] * 10
        
        trade['exit_price'] = exit_price
        trade['profit'] = round(profit, 2)
        trade['exit_reason'] = reason
        trade['exit_time'] = datetime.datetime.now().isoformat()
        
        self.active_trades.remove(trade)
        self.trade_history.append(trade)
        self.daily_profit += profit
        
        self.logger.info(f"🔚 Trade Closed: {trade['symbol']} {trade['type']} "
                        f"Profit: ${profit:.2f} Reason: {reason}")
    
    def run_trading_cycle(self) -> None:
        """Run one trading cycle"""
        
        self.logger.info(f"🔄 Running trading cycle - Balance: ${self.balance:.2f}")
        
        # Monitor existing positions
        self.monitor_positions()
        
        # Check if we can open new trades
        if len(self.active_trades) >= self.max_trades:
            self.logger.info(f"⏸️ Max trades reached ({len(self.active_trades)}/{self.max_trades})")
            return
        
        # Scan for new opportunities
        for symbol in self.symbols:
            if len(self.active_trades) >= self.max_trades:
                break
                
            market_data = self.get_market_data(symbol)
            if not market_data:
                continue
                
            signal = self.analyze_signal(symbol, market_data)
            if signal and signal['confidence'] > 0.6:
                
                trade = self.simulate_trade(symbol, signal)
                
                # Check daily loss limit
                if self.daily_profit < -5.0:  # Max $5 daily loss
                    self.logger.warning("❌ Daily loss limit reached")
                    break
                
                self.active_trades.append(trade)
                
                self.logger.info(f"📈 New Trade: {trade['symbol']} {trade['type']} "
                               f"Entry: ${trade['entry_price']:.5f} "
                               f"Lot: {trade['lot_size']} "
                               f"Risk: ${trade['potential_loss']:.2f}")
                break
    
    def get_status(self) -> Dict:
        """Get current trading status"""
        return {
            'account_id': self.account_id,
            'balance': self.balance,
            'daily_profit': round(self.daily_profit, 2),
            'active_trades': len(self.active_trades),
            'total_trades': len(self.trade_history),
            'max_trades': self.max_trades,
            'risk_per_trade': f"{self.max_risk_percent}%",
            'status': 'ACTIVE' if len(self.active_trades) > 0 else 'SCANNING'
        }
    
    def run_continuous(self) -> None:
        """Run continuous trading"""
        self.logger.info("🚀 Starting Micro Account Automated Trading")
        self.logger.info(f"💰 Account: {self.account_id} | Balance: ${self.balance}")
        self.logger.info(f"⚖️ Risk: {self.max_risk_percent}% | Max Trades: {self.max_trades}")
        
        while True:
            try:
                self.run_trading_cycle()
                
                # Status update every 10 cycles
                if len(self.trade_history) % 10 == 0:
                    status = self.get_status()
                    self.logger.info(f"📊 Status: {status}")
                
                time.sleep(60)  # Wait 1 minute between cycles
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Trading stopped by user")
                break
            except Exception as e:
                self.logger.error(f"❌ Error in trading cycle: {e}")
                time.sleep(30)

def main():
    """Main function"""
    trader = MicroAccountTrader()
    trader.run_continuous()

if __name__ == "__main__":
    main()