#!/usr/bin/env python3
"""
MT4 Automated Trading System - FBS Live Account
Comprehensive automated trading bot using MT4 instead of MT5
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
import requests

# Try to import MT4 libraries
try:
    import MetaTrader4 as mt4
    MT4_AVAILABLE = True
except ImportError:
    print("MetaTrader4 library not available, using simulation mode")
    MT4_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mt4_automated_trading.log'),
        logging.StreamHandler()
    ]
)

class MT4AutomatedTradingSystem:
    def __init__(self):
        # FBS MT4 Account Details
        self.account = 241926287
        self.password = "f0v/9iIH"
        self.server = "FBS-Real-4"
        self.server_ip = "95.179.194.198:443"
        self.company = "FBS Markets Inc."
        
        self.is_running = False
        self.trade_thread = None
        self.positions = []
        self.signals = []
        self.risk_per_trade = 0.01  # 1% for conservative start
        self.max_positions = 2
        self.min_signal_strength = 0.8
        
        # Trading parameters
        self.symbols = ["XAUUSD", "EURUSD", "GBPUSD"]
        self.paper_trades = []
        self.account_balance = 1000.0  # Will be updated from MT4
        
        # MT4 connection status
        self.mt4_connected = False
        
        logging.info("MT4 Automated Trading System initialized")
        logging.info(f"Target Account: {self.account} on {self.server}")
        
    def connect_mt4(self) -> bool:
        """Connect to MetaTrader 4"""
        try:
            if not MT4_AVAILABLE:
                logging.warning("MT4 library not available, using simulation mode")
                return self.simulate_mt4_connection()
            
            # Initialize MT4 connection
            if not mt4.initialize():
                logging.error("MT4 initialize() failed")
                return False
            
            # Connect to account
            if not mt4.login(self.account, password=self.password, server=self.server):
                logging.error(f"Failed to connect to MT4 account {self.account}")
                error = mt4.last_error()
                logging.error(f"MT4 Error: {error}")
                return False
            
            self.mt4_connected = True
            logging.info(f"Successfully connected to MT4 account {self.account}")
            
            # Get account info
            account_info = mt4.account_info()
            if account_info:
                self.account_balance = account_info.balance
                logging.info(f"Account Balance: ${self.account_balance:.2f}")
                logging.info(f"Account Equity: ${account_info.equity:.2f}")
                logging.info(f"Account Server: {account_info.server}")
            
            return True
            
        except Exception as e:
            logging.error(f"MT4 connection error: {e}")
            return False
    
    def simulate_mt4_connection(self) -> bool:
        """Simulate MT4 connection for testing"""
        logging.info("Using MT4 simulation mode")
        self.mt4_connected = True
        self.account_balance = 1000.0
        logging.info(f"Simulated Account Balance: ${self.account_balance:.2f}")
        return True
    
    def get_market_data(self, symbol: str, timeframe: str = "H1", count: int = 100) -> pd.DataFrame:
        """Get market data - using Yahoo Finance as fallback"""
        try:
            if MT4_AVAILABLE and self.mt4_connected:
                # Try to get data from MT4
                try:
                    rates = mt4.copy_rates_from_pos(symbol, mt4.TIMEFRAME_H1, 0, count)
                    if rates is not None and len(rates) > 0:
                        df = pd.DataFrame(rates)
                        df['time'] = pd.to_datetime(df['time'], unit='s')
                        return df[['time', 'open', 'high', 'low', 'close', 'tick_volume']].rename(columns={
                            'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'
                        })
                except Exception as e:
                    logging.warning(f"Failed to get MT4 data for {symbol}: {e}")
            
            # Fallback to Yahoo Finance
            yahoo_symbol = self.convert_symbol_to_yahoo(symbol)
            data = yf.download(yahoo_symbol, period="5d", interval="1h", verbose=False)
            
            if data.empty:
                logging.warning(f"No data available for {symbol}")
                return pd.DataFrame()
            
            return data
            
        except Exception as e:
            logging.error(f"Error getting market data for {symbol}: {e}")
            return pd.DataFrame()
    
    def convert_symbol_to_yahoo(self, symbol: str) -> str:
        """Convert MT4 symbol to Yahoo Finance symbol"""
        conversions = {
            "XAUUSD": "GC=F",  # Gold futures
            "EURUSD": "EURUSD=X",
            "GBPUSD": "GBPUSD=X",
            "USDJPY": "USDJPY=X",
            "USDCHF": "USDCHF=X",
            "AUDUSD": "AUDUSD=X",
            "NZDUSD": "NZDUSD=X"
        }
        return conversions.get(symbol, symbol)
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate technical indicators"""
        if len(data) < 50:
            return {}
        
        close = data['Close']
        high = data['High']
        low = data['Low']
        
        # RSI
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
        
        # Bollinger Bands
        sma20 = close.rolling(window=20).mean()
        std20 = close.rolling(window=20).std()
        bb_upper = sma20 + (std20 * 2)
        bb_lower = sma20 - (std20 * 2)
        
        # Moving Averages
        sma50 = close.rolling(window=50).mean()
        ema20 = close.ewm(span=20).mean()
        
        return {
            'rsi': rsi.iloc[-1] if not rsi.empty else 50,
            'macd': macd.iloc[-1] if not macd.empty else 0,
            'macd_signal': signal_line.iloc[-1] if not signal_line.empty else 0,
            'bb_upper': bb_upper.iloc[-1] if not bb_upper.empty else 0,
            'bb_lower': bb_lower.iloc[-1] if not bb_lower.empty else 0,
            'sma20': sma20.iloc[-1] if not sma20.empty else 0,
            'sma50': sma50.iloc[-1] if not sma50.empty else 0,
            'ema20': ema20.iloc[-1] if not ema20.empty else 0,
            'current_price': close.iloc[-1] if not close.empty else 0
        }
    
    def generate_signal(self, symbol: str) -> Dict:
        """Generate trading signal for a symbol"""
        try:
            data = self.get_market_data(symbol)
            if data.empty:
                return {"symbol": symbol, "signal": "no_data", "strength": 0, "price": 0}
            
            indicators = self.calculate_technical_indicators(data)
            if not indicators:
                return {"symbol": symbol, "signal": "insufficient_data", "strength": 0, "price": 0}
            
            current_price = indicators['current_price']
            rsi = indicators['rsi']
            macd = indicators['macd']
            macd_signal = indicators['macd_signal']
            
            signal_strength = 0
            signal_type = "hold"
            reasons = []
            
            # RSI signals (stronger weight)
            if rsi < 25:
                signal_strength += 0.4
                signal_type = "buy"
                reasons.append(f"RSI oversold ({rsi:.1f})")
            elif rsi > 75:
                signal_strength += 0.4
                signal_type = "sell"
                reasons.append(f"RSI overbought ({rsi:.1f})")
            elif rsi < 35:
                signal_strength += 0.2
                signal_type = "buy"
                reasons.append(f"RSI low ({rsi:.1f})")
            elif rsi > 65:
                signal_strength += 0.2
                signal_type = "sell"
                reasons.append(f"RSI high ({rsi:.1f})")
            
            # MACD signals
            if macd > macd_signal and macd > 0:
                signal_strength += 0.3
                if signal_type != "sell":
                    signal_type = "buy"
                reasons.append("MACD bullish crossover")
            elif macd < macd_signal and macd < 0:
                signal_strength += 0.3
                if signal_type != "buy":
                    signal_type = "sell"
                reasons.append("MACD bearish crossover")
            
            # Bollinger Bands
            if indicators['bb_lower'] > 0 and current_price <= indicators['bb_lower']:
                signal_strength += 0.2
                if signal_type != "sell":
                    signal_type = "buy"
                reasons.append("Price at BB lower band")
            elif indicators['bb_upper'] > 0 and current_price >= indicators['bb_upper']:
                signal_strength += 0.2
                if signal_type != "buy":
                    signal_type = "sell"
                reasons.append("Price at BB upper band")
            
            # Moving average confirmation
            if indicators['ema20'] > indicators['sma50']:
                if signal_type == "buy":
                    signal_strength += 0.1
                    reasons.append("EMA20 > SMA50 (uptrend)")
            elif indicators['ema20'] < indicators['sma50']:
                if signal_type == "sell":
                    signal_strength += 0.1
                    reasons.append("EMA20 < SMA50 (downtrend)")
            
            return {
                "symbol": symbol,
                "signal": signal_type,
                "strength": round(min(signal_strength, 1.0), 2),
                "price": current_price,
                "rsi": round(rsi, 2),
                "macd": round(macd, 4),
                "reasons": reasons,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating signal for {symbol}: {e}")
            return {"symbol": symbol, "signal": "error", "strength": 0, "price": 0}
    
    def place_trade(self, signal: Dict) -> bool:
        """Place a trade based on signal"""
        try:
            if signal["strength"] < self.min_signal_strength:
                logging.info(f"Signal strength {signal['strength']} below minimum {self.min_signal_strength}")
                return False
            
            if len(self.positions) >= self.max_positions:
                logging.info(f"Maximum positions ({self.max_positions}) reached")
                return False
            
            # Calculate position size
            risk_amount = self.account_balance * self.risk_per_trade
            
            if MT4_AVAILABLE and self.mt4_connected:
                # Real MT4 trading
                return self.place_mt4_trade(signal, risk_amount)
            else:
                # Paper trading
                return self.place_paper_trade(signal, risk_amount)
            
        except Exception as e:
            logging.error(f"Error placing trade: {e}")
            return False
    
    def place_mt4_trade(self, signal: Dict, risk_amount: float) -> bool:
        """Place real trade in MT4"""
        try:
            symbol = signal["symbol"]
            trade_type = mt4.ORDER_TYPE_BUY if signal["signal"] == "buy" else mt4.ORDER_TYPE_SELL
            
            # Get symbol info
            symbol_info = mt4.symbol_info(symbol)
            if not symbol_info:
                logging.error(f"Symbol {symbol} not found")
                return False
            
            # Calculate lot size based on risk
            point = symbol_info.point
            tick_value = symbol_info.tick_value
            lot_size = round(risk_amount / (100 * tick_value), 2)
            lot_size = max(lot_size, symbol_info.volume_min)
            lot_size = min(lot_size, symbol_info.volume_max)
            
            # Calculate SL and TP
            price = signal["price"]
            sl_pips = 50  # 50 pips stop loss
            tp_pips = 100  # 100 pips take profit
            
            if signal["signal"] == "buy":
                sl = price - (sl_pips * point)
                tp = price + (tp_pips * point)
            else:
                sl = price + (sl_pips * point)
                tp = price - (tp_pips * point)
            
            # Place order
            request = {
                "action": mt4.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": trade_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "comment": f"Auto trade - {signal['reasons'][0] if signal['reasons'] else 'Signal'}",
                "magic": 234000,
            }
            
            result = mt4.order_send(request)
            
            if result.retcode == mt4.TRADE_RETCODE_DONE:
                trade = {
                    "id": result.order,
                    "symbol": symbol,
                    "type": signal["signal"],
                    "lot_size": lot_size,
                    "entry_price": result.price,
                    "sl": sl,
                    "tp": tp,
                    "timestamp": datetime.now().isoformat(),
                    "status": "open",
                    "reasons": signal["reasons"]
                }
                
                self.positions.append(trade)
                logging.info(f"MT4 trade placed: {trade['type']} {trade['lot_size']} lots of {trade['symbol']} at {trade['entry_price']}")
                return True
            else:
                logging.error(f"MT4 trade failed: {result.retcode} - {result.comment}")
                return False
                
        except Exception as e:
            logging.error(f"Error placing MT4 trade: {e}")
            return False
    
    def place_paper_trade(self, signal: Dict, risk_amount: float) -> bool:
        """Place paper trade for simulation"""
        try:
            lot_size = round(risk_amount / 1000, 2)  # Simplified calculation
            
            trade = {
                "id": len(self.paper_trades) + 1,
                "symbol": signal["symbol"],
                "type": signal["signal"],
                "lot_size": lot_size,
                "entry_price": signal["price"],
                "timestamp": datetime.now().isoformat(),
                "status": "open",
                "reasons": signal["reasons"]
            }
            
            self.positions.append(trade)
            self.paper_trades.append(trade)
            
            logging.info(f"Paper trade placed: {trade['type']} {trade['lot_size']} lots of {trade['symbol']} at {trade['entry_price']}")
            return True
            
        except Exception as e:
            logging.error(f"Error placing paper trade: {e}")
            return False
    
    def run_trading_loop(self):
        """Main trading loop"""
        logging.info("Starting MT4 trading loop...")
        
        while self.is_running:
            try:
                # Generate signals for all symbols
                for symbol in self.symbols:
                    signal = self.generate_signal(symbol)
                    
                    if signal["signal"] in ["buy", "sell"] and signal["strength"] >= self.min_signal_strength:
                        logging.info(f"Strong signal detected: {signal}")
                        self.place_trade(signal)
                
                # Monitor existing positions
                self.monitor_positions()
                
                # Print status
                logging.info(f"Account Balance: ${self.account_balance:.2f}, Open Positions: {len(self.positions)}")
                
                # Wait before next cycle
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logging.error(f"Error in trading loop: {e}")
                time.sleep(60)
    
    def monitor_positions(self):
        """Monitor open positions"""
        for position in self.positions.copy():
            try:
                # Get current price
                current_data = self.get_market_data(position["symbol"])
                if current_data.empty:
                    continue
                
                current_price = current_data['Close'].iloc[-1]
                entry_price = position["entry_price"]
                
                # Simple exit conditions for paper trading
                if not MT4_AVAILABLE or not self.mt4_connected:
                    self.monitor_paper_position(position, current_price)
                
            except Exception as e:
                logging.error(f"Error monitoring position: {e}")
    
    def monitor_paper_position(self, position, current_price):
        """Monitor paper trading position"""
        entry_price = position["entry_price"]
        
        # Calculate P&L
        if position["type"] == "buy":
            pnl = (current_price - entry_price) * position["lot_size"] * 100
        else:
            pnl = (entry_price - current_price) * position["lot_size"] * 100
        
        # Simple exit conditions
        profit_target = entry_price * 0.02  # 2% profit target
        stop_loss = entry_price * 0.01      # 1% stop loss
        
        should_close = False
        close_reason = ""
        
        if position["type"] == "buy":
            if current_price >= entry_price + profit_target:
                should_close = True
                close_reason = "Profit target reached"
            elif current_price <= entry_price - stop_loss:
                should_close = True
                close_reason = "Stop loss hit"
        else:  # sell
            if current_price <= entry_price - profit_target:
                should_close = True
                close_reason = "Profit target reached"
            elif current_price >= entry_price + stop_loss:
                should_close = True
                close_reason = "Stop loss hit"
        
        if should_close:
            position["exit_price"] = current_price
            position["pnl"] = pnl
            position["status"] = "closed"
            position["close_reason"] = close_reason
            position["close_timestamp"] = datetime.now().isoformat()
            
            self.account_balance += pnl
            self.positions.remove(position)
            
            logging.info(f"Position closed: {position['symbol']} P&L: ${pnl:.2f} - {close_reason}")
    
    def start(self):
        """Start the trading system"""
        if self.is_running:
            logging.warning("Trading system is already running")
            return
        
        # Try to connect to MT4
        if not self.connect_mt4():
            logging.error("Failed to connect to MT4, continuing in simulation mode")
        
        self.is_running = True
        self.trade_thread = threading.Thread(target=self.run_trading_loop)
        self.trade_thread.start()
        logging.info("MT4 Automated trading system started")
    
    def stop(self):
        """Stop the trading system"""
        self.is_running = False
        if self.trade_thread:
            self.trade_thread.join()
        
        if MT4_AVAILABLE:
            mt4.shutdown()
        
        logging.info("MT4 Automated trading system stopped")
    
    def get_status(self) -> Dict:
        """Get system status"""
        return {
            "running": self.is_running,
            "mt4_connected": self.mt4_connected,
            "account": self.account,
            "server": self.server,
            "balance": self.account_balance,
            "open_positions": len(self.positions),
            "total_trades": len(self.paper_trades) if not MT4_AVAILABLE else 0,
            "positions": self.positions
        }

def main():
    """Main function to run MT4 trading system"""
    print("🎯 MT4 AUTOMATED TRADING SYSTEM")
    print("===============================")
    print("FBS Live Account: 241926287")
    print("Server: FBS-Real-4")
    print("")
    
    system = MT4AutomatedTradingSystem()
    
    try:
        print("🚀 Starting MT4 automated trading system...")
        system.start()
        
        print("\n📊 System is running!")
        print(f"💰 Account: {system.account}")
        print(f"🏢 Server: {system.server}")
        print("📈 Monitoring: XAUUSD, EURUSD, GBPUSD")
        print("⚙️ Risk per trade: 1%")
        print("🔄 Checking signals every 5 minutes")
        print("\nPress Ctrl+C to stop...")
        
        while system.is_running:
            time.sleep(10)
            status = system.get_status()
            if len(status["positions"]) > 0:
                print(f"\n📊 Status: Balance=${status['balance']:.2f}, Open Positions={status['open_positions']}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Stopping MT4 trading system...")
        system.stop()
        
        final_status = system.get_status()
        print(f"\n📊 Final Results:")
        print(f"   MT4 Connected: {final_status['mt4_connected']}")
        print(f"   Final Balance: ${final_status['balance']:.2f}")
        print(f"   Open Positions: {final_status['open_positions']}")

if __name__ == "__main__":
    main()