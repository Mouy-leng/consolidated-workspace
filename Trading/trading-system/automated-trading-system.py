#!/usr/bin/env python3
"""
Automated Trading System - Full Execution
Comprehensive automated trading bot with signal generation and trade execution
"""

import time
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import logging
import yfinance as yf
from typing import Dict, List, Optional, Tuple
import MetaTrader5 as mt5
import os
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automated_trading.log'),
        logging.StreamHandler()
    ]
)

class AutomatedTradingSystem:
    def __init__(self):
        self.account = 40933210
        self.password = "8IA.KFIB"
        self.server = "FBS-Real"
        self.is_running = False
        self.trade_thread = None
        self.positions = []
        self.signals = []
        self.risk_per_trade = 0.02  # 2%
        self.max_positions = 3
        self.min_signal_strength = 0.7
        
        # Trading parameters
        self.symbols = ["XAUUSD", "EURUSD", "GBPUSD"]
        self.timeframes = [mt5.TIMEFRAME_M15, mt5.TIMEFRAME_H1]
        
        # Initialize MT5 connection
        self.mt5_connected = False
        
    def connect_mt5(self) -> bool:
        """Connect to MetaTrader 5"""
        try:
            if not mt5.initialize():
                logging.error("MT5 initialize() failed")
                return False
            
            # Connect to account
            if not mt5.login(self.account, password=self.password, server=self.server):
                logging.error(f"Failed to connect to account {self.account}")
                return False
            
            self.mt5_connected = True
            logging.info(f"Connected to MT5 account {self.account}")
            return True
            
        except Exception as e:
            logging.error(f"MT5 connection error: {e}")
            return False
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        if not self.mt5_connected:
            return {}
        
        account_info = mt5.account_info()
        if account_info is None:
            return {}
        
        return {
            'balance': account_info.balance,
            'equity': account_info.equity,
            'margin': account_info.margin,
            'free_margin': account_info.margin_free,
            'margin_level': account_info.margin_level,
            'currency': account_info.currency
        }
    
    def calculate_position_size(self, symbol: str, stop_loss_pips: float, balance: float) -> float:
        """Calculate position size based on risk management"""
        try:
            # Get symbol info
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                return 0.01
            
            # Calculate risk amount
            risk_amount = balance * self.risk_per_trade
            
            # Calculate position size
            pip_value = symbol_info.trade_tick_value
            position_size = risk_amount / (stop_loss_pips * pip_value)
            
            # Round to acceptable lot size
            min_lot = symbol_info.volume_min
            max_lot = symbol_info.volume_max
            lot_step = symbol_info.volume_step
            
            position_size = max(min_lot, min(max_lot, round(position_size / lot_step) * lot_step))
            
            return position_size
            
        except Exception as e:
            logging.error(f"Position size calculation error: {e}")
            return 0.01
    
    def generate_signals(self, symbol: str, timeframe: int) -> Dict:
        """Generate trading signals using technical analysis"""
        try:
            # Get market data
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 200)
            if rates is None or len(rates) < 50:
                return {'signal': 'NONE', 'strength': 0}
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            # Calculate technical indicators
            signals = self.analyze_technical_indicators(df)
            smart_money = self.analyze_smart_money_concepts(df)
            pattern = self.analyze_patterns(df)
            
            # Combine signals
            final_signal = self.combine_signals(signals, smart_money, pattern)
            
            return final_signal
            
        except Exception as e:
            logging.error(f"Signal generation error for {symbol}: {e}")
            return {'signal': 'NONE', 'strength': 0}
    
    def analyze_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Analyze technical indicators"""
        # RSI
        df['rsi'] = self.calculate_rsi(df['close'], 14)
        
        # MACD
        macd_data = self.calculate_macd(df['close'])
        df['macd'] = macd_data['macd']
        df['signal'] = macd_data['signal']
        df['histogram'] = macd_data['histogram']
        
        # Moving Averages
        df['ma20'] = df['close'].rolling(20).mean()
        df['ma50'] = df['close'].rolling(50).mean()
        
        # Bollinger Bands
        bb_data = self.calculate_bollinger_bands(df['close'])
        df['bb_upper'] = bb_data['upper']
        df['bb_lower'] = bb_data['lower']
        
        # Generate signals
        current = df.iloc[-1]
        prev = df.iloc[-2]
        
        signals = []
        
        # RSI signals
        if current['rsi'] < 30:
            signals.append({'type': 'BUY', 'strength': 0.7, 'reason': 'RSI Oversold'})
        elif current['rsi'] > 70:
            signals.append({'type': 'SELL', 'strength': 0.7, 'reason': 'RSI Overbought'})
        
        # MACD signals
        if current['macd'] > current['signal'] and prev['macd'] <= prev['signal']:
            signals.append({'type': 'BUY', 'strength': 0.8, 'reason': 'MACD Bullish Cross'})
        elif current['macd'] < current['signal'] and prev['macd'] >= prev['signal']:
            signals.append({'type': 'SELL', 'strength': 0.8, 'reason': 'MACD Bearish Cross'})
        
        # MA signals
        if current['ma20'] > current['ma50'] and current['close'] > current['ma20']:
            signals.append({'type': 'BUY', 'strength': 0.6, 'reason': 'MA Bullish Alignment'})
        elif current['ma20'] < current['ma50'] and current['close'] < current['ma20']:
            signals.append({'type': 'SELL', 'strength': 0.6, 'reason': 'MA Bearish Alignment'})
        
        return {'signals': signals}
    
    def analyze_smart_money_concepts(self, df: pd.DataFrame) -> Dict:
        """Analyze smart money concepts"""
        signals = []
        
        # Order blocks detection
        order_blocks = self.detect_order_blocks(df)
        
        # Market structure analysis
        structure = self.analyze_market_structure(df)
        
        # Liquidity zones
        liquidity = self.detect_liquidity_zones(df)
        
        current_price = df.iloc[-1]['close']
        
        # Check if price is at significant levels
        for ob in order_blocks:
            if ob['zone_low'] <= current_price <= ob['zone_high']:
                if ob['type'] == 'bullish':
                    signals.append({'type': 'BUY', 'strength': 0.9, 'reason': 'Bullish Order Block'})
                else:
                    signals.append({'type': 'SELL', 'strength': 0.9, 'reason': 'Bearish Order Block'})
        
        return {'signals': signals}
    
    def analyze_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze chart patterns"""
        signals = []
        
        # Double top/bottom detection
        patterns = self.detect_double_patterns(df)
        
        # Triangle patterns
        triangles = self.detect_triangles(df)
        
        # Head and shoulders
        hs_patterns = self.detect_head_shoulders(df)
        
        for pattern in patterns + triangles + hs_patterns:
            if pattern['type'] in ['double_bottom', 'ascending_triangle', 'head_shoulders_bottom']:
                signals.append({'type': 'BUY', 'strength': pattern['strength'], 'reason': f"Pattern: {pattern['type']}"})
            elif pattern['type'] in ['double_top', 'descending_triangle', 'head_shoulders_top']:
                signals.append({'type': 'SELL', 'strength': pattern['strength'], 'reason': f"Pattern: {pattern['type']}"})
        
        return {'signals': signals}
    
    def combine_signals(self, technical: Dict, smart_money: Dict, patterns: Dict) -> Dict:
        """Combine all signals into final decision"""
        all_signals = []
        all_signals.extend(technical.get('signals', []))
        all_signals.extend(smart_money.get('signals', []))
        all_signals.extend(patterns.get('signals', []))
        
        if not all_signals:
            return {'signal': 'NONE', 'strength': 0, 'reasons': []}
        
        # Calculate weighted signal
        buy_strength = sum([s['strength'] for s in all_signals if s['type'] == 'BUY'])
        sell_strength = sum([s['strength'] for s in all_signals if s['type'] == 'SELL'])
        
        buy_count = len([s for s in all_signals if s['type'] == 'BUY'])
        sell_count = len([s for s in all_signals if s['type'] == 'SELL'])
        
        # Determine final signal
        if buy_strength > sell_strength and buy_strength >= self.min_signal_strength:
            signal_type = 'BUY'
            strength = min(1.0, buy_strength / buy_count if buy_count > 0 else 0)
        elif sell_strength > buy_strength and sell_strength >= self.min_signal_strength:
            signal_type = 'SELL'
            strength = min(1.0, sell_strength / sell_count if sell_count > 0 else 0)
        else:
            signal_type = 'NONE'
            strength = 0
        
        reasons = [s['reason'] for s in all_signals if s['type'] == signal_type]
        
        return {
            'signal': signal_type,
            'strength': strength,
            'reasons': reasons,
            'buy_signals': buy_count,
            'sell_signals': sell_count
        }
    
    def place_trade(self, symbol: str, signal: Dict) -> bool:
        """Place a trade based on signal"""
        try:
            if signal['signal'] == 'NONE' or signal['strength'] < self.min_signal_strength:
                return False
            
            # Check maximum positions
            if len(self.get_open_positions()) >= self.max_positions:
                logging.info("Maximum positions reached")
                return False
            
            # Get account info
            account_info = self.get_account_info()
            balance = account_info.get('balance', 10000)
            
            # Get current price
            if signal['signal'] == 'BUY':
                price = mt5.symbol_info_tick(symbol).ask
                order_type = mt5.ORDER_TYPE_BUY
            else:
                price = mt5.symbol_info_tick(symbol).bid
                order_type = mt5.ORDER_TYPE_SELL
            
            # Calculate stop loss and take profit
            sl, tp = self.calculate_sl_tp(symbol, signal['signal'], price)
            
            # Calculate position size
            sl_pips = abs(price - sl) / mt5.symbol_info(symbol).point
            lot_size = self.calculate_position_size(symbol, sl_pips, balance)
            
            # Create trade request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 10,
                "magic": 123456,
                "comment": f"Auto trade - {signal['strength']:.2f}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send trade
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logging.error(f"Trade failed: {result.comment}")
                return False
            
            # Log successful trade
            trade_info = {
                'ticket': result.order,
                'symbol': symbol,
                'action': signal['signal'],
                'volume': lot_size,
                'price': price,
                'sl': sl,
                'tp': tp,
                'strength': signal['strength'],
                'reasons': signal['reasons'],
                'time': datetime.now()
            }
            
            self.positions.append(trade_info)
            
            logging.info(f"Trade placed: {signal['signal']} {symbol} @ {price}, SL: {sl}, TP: {tp}")
            return True
            
        except Exception as e:
            logging.error(f"Trade placement error: {e}")
            return False
    
    def calculate_sl_tp(self, symbol: str, action: str, price: float) -> Tuple[float, float]:
        """Calculate stop loss and take profit levels"""
        symbol_info = mt5.symbol_info(symbol)
        point = symbol_info.point
        
        # Default values (adjust based on symbol)
        if symbol == "XAUUSD":
            sl_distance = 150 * point  # 15 dollars
            tp_distance = 300 * point  # 30 dollars (1:2 RR)
        else:  # Forex pairs
            sl_distance = 200 * point  # 20 pips
            tp_distance = 400 * point  # 40 pips (1:2 RR)
        
        if action == 'BUY':
            sl = price - sl_distance
            tp = price + tp_distance
        else:
            sl = price + sl_distance
            tp = price - tp_distance
        
        return sl, tp
    
    def get_open_positions(self) -> List:
        """Get current open positions"""
        if not self.mt5_connected:
            return []
        
        positions = mt5.positions_get()
        return list(positions) if positions else []
    
    def manage_existing_trades(self):
        """Manage existing open trades"""
        positions = self.get_open_positions()
        
        for position in positions:
            # Check if we should trail stop or close early
            self.check_trade_management(position)
    
    def check_trade_management(self, position):
        """Check individual trade for management actions"""
        symbol = position.symbol
        current_price = mt5.symbol_info_tick(symbol).bid if position.type == 0 else mt5.symbol_info_tick(symbol).ask
        
        # Calculate current profit in pips
        if position.type == 0:  # Buy position
            profit_pips = (current_price - position.price_open) / mt5.symbol_info(symbol).point
        else:  # Sell position
            profit_pips = (position.price_open - current_price) / mt5.symbol_info(symbol).point
        
        # Trail stop loss if in profit
        if profit_pips > 100:  # If 10+ pips profit
            self.trail_stop_loss(position, current_price)
    
    def trail_stop_loss(self, position, current_price: float):
        """Trail stop loss for profitable positions"""
        symbol_info = mt5.symbol_info(position.symbol)
        point = symbol_info.point
        
        # Calculate new stop loss
        if position.type == 0:  # Buy position
            new_sl = current_price - (100 * point)  # Trail by 10 pips
            if new_sl > position.sl:
                self.modify_position(position.ticket, new_sl, position.tp)
        else:  # Sell position
            new_sl = current_price + (100 * point)  # Trail by 10 pips
            if new_sl < position.sl:
                self.modify_position(position.ticket, new_sl, position.tp)
    
    def modify_position(self, ticket: int, sl: float, tp: float):
        """Modify existing position"""
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "sl": sl,
            "tp": tp,
        }
        
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logging.info(f"Position {ticket} modified: SL={sl}, TP={tp}")
    
    def start_automated_trading(self):
        """Start the automated trading loop"""
        if not self.connect_mt5():
            logging.error("Failed to connect to MT5")
            return
        
        self.is_running = True
        logging.info("Starting automated trading system...")
        
        def trading_loop():
            while self.is_running:
                try:
                    # Manage existing trades
                    self.manage_existing_trades()
                    
                    # Generate new signals
                    for symbol in self.symbols:
                        for timeframe in self.timeframes:
                            signal = self.generate_signals(symbol, timeframe)
                            
                            if signal['signal'] != 'NONE':
                                logging.info(f"Signal: {symbol} {timeframe} - {signal['signal']} ({signal['strength']:.2f})")
                                
                                # Place trade if signal is strong enough
                                if signal['strength'] >= self.min_signal_strength:
                                    self.place_trade(symbol, signal)
                    
                    # Wait before next iteration
                    time.sleep(300)  # 5 minutes
                    
                except Exception as e:
                    logging.error(f"Trading loop error: {e}")
                    time.sleep(60)  # Wait 1 minute before retry
        
        self.trade_thread = threading.Thread(target=trading_loop)
        self.trade_thread.daemon = True
        self.trade_thread.start()
    
    def stop_automated_trading(self):
        """Stop the automated trading system"""
        self.is_running = False
        logging.info("Stopping automated trading system...")
        if self.trade_thread:
            self.trade_thread.join()
        mt5.shutdown()
    
    # Technical indicator calculation methods
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        
        return {
            'macd': macd,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Dict:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        return {
            'upper': sma + (std * std_dev),
            'middle': sma,
            'lower': sma - (std * std_dev)
        }
    
    def detect_order_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """Detect order blocks"""
        # Simplified order block detection
        order_blocks = []
        
        for i in range(20, len(df) - 5):
            # Look for strong rejection candles
            current = df.iloc[i]
            
            # Bullish order block
            if current['low'] < df.iloc[i-1]['low'] and current['close'] > current['open']:
                order_blocks.append({
                    'type': 'bullish',
                    'zone_low': current['low'],
                    'zone_high': current['open'],
                    'strength': 0.8,
                    'index': i
                })
            
            # Bearish order block
            if current['high'] > df.iloc[i-1]['high'] and current['close'] < current['open']:
                order_blocks.append({
                    'type': 'bearish',
                    'zone_low': current['close'],
                    'zone_high': current['high'],
                    'strength': 0.8,
                    'index': i
                })
        
        return order_blocks[-5:]  # Return last 5 order blocks
    
    def analyze_market_structure(self, df: pd.DataFrame) -> Dict:
        """Analyze market structure"""
        # Simplified market structure analysis
        highs = []
        lows = []
        
        for i in range(5, len(df) - 5):
            if df.iloc[i]['high'] == df.iloc[i-5:i+5]['high'].max():
                highs.append({'price': df.iloc[i]['high'], 'index': i})
            
            if df.iloc[i]['low'] == df.iloc[i-5:i+5]['low'].min():
                lows.append({'price': df.iloc[i]['low'], 'index': i})
        
        # Determine trend
        if len(highs) >= 2 and len(lows) >= 2:
            recent_highs = highs[-2:]
            recent_lows = lows[-2:]
            
            if recent_highs[-1]['price'] > recent_highs[-2]['price'] and recent_lows[-1]['price'] > recent_lows[-2]['price']:
                trend = 'uptrend'
            elif recent_highs[-1]['price'] < recent_highs[-2]['price'] and recent_lows[-1]['price'] < recent_lows[-2]['price']:
                trend = 'downtrend'
            else:
                trend = 'sideways'
        else:
            trend = 'unclear'
        
        return {
            'trend': trend,
            'swing_highs': highs[-3:],
            'swing_lows': lows[-3:]
        }
    
    def detect_liquidity_zones(self, df: pd.DataFrame) -> List[Dict]:
        """Detect liquidity zones"""
        zones = []
        
        # Find areas where price has touched multiple times
        for i in range(10, len(df) - 10):
            price_level = df.iloc[i]['high']
            touches = 0
            
            # Count touches within 0.1% range
            for j in range(max(0, i-50), min(len(df), i+50)):
                if abs(df.iloc[j]['high'] - price_level) / price_level < 0.001:
                    touches += 1
            
            if touches >= 3:
                zones.append({
                    'level': price_level,
                    'touches': touches,
                    'zone_type': 'resistance',
                    'strength': min(1.0, touches / 5)
                })
        
        return zones[-5:]  # Return last 5 zones
    
    def detect_double_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Detect double top/bottom patterns"""
        patterns = []
        highs = []
        lows = []
        
        # Find swing highs and lows
        for i in range(10, len(df) - 10):
            if df.iloc[i]['high'] == df.iloc[i-10:i+10]['high'].max():
                highs.append({'price': df.iloc[i]['high'], 'index': i})
            
            if df.iloc[i]['low'] == df.iloc[i-10:i+10]['low'].min():
                lows.append({'price': df.iloc[i]['low'], 'index': i})
        
        # Check for double tops
        for i in range(1, len(highs)):
            current_high = highs[i]
            prev_high = highs[i-1]
            
            if abs(current_high['price'] - prev_high['price']) / prev_high['price'] < 0.002:  # Within 0.2%
                patterns.append({
                    'type': 'double_top',
                    'strength': 0.7,
                    'start_index': prev_high['index'],
                    'end_index': current_high['index']
                })
        
        # Check for double bottoms
        for i in range(1, len(lows)):
            current_low = lows[i]
            prev_low = lows[i-1]
            
            if abs(current_low['price'] - prev_low['price']) / prev_low['price'] < 0.002:  # Within 0.2%
                patterns.append({
                    'type': 'double_bottom',
                    'strength': 0.7,
                    'start_index': prev_low['index'],
                    'end_index': current_low['index']
                })
        
        return patterns[-3:]  # Return last 3 patterns
    
    def detect_triangles(self, df: pd.DataFrame) -> List[Dict]:
        """Detect triangle patterns"""
        # Simplified triangle detection
        return []  # Placeholder
    
    def detect_head_shoulders(self, df: pd.DataFrame) -> List[Dict]:
        """Detect head and shoulders patterns"""
        # Simplified H&S detection
        return []  # Placeholder

def main():
    """Main function to run automated trading"""
    print("🤖 AUTOMATED TRADING SYSTEM")
    print("===========================")
    print()
    
    # Create trading system
    trader = AutomatedTradingSystem()
    
    try:
        # Start automated trading
        trader.start_automated_trading()
        
        print("✅ Automated trading started!")
        print("📊 Monitoring signals and executing trades...")
        print("⚠️  Press Ctrl+C to stop")
        print()
        
        # Keep running until interrupted
        while True:
            # Display status
            account_info = trader.get_account_info()
            positions = trader.get_open_positions()
            
            print(f"\r💰 Balance: ${account_info.get('balance', 0):,.2f} | "
                  f"Equity: ${account_info.get('equity', 0):,.2f} | "
                  f"Positions: {len(positions)}", end="")
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping automated trading...")
        trader.stop_automated_trading()
        print("✅ Automated trading stopped safely")

if __name__ == "__main__":
    main()