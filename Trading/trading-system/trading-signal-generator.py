#!/usr/bin/env python3
"""
Trading Signal Generator & Paper Trading System
Generates live trading signals and simulates trade execution
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import yfinance as yf
from typing import Dict, List, Optional
import time

class TradingSignalGenerator:
    def __init__(self):
        self.symbol = "XAUUSD"
        self.signals = []
        self.paper_trades = []
        self.balance = 1000.0  # Starting paper trading balance
        self.risk_per_trade = 0.02  # 2% risk per trade
        
    def fetch_live_data(self, symbol: str = "GC=F", period: str = "1d", interval: str = "15m"):
        """Fetch live market data"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            return data
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    def detect_pattern_signals(self, data: pd.DataFrame) -> List[Dict]:
        """Detect trading patterns and generate signals"""
        signals = []
        
        if len(data) < 50:
            return signals
        
        # Calculate indicators
        data['RSI'] = self.calculate_rsi(data['Close'])
        data['MACD'], data['Signal'], data['Histogram'] = self.calculate_macd(data['Close'])
        data['MA20'] = data['Close'].rolling(20).mean()
        data['MA50'] = data['Close'].rolling(50).mean()
        
        current_price = data['Close'].iloc[-1]
        current_rsi = data['RSI'].iloc[-1]
        current_macd = data['MACD'].iloc[-1]
        current_signal = data['Signal'].iloc[-1]
        ma20 = data['MA20'].iloc[-1]
        ma50 = data['MA50'].iloc[-1]
        
        # RSI Oversold Signal
        if current_rsi < 30 and current_macd > current_signal:
            signals.append({
                'type': 'BUY',
                'reason': 'RSI Oversold + MACD Bullish',
                'entry': current_price,
                'stop_loss': current_price * 0.98,  # 2% stop loss
                'take_profit': current_price * 1.04,  # 4% take profit (1:2 RR)
                'confidence': 'HIGH',
                'timestamp': datetime.now(),
                'rsi': current_rsi,
                'setup': 'RSI_OVERSOLD_MACD_BULL'
            })
        
        # RSI Overbought Signal
        if current_rsi > 70 and current_macd < current_signal:
            signals.append({
                'type': 'SELL',
                'reason': 'RSI Overbought + MACD Bearish',
                'entry': current_price,
                'stop_loss': current_price * 1.02,  # 2% stop loss
                'take_profit': current_price * 0.96,  # 4% take profit (1:2 RR)
                'confidence': 'HIGH',
                'timestamp': datetime.now(),
                'rsi': current_rsi,
                'setup': 'RSI_OVERBOUGHT_MACD_BEAR'
            })
        
        # Moving Average Crossover
        if ma20 > ma50 and current_price > ma20:
            signals.append({
                'type': 'BUY',
                'reason': 'MA Bullish Trend + Price Above MA20',
                'entry': current_price,
                'stop_loss': ma20 * 0.995,  # Stop below MA20
                'take_profit': current_price * 1.03,  # 3% target
                'confidence': 'MEDIUM',
                'timestamp': datetime.now(),
                'rsi': current_rsi,
                'setup': 'MA_CROSS_BULL'
            })
        
        return signals
    
    def simulate_trade_execution(self, signal: Dict) -> Dict:
        """Simulate trade execution in paper trading"""
        position_size = self.calculate_position_size(signal)
        
        trade = {
            'id': len(self.paper_trades) + 1,
            'symbol': self.symbol,
            'type': signal['type'],
            'entry_price': signal['entry'],
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit'],
            'position_size': position_size,
            'entry_time': signal['timestamp'],
            'status': 'OPEN',
            'reason': signal['reason'],
            'setup': signal['setup'],
            'confidence': signal['confidence']
        }
        
        self.paper_trades.append(trade)
        return trade
    
    def calculate_position_size(self, signal: Dict) -> float:
        """Calculate position size based on risk management"""
        entry_price = signal['entry']
        stop_loss = signal['stop_loss']
        
        risk_amount = self.balance * self.risk_per_trade
        price_diff = abs(entry_price - stop_loss)
        
        if price_diff > 0:
            position_size = risk_amount / price_diff
        else:
            position_size = 0.01  # Minimum position
        
        return round(position_size, 2)
    
    def generate_live_signals(self) -> List[Dict]:
        """Generate live trading signals"""
        print("🔍 Analyzing live market data...")
        
        # Fetch live data
        data = self.fetch_live_data()
        if data is None or len(data) == 0:
            print("❌ No data available")
            return []
        
        # Generate signals
        signals = self.detect_pattern_signals(data)
        
        if signals:
            print(f"✅ Generated {len(signals)} trading signals")
            for signal in signals:
                print(f"📊 {signal['type']} Signal: {signal['reason']}")
                print(f"   Entry: ${signal['entry']:.2f}")
                print(f"   Stop Loss: ${signal['stop_loss']:.2f}")
                print(f"   Take Profit: ${signal['take_profit']:.2f}")
                print(f"   Confidence: {signal['confidence']}")
                print(f"   RSI: {signal['rsi']:.1f}")
                print()
        else:
            print("⏳ No trading signals generated at this time")
        
        return signals
    
    def create_trade_notification(self, signal: Dict) -> str:
        """Create formatted trade notification"""
        notification = f"""
🚨 TRADING SIGNAL ALERT 🚨
========================

📊 Symbol: {self.symbol}
🎯 Action: {signal['type']}
💡 Setup: {signal['setup']}
🔍 Reason: {signal['reason']}

💰 Entry: ${signal['entry']:.2f}
🛑 Stop Loss: ${signal['stop_loss']:.2f}
🎯 Take Profit: ${signal['take_profit']:.2f}
📈 Risk/Reward: 1:2

📊 Technical Data:
   RSI: {signal['rsi']:.1f}
   Confidence: {signal['confidence']}
   Time: {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

⚠️  PAPER TRADING SIMULATION
This is for analysis only - not live execution
        """
        return notification
    
    def save_signals_log(self, signals: List[Dict]):
        """Save signals to log file"""
        log_file = "trading_signals_log.json"
        
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    existing_signals = json.load(f)
            else:
                existing_signals = []
            
            # Convert datetime objects to strings for JSON serialization
            for signal in signals:
                signal['timestamp'] = signal['timestamp'].isoformat()
            
            existing_signals.extend(signals)
            
            with open(log_file, 'w') as f:
                json.dump(existing_signals, f, indent=2)
            
            print(f"💾 Signals saved to {log_file}")
            
        except Exception as e:
            print(f"❌ Error saving signals: {e}")

class LiveTradingAssistant:
    def __init__(self):
        self.signal_generator = TradingSignalGenerator()
        
    def start_signal_monitoring(self, interval_minutes: int = 15):
        """Start live signal monitoring"""
        print("🚀 Starting Live Signal Monitoring")
        print("==================================")
        print(f"⏰ Checking every {interval_minutes} minutes")
        print(f"📊 Symbol: {self.signal_generator.symbol}")
        print(f"💰 Paper Trading Balance: ${self.signal_generator.balance}")
        print()
        print("⚠️  PAPER TRADING MODE - No real money at risk")
        print("⚠️  Use signals for manual execution on live account")
        print()
        
        try:
            while True:
                print(f"🔍 Market Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 50)
                
                # Generate signals
                signals = self.signal_generator.generate_live_signals()
                
                # Process each signal
                for signal in signals:
                    # Create notification
                    notification = self.signal_generator.create_trade_notification(signal)
                    print(notification)
                    
                    # Simulate trade execution
                    trade = self.signal_generator.simulate_trade_execution(signal)
                    print(f"📝 Paper Trade #{trade['id']} created")
                    
                    # Save to log
                    self.signal_generator.save_signals_log([signal])
                
                print(f"⏳ Next analysis in {interval_minutes} minutes...")
                print("=" * 60)
                print()
                
                # Wait for next iteration
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 Signal monitoring stopped by user")
        except Exception as e:
            print(f"❌ Error in monitoring: {e}")
    
    def manual_signal_check(self):
        """Generate one-time signal check"""
        print("🔍 MANUAL SIGNAL CHECK")
        print("=====================")
        
        signals = self.signal_generator.generate_live_signals()
        
        if signals:
            for signal in signals:
                notification = self.signal_generator.create_trade_notification(signal)
                print(notification)
                
                # Ask user if they want to execute manually
                print("🤔 Would you like to execute this trade manually?")
                print("   - Open MT5 terminal")
                print("   - Place the trade with recommended parameters")
                print("   - Apply proper risk management")
                print()
        
        return signals

if __name__ == "__main__":
    assistant = LiveTradingAssistant()
    
    print("🎯 TRADING SIGNAL GENERATOR")
    print("===========================")
    print("Choose an option:")
    print("1. Manual signal check (one-time)")
    print("2. Start live monitoring (continuous)")
    print("3. View paper trading balance")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        assistant.manual_signal_check()
    elif choice == "2":
        interval = input("Enter monitoring interval in minutes (default 15): ").strip()
        interval = int(interval) if interval else 15
        assistant.start_signal_monitoring(interval)
    elif choice == "3":
        print(f"💰 Current paper trading balance: ${assistant.signal_generator.balance}")
        print(f"📊 Total paper trades: {len(assistant.signal_generator.paper_trades)}")
    else:
        print("Invalid choice")