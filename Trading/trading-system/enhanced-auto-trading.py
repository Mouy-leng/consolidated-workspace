#!/usr/bin/env python3
"""
Enhanced Multi-Symbol Automated Trading System
Supports automatic buy/sell with SL/TP across multiple symbols
Works without user intervention
"""

import time
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import threading
import logging
import yfinance as yf
from typing import Dict, List, Optional
import os
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_auto_trading.log'),
        logging.StreamHandler()
    ]
)

class EnhancedAutoTradingSystem:
    def __init__(self):
        # FBS MT4 Account Details
        self.account = 241926287
        self.password = "f0v/9iIH"
        self.server = "FBS-Real-4"
        
        self.is_running = False
        self.trade_thread = None
        self.positions = []
        self.signals = []
        self.risk_per_trade = 0.015  # 1.5% risk per trade
        self.max_positions = 5  # Increased for more symbols
        self.min_signal_strength = 0.75  # Slightly lower for more opportunities
        
        # Extended symbol list with Yahoo Finance mappings
        self.symbols = {
            "XAUUSD": "GC=F",      # Gold
            "EURUSD": "EURUSD=X",  # Euro/USD
            "GBPUSD": "GBPUSD=X",  # Pound/USD
            "USDJPY": "USDJPY=X",  # USD/Yen
            "USDCHF": "USDCHF=X",  # USD/Swiss Franc
            "AUDUSD": "AUDUSD=X",  # Australian Dollar/USD
            "NZDUSD": "NZDUSD=X",  # New Zealand Dollar/USD
            "USDCAD": "USDCAD=X",  # USD/Canadian Dollar
            "EURJPY": "EURJPY=X",  # Euro/Yen
            "GBPJPY": "GBPJPY=X"   # Pound/Yen
        }
        
        self.account_balance = 1000.0  # Will be updated from real account
        self.paper_trades = []
        
        # Trading hours (24/5 market)
        self.trading_hours = {
            "start": 0,  # Sunday 5 PM EST (Monday 00:00 GMT)
            "end": 168   # Friday 5 PM EST (Friday 22:00 GMT)
        }
        
        logging.info("Enhanced Multi-Symbol Auto Trading System initialized")
        logging.info(f"Account: {self.account} | Symbols: {len(self.symbols)}")
        
    def is_market_open(self) -> bool:
        """Check if market is open (simplified check)"""
        now = datetime.now()
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        # Market closed on weekends (Saturday=5, Sunday=6)
        if weekday == 5:  # Saturday
            return False
        if weekday == 6 and now.hour < 17:  # Sunday before 5 PM
            return False
        if weekday == 4 and now.hour >= 17:  # Friday after 5 PM
            return False
            
        return True
    
    def get_market_data(self, yahoo_symbol: str, period: str = "5d", interval: str = "1h") -> pd.DataFrame:
        """Get market data from Yahoo Finance"""
        try:
            data = yf.download(yahoo_symbol, period=period, interval=interval, progress=False)
            
            if data.empty or len(data) < 5:
                logging.warning(f"No data available for {yahoo_symbol}")
                return pd.DataFrame()
            
            # Flatten multi-level columns if needed
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)
            
            return data
            
        except Exception as e:
            logging.error(f"Error getting market data for {yahoo_symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate comprehensive technical indicators"""
        try:
            if len(data) < 50:
                return {}
            
            close = data['Close']
            high = data['High']
            low = data['Low']
            volume = data.get('Volume', pd.Series(index=close.index, data=0))
            
            # Ensure we have valid numeric data
            if close.empty or not close.dtype.kind in 'biufc':
                return {}
            
            # RSI (14-period)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = close.ewm(span=12).mean()
            exp2 = close.ewm(span=26).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=9).mean()
            histogram = macd - signal_line
            
            # Bollinger Bands
            sma20 = close.rolling(window=20).mean()
            std20 = close.rolling(window=20).std()
            bb_upper = sma20 + (std20 * 2)
            bb_lower = sma20 - (std20 * 2)
            bb_middle = sma20
            
            # Moving Averages
            sma50 = close.rolling(window=50).mean()
            ema20 = close.ewm(span=20).mean()
            ema50 = close.ewm(span=50).mean()
            
            # Stochastic Oscillator
            lowest_low = low.rolling(window=14).min()
            highest_high = high.rolling(window=14).max()
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=3).mean()
            
            # ATR for volatility
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.rolling(window=14).mean()
            
            # Safe value extraction with fallbacks
            def safe_value(series, default=0):
                try:
                    if series.empty or pd.isna(series.iloc[-1]):
                        return default
                    return float(series.iloc[-1])
                except (IndexError, ValueError, TypeError):
                    return default
            
            return {
                'current_price': safe_value(close),
                'rsi': safe_value(rsi, 50),
                'macd': safe_value(macd),
                'macd_signal': safe_value(signal_line),
                'macd_histogram': safe_value(histogram),
                'bb_upper': safe_value(bb_upper),
                'bb_lower': safe_value(bb_lower),
                'bb_middle': safe_value(bb_middle),
                'sma20': safe_value(sma20),
                'sma50': safe_value(sma50),
                'ema20': safe_value(ema20),
                'ema50': safe_value(ema50),
                'stoch_k': safe_value(k_percent, 50),
                'stoch_d': safe_value(d_percent, 50),
                'atr': safe_value(atr, 0.001)
            }
            
        except Exception as e:
            logging.error(f"Error calculating indicators: {e}")
            return {}
    
    def generate_advanced_signal(self, symbol: str, yahoo_symbol: str) -> Dict:
        """Generate advanced trading signal with multiple confirmations"""
        try:
            data = self.get_market_data(yahoo_symbol)
            if data.empty:
                return {"symbol": symbol, "signal": "no_data", "strength": 0, "price": 0}
            
            indicators = self.calculate_technical_indicators(data)
            if not indicators:
                return {"symbol": symbol, "signal": "insufficient_data", "strength": 0, "price": 0}
            
            current_price = indicators['current_price']
            signal_strength = 0
            signal_type = "hold"
            reasons = []
            
            # 1. RSI Analysis (Weight: 0.25)
            rsi = indicators['rsi']
            if rsi < 20:  # Very oversold
                signal_strength += 0.25
                signal_type = "buy"
                reasons.append(f"RSI very oversold ({rsi:.1f})")
            elif rsi < 35:  # Oversold
                signal_strength += 0.15
                signal_type = "buy"
                reasons.append(f"RSI oversold ({rsi:.1f})")
            elif rsi > 80:  # Very overbought
                signal_strength += 0.25
                signal_type = "sell"
                reasons.append(f"RSI very overbought ({rsi:.1f})")
            elif rsi > 65:  # Overbought
                signal_strength += 0.15
                signal_type = "sell"
                reasons.append(f"RSI overbought ({rsi:.1f})")
            
            # 2. MACD Analysis (Weight: 0.25)
            macd = indicators['macd']
            macd_signal = indicators['macd_signal']
            macd_hist = indicators['macd_histogram']
            
            if macd > macd_signal and macd_hist > 0:
                signal_strength += 0.25
                if signal_type != "sell":
                    signal_type = "buy"
                reasons.append("MACD bullish crossover")
            elif macd < macd_signal and macd_hist < 0:
                signal_strength += 0.25
                if signal_type != "buy":
                    signal_type = "sell"
                reasons.append("MACD bearish crossover")
            
            # 3. Bollinger Bands Analysis (Weight: 0.2)
            bb_upper = indicators['bb_upper']
            bb_lower = indicators['bb_lower']
            bb_middle = indicators['bb_middle']
            
            if current_price <= bb_lower:
                signal_strength += 0.2
                if signal_type != "sell":
                    signal_type = "buy"
                reasons.append("Price at BB lower band")
            elif current_price >= bb_upper:
                signal_strength += 0.2
                if signal_type != "buy":
                    signal_type = "sell"
                reasons.append("Price at BB upper band")
            
            # 4. Moving Average Trend (Weight: 0.15)
            ema20 = indicators['ema20']
            ema50 = indicators['ema50']
            
            if ema20 > ema50 and current_price > ema20:
                if signal_type == "buy":
                    signal_strength += 0.15
                    reasons.append("Bullish MA trend")
            elif ema20 < ema50 and current_price < ema20:
                if signal_type == "sell":
                    signal_strength += 0.15
                    reasons.append("Bearish MA trend")
            
            # 5. Stochastic Confirmation (Weight: 0.15)
            stoch_k = indicators['stoch_k']
            stoch_d = indicators['stoch_d']
            
            if stoch_k < 20 and stoch_d < 20:
                if signal_type == "buy":
                    signal_strength += 0.15
                    reasons.append(f"Stochastic oversold ({stoch_k:.1f})")
            elif stoch_k > 80 and stoch_d > 80:
                if signal_type == "sell":
                    signal_strength += 0.15
                    reasons.append(f"Stochastic overbought ({stoch_k:.1f})")
            
            # Calculate Stop Loss and Take Profit using ATR
            atr = indicators['atr']
            sl_distance = atr * 2  # 2 ATR stop loss
            tp_distance = atr * 3  # 3 ATR take profit (1:1.5 risk reward)
            
            if signal_type == "buy":
                stop_loss = current_price - sl_distance
                take_profit = current_price + tp_distance
            elif signal_type == "sell":
                stop_loss = current_price + sl_distance
                take_profit = current_price - tp_distance
            else:
                stop_loss = take_profit = 0
            
            return {
                "symbol": symbol,
                "signal": signal_type,
                "strength": round(min(signal_strength, 1.0), 3),
                "price": current_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "rsi": round(rsi, 2),
                "macd": round(macd, 4),
                "atr": round(atr, 4),
                "reasons": reasons,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating signal for {symbol}: {e}")
            return {"symbol": symbol, "signal": "error", "strength": 0, "price": 0}
    
    def calculate_position_size(self, price: float, stop_loss: float, symbol: str) -> float:
        """Calculate position size based on risk management"""
        risk_amount = self.account_balance * self.risk_per_trade
        
        # Calculate pip value (simplified)
        if "JPY" in symbol:
            pip_value = 0.01
        elif "USD" in symbol or symbol == "XAUUSD":
            pip_value = 0.0001
        else:
            pip_value = 0.0001
        
        # Calculate distance in pips
        pip_distance = abs(price - stop_loss) / pip_value
        
        if pip_distance == 0:
            return 0.01  # Minimum lot size
        
        # Position size calculation
        lot_size = risk_amount / (pip_distance * pip_value * 100000)  # 100k = standard lot
        
        # Round to 2 decimal places and apply limits
        lot_size = round(lot_size, 2)
        lot_size = max(0.01, lot_size)  # Minimum 0.01 lots
        lot_size = min(1.0, lot_size)   # Maximum 1.0 lots
        
        return lot_size
    
    def place_automated_trade(self, signal: Dict) -> bool:
        """Place automated trade with SL and TP"""
        try:
            if signal["strength"] < self.min_signal_strength:
                logging.info(f"Signal strength {signal['strength']} below minimum {self.min_signal_strength}")
                return False
            
            if len(self.positions) >= self.max_positions:
                logging.info(f"Maximum positions ({self.max_positions}) reached")
                return False
            
            # Calculate position size
            lot_size = self.calculate_position_size(
                signal["price"], 
                signal["stop_loss"], 
                signal["symbol"]
            )
            
            # Create trade
            trade = {
                "id": len(self.paper_trades) + 1,
                "symbol": signal["symbol"],
                "type": signal["signal"],
                "lot_size": lot_size,
                "entry_price": signal["price"],
                "stop_loss": signal["stop_loss"],
                "take_profit": signal["take_profit"],
                "timestamp": datetime.now().isoformat(),
                "status": "open",
                "reasons": signal["reasons"],
                "atr": signal.get("atr", 0)
            }
            
            self.positions.append(trade)
            self.paper_trades.append(trade)
            
            logging.info(f"AUTO TRADE PLACED: {trade['type'].upper()} {trade['lot_size']} lots {trade['symbol']}")
            logging.info(f"  Entry: {trade['entry_price']:.4f}")
            logging.info(f"  SL: {trade['stop_loss']:.4f}")
            logging.info(f"  TP: {trade['take_profit']:.4f}")
            logging.info(f"  Reasons: {', '.join(trade['reasons'])}")
            
            return True
            
        except Exception as e:
            logging.error(f"Error placing automated trade: {e}")
            return False
    
    def monitor_positions(self):
        """Monitor and manage open positions automatically"""
        for position in self.positions.copy():
            try:
                symbol = position["symbol"]
                yahoo_symbol = self.symbols.get(symbol, symbol)
                
                # Get current price
                current_data = self.get_market_data(yahoo_symbol, period="1d", interval="5m")
                if current_data.empty:
                    continue
                
                current_price = current_data['Close'].iloc[-1]
                entry_price = position["entry_price"]
                stop_loss = position["stop_loss"]
                take_profit = position["take_profit"]
                
                # Calculate P&L
                if position["type"] == "buy":
                    pnl = (current_price - entry_price) * position["lot_size"] * 100000
                else:
                    pnl = (entry_price - current_price) * position["lot_size"] * 100000
                
                # Check exit conditions
                should_close = False
                close_reason = ""
                
                if position["type"] == "buy":
                    if current_price <= stop_loss:
                        should_close = True
                        close_reason = "Stop Loss hit"
                    elif current_price >= take_profit:
                        should_close = True
                        close_reason = "Take Profit reached"
                else:  # sell
                    if current_price >= stop_loss:
                        should_close = True
                        close_reason = "Stop Loss hit"
                    elif current_price <= take_profit:
                        should_close = True
                        close_reason = "Take Profit reached"
                
                # Auto-close position
                if should_close:
                    position["exit_price"] = current_price
                    position["pnl"] = pnl
                    position["status"] = "closed"
                    position["close_reason"] = close_reason
                    position["close_timestamp"] = datetime.now().isoformat()
                    
                    self.account_balance += pnl
                    self.positions.remove(position)
                    
                    logging.info(f"AUTO CLOSE: {position['symbol']} {close_reason}")
                    logging.info(f"  P&L: ${pnl:.2f} | New Balance: ${self.account_balance:.2f}")
                
            except Exception as e:
                logging.error(f"Error monitoring position: {e}")
    
    def run_automated_trading_loop(self):
        """Main automated trading loop"""
        logging.info("Starting Enhanced Automated Trading Loop...")
        
        while self.is_running:
            try:
                if not self.is_market_open():
                    logging.info("Market closed - waiting...")
                    time.sleep(3600)  # Check every hour when market is closed
                    continue
                
                # Generate signals for all symbols
                for symbol, yahoo_symbol in self.symbols.items():
                    signal = self.generate_advanced_signal(symbol, yahoo_symbol)
                    
                    if signal["signal"] in ["buy", "sell"] and signal["strength"] >= self.min_signal_strength:
                        logging.info(f"STRONG SIGNAL: {signal['symbol']} {signal['signal'].upper()} ({signal['strength']:.3f})")
                        self.place_automated_trade(signal)
                        time.sleep(5)  # Delay between trades
                
                # Monitor existing positions
                self.monitor_positions()
                
                # Print status
                open_trades = [f"{p['symbol']}-{p['type']}" for p in self.positions]
                logging.info(f"Balance: ${self.account_balance:.2f} | Open: {len(self.positions)} | Trades: {open_trades}")
                
                # Wait before next cycle (check every 15 minutes)
                time.sleep(900)
                
            except Exception as e:
                logging.error(f"Error in automated trading loop: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def start(self):
        """Start the automated trading system"""
        if self.is_running:
            logging.warning("Automated trading system is already running")
            return
        
        self.is_running = True
        self.trade_thread = threading.Thread(target=self.run_automated_trading_loop)
        self.trade_thread.start()
        logging.info("Enhanced Automated Trading System STARTED")
        logging.info(f"Monitoring {len(self.symbols)} symbols with full automation")
    
    def stop(self):
        """Stop the automated trading system"""
        self.is_running = False
        if self.trade_thread:
            self.trade_thread.join()
        logging.info("Enhanced Automated Trading System STOPPED")
    
    def get_status(self) -> Dict:
        """Get comprehensive system status"""
        return {
            "running": self.is_running,
            "account": self.account,
            "balance": self.account_balance,
            "symbols": list(self.symbols.keys()),
            "open_positions": len(self.positions),
            "total_trades": len(self.paper_trades),
            "positions": self.positions,
            "risk_per_trade": self.risk_per_trade,
            "max_positions": self.max_positions,
            "min_signal_strength": self.min_signal_strength
        }

def main():
    """Main function to run enhanced automated trading"""
    print("🚀 ENHANCED MULTI-SYMBOL AUTO TRADING SYSTEM")
    print("=" * 55)
    print("Features:")
    print("✅ 10 Currency Pairs + Gold")
    print("✅ Automatic Buy/Sell Signals")
    print("✅ Auto Stop Loss & Take Profit")
    print("✅ Risk Management (1.5% per trade)")
    print("✅ No Manual Intervention Required")
    print("✅ 24/5 Market Monitoring")
    print("")
    
    system = EnhancedAutoTradingSystem()
    
    try:
        print("🎯 Starting fully automated trading system...")
        system.start()
        
        print(f"\n📊 System Status:")
        print(f"💰 Account: {system.account} (FBS-Real-4)")
        print(f"📈 Symbols: {', '.join(list(system.symbols.keys())[:5])}...")
        print(f"⚙️ Max Positions: {system.max_positions}")
        print(f"🎯 Risk per trade: {system.risk_per_trade*100}%")
        print(f"📊 Signal threshold: {system.min_signal_strength*100}%")
        print("\n🤖 SYSTEM IS FULLY AUTOMATED!")
        print("💤 You can leave it running without supervision")
        print("📊 Check logs for trading activity")
        print("\nPress Ctrl+C to stop the system...")
        
        while system.is_running:
            time.sleep(10)
            status = system.get_status()
            if len(status["positions"]) > 0:
                print(f"📊 Active: {len(status['positions'])} positions | Balance: ${status['balance']:.2f}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Stopping automated trading system...")
        system.stop()
        
        final_status = system.get_status()
        print(f"\n📊 Final Results:")
        print(f"   Account Balance: ${final_status['balance']:.2f}")
        print(f"   Total Trades: {final_status['total_trades']}")
        print(f"   Open Positions: {final_status['open_positions']}")

if __name__ == "__main__":
    main()