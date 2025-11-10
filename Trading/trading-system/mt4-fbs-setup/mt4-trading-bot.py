#!/usr/bin/env python3
"""
MT4 Trading Bot for FBS Account
"""

import json
import time
import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf

class MT4TradingBot:
    def __init__(self):
        # Load FBS MT4 config
        with open("fbs_mt4_config.json", 'r') as f:
            self.config = json.load(f)
        
        self.login = self.config["login"]
        self.server = self.config["server"]
        self.company = self.config["company"]
        self.balance = 1000.0  # Starting balance
        self.positions = []
        self.signals_log = []
        
    def get_live_data(self, symbol="EURUSD"):
        """Get live market data using yfinance as proxy"""
        try:
            # Map MT4 symbols to Yahoo Finance
            symbol_map = {
                "EURUSD": "EURUSD=X",
                "GBPUSD": "GBPUSD=X", 
                "USDJPY": "USDJPY=X",
                "XAUUSD": "GC=F",  # Gold futures
                "XAGUSD": "SI=F"   # Silver futures
            }
            
            yahoo_symbol = symbol_map.get(symbol, f"{symbol}=X")
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period="1d", interval="5m")
            
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                return {
                    "symbol": symbol,
                    "bid": current_price - 0.0001,
                    "ask": current_price + 0.0001,
                    "time": datetime.now(),
                    "data": data
                }
        except Exception as e:
            print(f"Error getting data for {symbol}: {e}")
        
        return None
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def generate_signal(self, symbol):
        """Generate trading signal based on RSI"""
        market_data = self.get_live_data(symbol)
        if not market_data:
            return None
        
        data = market_data["data"]
        if len(data) < 20:
            return None
        
        # Calculate indicators
        rsi = self.calculate_rsi(data['Close'])
        current_price = market_data["ask"]
        
        signal = None
        
        # RSI-based signals
        if rsi < 30:  # Oversold
            signal = {
                "symbol": symbol,
                "action": "BUY",
                "price": current_price,
                "lots": 0.01,
                "rsi": rsi,
                "time": datetime.now(),
                "reason": "RSI Oversold"
            }
        elif rsi > 70:  # Overbought
            signal = {
                "symbol": symbol,
                "action": "SELL", 
                "price": current_price,
                "lots": 0.01,
                "rsi": rsi,
                "time": datetime.now(),
                "reason": "RSI Overbought"
            }
        
        return signal
    
    def simulate_order(self, signal):
        """Simulate order execution"""
        if not signal:
            return None
        
        order = {
            "ticket": len(self.positions) + 1000,
            "symbol": signal["symbol"],
            "action": signal["action"],
            "lots": signal["lots"],
            "open_price": signal["price"],
            "open_time": signal["time"],
            "status": "OPEN",
            "profit": 0.0,
            "reason": signal["reason"]
        }
        
        self.positions.append(order)
        self.signals_log.append(signal)
        
        print(f"ORDER EXECUTED: {signal['action']} {signal['symbol']} {signal['lots']} lots at {signal['price']:.5f}")
        print(f"Reason: {signal['reason']} (RSI: {signal['rsi']:.1f})")
        
        return order
    
    def update_positions(self):
        """Update open positions with current P&L"""
        for position in self.positions:
            if position["status"] == "OPEN":
                market_data = self.get_live_data(position["symbol"])
                if market_data:
                    current_price = market_data["bid"] if position["action"] == "BUY" else market_data["ask"]
                    
                    if position["action"] == "BUY":
                        position["profit"] = (current_price - position["open_price"]) * 100000 * position["lots"]
                    else:
                        position["profit"] = (position["open_price"] - current_price) * 100000 * position["lots"]
    
    def close_position(self, ticket, reason="Manual"):
        """Close position by ticket"""
        for position in self.positions:
            if position["ticket"] == ticket and position["status"] == "OPEN":
                position["status"] = "CLOSED"
                position["close_time"] = datetime.now()
                position["close_reason"] = reason
                
                print(f"POSITION CLOSED: {position['symbol']} Profit: ${position['profit']:.2f}")
                return True
        return False
    
    def get_account_summary(self):
        """Get account summary"""
        total_profit = sum(pos["profit"] for pos in self.positions if pos["status"] == "OPEN")
        open_positions = len([pos for pos in self.positions if pos["status"] == "OPEN"])
        
        return {
            "login": self.login,
            "server": self.server,
            "company": self.company,
            "balance": self.balance,
            "equity": self.balance + total_profit,
            "profit": total_profit,
            "open_positions": open_positions,
            "total_orders": len(self.positions)
        }
    
    def run_bot(self, symbols=["EURUSD", "GBPUSD", "XAUUSD"]):
        """Run the trading bot"""
        print("FBS MT4 Trading Bot Started")
        print("=" * 30)
        print(f"Account: {self.login}")
        print(f"Server: {self.server}")
        print(f"Company: {self.company}")
        print(f"Symbols: {', '.join(symbols)}")
        
        try:
            while True:
                print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Check each symbol for signals
                for symbol in symbols:
                    signal = self.generate_signal(symbol)
                    if signal:
                        # Check if we already have a position in this symbol
                        has_position = any(
                            pos["symbol"] == symbol and pos["status"] == "OPEN" 
                            for pos in self.positions
                        )
                        
                        if not has_position:
                            self.simulate_order(signal)
                
                # Update positions
                self.update_positions()
                
                # Display account summary
                summary = self.get_account_summary()
                print(f"Balance: ${summary['balance']:.2f} | Equity: ${summary['equity']:.2f} | Profit: ${summary['profit']:.2f}")
                print(f"Open Positions: {summary['open_positions']}")
                
                # Display open positions
                for pos in self.positions:
                    if pos["status"] == "OPEN":
                        print(f"  {pos['symbol']} {pos['action']} {pos['lots']} lots | P&L: ${pos['profit']:.2f}")
                
                # Wait 1 minute
                time.sleep(60)
                
        except KeyboardInterrupt:
            print("\nBot stopped by user")
            
            # Save trading log
            log_data = {
                "account": summary,
                "positions": self.positions,
                "signals": self.signals_log
            }
            
            with open(f"mt4_trading_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
                json.dump(log_data, f, indent=2, default=str)
            
            print("Trading log saved")

def main():
    bot = MT4TradingBot()
    bot.run_bot()

if __name__ == "__main__":
    main()