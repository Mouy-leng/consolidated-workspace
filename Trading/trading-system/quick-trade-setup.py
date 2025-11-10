#!/usr/bin/env python3
"""
Quick Trade Setup - Immediate Trading with Multiple Symbols
Fast automated trading setup for immediate execution
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import json
import time

class QuickTradeSetup:
    def __init__(self):
        self.symbols = {
            "XAUUSD": "GC=F",      # Gold - High volatility
            "EURUSD": "EURUSD=X",  # Major pair
            "GBPUSD": "GBPUSD=X",  # Volatile major
            "USDJPY": "USDJPY=X",  # Trending pair
            "USDCHF": "USDCHF=X",  # Swiss stability
            "AUDUSD": "AUDUSD=X",  # Commodity currency
            "NZDUSD": "NZDUSD=X",  # Risk-on currency
            "USDCAD": "USDCAD=X",  # Oil correlation
            "EURJPY": "EURJPY=X",  # Cross pair
            "GBPJPY": "GBPJPY=X"   # Volatile cross
        }
        
        # FBS Real Account
        self.account = 241926287
        self.server = "FBS-Real-4"
        
        # Aggressive settings for more trades
        self.risk_per_trade = 0.02  # 2% risk
        self.min_signal_strength = 0.6  # Lower threshold
        self.max_positions = 8  # More positions
        
    def quick_analysis(self, symbol: str, yahoo_symbol: str) -> dict:
        """Fast technical analysis for immediate signals"""
        try:
            # Get recent data (last 2 days, 15min intervals)
            data = yf.download(yahoo_symbol, period="2d", interval="15m", progress=False)
            
            if data.empty or len(data) < 20:
                return {"symbol": symbol, "signal": "no_data", "strength": 0}
            
            close = data['Close']
            high = data['High']
            low = data['Low']
            
            current_price = close.iloc[-1]
            
            # Fast RSI (7-period for quicker signals)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=7).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=7).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Quick MACD (8,21,5)
            exp1 = close.ewm(span=8).mean()
            exp2 = close.ewm(span=21).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=5).mean()
            current_macd = macd.iloc[-1]
            current_signal = signal_line.iloc[-1]
            
            # Simple moving averages
            sma10 = close.rolling(window=10).mean()
            sma20 = close.rolling(window=20).mean()
            
            # ATR for SL/TP
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = true_range.rolling(window=10).mean().iloc[-1]
            
            # Signal generation
            signal_strength = 0
            signal_type = "hold"
            reasons = []
            
            # RSI signals (aggressive)
            if current_rsi < 25:
                signal_strength += 0.4
                signal_type = "buy"
                reasons.append(f"RSI oversold ({current_rsi:.1f})")
            elif current_rsi > 75:
                signal_strength += 0.4
                signal_type = "sell"
                reasons.append(f"RSI overbought ({current_rsi:.1f})")
            
            # MACD crossover
            if current_macd > current_signal:
                if signal_type != "sell":
                    signal_strength += 0.3
                    signal_type = "buy"
                    reasons.append("MACD bullish")
            elif current_macd < current_signal:
                if signal_type != "buy":
                    signal_strength += 0.3
                    signal_type = "sell"
                    reasons.append("MACD bearish")
            
            # Price vs MA
            sma10_current = sma10.iloc[-1]
            sma20_current = sma20.iloc[-1]
            
            if current_price > sma10_current > sma20_current:
                if signal_type == "buy":
                    signal_strength += 0.3
                    reasons.append("Price above MAs")
            elif current_price < sma10_current < sma20_current:
                if signal_type == "sell":
                    signal_strength += 0.3
                    reasons.append("Price below MAs")
            
            # Calculate SL/TP
            if signal_type == "buy":
                stop_loss = current_price - (atr * 1.5)
                take_profit = current_price + (atr * 2.5)
            elif signal_type == "sell":
                stop_loss = current_price + (atr * 1.5)
                take_profit = current_price - (atr * 2.5)
            else:
                stop_loss = take_profit = 0
            
            return {
                "symbol": symbol,
                "signal": signal_type,
                "strength": round(min(signal_strength, 1.0), 3),
                "price": round(current_price, 5),
                "rsi": round(current_rsi, 1),
                "macd": round(current_macd, 5),
                "stop_loss": round(stop_loss, 5),
                "take_profit": round(take_profit, 5),
                "atr": round(atr, 5),
                "reasons": reasons,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            
        except Exception as e:
            return {"symbol": symbol, "signal": "error", "strength": 0, "error": str(e)}
    
    def scan_all_symbols(self):
        """Scan all symbols for immediate opportunities"""
        print("🔍 SCANNING ALL SYMBOLS FOR IMMEDIATE OPPORTUNITIES...")
        print("=" * 60)
        
        opportunities = []
        
        for symbol, yahoo_symbol in self.symbols.items():
            print(f"📊 Analyzing {symbol}...", end=" ")
            
            signal = self.quick_analysis(symbol, yahoo_symbol)
            
            if signal["signal"] in ["buy", "sell"]:
                strength_pct = signal["strength"] * 100
                print(f"🎯 {signal['signal'].upper()} ({strength_pct:.1f}%)")
                opportunities.append(signal)
            else:
                print("⏸️ HOLD")
            
            time.sleep(0.5)  # Brief delay
        
        return opportunities
    
    def generate_trade_plan(self, opportunities):
        """Generate immediate trade execution plan"""
        if not opportunities:
            print("\n❌ No immediate trading opportunities found")
            return
        
        print(f"\n🎯 FOUND {len(opportunities)} IMMEDIATE OPPORTUNITIES!")
        print("=" * 50)
        
        for i, opp in enumerate(opportunities, 1):
            if opp["strength"] >= self.min_signal_strength:
                print(f"\n🚀 TRADE #{i}: {opp['symbol']} {opp['signal'].upper()}")
                print(f"   💰 Entry: {opp['price']}")
                print(f"   ⛔ Stop Loss: {opp['stop_loss']}")
                print(f"   🎯 Take Profit: {opp['take_profit']}")
                print(f"   📊 Strength: {opp['strength']*100:.1f}%")
                print(f"   📈 RSI: {opp['rsi']} | MACD: {opp['macd']}")
                print(f"   📝 Reasons: {', '.join(opp['reasons'])}")
                
                # Calculate position size
                risk_amount = 1000 * self.risk_per_trade  # Assuming $1000 account
                pip_distance = abs(opp['price'] - opp['stop_loss']) / 0.0001
                lot_size = round(risk_amount / (pip_distance * 1), 2)  # Simplified
                lot_size = max(0.01, min(1.0, lot_size))
                
                print(f"   📏 Suggested Lot Size: {lot_size}")
        
        print(f"\n📋 EXECUTION INSTRUCTIONS:")
        print(f"   🏦 Account: {self.account}")
        print(f"   🖥️ Server: {self.server}")
        print(f"   💎 Risk per trade: {self.risk_per_trade*100}%")
        print(f"   📊 Total opportunities: {len(opportunities)}")
        
        return opportunities

def main():
    print("⚡ QUICK TRADE SETUP - IMMEDIATE OPPORTUNITIES")
    print("=" * 55)
    print("🎯 Scanning for HIGH-PROBABILITY trades RIGHT NOW!")
    print("💰 FBS Real Account 241926287")
    print("")
    
    scanner = QuickTradeSetup()
    
    # Scan for opportunities
    opportunities = scanner.scan_all_symbols()
    
    # Generate trade plan
    scanner.generate_trade_plan(opportunities)
    
    print("\n" + "=" * 55)
    print("⚡ READY FOR IMMEDIATE EXECUTION!")
    print("🚀 Use these signals to place trades manually or")
    print("🤖 Start the enhanced auto trading system")
    print("📊 Run: python enhanced-auto-trading.py")

if __name__ == "__main__":
    main()