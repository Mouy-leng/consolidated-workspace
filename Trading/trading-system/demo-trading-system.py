#!/usr/bin/env python3
"""
Demo Trading System - Works without MT5 connection
Test version for signal generation and paper trading
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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('demo_trading.log'),
        logging.StreamHandler()
    ]
)

class DemoTradingSystem:
    def __init__(self):
        self.account_balance = 10000.0  # Demo account
        self.is_running = False
        self.positions = []
        self.signals = []
        self.risk_per_trade = 0.02  # 2%
        self.max_positions = 3
        self.min_signal_strength = 0.7
        
        # Trading parameters
        self.symbols = ["XAUUSD", "EURUSD", "GBPUSD"]
        self.paper_trades = []
        
        logging.info("Demo Trading System initialized")
        logging.info(f"Account Balance: ${self.account_balance}")
        
    def get_market_data(self, symbol: str) -> pd.DataFrame:
        """Get market data using Yahoo Finance"""
        try:
            # Convert symbol for Yahoo Finance
            yahoo_symbol = self.convert_symbol_to_yahoo(symbol)
            
            # Get data
            data = yf.download(yahoo_symbol, period="5d", interval="15m")
            
            if data.empty:
                logging.warning(f"No data available for {symbol}")
                return pd.DataFrame()
            
            return data
            
        except Exception as e:
            logging.error(f"Error getting market data for {symbol}: {e}")
            return pd.DataFrame()
    
    def convert_symbol_to_yahoo(self, symbol: str) -> str:
        """Convert MT5 symbol to Yahoo Finance symbol"""
        conversions = {
            "XAUUSD": "GC=F",  # Gold futures
            "EURUSD": "EURUSD=X",
            "GBPUSD": "GBPUSD=X",
            "USDJPY": "USDJPY=X",
            "USDCHF": "USDCHF=X"
        }
        return conversions.get(symbol, symbol)
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        if len(data) < period:
            return pd.Series()
        
        close = data['Close']
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, data: pd.DataFrame) -> Dict:
        """Calculate MACD indicator"""
        if len(data) < 26:
            return {"macd": pd.Series(), "signal": pd.Series(), "histogram": pd.Series()}
        
        close = data['Close']
        exp1 = close.ewm(span=12).mean()
        exp2 = close.ewm(span=26).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()
        histogram = macd - signal
        
        return {"macd": macd, "signal": signal, "histogram": histogram}
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20) -> Dict:
        """Calculate Bollinger Bands"""
        if len(data) < period:
            return {"upper": pd.Series(), "middle": pd.Series(), "lower": pd.Series()}
        
        close = data['Close']
        middle = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        upper = middle + (std * 2)
        lower = middle - (std * 2)
        
        return {"upper": upper, "middle": middle, "lower": lower}
    
    def generate_signal(self, symbol: str) -> Dict:
        """Generate trading signal for a symbol"""
        try:
            data = self.get_market_data(symbol)
            if data.empty:
                return {"symbol": symbol, "signal": "no_data", "strength": 0, "price": 0}
            
            current_price = data['Close'].iloc[-1]
            
            # Technical indicators
            rsi = self.calculate_rsi(data)
            macd_data = self.calculate_macd(data)
            bb_data = self.calculate_bollinger_bands(data)
            
            if rsi.empty or macd_data["macd"].empty:
                return {"symbol": symbol, "signal": "insufficient_data", "strength": 0, "price": current_price}
            
            # Signal logic
            current_rsi = rsi.iloc[-1]
            current_macd = macd_data["macd"].iloc[-1]
            current_signal = macd_data["signal"].iloc[-1]
            
            signal_strength = 0
            signal_type = "hold"
            reasons = []
            
            # RSI signals
            if current_rsi < 30:
                signal_strength += 0.3
                signal_type = "buy"
                reasons.append("RSI oversold")
            elif current_rsi > 70:
                signal_strength += 0.3
                signal_type = "sell"
                reasons.append("RSI overbought")
            
            # MACD signals
            if current_macd > current_signal:
                signal_strength += 0.2
                if signal_type != "sell":
                    signal_type = "buy"
                reasons.append("MACD bullish")
            elif current_macd < current_signal:
                signal_strength += 0.2
                if signal_type != "buy":
                    signal_type = "sell"
                reasons.append("MACD bearish")
            
            # Bollinger Bands
            if not bb_data["lower"].empty:
                current_bb_lower = bb_data["lower"].iloc[-1]
                current_bb_upper = bb_data["upper"].iloc[-1]
                
                if current_price <= current_bb_lower:
                    signal_strength += 0.2
                    if signal_type != "sell":
                        signal_type = "buy"
                    reasons.append("Price at BB lower")
                elif current_price >= current_bb_upper:
                    signal_strength += 0.2
                    if signal_type != "buy":
                        signal_type = "sell"
                    reasons.append("Price at BB upper")
            
            # Additional confirmation
            if len(reasons) >= 2:
                signal_strength += 0.1
            
            return {
                "symbol": symbol,
                "signal": signal_type,
                "strength": round(signal_strength, 2),
                "price": current_price,
                "rsi": round(current_rsi, 2),
                "reasons": reasons,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating signal for {symbol}: {e}")
            return {"symbol": symbol, "signal": "error", "strength": 0, "price": 0}
    
    def place_demo_trade(self, signal: Dict) -> bool:
        """Place a demo trade based on signal"""
        try:
            if signal["strength"] < self.min_signal_strength:
                logging.info(f"Signal strength {signal['strength']} below minimum {self.min_signal_strength}")
                return False
            
            if len(self.positions) >= self.max_positions:
                logging.info(f"Maximum positions ({self.max_positions}) reached")
                return False
            
            # Calculate position size
            risk_amount = self.account_balance * self.risk_per_trade
            
            # Simulate lot size calculation
            lot_size = round(risk_amount / 1000, 2)  # Simplified calculation
            
            # Create trade
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
            
            logging.info(f"Demo trade placed: {trade['type']} {trade['lot_size']} lots of {trade['symbol']} at {trade['entry_price']}")
            
            return True
            
        except Exception as e:
            logging.error(f"Error placing demo trade: {e}")
            return False
    
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
                
                # Calculate P&L
                if position["type"] == "buy":
                    pnl = (current_price - entry_price) * position["lot_size"] * 100
                else:
                    pnl = (entry_price - current_price) * position["lot_size"] * 100
                
                # Simple exit conditions (demo)
                profit_target = entry_price * 0.01  # 1% profit target
                stop_loss = entry_price * 0.005     # 0.5% stop loss
                
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
                
            except Exception as e:
                logging.error(f"Error monitoring position: {e}")
    
    def run_trading_loop(self):
        """Main trading loop"""
        logging.info("Starting demo trading loop...")
        
        while self.is_running:
            try:
                # Generate signals for all symbols
                for symbol in self.symbols:
                    signal = self.generate_signal(symbol)
                    
                    if signal["signal"] in ["buy", "sell"] and signal["strength"] >= self.min_signal_strength:
                        logging.info(f"Signal: {signal}")
                        self.place_demo_trade(signal)
                
                # Monitor existing positions
                self.monitor_positions()
                
                # Print status
                logging.info(f"Account Balance: ${self.account_balance:.2f}, Open Positions: {len(self.positions)}")
                
                # Wait before next cycle
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logging.error(f"Error in trading loop: {e}")
                time.sleep(10)
    
    def start(self):
        """Start the demo trading system"""
        if self.is_running:
            logging.warning("Demo trading system is already running")
            return
        
        self.is_running = True
        self.trade_thread = threading.Thread(target=self.run_trading_loop)
        self.trade_thread.start()
        logging.info("Demo trading system started")
    
    def stop(self):
        """Stop the demo trading system"""
        self.is_running = False
        if self.trade_thread:
            self.trade_thread.join()
        logging.info("Demo trading system stopped")
    
    def get_status(self) -> Dict:
        """Get system status"""
        return {
            "running": self.is_running,
            "balance": self.account_balance,
            "open_positions": len(self.positions),
            "total_trades": len(self.paper_trades),
            "positions": self.positions
        }

def main():
    """Main function to run demo trading system"""
    print("🎯 DEMO TRADING SYSTEM")
    print("=====================")
    print("This system works without MT5 connection for testing")
    print("")
    
    system = DemoTradingSystem()
    
    try:
        print("Starting demo trading system...")
        system.start()
        
        print("\n📊 Demo system is running!")
        print("💰 Starting balance: $10,000")
        print("📈 Monitoring: XAUUSD, EURUSD, GBPUSD")
        print("⚙️ Risk per trade: 2%")
        print("🔄 Checking signals every minute")
        print("\nPress Ctrl+C to stop...")
        
        while system.is_running:
            time.sleep(5)
            status = system.get_status()
            if len(status["positions"]) > 0:
                print(f"\n📊 Status: Balance=${status['balance']:.2f}, Open Positions={status['open_positions']}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Stopping demo trading system...")
        system.stop()
        
        final_status = system.get_status()
        print(f"\n📊 Final Results:")
        print(f"   Final Balance: ${final_status['balance']:.2f}")
        print(f"   Total Trades: {final_status['total_trades']}")
        print(f"   P&L: ${final_status['balance'] - 10000:.2f}")
        
        if system.paper_trades:
            print(f"\n📈 Trade History:")
            for trade in system.paper_trades[-5:]:  # Show last 5 trades
                pnl = trade.get('pnl', 0)
                print(f"   {trade['symbol']} {trade['type']}: ${pnl:.2f}")

if __name__ == "__main__":
    main()